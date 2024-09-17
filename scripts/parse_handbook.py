from csv import DictWriter
import json
import re
from typing import Dict
import unicodedata


def convert_consonants(phonetics: str) -> str:
    return (
        phonetics.replace("t", "d")
        .replace("dh", "t")
        .replace("k", "g")
        .replace("gh", "k")
    )


def convert_tones(source: str):
    # ¹²³⁴
    out = unicodedata.normalize("NFD", source)
    out = re.sub("([aeiouv])\u0301([aeiouv])\u0301", r"\1³³", out)
    out = re.sub("([aeiouv])\u0301([aeiouv])", r"\1³²", out)
    out = re.sub("([aeiouv])([aeiouv])\u0301", r"\1²³", out)
    out = re.sub("([aeiouv])\u0301", r"\1³", out)
    out = re.sub("([aeiouv])\u0300([aeiouv])\u0300", r"\1²¹", out)
    out = re.sub("([aeiouv])\u0300", r"\1¹", out)
    out = re.sub("([aeiouv])([aeiouv])", r"\1²²", out)
    out = re.sub("([aeiouv])(?![¹²³⁴])", r"\1²", out)  # vowels without tones are level
    return out


def main():
    # [verb][tense][person]
    all_forms: Dict[str, Dict[str, Dict[str, str]]] = {}
    with open("handbook-verbs.txt") as f, open("handbook-verbs.csv", "w") as out:
        writer = DictWriter(
            out, ["verb", "person", "tense", "form", "form (JW)", "notes"]
        )
        writer.writeheader()
        verb = None
        for line in f:
            line = line.strip()

            if not line.startswith("\\"):
                continue

            if " " in line:
                label, data = line.split(" ", 1)
            else:
                label = line
                data = ""

            if label == "\\eng":
                verb = data
            else:
                person, tense = label.split("-")
                person = person.strip("\\")

                if " " in data:
                    form, notes = data.split(" ", 1)
                else:
                    form = data
                    notes = ""

                if not verb:
                    continue

                jw_form = convert_consonants(convert_tones(form))

                if verb not in all_forms:
                    all_forms[verb] = {}
                if tense not in all_forms[verb]:
                    all_forms[verb][tense] = {}
                if person not in all_forms[verb][tense]:
                    all_forms[verb][tense][person] = jw_form

                writer.writerow(
                    {
                        "verb": verb,
                        "person": person.strip("\\"),
                        "tense": tense,
                        "form": form,
                        "form (JW)": jw_form,
                        "notes": notes.strip(),
                    }
                )

    json.dump(all_forms, open("handbook-verbs.json", "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
