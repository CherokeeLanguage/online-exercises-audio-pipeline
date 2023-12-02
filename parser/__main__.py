from dataclasses import dataclass, asdict

import json
import re
from typing import Dict, List, Tuple
from tabulate import tabulate
from parser.root_frequencies import count_roots_with_dict

from parser.utils import SYLLABLE_VOWELS
from .prefixes import ParsedWord, Prefix, PronominalPrefix, all_parses


@dataclass
class SentenceRow:
    syllabary: str
    phonetics: str
    english: str


@dataclass
class VerbRow:
    index: str
    source: str
    definition: str
    third_present: str
    third_present_syllabary: str
    first_present: str
    first_present_syllabary: str
    second_command: str
    second_command_syllabary: str
    third_completive_past: str
    third_completive_past_syllabary: str
    third_incompletive_habitual: str
    third_incompletive_habitual_syllabary: str
    third_infinitive: str
    third_infinitive_syllabary: str
    sentence: SentenceRow


def infixes(parse: ParsedWord) -> List[Prefix]:
    for idx, prefix in enumerate(parse.prefixes):
        if isinstance(prefix, PronominalPrefix):
            return parse.prefixes[idx + 1 :]

    return []


def infixes_match(parse1: ParsedWord, parse2: ParsedWord):
    return infixes(parse1) == infixes(parse2)


def equal_up_to_h_alternation(third_form: str, first_form: str) -> bool:
    if third_form == first_form:
        return True

    if len(third_form) != len(first_form):
        return False

    if first_form == third_form.replace("Ꭽ", "Ꭰ", 1):
        return True
    if first_form == third_form.replace("Ꭾ", "Ꭰ", 1):
        return True
    if first_form == third_form.replace("Ꭿ", "Ꭰ", 1):
        return True
    if first_form == third_form.replace("Ꮀ", "Ꭰ", 1):
        return True
    if first_form == third_form.replace("Ꮁ", "Ꭰ", 1):
        return True
    if first_form == third_form.replace("Ꮂ", "Ꭰ", 1):
        return True

    # only one letter different? that's cool
    first_difference = [a != b for a, b in zip(first_form, third_form)].index(True)
    if (
        SYLLABLE_VOWELS[first_form[first_difference]]
        == SYLLABLE_VOWELS[third_form[first_difference]]
    ):
        # only consonant changed? cool
        return True

    return False


def roots_for_row(word: VerbRow) -> List[ParsedWord]:
    # parse each form as best we can
    parsed_forms: Dict[str, Tuple[str, List[ParsedWord]]] = {
        name: (
            form,
            [
                parse
                for parse in all_parses(form)
                if next(
                    (
                        True
                        for p in parse.prefixes
                        if isinstance(p, PronominalPrefix)
                        and p.person.startswith(expected_person)
                        and p.set.startswith(expected_set)  # handles "" well
                    ),
                    False,
                )
            ],
        )
        for name, form, expected_person, expected_set in [
            ("First present", word.first_present_syllabary, "1", ""),
            ("Second command", word.second_command_syllabary, "2", ""),
            ("Third habitual", word.third_incompletive_habitual_syllabary, "3", ""),
            ("Third present", word.third_present_syllabary, "3", ""),
            ("Third completive past", word.third_completive_past_syllabary, "3", "B"),
            ("Third infinitive", word.third_infinitive_syllabary, "3", "B"),
        ]
    }

    problems = []

    for name, (form, parses) in parsed_forms.items():
        if len(parses) == 0:
            print(f"problem with {name}: {form}")
            problems.append(f"[{name}]: could not parse {form}")

    if len(problems):
        return []
        return problems

    present_roots = {
        parse
        for parse in parsed_forms["Third present"][1]
        if any(
            equal_up_to_h_alternation(parse.root, parse2.root)
            and infixes_match(parse, parse2)
            for parse2 in parsed_forms["First present"][1]
        )
    }

    if len(present_roots) == 0:
        print("Couldn't resolve present root for", word)
        return []
        return [
            "no consistent present roots",
            word.first_present_syllabary,
            word.third_present_syllabary,
        ]

    # longest root
    present_root = max(
        present_roots, key=lambda root: 10 * len(infixes(root)) + len(root.root)
    )
    print("present", present_root)

    completive_roots = {
        parse
        for parse in parsed_forms["Third completive past"][1]
        if any(s.name == "EXP" for s in parse.suffixes)
        and parse.root.startswith(present_root.root[0])
        and infixes_match(parse, present_root)
        # and parse.root.startswith(
        #     present_root[0:-2]
        # )  # should be at least a bit similar
    }
    print("completive", completive_roots)

    incompletive_roots = {
        parse
        for parse in parsed_forms["Third habitual"][1]
        if any(s.name == "HBT" for s in parse.suffixes)
        and parse.root.startswith(present_root.root[0])
        and infixes_match(parse, present_root)
        # and parse.root.startswith(
        #     present_root[0:-2]
        # )  # should be at least a bit similar
    }
    print("incompletive", incompletive_roots)

    infinitive_roots = {
        parse
        for parse in parsed_forms["Third infinitive"][1]
        if any(s.name == "INF" for s in parse.suffixes)
        and parse.root.startswith(present_root.root[0])
        and infixes_match(parse, present_root)
        # and parse.root.startswith(
        #     present_root[0:-2]
        # )  # should be at least a bit similar
    }
    print("infinitive", infinitive_roots)

    return [*present_roots, *incompletive_roots, *completive_roots, *infinitive_roots]

    if len(incompletive_roots) == len(completive_roots) == len(infinitive_roots) == 1:
        return []

    else:
        return [
            "multiple root forms",
            str(present_root),
            str(incompletive_roots),
            str(completive_roots),
            str(infinitive_roots),
        ]


def main():
    data: Dict[str, VerbRow] = {
        k: VerbRow(
            **{k: v for k, v in d.items() if not k == "sentence"},
            sentence=SentenceRow(
                **{
                    k: v.replace("*", "")
                    .replace("?", "")
                    .replace(".", "")
                    .replace("!", "")
                    .replace(",", "")
                    .replace('"', "")
                    for k, v in d["sentence"].items()
                }
            ),
        )
        for k, d in json.load(
            open("dict_verbs.json"),
        ).items()
    }

    # row = data["1538"]  # ᏂᎦᏪᎠ
    # for parse in all_parses(row.third_completive_past_syllabary):
    #     print(parse)

    # root_for_row(row)

    problem_words = []
    # perfect_words = []

    for parse in all_parses("ᎤᏓᏱᎸᎢ"):
        print(parse)

    input()

    root_based_dict: Dict[str, List[VerbRow]] = {}

    for id, word in data.items():
        if "," in word.first_present + word.second_command:
            continue
        roots = roots_for_row(word)
        if len(roots) == []:
            problem_words.append(word)
        for parse in roots:
            if parse.root not in root_based_dict:
                root_based_dict[parse.root] = [word]
            if not any(
                dict_word.index == word.index
                for dict_word in root_based_dict[parse.root]
            ):
                root_based_dict[parse.root].append(word)

    json.dump(
        {
            root: [verb.index for verb in verbs]
            for root, verbs in root_based_dict.items()
        },
        open("root_based_dict.json", "w"),
        ensure_ascii=False,
    )

    counts = count_roots_with_dict(
        root_dict=set(root_based_dict.keys()),
        sentences=(word.sentence.syllabary for _id, word in data.items()),
    )

    counts_by_id: dict[str, int] = {}

    for root, count in counts.items():
        for row in root_based_dict[root]:
            counts_by_id[row.index] = counts_by_id.get(row.index, 0) + count

    most_common_roots = sorted(
        counts_by_id.items(), key=lambda item: item[1], reverse=True
    )

    for start in range(0, len(most_common_roots), 10):
        for i, (root_id, count) in enumerate(most_common_roots[start : start + 10]):
            row = data[root_id]
            print(f"{start+i+1}: {row.third_present_syllabary} has {count} occurances")
            print(f"\t{row.third_present_syllabary} / {row.definition}")

        input()

    # for id, dict_word in data.items():
    #     print(f"{dict_word.third_present_syllabary} / {dict_word.definition}")
    #     print(f"{dict_word.sentence.syllabary}")
    #     print(f"{dict_word.sentence.english}")
    #     print()
    #     for word in dict_word.sentence.syllabary.split(" "):
    #         word = re.sub('[ \*\.,\?"]', "", word)
    #         found = ""
    #         for parses in all_parses(word):
    #             if parses.root in root_based_dict:
    #                 found = root_based_dict[parses.root][0].definition

    #         if len(found):
    #             print(found, end="\t")
    #     input()

    for id, dict_word in data.items():
        if (
            "," in dict_word.first_present + dict_word.second_command
            or dict_word in problem_words
        ):
            continue
        example_forms = re.findall(r"\*([^\*]*)\*", dict_word.sentence.syllabary)
        for example in example_forms:
            parses = list(all_parses(example))
            for parse in parses:
                if parse.root in root_based_dict:
                    if any(row.index == id for row in root_based_dict[parse.root]):
                        # we found a match!
                        print(dict_word.definition, example, parse)
                        break

            else:
                print(
                    f"Couldn't parse form in example sentence ({dict_word.third_present_syllabary}: {dict_word.definition})"
                )
                print(dict_word.sentence.syllabary)
                print(dict_word.sentence.english)
                print(example)
                print("\n".join(f"\t{p}" for p in parses))
                input()

    #     if len(problems):
    #         problem_words.append((id, word.definition, problems))
    #     else:
    #         perfect_words.append((id, word.definition))

    # json.dump(problem_words, open("problem_words.json", "w"), ensure_ascii=False)
    # json.dump(perfect_words, open("perfect_words.json", "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
