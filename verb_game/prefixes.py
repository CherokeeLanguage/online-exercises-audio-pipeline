"""
Module for deducing which pronoun set a verb is built from
"""

from typing import Optional, Tuple

from .structs import PronounSet, RawConjugatedVerb, Person


def try_determine_prefixes(
    form: RawConjugatedVerb,
) -> Tuple[list[str], Optional[PronounSet]]:
    pass
