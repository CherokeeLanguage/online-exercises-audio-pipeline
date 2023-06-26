"""
Python module for matching Cherokee phonetics against annotations from ELAN
"""
from dataclasses import dataclass
from pathlib import Path
import re
from typing import List
from pydub import AudioSegment
from pydub.effects import normalize


from common.structs import DatasetMetadata
from common.annotations import Annotation, cherokee_annotations


@dataclass
class MatchableAudio:
    cherokee: str  # phonetics, without tones
    file: Path

    @staticmethod
    def from_annotation(
        dataset: DatasetMetadata, audio_source: AudioSegment, annotation: Annotation
    ):
        annotation.ensure_split_audio_exists(dataset, audio_source)
        return MatchableAudio(
            annotation.annotation_text, file=annotation.split_audio_path(dataset)
        )


def get_matchable_audio_from_annotations(
    dataset: DatasetMetadata, audio_source: AudioSegment
):
    return [
        MatchableAudio.from_annotation(dataset, audio_source, annotation)
        for annotation in cherokee_annotations(dataset)
    ]


trigrams = lambda a: zip(a, a[1:], a[2:])


def trigram_similarity(a, b):
    a_t = set(trigrams(a))
    b_t = set(trigrams(b))
    return len(a_t & b_t) / len(a_t | b_t)


def minify_pronounce(rich: str):
    return (
        re.sub(
            r"[\:ɂ¹²³⁴]|(.,)",  # JW uses commas for drop-vowels
            "",
            rich,
        )
    ).lower()


def top_n_matches(
    target_cherokee: str, available_cherokee_audio: List[MatchableAudio], n: int
) -> List[MatchableAudio]:
    return sorted(
        available_cherokee_audio,
        key=lambda match: trigram_similarity(
            minify_pronounce(target_cherokee.lower()), match.cherokee.lower()
        ),
        reverse=True,
    )[:n]
