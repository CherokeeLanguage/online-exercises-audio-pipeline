"""
Compute the most common roots based on the CED and the Bible
"""

from traceback import print_exc, print_tb
from typing import Generator
from parsing.prefixes import all_parses


def count_roots_in_sentence(sentence: str) -> dict[str, int]:
    counts = {}
    for word in sentence.split():
        if len(word) <= 3:
            continue
        try:
            parses = sorted(all_parses(word), key=lambda p: len(p.root))
            # if len(parses) == 0:
            #     continue

            # parse = parses[0]
            for parse in parses:
                if len(parse.root) > 1:
                    counts[parse.root] = counts.get(parse.root, 0) + 1
        except Exception as e:
            print_exc()
            continue

    return counts


def count_roots_with_dict(
    sentences: Generator[str, None, None], root_dict: set[str]
) -> dict[str, int]:
    counts = {}
    for sentence in sentences:
        sentence_counts = count_roots_in_sentence(sentence)
        counts.update(
            {
                root: count + counts.get(root, 0)
                for root, count in sentence_counts.items()
                if root in root_dict
            }
        )

    return counts
