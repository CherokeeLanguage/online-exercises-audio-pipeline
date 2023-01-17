import argparse
import os
import re
from pathlib import Path
from csv import DictWriter
from dataclasses import asdict

from pydub import AudioSegment
from pydub.playback import play

from common.structs import DatasetMetadata

from .matching import get_matchable_audio_from_annotations, top_n_matches

from common.terms import TERM_FIELDS, read_terms_for_dataset
from common.online_exercises_structs import export_terms_to_json


def text_to_path(text: str):
    return re.sub(r"[^0-9a-zA-Z]+", "_", text)


def match_segments_and_extract_audio(dataset: DatasetMetadata) -> None:
    audio_source: AudioSegment = AudioSegment.from_wav(dataset.audio_source)

    os.makedirs(dataset.split_audio_dir, exist_ok=True)

    available_cherokee_audio = get_matchable_audio_from_annotations(
        dataset, audio_source
    )

    with open(dataset.new_terms, "w") as f:
        writer = DictWriter(f, fieldnames=TERM_FIELDS, delimiter=",")
        for term in read_terms_for_dataset(dataset):
            if term.audio == "" and term.has_problems == "":
                matches = top_n_matches(term.cherokee, available_cherokee_audio, n=5)
                accepted = False
                while not accepted:
                    print(f"Term: {term.cherokee} ({term.english})")
                    for i, match in enumerate(matches):
                        print(f"{i}) {match.cherokee}")

                    selected = input("Selected match: ")
                    try:
                        if selected.endswith("?"):
                            selected_idx = int(selected[:-1])
                            selected_match = matches[selected_idx]
                            play(AudioSegment.from_file(selected_match.file))
                        elif selected == "":
                            accepted = True
                            term.has_problems = "*"
                        else:
                            accepted = True
                            selected_idx = int(selected)
                            selected_match = matches[selected_idx]
                            term.audio = str(selected_match.file)
                    except:
                        print("Not understood")

            writer.writerow(asdict(term))

    # write terms to backup; new file to terms
    dataset.terms.rename(dataset.backup_terms)
    dataset.new_terms.rename(dataset.terms)


def main(dataset_folder: Path, export_json: bool):
    dataset = DatasetMetadata.from_file(dataset_folder / "dataset.json")
    match_segments_and_extract_audio(dataset)
    if export_json:
        export_terms_to_json(dataset)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "match_audio", description="Match audio files to each row in a terms CSV"
    )
    parser.add_argument(
        "dataset_folder",
        type=str,
        help="Path to folder containing dataset, eg. `data/jw-living-phrases`",
    )
    parser.add_argument(
        "--export-json",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Export a JSON file for the online exercises site (will not contain English audio).",
    )

    args = parser.parse_args()
    main(dataset_folder=Path(args.dataset_folder), export_json=args.export_json)
