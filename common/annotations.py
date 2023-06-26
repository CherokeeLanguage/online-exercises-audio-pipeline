"""
Python module for interfacing with an annotation TSV file from ELAN (ie. the TSV referenced by `DatasetMetadata.annotations`)
"""


from csv import DictReader
from dataclasses import dataclass
import itertools
from pathlib import Path
from typing import Generator, Iterable, Tuple, TypeVar

from common.structs import AnnotationFormat, DatasetMetadata

from pydub import AudioSegment
from pydub.effects import normalize


@dataclass
class Annotation:
    tier: str
    start_ms: int
    end_ms: int
    duration_ms: int
    annotation_text: str

    def split_audio_path(self, dataset: DatasetMetadata):
        """Path to file containing the audio for just this annotation."""
        return (
            dataset.audio_output_dir / f"split_audio_{self.start_ms}_{self.end_ms}.mp3"
        )

    def ensure_split_audio_exists(
        self, dataset: DatasetMetadata, audio_source: AudioSegment
    ):
        """Ensure that a file with just the annotated audio exists on disk."""
        split_audio_path = self.split_audio_path(dataset)
        if not split_audio_path.exists():
            cherokee_audio: AudioSegment = normalize(audio_source[self.start_ms : self.end_ms])  # type: ignore
            cherokee_audio.export(
                split_audio_path, format="mp3", parameters=["-qscale:a", "0"]
            )


def read_annotations_tsv(dataset: DatasetMetadata):
    return read_annotations_tsv_from_path(dataset.annotations)


def read_annotations_tsv_from_path(path: Path):
    with open(path) as f:
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
