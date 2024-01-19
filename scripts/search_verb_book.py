from csv import DictReader
import re
from tabulate import tabulate

COLUMNS = ["verb", "person", "tense", "form", "form (JW)", "notes"]
TENSES = [
    "pres",
    "hab",
    "rempast",
    "reppast",
    "immpast",
    "fut",
    "inf",
    "presimp",
    "futimp",
]


def read_csv():
    rows = []
    with open("handbook-verbs.csv") as f:
        for row in DictReader(
            f,
            fieldnames=COLUMNS,
            delimiter=",",
        ):
            if row == {} or row == {c: c for c in COLUMNS}:
                continue
            rows.append(row)
    return rows


def main():
    # ¹²³⁴
    rows = read_csv()

    # pattern for pronominals that are expected to be long
    # osdi, otsi, sdi, itsi
    short_pronominal = re.compile(r".*((sd)|j|n|d)i[¹²³⁴]\.")
    forms_with_short_pronominal = [
        row
        for row in rows
        if row["person"] not in {"1s", "2s"}
        and short_pronominal.match(row["form (JW)"])
    ]

    words_with_short_pronominal = set(
        row["verb"] for row in forms_with_short_pronominal
    )

    print(len(forms_with_short_pronominal), len(words_with_short_pronominal))

    # how many are followed by glottals?
    glottal_after_pronoun = re.compile(r".*\.ʔ")
    forms_followed_by_glottals = [
        row
        for row in forms_with_short_pronominal
        if glottal_after_pronoun.match(row["form (JW)"])
    ]

    aspirated_consonant = re.compile(r".*\.(([^\.]h)|(h[^aeiouv]))[^aeiouv]")
    forms_followed_by_aspirated_consonant = [
        row
        for row in forms_with_short_pronominal
        if aspirated_consonant.match(row["form (JW)"])
    ]

    print(
        len(forms_with_short_pronominal),
        len(forms_followed_by_glottals),
        len(forms_followed_by_aspirated_consonant),
        len(forms_followed_by_aspirated_consonant) + len(forms_followed_by_glottals),
    )

    accounted_for = set(
        row["form (JW)"]
        for row in forms_followed_by_glottals + forms_followed_by_aspirated_consonant
    )

    neither = [
        row
        for row in forms_with_short_pronominal
        if not row["form (JW)"] in accounted_for
    ]

    print(tabulate(neither))

    # now reverse analysis!

    # pattern for pronominals that are expected to be long
    # osdi, otsi, sdi, itsi
    long_pronominal = re.compile(r".*((sd)|j|n|d)i[¹²³⁴][¹²³⁴]\.")
    forms_followed_by_glottals_with_long = [
        row
        for row in rows
        if glottal_after_pronoun.match(row["form (JW)"])
        and long_pronominal.match(row["form (JW)"])
        if row["person"] not in {"1s", "2s"} and not row["form (JW)"].startswith("e")
    ]

    # should all be *animate* forms, where there is 21 + glottal
    print(tabulate(forms_followed_by_glottals_with_long))

    forms_followed_by_aspirated_consonant_with_long = [
        row
        for row in rows
        if aspirated_consonant.match(row["form (JW)"])
        and long_pronominal.match(row["form (JW)"])
        if row["person"] not in {"1s", "2s"} and not row["form (JW)"].startswith("e")
    ]

    # should all be *animate* forms, where there is 21 + glottal
    print(tabulate(forms_followed_by_aspirated_consonant_with_long))


if __name__ == "__main__":
    main()
