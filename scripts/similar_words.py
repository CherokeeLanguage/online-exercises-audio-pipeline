import csv
import json
from dataclasses import dataclass
import traceback
from typing import Dict, List, Tuple
from fuzzy_match import match
from rich import print
import readline


def normalize(cherokee: str):
    return (
        cherokee.lower()
        .replace("j", "ts")
        .replace("qu", "gw")
        .replace("Ɂ", "ɂ")
        .replace("ʔ", "ɂ")
        .replace("ː", ":")
    )


@dataclass
class SentenceRow:
    index: int
    syllabary: str
    phonetics: str
    english: str


def read_sentences():
    with open("Cherokee Dictionary (w_ MDS) - Dictionary.csv") as f:
        headers = next(csv.reader(f))

        reader = csv.DictReader(f, fieldnames=headers)

        for row in reader:
            try:
                sentence = SentenceRow(
                    index=int(row["Index"].strip()),
                    syllabary=row["Sentence (Syllabary)"].strip().replace("*", ""),
                    phonetics=normalize(
                        row["Sentence (Transliteration)"].strip().replace("*", "")
                    ),
                    english=row["Sentence (English)"].strip().replace("*", ""),
                )
                if (
                    len(sentence.english)
                    and len(sentence.phonetics)
                    and len(sentence.syllabary)
                ):
                    yield sentence
            except:
                print("Error reading row", row["Index"], row["Entry"])


COLORS = ["magenta", "red", "blue", "green"]


def main():
    sentences = list(read_sentences())
    sentences_by_word: Dict[str, List[SentenceRow]] = {}
    sentences_by_syllabary_word: Dict[str, List[SentenceRow]] = {}

    for sentence in sentences:
        for word in sentence.syllabary.split(" "):
            word = word.strip(".,;?'\"")
            if not word in sentences_by_syllabary_word:
                sentences_by_syllabary_word[word] = [sentence]
            else:
                sentences_by_syllabary_word[word].append(sentence)
        for word in sentence.phonetics.split(" "):
            if not word in sentences_by_word:
                sentences_by_word[word] = [sentence]
            else:
                sentences_by_word[word].append(sentence)

    words = sentences_by_word.keys()
    syllabary_words = sentences_by_syllabary_word.keys()

    average_word_length = sum((len(w) for w in words)) / len(words)
    print("avg word length (phonetics)", average_word_length)
    average_syllabary_word_length = sum((len(w) for w in syllabary_words)) / len(
        syllabary_words
    )
    print("avg word length (syllabary)", average_syllabary_word_length)

    for length in range(1, 20):
        num_words = sum(1 if len(w) == length else 0 for w in syllabary_words)
        print(f"num {length} letter words:\t{num_words}")

    wordle_words = {
        word: [sentence.index for sentence in sentences_by_syllabary_word[word]]
        for word in syllabary_words
        if len(word) == 6
    }

    with open("wordle_words.json", "w+") as f:
        json.dump(wordle_words, f, ensure_ascii=False)

    # similar words game
    search = None  # term to search
    exclude = []  # sentence to not print (eg. if it was used to search)
    while True:
        try:
            if search is None:
                search = input("Term: ")
                exclude = None
            results: List[Tuple[str, float]] = []
            for search_word in search.split():
                res = match.extract(
                    search_word, words, limit=50, score_cutoff=0.2  # type: ignore
                )
                if res is not None:
                    results.extend(res)
            search = None

            if results is []:
                continue

            words_by_sentence: Dict[int, List[Tuple[str, float]]] = {}
            match_sentences: List[SentenceRow] = []

            for hit, score in results:
                hit_sentences = sentences_by_word[hit]
                for sentence in hit_sentences:
                    if sentence.index == exclude:
                        continue

                    if sentence.index in words_by_sentence:
                        words_by_sentence[sentence.index].append((hit, score))
                    else:
                        words_by_sentence[sentence.index] = [(hit, score)]
                        match_sentences.append(sentence)

            match_sentences.sort(
                key=lambda s: -sum(score for _hit, score in words_by_sentence[s.index])
            )

            for sentence in match_sentences:
                results = words_by_sentence[sentence.index]
                syllabary = sentence.syllabary.split()
                phonetics = sentence.phonetics.split()
                seen = set()
                for i, (hit, score) in enumerate(results):
                    if hit in seen:
                        continue
                    seen.add(hit)
                    print(
                        f"{int(score * 100)}%",
                        "Found:",
                        f"[$COLOR$]{hit}[/$COLOR$]".replace(
                            "$COLOR$", COLORS[i % len(COLORS)]
                        ),
                        sep="\t",
                    )
                    nth_word = sentence.phonetics.split().index(hit)
                    syllabary[
                        nth_word
                    ] = f"[underline $COLOR$]{syllabary[nth_word]}[/underline $COLOR$]".replace(
                        "$COLOR$", COLORS[i % len(COLORS)]
                    )
                    phonetics[
                        nth_word
                    ] = f"[underline $COLOR$]{phonetics[nth_word]}[/underline $COLOR$]".replace(
                        "$COLOR$", COLORS[i % len(COLORS)]
                    )
                print(" ".join(syllabary))
                print(" ".join(phonetics))
                print()
                print(sentence.english)

                cont = input("> ")
                if cont == "q":
                    break
                if cont == "s":
                    print("Searching for related setences")
                    search = sentence.phonetics
                    exclude = sentence.index
                    break

                print()
                print()
            else:
                print("[dim]... No more matches ...[/dim]")

        except KeyboardInterrupt as e:
            break
        except Exception as e:
            print("Something went wrong", e)
            traceback.print_exc()
            continue


if __name__ == "__main__":
    main()
