import os

import nltk
import json
from nltk.wsd import lesk
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS

# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')


app = Flask(__name__, static_folder='deploy/web')
CORS(app)


# Route for serving React app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


def basic_lesk(sentence, ambiguous_word):
    """
    Use the Lesk algorithm to find the meaning of an ambiguous word within a sentence.

    :param sentence: The sentence containing the ambiguous word.
    :param ambiguous_word: The word for which we want to disambiguate the meaning.
    :return: The meaning of the ambiguous word.
    """
    # Tokenize the sentence
    tokens = tokenize_and_lemmatize(sentence)

    # Apply the Lesk algorithm
    synset = lesk(tokens, ambiguous_word)

    # Return the definition of the word if a synset is found, otherwise return None
    return synset, tokens


def tokenize_and_lemmatize(text):
    lemmatizer = nltk.WordNetLemmatizer()
    tokens = word_tokenize(text)
    return [lemmatizer.lemmatize(token.lower()) for token in tokens]


def get_signature(synset):
    # Get the words from the definition and examples of the synset
    signature = tokenize_and_lemmatize(synset.definition())
    for example in synset.examples():
        signature.extend(tokenize_and_lemmatize(example))
    return set(signature)


def get_related_signature(synset):
    # Get the words from the definitions and examples of hypernyms and hyponyms
    related_synsets = synset.hypernyms() + synset.hyponyms()
    related_signature = []
    for related_synset in related_synsets:
        related_signature.extend(tokenize_and_lemmatize(related_synset.definition()))
        for example in related_synset.examples():
            related_signature.extend(tokenize_and_lemmatize(example))
    return set(related_signature)


def enhanced_signature(synset):
    signature = get_signature(synset)
    related_signature = get_related_signature(synset)
    # Combine the original signature with the related signature
    return signature.union(related_signature), signature, related_signature


def advanced_lesk(context_sentence, ambiguous_word, pos=None):
    best_sense = None
    max_overlap = 0
    context = set(tokenize_and_lemmatize(context_sentence))

    for synset in wn.synsets(ambiguous_word, pos=pos):
        signature, original_sig, related_sig = enhanced_signature(synset)
        overlap = len(context.intersection(signature))

        if overlap > max_overlap:
            max_overlap = overlap
            best_sense = synset
            best_signature = signature
            best_original_sig = original_sig
            best_related_sig = related_sig

    return best_sense, best_signature, best_original_sig, best_related_sig, list(context)


def word_info(word):
    """
    Get all the hypernyms and hyponyms for all synsets of a word in JSON format.

    :param word: str. The word to get the hypernyms and hyponyms for.
    :return: str. A JSON string with hypernyms and hyponyms including synset names and definitions.
    """
    # Initialize a list to hold the hypernym and hyponym information
    synset_relations = []

    # Iterate over all synsets of the word
    for synset in wn.synsets(word):
        # Get hypernyms and hyponyms for the current synset
        hypernyms = [{'sense': hypernym.name(), 'definition': hypernym.definition()} for hypernym in synset.hypernyms()]
        hyponyms = [{'sense': hyponym.name(), 'definition': hyponym.definition()} for hyponym in synset.hyponyms()]

        # Store them in the list with the synset's name and definition
        synset_relations.append({
            'sense': synset.name(),
            'definition': synset.definition(),
            'hypernyms': hypernyms,
            'hyponyms': hyponyms
        })

    # Convert the list to JSON format
    return synset_relations


@app.route('/api/basic_lesk', methods=['POST'])
def get_lesk():
    if not request.is_json:
        return jsonify({"error": "Request payload must be in JSON format."}), 400

    context_sentence = request.json.get('context_sentence')
    ambiguous_word = request.json.get('ambiguous_word')

    if not context_sentence or not ambiguous_word:
        return jsonify(
            {"error": "Both 'context_sentence' and 'ambiguous_word' fields are required in the JSON payload."}), 400

    sense, tokens = basic_lesk(context_sentence, ambiguous_word)
    if not sense:
        return jsonify(
            {"error": f"No sense found for the word: {ambiguous_word}"}), 404

    result = {
        "sense": sense.name(),
        "definition": sense.definition(),
        "cleanedSentence": " ".join(tokens)
    }
    response = jsonify(result)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/api/extended_lesk', methods=['POST'])
def get_extended_lesk():
    if not request.is_json:
        return jsonify({"error": "Request payload must be in JSON format."}), 400

    context_sentence = request.json.get('context_sentence')
    ambiguous_word = request.json.get('ambiguous_word')

    if not context_sentence or not ambiguous_word:
        return jsonify(
            {"error": "Both 'context_sentence' and 'ambiguous_word' fields are required in the JSON payload."}), 400

    sense, signature, original_signature, related_signature, tokens = advanced_lesk(context_sentence, ambiguous_word)

    if not sense:
        return jsonify(
            {"error": f"No sense found for the word: {ambiguous_word}"}), 404

    result = {
        "sense": str(sense.name()),
        "definition": str(sense.definition()),
        "original_signature": list(original_signature),
        "related_signature": list(related_signature),
        "cleanedSentence": " ".join(tokens)
    }
    response = jsonify(result)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/api/word_info/<word>', methods=['GET'])
def get_word_info(word):
    if not word:
        return jsonify(
            {"error": "No word provided."}), 400
    result = word_info(word)
    response = jsonify(result)
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ == '__main__':
    app.run(use_reloader=True, port=5000, threaded=True)

# Define a list of examples with sentences and their ambiguous words
examples = [
    ("Hard day is coming", "hard"),
    ("Sam was born in May", "May"),
    ("The exam was too hard to pass", "hard"),
    ("I am going to bank with some money", "bank"),
    ("I was walking by the bank of river", "bank"),
    (
        "The bank can guarantee deposits will eventually cover future tuition costs because it invests in adjustable-rate mortgage securities.",
        "bank"),
]
#
# # Iterate over each example and apply both the basic and advanced Lesk algorithms
# for sentence, ambiguous_word in examples:
#
#     print(f"Sentence: '{sentence}'\nAmbiguous Word: '{ambiguous_word}'")
#
#     # Basic Lesk
#     print("Basic Lesk: ")
#     sense = basic_lesk(sentence, ambiguous_word)
#     if sense:
#         print(f"- Definition: {sense.definition()}.")
#         print(f"- Sense: {sense.name()}")
#     else:
#         print("No sense found for the word.")
#     # Advanced Lesk
#     print("Advanced Lesk: ")
#     best_sense, best_signature, best_original_sig, best_related_sig = advanced_lesk(sentence, ambiguous_word)
#     if best_sense:
#         print(f"- Definition: {best_sense.definition()}")
#         print(f"- Sense: {best_sense.name()}")
#         print(f"- Original Signature: {best_original_sig}")
#         print(f"- Related Signature (from hypernyms and hyponyms): {best_related_sig}")
#     else:
#         print("No sense found for the word.")
#     print("-----------")  # Separator between each example run
#
# # Example usage:
# word = "bank"
# related_synsets_json = get_hypernyms_hyponyms_json(word)
# print(related_synsets_json)
