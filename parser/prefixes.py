from ast import Tuple
from dataclasses import dataclass
from typing import Callable, Dict, Generator, List

from parser.utils import SYLLABLE_VOWELS, get_protypical_syllable

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
        forms={
            "Ꮿ": ["Ꭰ"],
            "Ᏸ": ["Ꭱ"],
            "Ᏹ": ["", "Ꭲ"],
            "Ᏺ": ["Ꭳ"],
            "Ᏻ": ["Ꭴ", ""],  # Ᏻ before WI
            "Ᏼ": ["Ꭵ"],
        }
    ),
)

TSI = Prefix(
    name="TSI",
    remove=remove_prefix_from_forms(
        forms={
            "Ꮳ": ["Ꭰ"],
            "Ꮴ": ["Ꭱ"],
            "Ꮵ": ["", "Ꭲ"],
            "Ꮶ": ["Ꭳ"],
            "Ꮷ": ["Ꭴ"],
            "Ꮸ": ["Ꭵ"],
        }
    ),
)

WI = Prefix(
    name="WI",
    remove=remove_prefix_from_forms(
        forms={
            "Ꮹ": ["Ꭰ"],
            "Ꮻ": ["", "Ꭲ"],
            "Ꮺ": ["Ꭱ"],
            "Ꮼ": ["Ꭳ"],
            "Ꮽ": ["Ꭴ"],
            "Ꮾ": ["Ꭵ"],
        }
    ),
)

NI = Prefix(
    name="NI",
    remove=remove_prefix_from_forms(
        forms={
            "Ꮎ": ["Ꭰ", "Ꭽ"],
            "Ꮏ": ["Ꭽ"],
            "Ꮑ": ["Ꭱ", "Ꭾ"],
            "Ꮒ": ["", "Ꭲ", "Ꭿ"],
            "Ꮓ": ["Ꭳ", "Ꮀ"],
            "Ꮔ": ["Ꭴ", "Ꮁ"],
            "Ꮕ": ["Ꭵ", "Ꮂ"],
        }
    ),
)

NI2 = Prefix(
    name="NI2",
    remove=remove_prefix_from_forms(
        forms={
            "ᎢᏯ": ["Ꭰ"],
            "ᎢᏰ": ["Ꭱ"],
            "Ꭲ": ["", "Ꭲ"],
            "ᎢᏲ": ["Ꭳ"],
            "ᎢᏳ": ["Ꭴ"],
            "ᎢᏴ": ["Ꭵ"],
        }
    ),
)

DE = Prefix(
    name="DE_PLURAL",
    remove=remove_prefix_from_forms(
        forms={
            "Ꮣ": ["Ꭰ"],
            "Ꮥ": ["", "Ꭱ", "Ꭲ"],
            # do can be hiding, Ꭲ/Ꭵ again or just be caused by Ꮣ future after
            "Ꮩ": ["Ꭳ", "Ꭲ", "Ꭵ", ""],
            "Ꮪ": ["Ꭴ"],
            "Ꮫ": ["Ꭵ"],
        }
    ),
)

DE2 = Prefix(
    name="DE_PLURAL",
    remove=remove_prefix_from_forms(
        forms={
            "Ꮧ": ["Ꭰ", "Ꭲ", ""],
            "Ꮴ": ["Ꭱ"],
            "Ꮶ": ["Ꭳ"],
            "Ꮷ": ["Ꭴ"],
            # fused forms
            "Ꮤ": ["Ꭽ"],
            "Ꮦ": ["Ꭾ"],
            "Ꮨ": ["Ꭿ"],
            "Ꮩ": ["Ꮀ"],
            "Ꮪ": ["Ꮁ"],
            "Ꮫ": ["Ꮂ"],
            # "Ꮫ": ["Ꭵ"], # not sure...
        }
    ),
)

DA = Prefix(
    name="DA_FUTURE",
    remove=remove_prefix_from_forms(
        forms={
            "Ꮣ": ["", "Ꭲ"],  # da before consonant or Ꭲ
            "ᏓᏲ": ["Ꭳ"],  # day- before vowels
            "ᏓᏰ": ["Ꭱ"],  # day- before vowels
            "ᏓᏳ": ["Ꭴ"],  # day- before vowels
            "Ꮫ": ["Ꭵ", "Ꭰ", ""],  # Ꮫ before Ꭰ; some speakers say Ꮫ before a consonant
        }
    ),
)

I_AGAIN = Prefix(
    name="I_AGAIN",
    remove=remove_prefix_from_forms(
        forms={
            "Ꭲ": [""],
            "Ꭵ": [""],
        }
    ),
)

GA = Prefix(
    name="GA",
    remove=remove_prefix_from_forms(
        forms={"Ꭶ": [""], "Ꭸ": ["", "Ꭱ", "Ꭲ"], "Ꭼ": ["Ꭰ"], "ᎬᏩ": ["Ꭰ", "Ꭴ", "ᎤᏩ"]}
    ),
)

INITIAL_PREFIXES = [YI, TSI, WI, NI, NI2, DE, DE2, DA, I_AGAIN, GA]

SET_A_1SG = PronominalPrefix(
    person="1SG",
    set="A",
    name="1SG.A",
    remove=remove_prefix_from_forms(
        forms={
            "Ꭶ": ["Ꭰ"],
            "Ꭸ": ["Ꭱ"],
            "Ꮵ": [""],
            "Ꭺ": ["Ꭳ"],
            "Ꭻ": ["Ꭴ"],
            "Ꭼ": ["Ꭵ"],
        }
    ),
)


SET_A_1DL_IN = PronominalPrefix(
    person="1DL_IN",
    set="A",
    name="1DL_IN.A",
    remove=remove_prefix_from_forms(
        forms={
            "ᎢᎾ": ["Ꭰ"],
            "ᎢᏁ": ["Ꭱ"],
            "ᎢᏂ": [""],
            "ᎢᏃ": ["Ꭳ"],
            "ᎢᏄ": ["Ꭴ"],
            "ᎢᏅ": ["Ꭵ"],
        }
    ),
)


SET_A_1PL_IN = PronominalPrefix(
    person="1PL_IN",
    set="A",
    name="1PL_IN.A",
    remove=remove_prefix_from_forms(
        forms={
            "ᎢᏓ": ["Ꭰ"],
            "ᎢᏕ": ["Ꭱ"],
            "ᎢᏗ": [""],
            "ᎢᏙ": ["Ꭳ"],
            "ᎢᏚ": ["Ꭴ"],
            "ᎢᏛ": ["Ꭵ"],
        }
    ),
)


SET_A_1DL_EX = PronominalPrefix(
    person="1DL_EX",
    set="A",
    name="1DL_EX.A",
    remove=remove_prefix_from_forms(
        forms={
            "ᎣᏍᏓ": ["Ꭰ"],
            "ᎣᏍᏕ": ["Ꭱ"],
            "ᎣᏍᏗ": [""],
            "ᎣᏍᏙ": ["Ꭳ"],
            "ᎣᏍᏚ": ["Ꭴ"],
            "ᎣᏍᏛ": ["Ꭵ"],
        }
    ),
)


SET_A_1PL_EX = PronominalPrefix(
    person="1PL_EX",
    set="A",
    name="1PL_EX.A",
    remove=remove_prefix_from_forms(
        forms={
            "ᎣᏣ": ["Ꭰ"],
            "ᎣᏤ": ["Ꭱ"],
            "ᎣᏥ": [""],
            "ᎣᏦ": ["Ꭳ"],
            "ᎣᏧ": ["Ꭴ"],
            "ᎣᏨ": ["Ꭵ"],
        }
    ),
)

SET_A_2SG = PronominalPrefix(
    person="2SG",
    set="A",
    name="2SG.A",
    remove=remove_prefix_from_forms(
        forms={
            "Ꭽ": ["Ꭰ"],
            "Ꭾ": ["Ꭱ"],
            "Ꭿ": [""],
            "Ꮀ": ["Ꭳ"],
            "Ꮁ": ["Ꭴ"],
            "Ꮂ": ["Ꭵ"],
        }
    ),
)


SET_A_2DL = PronominalPrefix(
    person="2DL",
    set="A",
    name="2DL.A",
    remove=remove_prefix_from_forms(
        forms={
            "ᏍᏓ": ["Ꭰ"],
            "ᏍᏕ": ["Ꭱ"],
            "ᏍᏗ": [""],
            "ᏍᏙ": ["Ꭳ"],
            "ᏍᏚ": ["Ꭴ"],
            "ᏍᏛ": ["Ꭵ"],
        }
    ),
)

SET_A_2PL = PronominalPrefix(
    person="2PL",
    set="A",
    name="2PL.A",
    remove=remove_prefix_from_forms(
        forms={
            "ᎢᏣ": ["Ꭰ"],
            "ᎢᏕ": ["Ꭱ"],
            "ᎢᏥ": [""],
            "ᎢᏦ": ["Ꭳ"],
            "ᎢᏧ": ["Ꭴ"],
            "ᎢᏨ": ["Ꭵ"],
        }
    ),
)


SET_A_3SG = PronominalPrefix(
    person="3SG",
    set="A",
    name="3SG.A",
    remove=remove_prefix_from_forms(
        forms={
            "Ꭰ": ["", "Ꭰ"],
            "Ꭶ": ["", "Ꭰ"],
            "Ꭸ": ["Ꭱ"],
            "Ꭺ": ["Ꭳ"],
            "Ꭻ": ["Ꭴ"],
            "Ꭼ": ["Ꭵ"],
            "Ꭵ": ["Ꭵ"],  # some eastern words do this
        }
    ),
)


SET_A_3PL = PronominalPrefix(
    person="3PL",
    set="A",
    name="3PL.A",
    remove=remove_prefix_from_forms(
        forms={
            "ᎠᏂ": [""],
            "ᎠᎾ": ["Ꭰ"],
            "ᎠᏁ": ["Ꭱ"],
            "ᎠᏃ": ["Ꭳ"],
            "ᎠᏄ": ["Ꭴ"],
            "ᎠᏅ": ["Ꭵ"],
        }
    ),
)

SET_B_1SG = PronominalPrefix(
    person="1SG",
    set="B",
    name="1SG.B",
    remove=remove_prefix_from_forms(
        forms={
            "ᎠᏆ": ["Ꭰ"],
            "ᎠᏩ": ["Ꭰ"],
            "ᎠᏇ": ["Ꭱ"],
            "ᎠᏪ": ["Ꭱ"],
            "ᎠᎩ": [""],
            "ᎠᏉ": ["Ꭳ"],
            "ᎠᏬ": ["Ꭳ"],
            "ᎠᏋ": ["Ꭵ"],
            "ᎠᏮ": ["Ꭵ"],
        }
    ),
)

SET_B_1DL_EX = PronominalPrefix(
    person="1DL_EX",
    set="B",
    name="1DL_EX.B",
    remove=remove_prefix_from_forms(
        forms={
            "ᎣᎩᎾ": ["Ꭰ"],
            "ᎣᎩᏁ": ["Ꭱ"],
            "ᎣᎩᏂ": [""],
            "ᎣᎩᏃ": ["Ꭳ"],
            "ᎣᎩᏄ": ["Ꭴ"],
            "ᎣᎩᏅ": ["Ꭵ"],
        }
    ),
)

SET_B_1PL_EX = PronominalPrefix(
    person="1PL_EX",
    set="B",
    name="1PL_EX.B",
    remove=remove_prefix_from_forms(
        forms={
            "ᎣᎦ": ["Ꭰ"],
            "ᎣᎨ": ["Ꭱ"],
            "ᎣᎩ": [""],
            "ᎣᎪ": ["Ꭳ"],
            "ᎣᎫ": ["Ꭴ"],
            "ᎣᎬ": ["Ꭵ"],
        }
    ),
)

SET_B_1DL_IN = PronominalPrefix(
    person="1DL_IN",
    set="B",
    name="1DL_IN.B",
    remove=remove_prefix_from_forms(
        forms={
            "ᎩᎾ": ["Ꭰ"],
            "ᎩᏁ": ["Ꭱ"],
            "ᎩᏂ": [""],
            "ᎩᏃ": ["Ꭳ"],
            "ᎩᏄ": ["Ꭴ"],
            "ᎩᏅ": ["Ꭵ"],
        }
    ),
)

SET_B_1PL_IN = PronominalPrefix(
    person="1PL_IN",
    set="B",
    name="1PL_IN.B",
    remove=remove_prefix_from_forms(
        forms={
            "ᎢᎦ": ["Ꭰ"],
            "ᎢᎨ": ["Ꭱ"],
            "ᎢᎩ": [""],
            "ᎢᎪ": ["Ꭳ"],
            "ᎢᎫ": ["Ꭴ"],
            "ᎢᎬ": ["Ꭵ"],
        }
    ),
)

SET_B_2SG = PronominalPrefix(
    person="2SG",
    set="B",
    name="2SG.B",
    remove=remove_prefix_from_forms(
        forms={
            "Ꮳ": ["Ꭰ", ""],
            "Ꮴ": ["Ꭱ"],
            "Ꮶ": ["Ꭳ"],
            "Ꮷ": ["Ꭴ"],
            "Ꮸ": ["Ꭵ"],
        }
    ),
)

SET_B_2DL = PronominalPrefix(
    person="2DL",
    set="B",
    name="2DL.B",
    remove=remove_prefix_from_forms(
        forms={
            "ᏍᏓ": ["Ꭰ"],
            "ᏍᏕ": ["Ꭱ"],
            "ᏍᏗ": [""],
            "ᏍᏙ": ["Ꭳ"],
            "ᏍᏚ": ["Ꭴ"],
            "ᏍᏛ": ["Ꭵ"],
        }
    ),
)


SET_B_2PL = PronominalPrefix(
    person="2PL",
    set="B",
    name="2PL.B",
    remove=remove_prefix_from_forms(
        forms={
            "ᎢᏣ": ["Ꭰ"],
            "ᎢᏕ": ["Ꭱ"],
            "ᎢᏥ": [""],
            "ᎢᏦ": ["Ꭳ"],
            "ᎢᏧ": ["Ꭴ"],
            "ᎢᏨ": ["Ꭵ"],
        }
    ),
)


SET_B_3SG = PronominalPrefix(
    person="3SG",
    set="B",
    name="3SG.B",
    remove=remove_prefix_from_forms(
        forms={
            "Ꭴ": ["", "Ꭰ"],
            "ᎤᏪ": ["Ꭱ"],
            "ᎤᏬ": ["Ꭳ"],
            "ᎤᏭ": ["Ꭴ"],
            "ᎤᏩ": ["Ꭵ"],
        }
    ),
)


SET_B_3PL = PronominalPrefix(
    person="3PL",
    set="B",
    name="3PL.B",
    remove=remove_prefix_from_forms(
        forms={
            "ᎤᏂ": [""],
            "ᎤᎾ": ["Ꭰ"],
            "ᎤᏁ": ["Ꭱ"],
            "ᎤᏃ": ["Ꭳ"],
            "ᎤᏄ": ["Ꭴ"],
            "ᎤᏅ": ["Ꭵ"],
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
            "ᎠᏓ": ["", "Ꭰ"],
            "ᎠᏕ": ["Ꭱ"],
            "ᎠᏓᏙ": ["Ꭳ"],
            "ᎠᏙ": ["Ꭳ"],
            "ᎠᏓᏗ": ["Ꭲ"],
            "ᎠᏓᏛ": ["Ꭵ"],
        }
    ),
)

MIDDLE = Prefix(
    name="MDL",
    remove=remove_prefix_from_forms(
        forms={
            "ᎠᎵ": [""],
        }
    ),
)

ALL_PREFIXES: List[Prefix] = [*INITIAL_PREFIXES, *PRONOUN_PREFIXES, REFLEXIVE, MIDDLE]


def remove_consonant_initial_suffix(suffix_forms: List[str]) -> RemoveFn:
    def remove(word: str) -> Generator[str, None, None]:
        for form in suffix_forms:
            if word.endswith(form):
                yield word[: -len(form)]

    return remove


def remove_vowel_initial_suffix(suffix_forms: List[str]) -> RemoveFn:
    def remove(word: str) -> Generator[str, None, None]:
        for form in suffix_forms:
            if len(form) > len(word):
                continue
            if SYLLABLE_VOWELS[word[-len(form)]] + word[-len(form) :][1:] == form:
                yield word[: -len(form)] + get_protypical_syllable(word[-len(form)])

    return remove


REPORTED_PAST = Suffix(
    "NXP",
    remove=remove_vowel_initial_suffix(["ᎡᎢ", "Ꭱ"]),
)

HABITUAL = Suffix(
    "HBT",
    remove=remove_vowel_initial_suffix(["ᎣᎢ", "Ꭳ"]),
)

EXPERIENCED_PAST = Suffix(
    "EXP",
    remove=remove_vowel_initial_suffix(["ᎥᎢ", "Ꭵ"]),
)

INFINITIVE = Suffix(
    "INF",
    remove=remove_consonant_initial_suffix(["Ꮧ", "ᏗᏱ", "ᏗᎢ"]),
)

A_WHEN = Suffix(
    "A_WHEN",
    remove=remove_vowel_initial_suffix(["Ꭰ"]),
)


FUTURE_PROG = Suffix(
    "FUTURE_PROG",
    remove=remove_vowel_initial_suffix(["ᎡᏍᏗ"]),
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
    remove=remove_consonant_initial_suffix(["Ꮝ", "ᏍᎪ"]),
)

EM = Suffix(
    "EM",
    remove=remove_consonant_initial_suffix(["Ꮫ"]),
)

GWU_JUST = Suffix(
    "JUST",
    remove=remove_consonant_initial_suffix(["Ꮽ", "Ꮚ"]),
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
