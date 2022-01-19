#!/usr/bin/env python3

import os
import re
import random
import asyncio
from functools import reduce

from dotenv import load_dotenv
from models import Models

import discord

# used to start the bot locally, for docker the variables have to be set when the container is run
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


class HeidiClient(discord.Client):
    def __init__(self):
        super().__init__(
            status="Nur eine kann GNTM werden!",
        )

        self.prefix = "Heidi, "
        self.prefix_regex = "^" + self.prefix

        self.models = Models()  # scraped model list

        # automatic actions
        self.triggers = {
            lambda m: m.author.nick.lower() in self.models.get_in_names(): self.autoreact_to_girls,
            lambda m: "jeremy" in m.author.nick.lower(): self.autoreact_to_jeremy}

        # commands
        self.matchers = {"Hilfe$": self.show_help,
                         "Heidi!$": self.say_name,

                         # GNTM stuff
                         "wer ist dabei\\?$": self.list_models_in,
                         "wer ist raus\\?$": self.list_models_out,
                         "gib Bild von .+$": self.show_model_picture,
                         "gib Link$": self.show_link,

                         # Fun stuff
                         "welche Farbe .+\\?": self.random_color,
                         ".+, ja oder nein\\?": self.magic_shell,
                         "wähle: (.+,?)+$": self.choose,
                         "sprechen": self.list_voicelines,
                         "sag .+$": self.say_voiceline}

    # Helpers ------------------------------------------------------------------------------------

    def _help_text(self):
        """
        Generate help-string from docstrings of matchers and triggers
        """
        docstrings_triggers = [
            "  - " + func.__doc__.strip() for func in self.triggers.values()
        ]
        docstrings_matchers = [
            "  - " + func.__doc__.strip() for func in self.matchers.values()
        ]

        response = 'Präfix: "' + self.prefix + '" (mit Leerzeichen)\n'
        response += "--------------------------------------------------\n"

        response += "Automatisch:\n"
        response += "\n".join(docstrings_triggers)

        response += "\n\nCommands:\n"
        response += "\n".join(docstrings_matchers)

        return response

    def _match(self, matcher, message):
        """
        Check if a string matches against prefix + matcher (case-insensitive)
        """
        return re.match(self.prefix_regex + matcher, message.content, re.IGNORECASE)

    # Events -------------------------------------------------------------------------------------

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

    # Commands -----------------------------------------------------------------------------------

    async def show_help(self, message):
        """
        Hilfe (Senpai UwU)
        """
        await message.channel.send(self._help_text())

    @staticmethod
    async def say_name(message):
        """
        Heidi!
        """
        await message.channel.send("HEIDI!")

    async def list_models_in(self, message):
        """
        wer ist dabei?
        """
        await message.channel.send("\n".join(self.models.get_in_names()))

    async def list_models_out(self, message):
        """
        wer ist raus? (Liste der Keks welche ge*ickt wurden)
        """
        await message.channel.send("\n".join(self.models.get_out_names()))

    async def show_model_picture(self, message):
        """
        gib Bild von <Name>
        """
        name = message.content.split()[-1]
        picture = discord.Embed()
        picture.set_image(url=self.models.get_image(name))
        picture.set_footer(text=name)
        await message.channel.send(embed=picture)

    @staticmethod
    async def magic_shell(message):
        """
        <Frage>, ja oder nein?
        """
        choices = [
            "Ja!",
            "Jo.",
            "Total!",
            "Natürlich.",
            "Nein!",
            "Nö.",
            "Nä.",
            "Niemals!",
        ]
        await message.channel.send(random.choice(choices))

    # TODO: Accept multi-word inputs: "Heidi, wähle: Ipp ist dumm, ich bin dumm"
    @staticmethod
    async def choose(message):
        """
        wähle: <Option 1>, <Option 2>, ...
        """

        choices = message.content.replace(",", "").split()[2:]
        await message.channel.send(random.choice(choices))

    @staticmethod
    async def show_link(message):
        """
        gib Link
        """
        link_pro7 = "https://www.prosieben.de/tv/germanys-next-topmodel/livestream"
        link_joyn = "https://www.joyn.de/serien/germanys-next-topmodel"

        await message.channel.send(f"ProSieben: {link_pro7}\nJoyn: {link_joyn}")

    @staticmethod
    async def random_color(message):
        """
        welche Farbe ... <Ding>? (Zufällige Farbe)
        """
        choices = [
            "Rot",
            "Grün",
            "Gelb",
            "Blau",
            "Lila",
            "Pink",
            "Türkis",
            "Schwarz",
            "Weiß",
            "Grau",
            "Gelb",
            "Orange",
            "Olivegrün",
            "Mitternachtsblau",
            "Braun",
            "Tobe",
        ]
        await message.channel.send(random.choice(choices))

    # Voiceboard ---------------------------------------------------------------------------------

    @staticmethod
    async def list_voicelines(message):
        """
        sprechen
        """
        voicelines = map(lambda x: x.split(".")[0], os.listdir("/sounds"))  # only works from docker
        await message.channel.send("Voicelines:\n- " + reduce(lambda x, y: x + "\n- " + y, voicelines))
        # await message.channel.send("Test")

    @staticmethod
    async def say_voiceline(message):
        """
        sag <Voiceline>
        """
        try:
            voice_channel = message.author.voice.channel
        except AttributeError:
            print("Error: Caller not in channel!")
            return

        soundfile = message.content.split(" ")[-1]

        voice_client = await voice_channel.connect()
        audio_source = discord.FFmpegPCMAudio("/sounds/" + soundfile + ".mp3")  # only works from docker
        voice_client.play(audio_source)

        while voice_client.is_playing():
            await asyncio.sleep(1)

        await voice_client.disconnect()

    # Automatic Actions --------------------------------------------------------------------------

    @staticmethod
    async def autoreact_to_girls(message):
        """
        ❤ aktives Model
        """
        await message.add_reaction("❤")

    @staticmethod
    async def autoreact_to_jeremy(message):
        """
        🧀 Jeremy
        """
        await message.add_reaction("🧀")


client = HeidiClient()
client.run(TOKEN)
