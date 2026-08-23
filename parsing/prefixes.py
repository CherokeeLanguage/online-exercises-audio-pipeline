from ast import Tuple
from dataclasses import dataclass
from typing import Callable, Dict, Generator, List

from parsing.utils import SYLLABLE_VOWELS, get_protypical_syllable

RemoveFn = Callable[[str], Generator[str, None, None]]


@dataclass
class ParsedWord:
    prefixes: List["Prefix"]
    root: str
    suffixes: List["Suffix"]

    def __str__(self):
        return f"{'-'.join([str(p) for p in self.prefixes])}-{self.root}-{'-'.join([str(p) for p in self.suffixes])}"

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self):
        return hash(str(self))


@dataclass
class Prefix:
    name: str
    # possible results from removing this prefix
    # return empty list if not possible
    remove: RemoveFn

    def parse(self, word: ParsedWord) -> Generator[ParsedWord, None, None]:
        for result in self.remove(word.root):
            yield ParsedWord(
                prefixes=[*word.prefixes, self], root=result, suffixes=word.suffixes
            )

        yield word

    def __str__(self):
        return f"{self.name}"


@dataclass
class PronominalPrefix(Prefix):
    person: str
    set: str


@dataclass
class Suffix:
    name: str
    # possible results from removing this suffix
    # return empty list if not possible
    remove: RemoveFn

    def parse(self, word: ParsedWord) -> Generator[ParsedWord, None, None]:
        for result in self.remove(word.root):
            yield ParsedWord(
                prefixes=word.prefixes, root=result, suffixes=[self, *word.suffixes]
            )

        yield word

    def __str__(self):
        return f"{self.name}"


def remove_prefix_from_forms(forms: Dict[str, List[str]]) -> RemoveFn:
    def remove(word: str) -> Generator[str, None, None]:
        for variant in forms:
            if word.startswith(variant):
                for form in forms[variant]:
                    yield form + word[len(variant) :]

    return remove


YI = Prefix(
    name="YI",
    remove=remove_prefix_from_forms(
        forms={"y": [""], "yi": [""], "yu": [""]}  # yu before wi
    ),
)

TSI = Prefix(
    name="TSI",
    remove=remove_prefix_from_forms(
        forms={
            "j": [""],
            "ji": [""],
        }
    ),
)

WI = Prefix(
    name="WI",
    remove=remove_prefix_from_forms(forms={"w": [""], "wi": [""]}),
)

NI = Prefix(
    name="NI",
    remove=remove_prefix_from_forms(
        forms={
            "hn": ["h"],
            "n": [""],
            "ni": [""],
            # "Ꮎ": ["Ꭰ", "Ꭽ"],
            # "Ꮏ": ["Ꭽ"],
            # "Ꮑ": ["Ꭱ", "Ꭾ"],
            # "Ꮒ": ["", "Ꭲ", "Ꭿ"],
            # "Ꮓ": ["Ꭳ", "Ꮀ"],
            # "Ꮔ": ["Ꭴ", "Ꮁ"],
            # "Ꮕ": ["Ꭵ", "Ꮂ"],
        }
    ),
)

NI2 = Prefix(
    name="NI2",
    remove=remove_prefix_from_forms(
        forms={
            "iy": [""],
            "i": ["", "i"],
        }
    ),
)

DE = Prefix(
    name="DE_PLURAL",
    remove=remove_prefix_from_forms(
        forms={
            "d": [""],
            "do": ["v", "i", ""],
            "de": ["", "i"],
        }
    ),
)

DE2 = Prefix(
    name="DE_PLURAL",
    remove=remove_prefix_from_forms(
        forms={
            "d": [""],
            "di": ["i", "a", ""],
            "t": ["h"],
            # # fused forms
            # "Ꮤ": ["Ꭽ"],
            # "Ꮦ": ["Ꭾ"],
            # "Ꮨ": ["Ꭿ"],
            # "Ꮩ": ["Ꮀ"],
            # "Ꮪ": ["Ꮁ"],
            # "Ꮫ": ["Ꮂ"],
            # # "Ꮫ": ["Ꭵ"], # not sure...
        }
    ),
)

DA = Prefix(
    name="DA_FUTURE",
    remove=remove_prefix_from_forms(
        forms={
            "day": [""],
            "dv": ["v", "a", ""],
            "da": ["", "i"],
        }
    ),
)

I_AGAIN = Prefix(
    name="I_AGAIN",
    remove=remove_prefix_from_forms(
        forms={
            "i": [""],
            "v": [""],
            # sometimes also a tone... hrmrmmr
        }
    ),
)

GA = Prefix(
    name="GA",
    remove=remove_prefix_from_forms(
        forms={
            "ga": [""],
            "ge": ["", "e", "i"],
            "gv": ["a"],
            "gvwa": ["a", "u", "u1wa"],
        }
    ),
)

INITIAL_PREFIXES = [YI, TSI, WI, NI, NI2, DE, DE2, DA, I_AGAIN, GA]

SET_A_1SG = PronominalPrefix(
    person="1SG",
    set="A",
    name="1SG.A",
    remove=remove_prefix_from_forms(forms={"ji": [""], "g": [""]}),
)


SET_A_1DL_IN = PronominalPrefix(
    person="1DL_IN",
    set="A",
    name="1DL_IN.A",
    remove=remove_prefix_from_forms(forms={"ini": [""], "in": [""]}),
)


SET_A_1PL_IN = PronominalPrefix(
    person="1PL_IN",
    set="A",
    name="1PL_IN.A",
    remove=remove_prefix_from_forms(forms={"id": [""], "idi": [""]}),
)


SET_A_1DL_EX = PronominalPrefix(
    person="1DL_EX",
    set="A",
    name="1DL_EX.A",
    remove=remove_prefix_from_forms(forms={"osdi": [""], "osd": [""]}),
)


SET_A_1PL_EX = PronominalPrefix(
    person="1PL_EX",
    set="A",
    name="1PL_EX.A",
    remove=remove_prefix_from_forms(
        forms={
            "oji": [""],
            "oj": [""],
        }
    ),
)

SET_A_2SG = PronominalPrefix(
    person="2SG",
    set="A",
    name="2SG.A",
    remove=remove_prefix_from_forms(
        forms={
            "h": [""],
            "hi": [""],
        }
    ),
)


SET_A_2DL = PronominalPrefix(
    person="2DL",
    set="A",
    name="2DL.A",
    remove=remove_prefix_from_forms(
        forms={
            "sd": [""],
            "sdi": [""],
        }
    ),
)

SET_A_2PL = PronominalPrefix(
    person="2PL",
    set="A",
    name="2PL.A",
    remove=remove_prefix_from_forms(
        forms={
            "ij": [""],
            "iji": [""],
        }
    ),
)


SET_A_3SG = PronominalPrefix(
    person="3SG",
    set="A",
    name="3SG.A",
    remove=remove_prefix_from_forms(
        forms={
            "a": ["", "a"],
            "ga": ["", "a"],
            "g": [""],
            "k": ["h"],
            "ka": ["h", "ah"],
            "ke": ["eh"],
            "ku": ["uh"],
            "v": ["v"],  # some eastern words do this
        }
    ),
)


SET_A_3PL = PronominalPrefix(
    person="3PL",
    set="A",
    name="3PL.A",
    remove=remove_prefix_from_forms(
        forms={
            "ani": [""],
            "an": [""],
        }
    ),
)

SET_B_1SG = PronominalPrefix(
    person="1SG",
    set="B",
    name="1SG.B",
    remove=remove_prefix_from_forms(
        forms={
            "agi": [""],
            "agw": [""],
        }
    ),
)

SET_B_1DL_EX = PronominalPrefix(
    person="1DL_EX",
    set="B",
    name="1DL_EX.B",
    remove=remove_prefix_from_forms(
        forms={
            "ogini": [""],
            "ogin": [""],
        }
    ),
)

SET_B_1PL_EX = PronominalPrefix(
    person="1PL_EX",
    set="B",
    name="1PL_EX.B",
    remove=remove_prefix_from_forms(
        forms={
            "ogi": [""],
            "og": [""],
        }
    ),
)

SET_B_1DL_IN = PronominalPrefix(
    person="1DL_IN",
    set="B",
    name="1DL_IN.B",
    remove=remove_prefix_from_forms(
        forms={
            "gini": [""],
            "gin": [""],
        }
    ),
)

SET_B_1PL_IN = PronominalPrefix(
    person="1PL_IN",
    set="B",
    name="1PL_IN.B",
    remove=remove_prefix_from_forms(
        forms={
            "igi": [""],
            "ig": [""],
        }
    ),
)

SET_B_2SG = PronominalPrefix(
    person="2SG",
    set="B",
    name="2SG.B",
    remove=remove_prefix_from_forms(forms={"ja": [""], "j": [""]}),
)

SET_B_2DL = PronominalPrefix(
    person="2DL",
    set="B",
    name="2DL.B",
    remove=remove_prefix_from_forms(
        forms={
            "sd": [""],
            "sdi": [""],
        }
    ),
)


SET_B_2PL = PronominalPrefix(
    person="2PL",
    set="B",
    name="2PL.B",
    remove=remove_prefix_from_forms(
        forms={
            "ij": [""],
            "iji": [""],
        }
    ),
)


SET_B_3SG = PronominalPrefix(
    person="3SG",
    set="B",
    name="3SG.B",
    remove=remove_prefix_from_forms(
        forms={
            "u": ["", "a"],
            "uw": [""],
            "uwa": ["v"],
            "uwa": [""],
        }
    ),
)


SET_B_3PL = PronominalPrefix(
    person="3PL",
    set="B",
    name="3PL.B",
    remove=remove_prefix_from_forms(
        forms={
            "uni": [""],
            "un": [""],
        }
    ),
)

PRONOUN_PREFIXES = [
    SET_A_1SG,
    SET_A_1DL_EX,
    SET_A_1PL_EX,
    SET_A_1DL_IN,
    SET_A_1PL_IN,
    SET_A_2SG,
    SET_A_2DL,
    SET_A_2PL,
    SET_A_3SG,
    SET_A_3PL,
    # set B
    SET_B_1SG,
    SET_B_1DL_EX,
    SET_B_1PL_EX,
    SET_B_1DL_IN,
    SET_B_1PL_IN,
    SET_B_2SG,
    SET_B_2DL,
    SET_B_2PL,
    SET_B_3SG,
    SET_B_3PL,
]

REFLEXIVE = Prefix(
    name="RFLX",
    remove=remove_prefix_from_forms(
        forms={
            "ad": [""],
            "ada": [""],
            "adad": [""],
        }
    ),
)

MIDDLE = Prefix(
    name="MDL",
    remove=remove_prefix_from_forms(
        forms={
            "ali": [""],
        }
    ),
)

ALL_PREFIXES: List[Prefix] = [*INITIAL_PREFIXES, *PRONOUN_PREFIXES, REFLEXIVE, MIDDLE]


def remove_suffix(suffix_forms: List[str]) -> RemoveFn:
    def remove(word: str) -> Generator[str, None, None]:
        for form in suffix_forms:
            if word.endswith(form):
                yield word[: -len(form)]

    return remove


REPORTED_PAST = Suffix(
    "NXP",
    remove=remove_suffix(["ei", "e"]),
)

HABITUAL = Suffix(
    "HBT",
    remove=remove_suffix(["oi", "o"]),
)

EXPERIENCED_PAST = Suffix(
    "EXP",
    remove=remove_suffix(["vi", "v"]),
)

INFINITIVE = Suffix(
    "INF",
    remove=remove_suffix(["di", "diyi", "dii"]),
)

A_WHEN = Suffix(
    "A_WHEN",
    remove=remove_suffix(["a"]),
)


FUTURE_PROG = Suffix(
    "FUTURE_PROG",
    remove=remove_suffix(["esdi"]),
)

TENSE_ENDINGS = [
    A_WHEN,
    FUTURE_PROG,
    REPORTED_PAST,
    EXPERIENCED_PAST,
    HABITUAL,
    INFINITIVE,
]

QUESTION_SGO = Suffix(
    "INT",
    remove=remove_suffix(["s", "sg", "sgo"]),
)

EM = Suffix(
    "EM",
    remove=remove_suffix(["dv"]),
)

GWU_JUST = Suffix(
    "JUST",
    remove=remove_suffix(["wu", "gwu"]),
)

CLITICS = [QUESTION_SGO, EM, GWU_JUST]

SUFFIXES = [*CLITICS, *TENSE_ENDINGS]


def is_valid(word: ParsedWord):
    # valid parses have exactly one pronominal prefix
    if sum(isinstance(p, PronominalPrefix) for p in word.prefixes) != 1:
        return False

    if sum(s in TENSE_ENDINGS for s in word.suffixes) > 1:
        # only one tense ending
        # print("Word has multiple tense endings", word)
        return False

    return True


def all_parses(word: str):
    base = ParsedWord(prefixes=[], root=word, suffixes=[])
    options = [base]

    for prefix in ALL_PREFIXES:
        options = (output for base in options for output in prefix.parse(base))
        # TODO how to avoid materializing?
        options = list(options)

    for suffix in SUFFIXES:
        options = (output for base in options for output in suffix.parse(base))
        # TODO how to avoid materializing?
        options = list(options)

    yield from (o for o in options if is_valid(o))
