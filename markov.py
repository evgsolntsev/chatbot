"""All Markov chain logic associated funcs here."""

import json
import random

END = "END"

class Chain:
    """This class represents chain for one dialog."""

    data = {}
    length = 0
    probability = 10

    def __init__(self, data, probability=10):
        self.data = data
        self.length = 0
        self.probability = probability
        for _, inner_data in data.items():
            for _, value in inner_data.items():
                self.length += value

    def normalize(self, string):
        """Filter bad symbols, lower it and so on."""

        return " ".join(filter(
            lambda x: len(x) > 0,
            "".join(map(lambda c: c if c.isalnum() or c == "-" else " ", string)).split(" "),
        )).lower()

    def inc(self, word1, word2):
        """Increment pair probability."""

        if word1 in self.data:
            if word2 in self.data[word1]:
                self.data[word1][word2] += 1
            else:
                self.data[word1][word2] = 1
        else:
            self.data[word1] = {
                word2: 1
            }

        self.length += 1

    def add_message(self, message):
        """Adds info about one message (string)."""

        words = self.normalize(message).split()
        if len(words) == 0:
            return

        for i in range(len(words) - 1):
            self.inc(words[i], words[i + 1])

        self.inc(words[-1], END)

    def is_known(self, word):
        """Check if word is well-known."""

        length = 0
        for _, value in self.data[word].items():
            length += value

        return length >= 20

    def gen_answer(self, string, force=False):
        """Generate answer."""

        word = ""
        words = self.normalize(string).split()
        random.shuffle(words)
        for tmp in words:
            if self.is_known(tmp):
                word = tmp
                break
        else:
            if not force:
                return None
            word = random.choice(list(self.data.keys()))

        return self.gen_message(word)

    def gen_answer_with_probability(self, string, force=False):
        """Generate answer with given probability."""

        if not force and random.randrange(self.probability):
            return None
        return self.gen_answer(string, force=force)

    def gen_message(self, word):
        """Generate new message."""

        tmp = self.normalize(word)
        result = []
        res_length = 0
        while tmp != END and res_length < 1000:
            result.append(tmp)
            res_length += len(tmp)

            next_words = []
            weights = []
            for key, value in self.data.get(tmp, {}).items():
                next_words.append(key)
                weights.append(value)

            tmp = random.choices(next_words, weights=weights, k=1)[0]

        return " ".join(result) + "."

def write_to_file(chain, int_id):
    """Writes Chain to file."""

    data = {
        "data": json.dumps(chain.data),
        "probability": chain.probability
    }
    with open(to_filename(int_id), "w+", encoding="utf-8") as destination:
        destination.write(data)


def read_from_file(int_id):
    """Reads Chain from a file."""

    try:
        with open(to_filename(int_id), "r", encoding="utf-8") as source:
            dump = json.loads(source.read())
            return Chain(dump["data"], dump["probability"])
    except OSError:
        return Chain({})

def to_filename(int_id):
    """Converts integer ID to filename."""

    return str(int_id) + ".json"
