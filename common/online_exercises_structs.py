from dataclasses import asdict, dataclass
from enum import Enum
import json
from typing import Dict, List

from .structs import DatasetMetadata, PhoneticOrthography
from .terms import read_terms_for_dataset


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


def export_terms_to_json(
    dataset: DatasetMetadata,
):
    cards: List[OnlineExercisesCard] = []
    vocab_sets: Dict[str, VocabSet] = {}
    for term in read_terms_for_dataset(dataset):
        if term.has_problems == "":
            if not term.vocab_set in vocab_sets:
                vocab_sets[term.vocab_set] = VocabSet(
                    id=f"{dataset.collection_id}:{term.vocab_set}",
                    title=term.vocab_set,
                    terms=[],
                )

            vocab_sets[term.vocab_set].terms.append(term.cherokee)

            cards.append(
                OnlineExercisesCard(
                    english=term.english,
                    english_audio=[],
                    syllabary=term.syllabary,
                    cherokee=term.cherokee,
                    cherokee_audio=[term.audio],
                    alternate_pronunciations=[],
                    alternate_syllabary=[],
                    phoneticOrthography=dataset.phoneticOrthography,
                )
            )

    with open(dataset.card_json, "w") as f:
        json.dump([term.toDict() for term in cards], f, ensure_ascii=False)

    with open(dataset.collection_json, "w") as f:
        json.dump(
            asdict(
                VocabCollection(
                    id=dataset.collection_id,
                    title=dataset.collection_title,
                    sets=[vocab_set for vocab_set in vocab_sets.values()],
                )
            ),
            f,
            ensure_ascii=False,
        )
