#!/usr/bin/env python3

import os
import re
import random
from functools import reduce

from dotenv import load_dotenv

import discord
from discord import Intents
from discord.ext import commands

from scraper import Girls

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")  # Zocken mit Heidi


class HeidiClient(discord.Client):

    def __init__(self):
        super().__init__(intents=Intents.default(), status="Nur eine kann Germany's next Topmodel werden!")

        self.prefix = "Heidi, "
        self.prefix_regex = "^" + self.prefix

        self.girls = Girls() # scraped model list

        self.triggers = {} # automatic actions
        self.triggers[lambda m: m.author.nick in self.girls.get_in_names()] = self.autoreact_to_girls

        self.matchers = {} # react to messages
        self.matchers["Hilfe$"] = self.show_help
        self.matchers["Heidi!$"] = self.say_name
        self.matchers["wer ist dabei\\?$"] = self.list_models_in
        self.matchers["wer ist raus\\?$"] = self.list_models_out
        self.matchers[".+, ja oder nein\\?$"] = self.magic_shell
        self.matchers["wähle: (.+,)+"] = self.choose
        self.matchers["gib Bild von .+"] = self.show_model_picture


    ### Helpers ------------------------------------------------------------------------------------

    def _help_text(self):
        """
        Generate help-string from docstrings of matchers and triggers
        """
        docstrings_triggers = ["  - " + func.__doc__.strip() for func in self.triggers.values()]
        docstrings_matchers = ["  - " + func.__doc__.strip() for func in self.matchers.values()]

        response = "Präfix: \"" + self.prefix + "\" (mit Leerzeichen)\n"
        response += "--------------------------------------------------\n"

        response += "Das mache ich automatisch:\n"
        response += "\n".join(docstrings_triggers)

        response += "\n\nIch höre auf diese Befehle:\n"
        response += "\n".join(docstrings_matchers)

        return response


    def _match(self, matcher, message):
        """
        Check if a string matches against prefix + matcher (case-insensitive)
        """
        return re.match(self.prefix_regex + matcher, message.content, re.IGNORECASE)


    ### Events -------------------------------------------------------------------------------------

    async def on_ready(self):
        print(f"{self.user} (id: {self.user.id}) has connected to Discord!")


    async def on_message(self, message):
        if message.author == client.user:
            return


        for trigger in self.triggers:
            if trigger(message):
                await self.triggers[trigger](message)
                break


        for matcher in self.matchers:
            if self._match(matcher, message):
                await self.matchers[matcher](message)
                break


    ### Commands -----------------------------------------------------------------------------------

    async def show_help(self, message):
        """
        Hilfe (Ich höre auf diese Befehle, Senpai UwU)
        """
        await message.channel.send(self._help_text())


    async def say_name(self, message):
        """
        Heidi! (Ich sag meinen Namen)
        """
        await message.channel.send("HEIDI!")


    async def list_models_in(self, message):
        """
        wer ist dabei? (Liste der Models welche noch GNTM werden können)
        """
        await message.channel.send("\n".join(self.girls.get_in_names()))


    async def list_models_out(self, message):
        """
        wer ist raus? (Liste der Keks welche ich ge*ickt hab)
        """
        await message.channel.send("\n".join(self.girls.get_out_names()))


    async def show_model_picture(self, message):
        """
        gib Bild von <Name> (Zeigt ein Bild des entsprechenden Models)
        """
        name = message.content.split()[-1]
        picture = discord.Embed()
        picture.set_image(url=self.girls.get_image(name))
        picture.set_footer(text=name)
        await message.channel.send(embed=picture)


    async def magic_shell(self, message):
        """
        <Frage>, ja oder nein? (Ich beantworte dir eine Frage)
        """
        choices = ["Ja!", "Jo.", "Total!", "Natürlich.", "Nein!", "Nö.", "Nä.", "Niemals!"]
        await message.channel.send(random.choice(choices))


    async def choose(self, message):
        """
        wähle: <Option 1>, <Option 2>, ... (Ich treffe eine Wahl)
        """
        choices = message.content.replace(",", "").split()[2:]
        await message.channel.send(random.choice(choices))


    ### Automatic Actions --------------------------------------------------------------------------

    async def autoreact_to_girls(self, message):
        """
        Ich ❤-e Nachrichten einer aktiven GNTM Teilnehmerin
        """
        await message.add_reaction("❤")


client = HeidiClient()
client.run(TOKEN)
