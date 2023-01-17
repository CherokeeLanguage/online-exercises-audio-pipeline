"""
Python module for interfacing with an annotation TSV file from ELAN (ie. the TSV referenced by `DatasetMetadata.annotations`)
"""


from csv import DictReader
from dataclasses import dataclass
import itertools
from typing import Iterable, Tuple, TypeVar

from common.structs import DatasetMetadata


@dataclass
class Annotation:
    tier: str
    start_ms: int
    end_ms: int
    duration_ms: int
    annotation_text: str


def read_annotations_tsv(dataset: DatasetMetadata):
    with open(dataset.annotations) as f:
        for row in DictReader(
            f,
            ["tier", "_", "start_ms", "end_ms", "duration_ms", "annotation_text"],
            delimiter="\t",
        ):
            yield Annotation(
                tier=row["tier"],
                start_ms=int(row["start_ms"]),
                end_ms=int(row["end_ms"]),
                duration_ms=int(row["duration_ms"]),
                annotation_text=row["annotation_text"],
            )


def cherokee_annotations(dataset: DatasetMetadata):
    """
    Drop every other annotation (assumes annotations alternate between English and Cherokee, starting with English).

    This is ugly and we should just stop annotating the English.
    """
    for annotation in itertools.islice(read_annotations_tsv(dataset), 1, None, 2):
        yield annotation


T = TypeVar("T")


def iter_pairs(iterable: Iterable[T]) -> Iterable[Tuple[T, T]]:
    i1, i2 = itertools.tee(iterable, 2)
    return zip(itertools.islice(i1, 0, None, 2), itertools.islice(i2, 1, None, 2))
