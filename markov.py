"""All Markov chain logic associated funcs here."""

import json
import random

END = "END"

class Chain:
    """This class represents chain for one dialog."""

    data = {}
    length = 0

    def __init__(self, data):
        self.data = data
        self.length = 0
        for _, inner_data in data.items():
            for _, value in inner_data.items():
                self.length += value

    def normalize(self, string):
        """Filter bad symbols, lower it and so on."""

        return "".join(filter(lambda c: c.isalnum() or c == " ", string)).lower()

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

    def gen_answer(self, string):
        """Generate answer."""

        word = random.choice(self.normalize(string).split())
        if word not in self.data:
            return None

        length = 0
        for _, value in self.data[word].items():
            length += value

        if length < 20:
            return None

        if random.randrange(10) != 0:
            return None

        return self.gen_message(word)

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

    data = json.dumps(chain.data)
    with open(to_filename(int_id), "w+", encoding="utf-8") as destination:
        destination.write(data)


def read_from_file(int_id):
    """Reads Chain from a file."""

    try:
        with open(to_filename(int_id), "r", encoding="utf-8") as source:
            return Chain(json.loads(source.read()))
    except OSError:
        return Chain({})

def to_filename(int_id):
    """Converts integer ID to filename."""

    return str(int_id) + ".json"
