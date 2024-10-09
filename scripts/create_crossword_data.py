import json
import random

data = json.load(open("dict_large.json"))

num_words = 20


def target_word_for_key(key):
    sentence_syllabary = data[key]["sentence"]["syllabary"].split(".")[0]
    parts = sentence_syllabary.split("*")
    return "".join(parts[1:-1])


def print_word_row(word, prefix=""):
    target_word = target_word_for_key(word)
    clue = data[word]["sentence"]["english"].split(".")[0]
    print(prefix + target_word, clue)


def search_word(query: str, pool: list[str]) -> tuple[str | None, list[str]]:
    pool.sort(key=lambda w: -trigram_similarity(data[w]["sentence"]["english"], query))
    for i in range(5):
        print_word_row(pool[i], prefix=f"{i}: ")

    choice = input("> ").strip()
    if choice == "":
        return None, pool
    else:
        try:
            choice = int(choice)
            return pool[choice], pool[:choice] + pool[choice + 1 :]
        except:
            print("Failed to parse response...")
            return None, pool


trigrams = lambda a: zip(a, a[1:], a[2:])


def trigram_similarity(a, b):
    a_t = set(trigrams(a))
    b_t = set(trigrams(b))
    return len(a_t & b_t) / len(a_t | b_t)


def common_tokens(a, b):
    a_t = set(c for c in a)
    b_t = set(c for c in b)

    return len(a_t & b_t) / len(a_t | b_t)


ced_words = list(
    word
    for word in data
    if data[word]["source"] == "ced" and len(data[word]["sentence"]["syllabary"]) > 0
    # and len(data[word]["sentence"]["syllabary"].split("*")) > 1
    # and len(data[word]["sentence"]["english"].split("*")) > 1
    # and len(target_word_for_key(word)) > 4 and not " " in target_word_for_key(word)
)


def generate_random_crossword():
    seed_words = random.sample(ced_words, k=num_words // 4)

    pool = [word for word in ced_words if not word in seed_words]

    words = [*seed_words]
    while len(words) < num_words:
        pool.sort(
            key=lambda word: -max(common_tokens(word, seed) for seed in seed_words)
        )
        draw = pool[0]
        pool = pool[1:]

        print_word_row(draw)
        yn = input("'n' to reject: ").strip().lower()
        if yn == "n":
            continue

        words.append(pool[0])

    print_all_words(words)


def print_all_words(words: list[str]):
    print()
    print()
    print()
    print()

    for word in words:
        print_word_row(word)


def generate_user_crossword():
    pool = ced_words
    words = []
    while True:
        query = input("Query: ").strip()
        if query == "":
            break
        else:
            next_word, new_pool = search_word(query, pool)
            if next_word:
                words.append(next_word)
                pool = new_pool

    print_all_words(words)


if __name__ == "__main__":
    generate_user_crossword()
