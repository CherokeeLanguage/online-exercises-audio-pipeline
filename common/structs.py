from dataclasses import asdict, dataclass
from enum import Enum
import re
from typing import List


def normalizePronunciation(cherokee: str):
    return re.sub(r"[\.\?\,]", cherokee.strip().lower(), "")


def cleanSyllabary(syllabary: str):
    return syllabary.strip().upper()


class PhoneticOrthography(Enum):
    MCO = "MCO"
    WEBSTER = "WEBSTER"


@dataclass
class OnlineExercisesCard:
    cherokee: str
    cherokee_audio: List[str]
    syllabary: str

    alternate_pronunciations: List[str]
    alternate_syllabary: List[str]

    english: str
    english_audio: List[str]

    phoneticOrthography: PhoneticOrthography

    def toDict(self):
        d = asdict(self)
        d["phoneticOrthography"] = self.phoneticOrthography.name
        return d


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
