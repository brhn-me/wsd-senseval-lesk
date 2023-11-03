import nltk
from nltk.wsd import lesk
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize


def basic_lesk(sentence, ambiguous_word):
    """
    Use the Lesk algorithm to find the meaning of an ambiguous word within a sentence.

    :param sentence: The sentence containing the ambiguous word.
    :param ambiguous_word: The word for which we want to disambiguate the meaning.
    :return: The meaning of the ambiguous word.
    """
    # Tokenize the sentence
    tokens = word_tokenize(sentence)

    # Apply the Lesk algorithm
    synset = lesk(tokens, ambiguous_word)

    # Return the definition of the word if a synset is found, otherwise return None
    return synset


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

    return best_sense, best_signature, best_original_sig, best_related_sig


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

# Iterate over each example and apply both the basic and advanced Lesk algorithms
for sentence, ambiguous_word in examples:

    print(f"Sentence: '{sentence}'\nAmbiguous Word: '{ambiguous_word}'")

    # Basic Lesk
    print("Basic Lesk: ")
    sense = basic_lesk(sentence, ambiguous_word)
    if sense:
        print(f"- Definition: {sense.definition()}.")
        print(f"- Sense: {sense.name()}")
    else:
        print("No sense found for the word.")
    # Advanced Lesk
    print("Advanced Lesk: ")
    best_sense, best_signature, best_original_sig, best_related_sig = advanced_lesk(sentence, ambiguous_word)
    if best_sense:
        print(f"- Definition: {best_sense.definition()}")
        print(f"- Sense: {best_sense.name()}")
        print(f"- Original Signature: {best_original_sig}")
        print(f"- Related Signature (from hypernyms and hyponyms): {best_related_sig}")
    else:
        print("No sense found for the word.")
    print("-----------")  # Separator between each example run



import json


def get_hypernyms_hyponyms_json(word):
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
    return json.dumps(synset_relations, indent=4)

# Example usage:
word = "bank"
related_synsets_json = get_hypernyms_hyponyms_json(word)
print(related_synsets_json)
