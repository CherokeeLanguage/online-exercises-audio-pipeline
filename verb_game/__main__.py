"""
Converts the raw data from the Handbook of the Cherokee Verb.  into a nice, rich
JSON for an online verb game.
"""

import code
from csv import DictReader
from pathlib import Path

from verb_game.annotate_form import annotate_conjugations

from .structs import Person, RawConjugatedVerb, RawVerb, Verb, VerbForm


def read_raw_forms(path: Path) -> dict[str, RawVerb]:
    with open(path) as src:
        reader = DictReader(
            src, ["verb", "person", "tense", "form", "form (JW)", "notes"]
        )
        raw_forms: dict[str, RawVerb] = {}
        for row in reader:
            english = row["verb"]
            if english not in raw_forms:
                raw_forms[english] = RawVerb(english=english, forms={})

            verb = raw_forms[english]

            try:
                form = VerbForm(row["tense"])
                if form not in verb.forms:
                    verb.forms[form] = {}

                person = Person(row["person"])
                verb.forms[form][person] = RawConjugatedVerb(
                    verb=english, person=person, phonetics=row["form (JW)"]
                )
            except:
                print(f"couldn't parse form: {row}")
                continue

    return raw_forms


VERB_BOOK_CSV = Path("./handbook-verbs.csv")


def main():
    raw_forms = read_raw_forms(VERB_BOOK_CSV)

    annotated_verbs: dict[str, Verb] = {}

    for verb in raw_forms:
        annotated_verb = Verb(english=verb, forms={})
        annotated_verbs[verb] = annotated_verb

        for form, conjugations in raw_forms[verb].forms.items():
            annotated_verb.forms[form] = annotate_conjugations(form, conjugations)

    code.interact(local=dict(globals(), **locals()))


if __name__ == "__main__":
    main()
