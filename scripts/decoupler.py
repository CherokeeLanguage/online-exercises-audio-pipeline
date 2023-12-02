"""
Utility for converting folder structure to album metadata for the Decoupled app.
"""

import argparse
from pathlib import Path
from pydub import AudioSegment
from pydub.effects import normalize


def album_name_from_path(file_path: Path):
    # return " - ".join([p for p in file_path.parent.parts])
    return file_path.parts[0]


def annotate_and_convert_file(
    *, nth_file: int, root: Path, output: Path, file: Path, artist: str
):
    print("Getting relative path", end="... ")
    rel_file = file.relative_to(root.parent)  # this is good for some reason
    print("done")

    print(f"Loading {file}", end="... ")
    audio: AudioSegment = AudioSegment.from_file(file)
    print("done")

    # # flatten channels
    # channels = seg.split_to_mono()
    # audio, rest = channels[0], channels[1:]

    # for c in rest:
    #     audio.overlay(c)

    print("normalizing", end="... ")
    # convert to mono then back to stereo
    # this basically ensures that audio will play in both ears
    audio: AudioSegment = normalize(audio.set_channels(1).set_channels(2))
    print("done")

    out_path = output / rel_file.with_suffix(".mp3").name

    print("Making sure parent folder exists", end="... ")
    # make sure we can make this file
    if not out_path.parent.exists():
        out_path.parent.mkdir(parents=True, exist_ok=True)

    # preprend the track number for Decoupled
    # track_no = 1 + sum(f.is_file() for f in out_path.parent.iterdir())
    out_path = out_path.with_name(f"{nth_file + 1} - {out_path.name}")

    print("done")

    album = album_name_from_path(rel_file)

    print(f"Saving {album}: {out_path.name}", end="... ")
    audio.export(
        open(out_path, "wb"),
        format="mp3",
        tags={
            "artist": artist,
            "album": album,
            "title": " - ".join(file.relative_to(root).parts),
        },
    )
    print("done")


def main(*, source_dir: Path, target_dir: Path, artist: str):
    assert source_dir.exists(), "Source directory not found"
    print("Finding files", end="... ")
    files = list(source_dir.glob("**/*.wav"))
    print("done")

    print("Sorting", end="... ")
    files.sort()
    print("done")

    for i, audio in enumerate(files):
        annotate_and_convert_file(
            nth_file=i, root=source_dir, output=target_dir, file=audio, artist=artist
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "decoupler",
        description="Add album metadata to files so they can be played in Decoupled.",
    )
    parser.add_argument(
        "source_dir",
        type=str,
        help="Path to folder all the audio to be converted",
    )
    parser.add_argument(
        "target_dir",
        type=str,
        help="Where files should end up",
    )
    parser.add_argument(
        "artist",
        type=str,
        help="Artist name to use for files",
        default="Unknown artist",
    )

    args = parser.parse_args()
    main(
        source_dir=Path(args.source_dir),
        target_dir=Path(args.target_dir),
        artist=args.artist,
    )
