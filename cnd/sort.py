import json
from typing import List, Set, Tuple
import unicodedata
import math

from cnd.utils import Sentence


def remove_accents(s: str):
    """
    Removes all accents from a string.

    Args:
        s (str): The string to be processed.

    Returns:
        str: The string with accents removed.
    """
    nfkd_form = unicodedata.normalize("NFKD", s)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def sentence_word_trigrams(
    text,
) -> Tuple[Set[Tuple[str, str, str]], List[Set[Tuple[str, str, str]]]]:
    """
    Create trigrams for all words in the setnence, and also for each word individually.
    """
    words = text.split()
    sentence_trigrams: Set[Tuple[str, str, str]] = set()
    word_trigrams: List[Set[Tuple[str, str, str]]] = []
    for word in words:
        trigrams = set()
        if len(word) < 3:
            continue
        for i in range(len(word) - 2):
            trigram = (word[i], word[i + 1], word[i + 2])
            trigrams.add(trigram)
            sentence_trigrams.add(trigram)
        word_trigrams.append(trigrams)
    return sentence_trigrams, word_trigrams


def compute_trigram_frequencies(
    sentence_word_trigram_list: List[Set[Tuple[str, str, str]]],
) -> dict:
    """
    Compute the frequency of each trigram in the sentence trigrams.
    """
    frequencies = {}
    for sentence_trigrams in sentence_word_trigram_list:
        for trigram in set(t for t in sentence_trigrams):
            frequencies[trigram] = frequencies.get(trigram, 0) + 1
    return frequencies


def sentence_priority(
    word_trigrams: List[Set[Tuple[str, str, str]]], trigram_frequencies: dict
) -> float:
    """
    Compute a priority score for the sentence based on the frequencies of its word trigrams.
    Lower scores indicate higher priority (rarer trigrams).
    """
    score = 0
    for trigrams in word_trigrams:
        word_score = 0
        for trigram in trigrams:
            word_score += math.tanh(trigram_frequencies.get(trigram, 0) / 200) / len(
                trigrams
            )

        score += (
            word_score * word_score / len(word_trigrams)
        )  # square to emphasize rare words
    return score


def simplify_phonetics(s: str):
    """
    Simplify phonetics by removing diacritics and special characters.
    """
    # s = s.encode("ascii", "ignore").decode("utf-8")

    s = s.replace(":", "")  # length mark

    return remove_accents(s)


def sort_sentences(sentences: List[Sentence]) -> List[Sentence]:
    """
    Sort sentences based on the rarity of their trigrams.
    """
    all_sentence_trigrams: List[Set[Tuple[str, str, str]]] = []
    sentence_word_trigram_list: List[List[Set[Tuple[str, str, str]]]] = []

    for sentence in sentences:
        sentence_trigrams, word_trigrams = sentence_word_trigrams(
            simplify_phonetics(sentence.phonetic)
        )
        all_sentence_trigrams.append(sentence_trigrams)
        sentence_word_trigram_list.append(word_trigrams)

    trigram_frequencies = compute_trigram_frequencies(all_sentence_trigrams)

    sentence_scores = []
    for i, word_trigrams in enumerate(sentence_word_trigram_list):
        score = sentence_priority(word_trigrams, trigram_frequencies)
        sentence_scores.append((score, i))

    json.dump(
        [s for s, _ in sentence_scores],
        open("data/cnd/sentence_scores.json", "w"),
        indent=2,
    )
    json.dump(
        {str(t): freq for t, freq in trigram_frequencies.items()},
        open("data/cnd/trigram_frequencies.json", "w"),
        indent=2,
    )

    # Sort by score (ascending) and then by original index to maintain stability
    sentence_scores.sort(key=lambda x: x[0])

    sorted_sentences = [sentences[i] for _, i in sentence_scores]
    return sorted_sentences
