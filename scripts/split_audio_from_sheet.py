import argparse
from csv import DictReader
import os
from pathlib import Path
from typing import Optional
from pydub import AudioSegment
from pydub.effects import normalize

COLUMNS = [
    "Folder",
    "File",
    "Item #",
    "Start",
    "End",
    "Part",
    "Type",
    "Title",
    "Notes",
    "Topics",
]


def time_in_ms(time: str) -> Optional[int]:
    if time.lower() == "file start":
        return 0
    elif time.lower() == "file end":
        return None

    min, sec = time.split(":")
    return 1000 * (int(min) * 60 + int(sec))


def main(*, sheet: Path, src: Path, dest: Path):
    os.makedirs(dest, exist_ok=True)

    loaded_audio: dict[str, AudioSegment] = {}

    with open(sheet) as sheet_file:
        reader = DictReader(sheet_file, fieldnames=COLUMNS)
        rows = iter(reader)

        _headers = next(rows)
        # print(headers)
        # assert headers == COLUMNS

        for row in rows:
            print(f"Processing item {row['Item #']}", end="\r")
            if row["Type"] == "Noise":
                continue

            filename = row["File"]
            filename = filename[-6:-4] + " " + filename

            source_audio_path = str(src / row["Folder"] / filename)
            if source_audio_path not in loaded_audio:
                loaded_audio[source_audio_path] = AudioSegment.from_file(
                    source_audio_path
                )

            source_audio = loaded_audio[source_audio_path]

            start_ms = time_in_ms(row["Start"])
            end_ms = time_in_ms(row["End"])

            audio_slice: AudioSegment = (
                source_audio[start_ms:]
                if end_ms is None
                else source_audio[start_ms:end_ms]
            )  # type: ignore

            # mono
            audio_slice = audio_slice.set_channels(1)
            audio_slice = audio_slice.set_channels(2)

            # normalize
            audio_slice = normalize(audio_slice, headroom=0.15)

            file_title = (
                f'Item {row["Item #"]} - {row["Type"]} - {row["Title"]} ({row["Part"]})'
            )
            out_name = f'{row["Item #"]} - {row["Type"]}.mp3'
            audio_slice.export(
                open(dest / out_name, "wb"),
                format="mp3",
                tags={
                    "artist": "Cherokee Heritage Center",
                    "album": "Kilpatrick Audio Collection",
                    "title": file_title,
                },
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "split_audio_from_sheet",
        description="Split audio from a large number of files into even more files using a CSV",
    )

    parser.add_argument(
        "sheet",
        type=str,
        help="Path to CSV containing split data",
    )

    parser.add_argument(
        "src",
        type=str,
        help="Path folder containing audio",
    )

    parser.add_argument(
        "dest",
        type=str,
        help="Path folder desired output folder",
    )

    args = parser.parse_args()
    main(sheet=Path(args.sheet), src=Path(args.src), dest=Path(args.dest))
