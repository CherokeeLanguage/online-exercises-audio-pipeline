import argparse
import os
import re
from pathlib import Path

from pydub import AudioSegment

from common.annotations import read_annotations_tsv, read_annotations_tsv_from_path
from common.structs import DatasetMetadata
from common.terms import read_terms_for_dataset
from generate_english_audio.generate_english_audio_for_deck import (
    generate_audio_for_voice,
)
from generate_english_audio.tts import AMZ_VOICES_FEMALE

from match_audio.matching import get_matchable_audio_from_annotations


def main(dataset_folder: Path):
    dataset = DatasetMetadata.from_file(dataset_folder / "dataset.json")

    cherokee_annotations = list(read_annotations_tsv(dataset))

    if dataset.english_annotations:
        english_annotations = list(
            read_annotations_tsv_from_path(dataset.english_annotations)
        )
    else:
        english_annotations = []

    terms = list(read_terms_for_dataset(dataset))

    assert len(terms) == len(
        cherokee_annotations
    ), "Expected the same number of terms and Cherokee annotations"

    audio_source: AudioSegment = AudioSegment.from_file(dataset.audio_source)
    if dataset.english_audio_source:
        english_audio_source: AudioSegment = AudioSegment.from_file(
            dataset.english_audio_source
        )
    else:
        english_audio_source: AudioSegment = audio_source

    output_audio: AudioSegment = AudioSegment.empty()

    for term in terms:
        cherokee_annotation = next(
            (
                a
                for a in cherokee_annotations
                if a.annotation_text.strip() == term.syllabary.strip()
            ),
            None,
        )
        english_annotation = next(
            (
                a
                for a in english_annotations
                if a.annotation_text.strip() == term.english.strip()
            ),
            None,
        )

        assert cherokee_annotation, (
            "Must have Cherokee audio for all terms: " + term.syllabary
        )
        cherokee_annotation.ensure_split_audio_exists(dataset, audio_source)
        cherokee_sentence_audio: AudioSegment = AudioSegment.from_file(
            cherokee_annotation.split_audio_path(dataset)
        )

        if english_annotation:
            english_annotation.ensure_split_audio_exists(dataset, english_audio_source)
            english_sentence_audio: AudioSegment = AudioSegment.from_file(
                english_annotation.split_audio_path(dataset)
            )
        else:
            english_sentence_audio: AudioSegment = AudioSegment.from_file(
                generate_audio_for_voice(voice=AMZ_VOICES_FEMALE[0], text=term.english)
            )

        output_audio = (
            output_audio
            + cherokee_sentence_audio
            + AudioSegment.silent(
                duration=int(
                    # (len(cherokee_sentence_audio) + len(english_sentence_audio)) * 0.75
                    200
                )
            )
            + english_sentence_audio
            + AudioSegment.silent(200)
            + cherokee_sentence_audio
            + AudioSegment.silent(1500)
        )
    output_audio.export("test.mp3", format="mp3", parameters=["-qscale:a", "0"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "kanoheda", description="Generate story based content"
    )
    parser.add_argument(
        "dataset_folder",
        type=str,
        help="Path to folder containing dataset, eg. `data/jw-living-phrases`",
    )
    # parser.add_argument(
    #     "--export-json",
    #     action=argparse.BooleanOptionalAction,
    #     default=False,
    #     help="Export a JSON file for the online exercises site (will not contain English audio).",
    # )

    args = parser.parse_args()
    main(dataset_folder=Path(args.dataset_folder))
