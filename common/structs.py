from dataclasses import dataclass
import re
from typing import List


def normalizePronunciation(cherokee: str):
    return re.sub(r"[\.\?\,]", cherokee.strip().lower(), "")


def cleanSyllabary(syllabary: str):
    return syllabary.strip().upper()


@dataclass
class OnlineExercisesCard:
    cherokee: str
    cherokee_audio: List[str]
    syllabary: str

    alternate_pronunciations: List[str]
    alternate_syllabary: List[str]

    english: str
    english_audio: List[str]


@dataclass
class VocabSet:
    id: str
    title: str
    terms: List[str]  # cherokee pronunciation


@dataclass
class VocabCollection:
    id: str
    title: str
    sets: List[VocabSet]
