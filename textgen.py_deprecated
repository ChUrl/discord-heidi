#!/usr/bin/env python3

from rich.traceback import install

install()

import re
import random


class TextGen:
    def __init__(self, filename, n):
        with open(filename) as file:
            self.wordbase = re.sub(r"[^a-zäöüß'.,]+", " ", file.read().lower()).split()

        self.word_table = dict()
        self.order = n

        self.train_words(self.order)

    def train_words(self, n):
        """
        Erzeugt die Markov-Chain mit Prefix-Länge n
        """
        print(f"Training with {len(self.wordbase)} words.")

        # init the frequencies
        for i in range(len(self.wordbase) - n - 1):
            prefix = tuple(self.wordbase[i : i + n])
            suffix = self.wordbase[i + n]

            if prefix not in self.word_table:
                self.word_table[prefix] = []

            # if suffix not in self.table[prefix]: # disable for probabilities
            self.word_table[prefix].append(suffix)

        print(f"Generated suffixes for {len(self.word_table)} prefixes.")

    def generate_random(self, n):
        fword = random.choice(list(self.word_table.keys()))
        output = [*fword]

        for _ in range(self.order, n):
            output.append(self.generate_word_by_word(tuple(output[-self.order :])))

        return output

    def generate_word_by_word(self, prefix: tuple):
        if prefix not in self.word_table:
            print(f"Prefix {prefix} not in table")
            for key in self.word_table.keys():
                if key[-1] == prefix[-1]:
                    return random.choice(self.word_table[key])

        return random.choice(self.word_table[prefix])

    def generate_sentences(self, n):
        return [self.generate_sentence for _ in range(n)]

    def generate_sentence(self):
        fword = random.choice(list(self.word_table.keys()))
        output = [*fword]

        while "." not in output[-1]:
            output.append(self.generate_word_by_word(tuple(output[-self.order :])))

        return output
