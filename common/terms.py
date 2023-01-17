"""
Python module for interfacing with a terms CSV (ie. the CSV referenced by `DatasetMetadata.terms`)
"""
from csv import DictReader
from dataclasses import dataclass

from common.structs import DatasetMetadata

TERM_FIELDS = [
    "has_problems",
    "vocab_set",
    "english",
    "cherokee",
    "syllabary",
    "audio",
]


@dataclass
class TermRow:
    has_problems: str  # any value = yes, "" = no
    vocab_set: str
    english: str
    cherokee: str  # phonetics with tones
    syllabary: str
    audio: str  # path to audio


def read_terms_for_dataset(dataset: DatasetMetadata):
    with open(dataset.terms) as f:
        for row in DictReader(
            f,
            fieldnames=TERM_FIELDS,
            delimiter=",",
        ):
            if row == {}:
                continue

            yield TermRow(**row)
