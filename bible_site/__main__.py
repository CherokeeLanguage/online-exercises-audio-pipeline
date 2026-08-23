"""
Create data needed for the Bible Site
"""

import argparse
import json

from pathlib import Path
from dataclasses import asdict, dataclass
from typing import List
from common.annotations import Annotation, read_annotations_tsv

from common.structs import DatasetMetadata


@dataclass
class SourceSegment:
    """A segment of source audio in Cherokee, with transcription"""

    start: int
    end: int
    syllabary: str

    @staticmethod
    def from_annotation(annotation: Annotation) -> "SourceSegment":
        assert annotation.tier == "words", "Tier should be 'words'"
        return SourceSegment(
            start=annotation.start_ms,
            end=annotation.end_ms,
            syllabary=annotation.annotation_text,
        )


@dataclass
class Phrase:
    """Data on one phrase or verse of the Bible"""

    translation: str
    """English translation of the verse"""

    source: List[SourceSegment]
    """Segments within """


@dataclass
class Book:
    """Data on one book from the Bible"""

    title: str
    """User-facing title, eg. 'ᏣᏂ 1'"""

    phrases: List[Phrase]


def group_phrases(annotations: List[Annotation]) -> List[Phrase]:
    phrases_by_start = {
        annotation.start_ms: Phrase(translation=annotation.annotation_text, source=[])
        for annotation in annotations
        if annotation.tier == "phrases"
    }

    for annotation in annotations:
        if not annotation.tier == "words":
            continue

        last_match = None

        for phrase_start in phrases_by_start:
            if phrase_start < annotation.start_ms:
                last_match = phrase_start
            else:
                break

        if last_match is None:
            print(f"Couldn't find phrase for annotation {annotation}")
            continue

        phrases_by_start[last_match].source.append(
            SourceSegment.from_annotation(annotation)
        )

    return list(phrases_by_start.values())


def main(dataset_folder: Path):
    dataset = DatasetMetadata.from_file(dataset_folder / "dataset.json")

    annotations = list(read_annotations_tsv(dataset))
    phrases = group_phrases(annotations)
    json.dump(
        asdict(Book(title=dataset.collection_title, phrases=phrases)),
        open(dataset.folder / "book.json", "w"),
        ensure_ascii=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "bible_site", description="Make a nice JSON for the Bible Site"
    )
    parser.add_argument(
        "dataset_folder",
        type=str,
        help="Path to folder containing dataset, eg. `data/john-1`",
    )

    args = parser.parse_args()
    main(dataset_folder=Path(args.dataset_folder))
