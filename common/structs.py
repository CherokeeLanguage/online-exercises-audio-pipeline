from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Union


class PhoneticOrthography(Enum):
    MCO = "MCO"
    WEBSTER = "WEBSTER"


class AnnotationFormat(Enum):
    """
    An annotation format identifies which annotations in an ELAN TSV should be
    considered Cherokee audio.
    """

    ENGLISH_CHEROKEE_ALTERNATING = "ENGLISH_CHEROKEE_ALTERNATING"
    """Annotations alternate between English and Cherokee, starting with English."""

    CHEROKEE_NONEMPTY = "CHEROKEE_NONEMPTY"
    """All nonempty annotations are Cherokee audio."""

    @classmethod
    def default(cls):
        return cls.ENGLISH_CHEROKEE_ALTERNATING


@dataclass
class DatasetMetadata:
    audio_source: Path
    annotations: Path
    annotation_format: AnnotationFormat
    terms: Path
    folder: Path
    collection_title: str
    collection_id: str
    phoneticOrthography: PhoneticOrthography

    @staticmethod
    def from_file(path: Union[str, Path]):
        if isinstance(path, str):
            path = Path(path)

        with open(path) as f:
            data = json.load(f)

        return DatasetMetadata(
            audio_source=path.parent / Path(data["audio_source"]),
            annotations=path.parent / Path(data["annotations"]),
            annotation_format=AnnotationFormat(
                data.get("annotation_format", AnnotationFormat.default().value)
            ),
            terms=path.parent / Path(data["terms"]),
            folder=path.parent,
            collection_id=data["collection_id"],
            collection_title=data["collection_title"],
            phoneticOrthography=PhoneticOrthography(
                data.get("phonetic_orthography", None)
            ),
        )

    @property
    def backup_terms(self):
        return self.folder / "terms.back.csv"

    @property
    def new_terms(self):
        return self.folder / "terms.new.csv"

    @property
    def audio_output_dir(self):
        return self.folder / "card_audio"

    @property
    def cards_json(self):
        return self.folder / f"{self.collection_id}-cards.json"

    @property
    def collection_json(self):
        return self.folder / f"{self.collection_id}.json"
