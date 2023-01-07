import itertools
import json
import os
import re
from sys import argv
from pathlib import Path
from csv import DictReader
from dataclasses import asdict, dataclass
from typing import Iterable, List, Tuple, TypeVar

from pydub import AudioSegment
from pydub.effects import normalize
from pydub.playback import play

from .structs import DatasetMetadata
from common.structs import OnlineExercisesCard, VocabCollection, VocabSet


@dataclass
class Annotation:
    tier: str
    start_ms: int
    end_ms: int
    duration_ms: int
    annotation_text: str


def read_annotations_tsv(annotation_path: Path):
    with open(annotation_path) as f:
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


def read_terms_for_dataset(dataset: DatasetMetadata):
    terms: List[OnlineExercisesCard] = []
    with open(dataset.terms) as f:
        for row in DictReader(
            f,
            ["english", "cherokee", "syllabary"],
            delimiter=",",
        ):
            if row == {}:
                continue
            terms.append(
                OnlineExercisesCard(
                    cherokee=row["cherokee"],
                    syllabary=row["syllabary"],
                    english=row["english"],
                    english_audio=[],
                    cherokee_audio=[],
                    alternate_pronunciations=[],
                    alternate_syllabary=[],
                    phoneticOrthography=dataset.phoneticOrthography,
                )
            )
    return terms


T = TypeVar("T")


def iter_pairs(iterable: Iterable[T]) -> Iterable[Tuple[T, T]]:
    i1, i2 = itertools.tee(iterable, 2)
    return zip(itertools.islice(i1, 0, None, 2), itertools.islice(i2, 1, None, 2))


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


def match_to_real_term(
    real_terms: List[OnlineExercisesCard],
    *,
    chr: str,
    en: str,
) -> OnlineExercisesCard:
    return sorted(
        real_terms,
        key=lambda card: trigram_similarity(
            minify_pronounce(card.cherokee), chr.lower()
        )
        + trigram_similarity(card.english.lower(), en.lower()),
        reverse=True,
    )[0]


def term_is_valid(
    *,
    term: OnlineExercisesCard,
    cherokee_audio: AudioSegment,
    english_audio: AudioSegment,
) -> bool:
    print(f"\nENGLISH: {term.english}")
    play(english_audio)
    yesno = input("English sounds good? ")
    if yesno == "x":
        return False

    print(f"\nCHEROKEE: {term.cherokee} / {term.syllabary}")
    play(cherokee_audio)
    yesno = input("Cherokee sounds good? ")
    if yesno == "x":
        return False

    return True


def text_to_path(text: str):
    return re.sub(r"[^0-9a-zA-Z]+", "_", text)


def match_segments_and_extract_audio(dataset: DatasetMetadata) -> None:
    audio_source: AudioSegment = AudioSegment.from_wav(dataset.audio_source)

    out_dir = dataset.folder / "split_audio"
    os.makedirs(out_dir, exist_ok=True)

    real_terms = read_terms_for_dataset(dataset)
    print([t for t in real_terms if t.cherokee is None])
    for annotation_en, annotation_chr in iter_pairs(
        (
            a
            for a in read_annotations_tsv(dataset.annotations)
            if not a.annotation_text == ""
        ),
    ):
        matched_term = match_to_real_term(
            real_terms,
            chr=annotation_chr.annotation_text,
            en=annotation_en.annotation_text,
        )

        print("\n")
        print(
            f"en: {annotation_en.annotation_text} -> chr: {annotation_chr.annotation_text}"
        )
        print(f"en: {matched_term.english} -> chr: {matched_term.cherokee}")

        english_audio: AudioSegment = normalize(audio_source[annotation_en.start_ms : annotation_en.end_ms])  # type: ignore
        cherokee_audio: AudioSegment = normalize(audio_source[annotation_chr.start_ms : annotation_chr.end_ms])  # type: ignore

        # if term_is_valid(
        #     term=matched_term,
        #     english_audio=english_audio,
        #     cherokee_audio=cherokee_audio,
        # ):
        english_out = (
            out_dir
            / f"english_{text_to_path(matched_term.english)}_{len(matched_term.english_audio)}.mp3"
        )
        cherokee_out = (
            out_dir
            / f"cherokee_{text_to_path(matched_term.cherokee)}_{len(matched_term.cherokee_audio)}.mp3"
        )
        english_audio.export(english_out, format="mp3", parameters=["-qscale:a", "0"])
        cherokee_audio.export(cherokee_out, format="mp3", parameters=["-qscale:a", "0"])
        matched_term.english_audio.append(str(english_out))
        matched_term.cherokee_audio.append(str(cherokee_out))
        # else:
        #     break

    with open(dataset.folder / f"{dataset.collection_id}-cards.json", "w") as f:
        json.dump([term.toDict() for term in real_terms], f, ensure_ascii=False)

    with open(dataset.folder / f"{dataset.collection_id}.json", "w") as f:
        json.dump(
            asdict(
                VocabCollection(
                    id=dataset.collection_id,
                    title=dataset.collection_title,
                    sets=[
                        VocabSet(
                            id="all",
                            title="All terms",
                            terms=[
                                term.cherokee
                                for term in real_terms
                                if len(term.cherokee_audio) > 0
                            ],
                        )
                    ],
                )
            ),
            f,
            ensure_ascii=False,
        )


def main(dataset_folder: Path):
    dataset = DatasetMetadata.from_file(dataset_folder / "dataset.json")
    match_segments_and_extract_audio(dataset)


if __name__ == "__main__":
    assert len(argv) == 2
    dataset_folder = argv[1]
    main(dataset_folder=Path(dataset_folder))
