import nltk

# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')

from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.wsd import lesk

from flask import Flask, jsonify, request, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

sample1 = 'The exam was too hard for the students to pass'
sample2 = 'I am going to the bank with some money'


def extend_signature(signature):
    lemma_names_set = set()
    stop_words = set(stopwords.words("english"))
    signature = signature - stop_words

    for term in signature:
        lemma_names_set.add(term)
        synsets = wordnet.synsets(term)

        # for each synset, find its hyponyms and hypernyms
        for synset in synsets:
            hyponyms_set = set()
            hypernyms_set = set()

            hyponyms_set.update(synset.hyponyms())
            hypernyms_set.update(synset.hypernyms())

            hyponyms_and_hypernyms_set = hyponyms_set.union(hypernyms_set)

            for synset in hyponyms_and_hypernyms_set:
                for lemma in synset.lemmas():
                    l = lemma.name().lower().replace('_', ' ').replace('-', ' ')
                    words = l.split()
                    lemma_names_set.update(words)

    # return extended signature
    return lemma_names_set


def calculate_extended_lesk(context_sentence, ambigious_word):
    max_overlap = 0
    lesk_sense = None
    lesk_definition = ''
    context_words = nltk.word_tokenize(context_sentence)
    context_words = set(context_words)

    for sense in wordnet.synsets(ambigious_word):
        # print(f"sense: {sense}")
        signature = set()
        sense_definitions = nltk.word_tokenize(sense.definition())
        # print(f'sense_definitions : {sense_definitions}')
        signature = signature.union(set(sense_definitions))
        signature = signature.union(set(sense.lemma_names()))
        # print(f"examples: {sense.examples()}")
        for example in sense.examples():
            signature = signature.union(set(example.split()))
        # print(f"signature: {signature}")
        signature = extend_signature(signature)
        # print(f"extended_signature: {signature}")
        overlap = len(context_words.intersection(signature))
        if overlap > max_overlap:
            lesk_sense = sense
            max_overlap = overlap
            lesk_definition = sense.definition()
    return {
        "sense": str(lesk_sense),
        "definition": lesk_definition
    }


def calculate_lesk(context_sentence, ambigious_word):
    sense = lesk(("" + context_sentence).split(), ambigious_word)
    return {
        "sense": str(sense),
        "definition": sense.definition()
    }


@app.route('/lesk', methods=['POST'])
def get_lesk():
    if not request.is_json:
        return jsonify({"error": "Request payload must be in JSON format."}), 400

    context_sentence = request.json.get('context_sentence')
    ambiguous_word = request.json.get('ambiguous_word')

    if not context_sentence or not ambiguous_word:
        return jsonify(
            {"error": "Both 'context_sentence' and 'ambiguous_word' fields are required in the JSON payload."}), 400

    result = calculate_lesk(context_sentence, ambiguous_word)
    response = jsonify(result)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/extended_lesk', methods=['POST'])
def get_extended_lesk():
    if not request.is_json:
        return jsonify({"error": "Request payload must be in JSON format."}), 400

    context_sentence = request.json.get('context_sentence')
    ambiguous_word = request.json.get('ambiguous_word')

    if not context_sentence or not ambiguous_word:
        return jsonify(
            {"error": "Both 'context_sentence' and 'ambiguous_word' fields are required in the JSON payload."}), 400

    result = calculate_extended_lesk(context_sentence, ambiguous_word)
    response = jsonify(result)
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ == '__main__':
    app.run(debug=True)
