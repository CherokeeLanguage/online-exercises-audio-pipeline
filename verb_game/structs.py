from enum import Enum

from dataclasses import dataclass


class PronounSet(Enum):
    SetA = "A"
    SetB = "B"
    AnimateObject = "animate"


class VerbForm(Enum):
    Present = "pres"
    Habitual = "hab"
    ExperiencedPast = "rempast"
    ReportedPast = "reppast"
    ImmediatePast = "immpast"
    DaFuture = "fut"
    Infinitive = "inf"
    ImmediateCommand = "presimp"
    FutureCommand = "futimp"


class Person(Enum):
    FirstPersonSingluar = "1s"
    SecondPersonSingluar = "2s"
    SecondPersonDual = "2d"
    SecondPersonPlural = "2p"
    ExclusiveDual = "Ed"
    ExclusivePlural = "Ep"
    InclusiveDual = "Id"
    InclusivePlural = "Ip"
    ThirdPersonSingluar = "3s"
    ThirdPersonPlural = "3p"


@dataclass
class RawConjugatedVerb:
    verb: str
    person: Person

    phonetics: str


@dataclass
class ConjugatedVerb:
    form: RawConjugatedVerb

    animate_object: bool
    tonic: bool
    pronoun_set: PronounSet

    prefixes: list[str]


@dataclass
class RawVerb:
    english: str
    forms: dict[VerbForm, dict[Person, RawConjugatedVerb]]


@dataclass
class Verb:
    english: str
    forms: dict[VerbForm, dict[Person, ConjugatedVerb]]
