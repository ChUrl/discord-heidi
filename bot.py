# Example: https://github.com/Rapptz/discord.py/blob/master/examples/app_commands/basic.py

import os, re, random, logging, asyncio, discord
from discord import app_commands
from functools import reduce
from dotenv import load_dotenv
from typing import Optional

# TODO: Reenable and extend scraper
# from models import Models

# We're fancy today
from rich.traceback import install
install(show_locals=True)

# DONE: Migrate back to discord.py
# TODO: Rewrite bot with slash commands (and making actual use of discord.py)
# TODO: yt-dlp music support
# TODO: Send messages only to heidispam channel
# TODO: Print status messages to heidispam
# TODO: Somehow upload voicelines more easily (from discord voice message?)
# TODO: Reenable text/quote generation, allow uploading of training text files, allow switching "personalities"
# TODO: Zalgo generator

# IDs of the servers Heidi is used on
LINUS_GUILD = discord.Object(id=431154792308408340)
TEST_GUILD = discord.Object(id=821511861178204161)

class HeidiClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(status="Nur eine kann GNTM werden!", intents=intents)

        # Separate object that keeps all application command state
        self.tree = app_commands.CommandTree(self)

        # TODO: Replace with slash commands
        self.prefix = "Heidi, "
        self.prefix_regex = "^" + self.prefix

        # self.models = Models()  # scraped model list

        # automatic actions on all messages
        # auto_triggers is a map with tuples of two functions: (predicate, action)
        # if the predicate is true the action is performed
        self.auto_triggers = {
            # lambda m: m.author.nick.lower() in self.models.get_in_names(): self.autoreact_to_girls,
            lambda m: "jeremy" in m.author.nick.lower(): self._autoreact_to_jeremy
        }

        # TODO: Replace these by slash commands
        # explicit commands
        self.matchers = {
            "Hilfe$": self.show_help,
            "Heidi!$": self.say_name,

            # GNTM stuff
            # "wer ist dabei\\?$": self.list_models_in,
            # "wer ist raus\\?$": self.list_models_out,
            # "gib Bild von .+$": self.show_model_picture,
            "gib Link$": self.show_link,

            # Fun stuff
            "welche Farbe .+\\?": self.random_color,
            ".+, ja oder nein\\?": self.magic_shell,
            "wähle: (.+,?)+$": self.choose,
            "sprechen": self.list_voicelines,
            "sag .+$": self.say_voiceline
        }

    # Synchronize commands to guilds
    async def setup_hook(self):
        self.tree.copy_global_to(guild=LINUS_GUILD)
        await self.tree.sync(guild=LINUS_GUILD)

        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync(guild=TEST_GUILD)

    # Helpers ------------------------------------------------------------------------------------

    def _help_text(self):
        """
        Generate help-string from docstrings of matchers and triggers
        """
        docstrings_triggers = [
            "  - " + str(func.__doc__).strip() for func in self.auto_triggers.values()
        ]
        docstrings_matchers = [
            "  - " + str(func.__doc__).strip() for func in self.matchers.values()
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

    # async def list_models_in(self, message):
    #     """
    #     wer ist dabei?
    #     """
    #     await message.channel.send("\n".join(self.models.get_in_names()))

    # async def list_models_out(self, message):
    #     """
    #     wer ist raus? (Liste der Keks welche ge*ickt wurden)
    #     """
    #     await message.channel.send("\n".join(self.models.get_out_names()))

    # async def show_model_picture(self, message):
    #     """
    #     gib Bild von <Name>
    #     """
    #     name = message.content.split()[-1]
    #     picture = discord.Embed()
    #     picture.set_image(url=self.models.get_image(name))
    #     picture.set_footer(text=name)
    #     await message.channel.send(embed=picture)

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

    # TODO: Don't connect to voice when file not found
    # TODO: Filenames with spaces?
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

        try:
            open("/sounds/" + soundfile + ".mp3")
        except IOError:
            print("Error: Invalid soundfile!")
            return

        audio_source = discord.FFmpegPCMAudio("/sounds/" + soundfile + ".mp3")  # only works from docker
        voice_client = await voice_channel.connect()
        voice_client.play(audio_source)

        while voice_client.is_playing():
            await asyncio.sleep(1)

        await voice_client.disconnect()

    # Automatic Actions --------------------------------------------------------------------------

    # @staticmethod
    # async def autoreact_to_girls(message):
    #     """
    #     ❤ aktives Model
    #     """
    #     await message.add_reaction("❤")

    @staticmethod
    async def _autoreact_to_jeremy(message):
        """
        🧀 Jeremy
        """
        await message.add_reaction("🧀")

# ------------------------------------------------------------------------------------------------

# Log to file
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Intents specification is no longer optional
intents = discord.Intents.default()
intents.members = True # Allow to react to member join/leave etc
intents.message_content = True # Allow to read message content from arbitrary messages

# Setup our client
client = HeidiClient(intents=intents)

# ------------------------------------------------------------------------------------------------
# NOTE: I defined the events outside of the Client class, don't know if I like it or not...

@client.event
async def on_ready():
    print(f"{client.user} (id: {client.user.id}) has connected to Discord!")

@client.event
async def on_message(message):
    # Skip Heidis own messages
    if message.author == client.user:
        return

    # Automatic actions for all messages
    # python iterates over the keys of a map
    for predicate in client.auto_triggers:
        if predicate(message):
            action = client.auto_triggers[predicate]
            await action(message)
            break

    # TODO: Replace by slash commands
    for matcher in client.matchers:
        if client._match(matcher, message):
            await client.matchers[matcher](message)
            break

# ------------------------------------------------------------------------------------------------

# Used to start the bot locally, for docker the variables have to be set when the container is run
load_dotenv()
TOKEN: str = os.getenv("DISCORD_TOKEN") or ""

# Start client if TOKEN valid
if TOKEN != "":
    client.run(TOKEN, log_handler=handler)
else:
    print("DISCORD_TOKEN not found, exiting...")
