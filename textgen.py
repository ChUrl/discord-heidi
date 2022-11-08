#!/usr/bin/env python3

from rich.traceback import install
install()

from abc import ABC, abstractmethod

# In Python it is generally not needed to use abstract classes, but I wanted to do it safely

class textgen(ABC):
    @abstractmethod
    def init(self, filename):
        """
        filename - The file (same directory as textgen.py) that contains the training text
        """
        raise NotImplementedError("Can't use abstract class")

    @abstractmethod
    def load(self):
        """
        Load the trained markov chain from a precomputed file
        """
        raise NotImplementedError("Can't use abstract class")

    @abstractmethod
    def train(self):
        """
        Generate the markov chain, uses prefix length defined in init()
        """
        raise NotImplementedError("Can't use abstract class")

    @abstractmethod
    def generate_sentence(self):
        """
        Generate a series of words/characters until a . is generated
        """
        raise NotImplementedError("Can't use abstract class")

    @abstractmethod
    def complete_sentence(self, prefix):
        """
        Generate the rest of a sentence for a given beginning
        """
        raise NotImplementedError("Can't use abstract class")
