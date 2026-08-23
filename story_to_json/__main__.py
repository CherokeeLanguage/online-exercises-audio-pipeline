"""
Generate 
"""

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path

from pydub import AudioSegment

from common.annotations import (
    Annotation,
    read_annotations_tsv,
    read_annotations_tsv_from_path,
)
from common.online_exercises_structs import (
    OnlineExercisesCard,
    write_cards_json_for_dataset,
)
from common.structs import DatasetMetadata
from common.terms import read_terms_for_dataset
from generate_english_audio.generate_english_audio_for_deck import (
    generate_audio_for_voice,
)
from generate_english_audio.tts import AMZ_VOICES_FEMALE


@dataclass
class AnnotatedSegment:
    audio_path: str
    cherokee: str
    english: str


def main(dataset_folder: Path):
    dataset = DatasetMetadata.from_file(dataset_folder / "dataset.json")

    os.makedirs(dataset.audio_output_dir, exist_ok=True)

    audio_source = AudioSegment.from_wav(dataset.audio_source)

    all_annotations = list(read_annotations_tsv(dataset))

    annotations_chr: list[Annotation] = []
    annotations_eng: list[Annotation] = []

    for annotation in all_annotations:
        if not len(annotation.annotation_text):
            continue
        if annotation.tier == "chr":
            annotations_chr.append(annotation)
        elif annotation.tier == "eng":
            annotations_eng.append(annotation)

    assert len(annotations_chr) == len(
        annotations_eng
    ), "Must have same number of annotations"

    data = []

    for chr, eng in zip(annotations_chr, annotations_eng):
        chr.ensure_split_audio_exists(dataset=dataset, audio_source=audio_source)
        data.append(
            AnnotatedSegment(
                audio_path=str(chr.split_audio_path(dataset)),
                cherokee=chr.annotation_text,
                english=eng.annotation_text,
            )
        )

    json.dump([asdict(d) for d in data], open(dataset_folder / f"story.json", "w"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "story_to_json", description="Create a JSON structure around an annotated story"
    )
    parser.add_argument(
        "dataset_folder",
        type=str,
        help="Path to folder containing dataset, eg. `data/jw-living-phrases`",
    )

    args = parser.parse_args()
    main(dataset_folder=Path(args.dataset_folder))
