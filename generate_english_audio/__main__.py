import argparse
from pathlib import Path
from sys import argv

from common.structs import DatasetMetadata

from .generate_english_audio_for_deck import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "generate_english_audio",
        description="Generate English audio files for each card in a dataset",
    )
    parser.add_argument(
        "dataset_folder",
        type=str,
        help="Path to folder containing dataset, eg. `data/jw-living-phrases`",
    )
    args = parser.parse_args()
    dataset = DatasetMetadata.from_file(Path(args.dataset_folder) / "dataset.json")
    main(dataset)
