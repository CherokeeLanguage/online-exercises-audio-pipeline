import argparse
from os import makedirs
from pathlib import Path

from pydub import AudioSegment
from pydub.effects import normalize

from common.structs import DatasetMetadata
from common.annotations import read_annotations_tsv


def escape(s: str):
    return s.replace("'", "_").replace("/", "_").replace("\\", "_")


def main(dataset_folder: Path):
    dataset = DatasetMetadata.from_file(dataset_folder / "dataset.json")
    audio_source = AudioSegment.from_wav(dataset.audio_source)
    out_dir = dataset_folder / "split_audio"
    makedirs(out_dir, exist_ok=True)
    for annotation in read_annotations_tsv(dataset):
        if len(annotation.annotation_text.strip()) == 0:
            continue
        annotation_audio: AudioSegment = normalize(audio_source[annotation.start_ms : annotation.end_ms])  # type: ignore
        annotation_audio.export(
            out_dir / ("split - " + escape(annotation.annotation_text) + ".mp3"),
            format="mp3",
            parameters=["-qscale:a", "0"],
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "split_audio", description="Split audio files from an Elan-exported TSV file"
    )
    parser.add_argument(
        "dataset_folder",
        type=str,
        help="Path to folder containing dataset, eg. `data/jw-living-phrases`",
    )

    args = parser.parse_args()
    main(dataset_folder=Path(args.dataset_folder))
