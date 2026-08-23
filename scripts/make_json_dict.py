import csv
import json
from dataclasses import asdict, dataclass
import re
import traceback
from typing import Dict, List, Optional, Tuple
import unicodedata


def normalize_phonetics(cherokee: str):
    return (
        cherokee.lower()
        # .replace("j", "ts")
        # .replace("qu", "gw")
        .replace("Ɂ", "ɂ")
        .replace("ʔ", "ɂ")
        .replace("ː", ":")
    )


def clean_field(field: str) -> str:
    return unicodedata.normalize("NFD", field.strip())


def clean_cherokee_field(field: str) -> str:
    return clean_field(normalize_phonetics(field))


def clean_cherokee_field_or(field: str | None) -> str | None:
    return clean_cherokee_field(field) if field is not None else None


def upper_or(field: str | None) -> str | None:
    return field.upper() if field is not None else None


@dataclass
class SentenceRow:
    syllabary: str
    phonetics: str
    english: str

    @staticmethod
    def from_row(row: Dict) -> "SentenceRow":
        return SentenceRow(
            phonetics=clean_field(
                normalize_phonetics(row["Sentence (Transliteration)"])
            ),
            syllabary=clean_field(
                normalize_phonetics(row["Sentence (Syllabary)"])
            ).upper(),
            english=clean_field(row["Sentence (English)"]),
        )


def get_item(l: list[str], idx: int):
    try:
        return l[idx]
    except IndexError:
        return None


@dataclass
class VerbRow:
    index: str
    source: str
    definition: str
    third_present: str
    third_present_simple: str
    third_present_syllabary: str
    first_present: str
    first_present_simple: str
    first_present_syllabary: str
    first_present_alt: Optional[str]
    first_present_alt_simple: Optional[str]
    first_present_alt_syllabary: Optional[str]
    second_command: str
    second_command_simple: str
    second_command_syllabary: str
    second_command_alt: Optional[str]
    second_command_alt_simple: Optional[str]
    second_command_alt_syllabary: Optional[str]
    third_completive_past: str
    third_completive_past_simple: str
    third_completive_past_syllabary: str
    third_incompletive_habitual: str
    third_incompletive_habitual_simple: str
    third_incompletive_habitual_syllabary: str
    third_infinitive: str
    third_infinitive_simple: str
    third_infinitive_syllabary: str
    sentence: SentenceRow

    def has_all_fields(self):
        fields = [
            self.index,
            self.definition,
            self.third_present,
            self.first_present,
            self.second_command,
            self.third_completive_past,
            self.third_incompletive_habitual,
            self.third_infinitive,
        ]

        for field in fields:
            if field == "" or re.match(r"^-*$", field):
                return False

        return True

    @staticmethod
    def from_row(row: Dict) -> "VerbRow":
        return VerbRow(
            index=clean_field(row["Index"]),
            source=clean_field(row["Source"]),
            definition=clean_field(row["Definition"]),
            third_present=clean_cherokee_field(row["Entry Tone"]),
            third_present_simple=clean_cherokee_field(row["Entry"]),
            third_present_syllabary=clean_cherokee_field(row["Syllabary"]).upper(),
            first_present=clean_cherokee_field(
                row["Verb 1st Present (Tone)"].split(",")[0]
            ),
            first_present_simple=clean_cherokee_field(
                row["Verb 1st Present"].split(",")[0]
            ),
            first_present_syllabary=clean_cherokee_field(
                row["Verb 1st Present (Syllabary)"].split(",")[0]
            ).upper(),
            first_present_alt=clean_cherokee_field_or(
                get_item(row["Verb 1st Present (Tone)"].split(","), 1)
            ),
            first_present_alt_simple=clean_cherokee_field_or(
                get_item(row["Verb 1st Present"].split(","), 1)
            ),
            first_present_alt_syllabary=clean_cherokee_field_or(
                upper_or(get_item(row["Verb 1st Present (Syllabary)"].split(","), 1))
            ),
            third_completive_past=clean_cherokee_field(row["Verb 3rd Past (Tone)"]),
            third_completive_past_simple=clean_cherokee_field(row["Verb 3rd Past"]),
            third_completive_past_syllabary=clean_cherokee_field(
                row["Verb 3rd Past (Syllabary)"]
            ).upper(),
            third_incompletive_habitual=clean_cherokee_field(
                row["Verb 3rd Present Habitual (Tone)"]
            ),
            third_incompletive_habitual_simple=clean_cherokee_field(
                row["Verb 3rd Present Habitual"]
            ),
            third_incompletive_habitual_syllabary=clean_cherokee_field(
                row["Verb 3rd Present Habitual (Syllabary)"]
            ).upper(),
            second_command=clean_cherokee_field(
                row["Verb 2nd Imperative (Tone)"].split(",")[0]
            ),
            second_command_simple=clean_cherokee_field(
                row["Verb 2nd Imperative"].split(",")[0]
            ),
            second_command_syllabary=clean_cherokee_field(
                row["Verb 2nd Imperative (Syllabary)"].split(",")[0]
            ).upper(),
            second_command_alt=clean_cherokee_field_or(
                get_item(row["Verb 2nd Imperative (Tone)"].split(","), 1)
            ),
            second_command_alt_simple=clean_cherokee_field_or(
                get_item(row["Verb 2nd Imperative"].split(","), 1)
            ),
            second_command_alt_syllabary=clean_cherokee_field_or(
                upper_or(get_item(row["Verb 2nd Imperative (Syllabary)"].split(","), 1))
            ),
            third_infinitive=clean_cherokee_field(row["Verb 3rd Infinitive (Tone)"]),
            third_infinitive_simple=clean_cherokee_field(row["Verb 3rd Infinitive"]),
            third_infinitive_syllabary=clean_cherokee_field(
                row["Verb 3rd Infinitive (Syllabary)"]
            ).upper(),
            sentence=SentenceRow.from_row(row),
        )


SOURCES_WITH_TONE = ["ced"]


def read_verbs():
    with open("Cherokee Dictionary (w_ MDS) - Dictionary.csv") as f:
        headers = next(csv.reader(f))

        reader = csv.DictReader(f, fieldnames=headers)

        for row in reader:
            try:
                # if row["PoS"] not in ("vt", "v", "vi"):
                #     continue

                verb_row = VerbRow.from_row(row)
                # if verb_row.has_all_fields():
                if True:
                    yield verb_row
            except:
                print("Error reading row", row["Index"], row["Entry"])


COLORS = ["magenta", "red", "blue", "green"]


def main():
    sentences = {row.index: asdict(row) for row in read_verbs()}
    json.dump(sentences, open("dict_large_alt_forms.json", "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
