from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Optional, Union
import csv
import re
import unicodedata
from tabulate import tabulate


def clean_field(field: str) -> str:
    return unicodedata.normalize("NFD", field.strip())


DICT_CSV_COLUMNS = [
    "id",
    "definitiond",
    "nounadjpluralsyllf",
    "sentenceenglishs",
    "sentenceq",
    "sentencesyllr",
    "syllabaryb",
    "vfirstpresh",
    "vsecondimpersylln",
    "vthirdinfsyllp",
    "vthirdpastsyllj",
    "vthirdpressylll",
    "entrytone",
    "nounadjpluraltone",
    "vfirstprestone",
    "vsecondimpertone",
    "vthirdinftone",
    "vthirdpasttone",
    "vthirdprestone",
    "source",
]


@dataclass
class VerbRow:
    id: str
    definition: str
    third_present: str
    first_present: str
    second_command: str
    third_completive_past: str
    third_incompletive_habitual: str
    third_infinitive: str

    def has_all_fields(self):
        fields = [
            self.id,
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
            id=clean_field(row["id"]),
            definition=clean_field(row["definitiond"]),
            third_present=clean_field(row["entrytone"]).split(",")[0],
            first_present=clean_field(row["vfirstprestone"]).split(",")[0],
            third_completive_past=clean_field(row["vthirdpasttone"]),
            third_incompletive_habitual=clean_field(row["vthirdprestone"]),
            third_infinitive=clean_field(row["vthirdinftone"]),
            second_command=clean_field(row["vsecondimpertone"]),
        )


class PronounSet(Enum):
    SetA = "SetA"
    SetB = "SetB"


@dataclass
class Verb:
    pronoun_set: PronounSet
    uses_ga: bool
    h_alternates: bool
    present_root: str
    completive_root: str
    incompletive_root: str
    immediate_root: str
    infinitive_root: str

    @staticmethod
    def from_verb_row(row: VerbRow):
        """Deduce roots from row"""
        res = deduce_completive_and_incompletive_stems(row)
        if res is None:
            print("Couldn't deduce completive and incompletive stems")
            return

        set, completive, incompletive = res

        # deduce present tense and if verb starts with vowel
        third_pattern = (
            r"^a\u0323?([\d\.]*)|([¹²³⁴]*)"
            if set == PronounSet.SetA
            else r"^(u)([\d\.]*)|([¹²³⁴]*)"
        )

        if not re.match(third_pattern, row.third_present):
            print("Couldn't parse 3rd person")
            return

        present_continous = re.sub(third_pattern, "", row.third_present)

        first_pattern_vowel = (
            r"^g" if set == PronounSet.SetA else r"^a([\d\.]*)|([¹²³⁴]*)gw"
        )

        vowel_start = bool(re.match(first_pattern_vowel, row.first_present))
        euphonic_w = False

        verb_first_vowel = ""

        if vowel_start:
            print(vowel_start)
            # verb starts with vowel
            verb_first_vowel = re.match(
                r"^g([aeiouv]\u0323?([\d\.]*)|([¹²³⁴]*))", row.first_present
            )

            if verb_first_vowel is None:
                print("Verb starts with vowel but we couldn't find it!")
                return

            verb_first_vowel = verb_first_vowel.group(1)

            if verb_first_vowel.startswith("a"):
                completive = verb_first_vowel + completive
                incompletive = verb_first_vowel + incompletive
                present_continous = verb_first_vowel + present_continous
            else:
                if completive.startswith("w"):
                    euphonic_w = True
                    completive = completive[1:]
                if set == PronounSet.SetB and incompletive.startswith("w"):
                    euphonic_w = True
                    incompletive = incompletive[1:]
                if set == PronounSet.SetB and present_continous.startswith("w"):
                    euphonic_w = True
                    present_continous = present_continous[1:]

        pattern_first = (
            first_pattern_vowel
            if vowel_start
            else (
                r"^((j|(ts))i)\u0323?([\d\.]*)|([¹²³⁴]*)"
                if set == PronounSet.SetA
                else r"^(agi)\u0323?([\d\.]*)|([¹²³⁴]*)"
            )
        )
        present_continous_from_first = re.sub(pattern_first, "", row.first_present)
        if not present_continous == present_continous_from_first:
            present_continous += "/" + present_continous_from_first

        # Parse command form

        if set == PronounSet.SetA:
            assert row.second_command.startswith("h")
            immediate = re.sub(
                r"^h(i\u0323?([\d\.]*)|([¹²³⁴]*))?", "", row.second_command
            )
        else:
            # not actually immediate (Set B cannot be commanded with Set A)
            immediate = "not shown"

        # Parse infinitive
        infinitive = re.sub(
            r"u\u0323?([\d\.]*)|([¹²³⁴]*)w"
            if euphonic_w
            else r"u\u0323?([\d\.]*)|([¹²³⁴]*)",
            "",
            row.third_infinitive,
        )

        if euphonic_w and verb_first_vowel in ["v", "u"]:
            # fix vowel
            infinitive = verb_first_vowel + infinitive[1:]

        print()
        print(
            tabulate(
                [
                    [
                        unicodedata.normalize("NFC", form)
                        for form in [
                            "-" + present_continous,
                            "-" + completive + "-",
                            "-" + incompletive + "-",
                            "-" + immediate,
                            "-" + infinitive,
                        ]
                    ]
                ],
                headers=[
                    "present continuous",
                    "completive",
                    "incompletive",
                    "immediate",
                    "infinitive",
                ],
            ),
        )
        print()


def deduce_completive_and_incompletive_stems(row: VerbRow):
    completive_with_pronoun_and_prefixes = re.sub(
        r"(v2?3\?i)|(v²?³ɂi)$", "", row.third_completive_past
    )
    incompletive_with_pronoun_and_prefixes = re.sub(
        r"(o\.?3\?i)|(o³ɂi)$", "", row.third_incompletive_habitual
    )

    # print(completive_with_pronoun_and_prefixes, incompletive_with_pronoun_and_prefixes)

    if completive_with_pronoun_and_prefixes.startswith("u"):
        # no prefixes
        if re.match(r"^(ạ|a|g)", incompletive_with_pronoun_and_prefixes):
            # set A
            completive_root = re.sub(
                r"^u([\d\.]*)|([¹²³⁴]*)", "", completive_with_pronoun_and_prefixes
            )
            incompletive_root = re.sub(
                r"^(a|ạ|g)([\d\.]*)|([¹²³⁴]*)",
                "",
                incompletive_with_pronoun_and_prefixes,
            )
            return PronounSet.SetA, completive_root, incompletive_root
        elif incompletive_with_pronoun_and_prefixes.startswith("u"):
            completive_root = re.sub(
                r"^u([\d\.]*)|([¹²³⁴]*)", "", completive_with_pronoun_and_prefixes
            )
            incompletive_root = re.sub(
                r"^u([\d\.]*)|([¹²³⁴]*)", "", incompletive_with_pronoun_and_prefixes
            )
            return PronounSet.SetB, completive_root, incompletive_root
        else:
            print("Unexpected third person incompletive form")
            return
    else:
        print("Unexpected third person completive form")
        return


def main():
    reader = csv.DictReader(
        open("data/full-dict/full_dict_raw.txt"),
        fieldnames=DICT_CSV_COLUMNS,
        delimiter="|",
    )

    for dict_row in reader:
        verb_row = VerbRow.from_row(dict_row)
        if not verb_row.has_all_fields():
            continue
        match = "eating" in verb_row.definition
        if not match:
            continue

        print(
            tabulate(
                [
                    [
                        unicodedata.normalize("NFC", value)
                        for value in asdict(verb_row).values()
                    ]
                ],
                headers=[key for key in asdict(verb_row).keys()],
            )
        )
        print(Verb.from_verb_row(verb_row))
        input()


if __name__ == "__main__":
    main()
