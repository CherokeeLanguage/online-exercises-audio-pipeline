from matplotlib import pyplot as plt
import json

if __name__ == "__main__":
    trigrams = json.load(open("data/cnd/trigram_frequencies.json"))
    scores = json.load(open("data/cnd/sentence_scores.json"))

    values = sorted(trigrams.values())

    print(max(values))
    # make histogram
    plt.hist(values, bins="auto")
    plt.show()

    values = sorted(scores)

    print(max(values))
    # make histogram
    plt.hist(values, bins="auto")
    plt.show()
