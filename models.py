#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup


class Models:
    def __init__(self):
        url_girls = "https://www.prosieben.de/tv/germanys-next-topmodel/models"

        html_girls = requests.get(url_girls)
        soup_girls = BeautifulSoup(html_girls.text, "html.parser")

        girls_in = soup_girls.findAll("a", class_="candidate-in")
        girls_out = soup_girls.findAll("a", class_="candidate-out")

        self.girls_in = {girl.find("h4", class_="candidate-title").text.lower(): girl for girl in girls_in}
        self.girls_out = {girl.find("h4", class_="candidate-title").text.lower(): girl for girl in girls_out}
        self.girls = {**self.girls_in, **self.girls_out}

    def get_in_names(self):
        return self.girls_in.keys()

    def get_out_names(self):
        return self.girls_out.keys()

    def get_image(self, name):
        return self.girls[name.lower()].find("figure", class_="teaser-img")["style"].split("\"")[1]
