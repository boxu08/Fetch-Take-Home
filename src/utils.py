"""
Script Name: utils.py
Author: Bo Xu
Date: July 26, 2023

Description:
This script defines util functions used in offer searching.
"""
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import string


def stem_word(word):
    stemmer = PorterStemmer()
    return stemmer.stem(word)


def remove_punctuations(input_string: str):
    """
    This function removes punctuations from an input string.

    Args:
        input_string (str): an input string.

    Returns:
        str: a string with punctuations removed.
    """

    # Create a translation table to remove punctuations
    translator = str.maketrans('', '', string.punctuation)

    # Use the translate method to remove punctuations from the string
    return input_string.translate(translator)


def phrase_similarity(target_phrase: str, input_phrase: str):
    """
    This function calculates the Jaccard similarity between two phrases.

    Args:
        target_phrase (str): a target phrase.
        input_phrase (str): an input phrase.

    Returns:
        float: The Jaccard similarity
    """

    # return nan if either parameter is not a string
    if type(target_phrase) != str or type(input_phrase) != str:
        return float("nan")

    stop_words = set(stopwords.words('english'))

    # Tokenize and preprocess the input category
    input_phrase = remove_punctuations(input_phrase)
    words = input_phrase.split(' ')
    stemmed_words = [stem_word(word) for word in words]
    input_phrase = ' '.join(stemmed_words)
    input_tokens = set(word_tokenize(input_phrase.lower()))
    input_tokens = input_tokens - stop_words

    # Tokenize and preprocess the target category
    target_phrase = remove_punctuations(target_phrase)
    words = target_phrase.split(' ')
    stemmed_words = [stem_word(word) for word in words]
    target_phrase = ' '.join(stemmed_words)
    target_tokens = set(word_tokenize(target_phrase.lower()))
    target_tokens = target_tokens - stop_words

    # Calculate Jaccard similarity between input tokens and target tokens
    jaccard_similarity = len(input_tokens.intersection(target_tokens)) / len(input_tokens.union(target_tokens))

    return jaccard_similarity
