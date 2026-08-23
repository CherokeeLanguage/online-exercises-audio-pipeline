from dataclasses import asdict
import json
from typing import Dict, List
from csv import DictReader

from pathlib import Path
from cnd.file_downloader import download_files_parallel
from cnd.sort import sort_sentences
from cnd.utils import Sentence
from common.online_exercises_structs import (
    OnlineExercisesCard,
    VocabCollection,
    VocabSet,
    write_cards_json,
)
from requests import get

from common.structs import PhoneticOrthography

COLLECTION_ID = "cnd:sentences"
COLLECTION_TITLE = "Cherokee Nation Dictionary Sentences"

CVS_HEADERS = (
    "Headword",
    "Entry No.",
    "No.",
    "Syllabary",
    "Stem",
    "Practical",
    "Simple phonetics",
    "Tone and length 1",
    "Tone and length 2",
    "Part of speech",
    "Grammar sub entry",
    "Grammar note",
    "Translation 1A",
    "Translation 1B",
    "Translation 1C",
    "Translation 1D",
    "Translation 1E",
    "Translation 1F",
    "Translation 1G",
    "Translation 1H",
    "Translation 1 sub entry",
    "Translation 2A",
    "Translation 2B",
    "Translation 2C",
    "Translation 2D",
    "Translation 2 sub entry",
    "Translation 3A",
    "Translation 3B",
    "Translation 3C",
    "Translation 3D",
    "Translation 3 sub entry",
    "English gloss 1",
    "English gloss 2",
    "English gloss 3",
    "English gloss 4",
    "Compare 1",
    "Compare 2",
    "Compare 3",
    "Word audio",
    "Sentence 1 audio",
    "Sentence-1 SYLL",
    "Sentence-1 PHON",
    "Sentence-1 ENGL",
    "Sentence 2 audio",
    "Sentence-2 SYLL",
    "Sentence-2 PHON",
    "Sentence-2 ENGL",
    "Sentence 3 audio",
    "Sentence-3 SYLL",
    "Sentence-3 PHON",
    "Sentence-3 ENGL",
    "Source of sentence 1",
    "Source of sentence 2",
    "Source of sentence 3",
    "Speaker of sentence 1",
    "Speaker of sentence 2",
    "Speaker of sentence 3",
    "Notes on speaker of sentence 1",
    "Notes on speaker of sentence 2",
    "Notes on speaker of sentence 3",
    "Status",
)


def make_collection(sets: List[VocabSet]) -> VocabCollection:
    return VocabCollection(id=COLLECTION_ID, title=COLLECTION_TITLE, sets=sets)


def update_csv(data_dir: Path) -> Path:
    # use requests library to download the csv to local disk
    target = data_dir / "dictionary.csv"
    # url = "https://cherokeenationdictionary.net/dictionary.csv"
    # response = get(url)
    # response.raise_for_status()
    # with open(target, "wb") as f:
    #     f.write(response.content)

    return target


def update_sentences_json(data_dir: Path, csv_path: Path) -> List[Sentence]:
    sentences: Dict[str, Sentence] = {}
    with open(csv_path) as f:
        reader = DictReader(f, fieldnames=CVS_HEADERS)
        next(reader)  # skip header
        for line in reader:
            for i in range(1, 4):
                syll = line.get(f"Sentence-{i} SYLL", "").strip()
                phon = line.get(f"Sentence-{i} PHON", "").strip()
                engl = line.get(f"Sentence-{i} ENGL", "").strip()
                audio = line.get(f"Sentence {i} audio", "").strip()
                if audio:
                    if audio not in sentences:
                        sentences[audio] = Sentence(
                            syllabary=syll.replace("*", ""),
                            phonetic=phon.replace("*", ""),
                            english=engl.replace("*", ""),
                            audio=audio,
                            id=line["Entry No."].strip()
                            + f"-s{i}",  # hope this is stable lol
                        )

    target = data_dir / "sentences.json"
    with open(target, "w") as f:
        json.dump(
            [asdict(s) for s in sentences.values()], f, ensure_ascii=False, indent=2
        )

    return list(sentences.values())


def download_audio(data_dir: Path, sentences: List[Sentence]) -> None:
    target_dir = data_dir / "card_audio"
    files = [
        sen.audio_url for sen in sentences if not (target_dir / sen.audio).exists()
    ]
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"Missing audio for {len(files)} files")
    download_files_parallel(files, target_dir, max_workers=10)


def make_cards(sentences: List[Sentence]) -> List[OnlineExercisesCard]:
    return [
        OnlineExercisesCard(
            syllabary=sen.syllabary,
            cherokee=sen.phonetic,
            cherokee_audio=[f"data/{COLLECTION_ID}/card_audio/{sen.audio}"],
            english=sen.english,
            english_audio=[""],
            alternate_pronunciations=[],
            alternate_syllabary=[],
            phoneticOrthography=PhoneticOrthography.MCO,
        )
        for sen in sentences
        if sen.audio_path.exists()
    ]


def write_collection_json(collection: VocabCollection, target: Path) -> None:
    with open(target, "w") as f:
        json.dump(asdict(collection), f, ensure_ascii=False, indent=2)


def main():
    data_dir = Path("data/cnd")

    data_dir.mkdir(parents=True, exist_ok=True)
    csv_path = update_csv(data_dir)

    sentences = update_sentences_json(data_dir, csv_path=csv_path)

    # do grouping / ordering by usage
    sentences = sort_sentences(sentences)
    sentences.sort(key=lambda s: s.id)

    # download_audio(data_dir, sentences)

    cards = make_cards(sentences=sentences)

    write_cards_json(cards, data_dir / f"{COLLECTION_ID}-cards.json")

    vocab_sets = []
    for i in range(0, len(cards), 100):
        vocab_set = VocabSet(
            id=f"part-{i//100 + 1}",
            title=f"Sentences Part {i//100 + 1}",
            terms=[c.cherokee for c in cards[i : i + 100]],
        )
        vocab_sets.append(vocab_set)

    collection = make_collection(vocab_sets)
    write_collection_json(collection, data_dir / f"{collection.id}.json")


if __name__ == "__main__":
    main()
