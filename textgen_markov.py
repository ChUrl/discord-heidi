#!/usr/bin/env python3

import re
import random
from textgen import textgen

from rich.traceback import install
install()

# NOTE: This is word based, not character based
# @todo Serialize and save/load model (don't train on the server)
# @todo Maybe extract sentence beginnings and use them as starters?

class MarkovTextGenerator(textgen):
    # The greater the order (prefix length), the lesser the variation in generation, but the better the sentences (generally).
    # If the prefix length is high there are less options to choose from, so the sentences are very close to the training text.
    def __init__(self, order): # Set order here for better interface (only needed for markov model)
        self.order = order

    def init(self, filename): # Filename is needed for every type of model so it's part of the interface
        with open(f"./textfiles/{filename}.txt", "r") as file:
            # Remove all characters except a-zäöüß'.,
            self.wordbase = re.sub(r"[^a-zäöüß'.,]+", " ", file.read().lower()).split()

        self.word_table = dict()

    def load(self):
        print(f"Loaded Markov chain of order {self.order} with {len(self.wordbase)} words from file.")

    def train(self):
        print(f"Training Markov chain of order {self.order} with {len(self.wordbase)} words.")

        # init the frequencies
        for i in range(len(self.wordbase) - self.order - 1): # Look at every word in range
            prefix = tuple(self.wordbase[i:i+self.order]) # Look at the next self.order words from current position
            suffix = self.wordbase[i+self.order] # The next word is the suffix

            if prefix not in self.word_table: # New option wooo
                self.word_table[prefix] = []

            # if suffix not in self.table[prefix]: # disable for probabilities: if the suffixes are in the list multiple times they are more common
            self.word_table[prefix].append(suffix)

        print(f"Generated suffixes for {len(self.word_table)} prefixes.")

    # def generate_random(self, n):
    #     fword = random.choice(list(self.word_table.keys())) # Random first word
    #     output = [*fword]

    #     for _ in range(self.order, n):
    #         output.append(self.generate_word_by_word(tuple(output[-self.order :])))

    #     return output

    def generate_suffix_for_prefix(self, prefix: tuple):
        if len(prefix) > self.order: # In this case we look at the last self.order elements of prefix
            prefix = prefix[len(prefix)-self.order-1:-1]

        if prefix not in self.word_table: # In this case we need to choose a possible suffix from the last word in the prefix (if prefix too short for example)
            print(f"Prefix {prefix} not in table")
            for key in self.word_table.keys():
                if key[-1] == prefix[-1]:
                    return random.choice(self.word_table[key])

        return random.choice(self.word_table[prefix])

    def generate_sentence(self):
        fword = random.choice(list(self.word_table.keys()))
        output = [*fword]

        while "." not in output[-1]:
            output.append(self.generate_suffix_for_prefix(tuple(output[-self.order:])))

        return output

    def complete_sentence(self, prefix):
        output = [*prefix]

        while "." not in output[-1]:
            output.append(self.generate_suffix_for_prefix(tuple(output[-self.order:])))

        return output
