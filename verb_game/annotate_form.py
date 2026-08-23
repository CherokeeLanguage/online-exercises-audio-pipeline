from typing import Mapping
from verb_game.structs import ConjugatedVerb, Person, RawConjugatedVerb, VerbForm


DEFAULT_TONICITY: Mapping[VerbForm, bool] = {
    VerbForm.Present: True,
    VerbForm.Habitual: True,
    VerbForm.ExperiencedPast: True,
    VerbForm.ReportedPast: True,
    VerbForm.FutureCommand: True,
    VerbForm.ImmediatePast: True,
    VerbForm.ImmediateCommand: False,
    VerbForm.Infinitive: False,
    VerbForm.DaFuture: False,
}

IS_PLURAL: Mapping[Person, bool] = {
    Person.FirstPersonSingluar: False,
    Person.SecondPersonSingluar: False,
    Person.SecondPersonDual: True,
    Person.SecondPersonPlural: True,
    Person.ExclusiveDual: True,
    Person.ExclusivePlural: True,
    Person.InclusiveDual: True,
    Person.InclusivePlural: True,
    Person.ThirdPersonSingluar: False,
    Person.ThirdPersonPlural: True,
}


def annotate_conjugations(
    form: VerbForm, conjugations: dict[Person, RawConjugatedVerb]
) -> dict[Person, ConjugatedVerb]:
    """
    Annotate this family of conjugations.

    1. Determine any prefixes
    2. Determine the pronoun set
    3. Determine tonicity
    4. Find H3 assignment
    """

    if conjugations[Person.SecondPersonSingluar].phonetics.startswith("g"):
        # prefix
        pass
    pass
