"""
Python module for interfacing with an annotation TSV file from ELAN (ie. the TSV referenced by `DatasetMetadata.annotations`)
"""


from csv import DictReader
from dataclasses import dataclass
import itertools
from typing import Generator, Iterable, Tuple, TypeVar

from common.structs import AnnotationFormat, DatasetMetadata


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


def cherokee_annotations(dataset: DatasetMetadata) -> Generator[Annotation, None, None]:
    """
    Drop non-Cherokee annotations.
    """
    annotations = read_annotations_tsv(dataset)

    if dataset.annotation_format == AnnotationFormat.ENGLISH_CHEROKEE_ALTERNATING:
        """
        Drop every other annotation (assumes annotations alternate between English and Cherokee, starting with English).

        This is ugly and we should just stop annotating the English.
        """
        for annotation in itertools.islice(annotations, 1, None, 2):
            yield annotation

    elif dataset.annotation_format == AnnotationFormat.CHEROKEE_NONEMPTY:
        """
        Drop empty annotations
        """
        yield from (
            annotation
            for annotation in annotations
            if not annotation.annotation_text.strip() == ""
        )


T = TypeVar("T")


def iter_pairs(iterable: Iterable[T]) -> Iterable[Tuple[T, T]]:
    i1, i2 = itertools.tee(iterable, 2)
    return zip(itertools.islice(i1, 0, None, 2), itertools.islice(i2, 1, None, 2))
