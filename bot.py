#!/usr/bin/env python3

import os
import re
import random
import datetime
import asyncio

from dotenv import load_dotenv
from models import Models

import discord

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")  # Zocken mit Heidi


class HeidiClient(discord.Client):
    def __init__(self):
        super().__init__(
            status="Nur eine kann Germany's next Topmodel werden!",
        )

        self.prefix = "Heidi, "
        self.prefix_regex = "^" + self.prefix

        self.models = Models()  # scraped model list

        self.triggers = {
            lambda m: m.author.nick.lower() in self.models.get_in_names(): self.autoreact_to_girls,
            lambda m: "jeremy" in m.author.nick.lower(): self.autoreact_to_jeremy
        }  # automatic actions

        self.matchers = {"Hilfe$": self.show_help, "Heidi!$": self.say_name,
                         "wer ist dabei\\?$": self.list_models_in,
                         "wer ist raus\\?$": self.list_models_out,
                         ".+, ja oder nein\\?$": self.magic_shell, "wähle: (.+,?)+$": self.choose,
                         "gib Link": self.show_link, "welche Farbe .+\\?$": self.random_color,
                         "sag kein Foto$": self.say_kein_foto,
                         "sag Opfer": self.say_opfer
                         }  # react to messages

        # Voicelines

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
        await message.channel.send("\n".join(self.models.get_in_names()))

    async def list_models_out(self, message):
        """
        wer ist raus? (Liste der Keks welche ich ge*ickt hab)
        """
        await message.channel.send("\n".join(self.models.get_out_names()))

    async def show_model_picture(self, message):
        """
        gib Bild von <Name> (Zeigt ein Bild des entsprechenden Models)
        """
        name = message.content.split()[-1]
        picture = discord.Embed()
        picture.set_image(url=self.models.get_image(name))
        picture.set_footer(text=name)
        await message.channel.send(embed=picture)

    async def magic_shell(self, message):
        """
        <Frage>, ja oder nein? (Ich beantworte dir eine Frage)
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
    async def choose(self, message):
        """
        wähle: <Option 1>, <Option 2>, ... (Ich treffe eine Wahl)
        """

        choices = message.content.replace(",", "").split()[2:]
        await message.channel.send(random.choice(choices))

    async def show_link(self, message):
        """
        gib Link (Link zum Stream)
        """
        link_pro7 = "https://www.prosieben.de/tv/germanys-next-topmodel/livestream"
        link_joyn = "https://www.joyn.de/serien/germanys-next-topmodel"

        await message.channel.send(f"ProSieben: {link_pro7}\nJoyn: {link_joyn}")

    async def random_color(self, message):
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

    async def say_kein_foto(self, message):
        """
        sag kein Foto ("Ich habe heute leider kein Foto für dich")
        """
        voice_channel = message.author.voice.channel

        if voice_channel == None:
            return

        voice_client = await voice_channel.connect()
        audio_source = discord.FFmpegPCMAudio("sounds/kein_foto.mp3")
        voice_client.play(audio_source)

        while voice_client.is_playing():
            await asyncio.sleep(1)

        await voice_client.disconnect()

    async def say_opfer(self, message):
        """
        sag Opfer ("Opfer")
        """
        voice_channel = message.author.voice.channel

        if voice_channel == None:
            return

        voice_client = await voice_channel.connect()
        audio_source = discord.FFmpegPCMAudio("sounds/opfer.mp3")
        voice_client.play(audio_source)

        while voice_client.is_playing():
            await asyncio.sleep(1)

        await voice_client.disconnect()

    # Automatic Actions --------------------------------------------------------------------------

    async def autoreact_to_girls(self, message):
        """
        Ich ❤-e Nachrichten einer aktiven GNTM Teilnehmerin
        """
        await message.add_reaction("❤")

    async def autoreact_to_jeremy(self, message):
        """
        Ich ❤-e Nachrichten von Jeremy
        """
        await message.add_reaction("🧀")


client = HeidiClient()
client.run(TOKEN)
