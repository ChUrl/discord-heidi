# Example: https://github.com/Rapptz/discord.py/blob/master/examples/app_commands/basic.py

import os, re, random, logging, asyncio, discord
from discord import app_commands
from discord.app_commands import Choice
from functools import reduce
from dotenv import load_dotenv
from typing import Optional

# TODO: Reenable and extend scraper
# from models import Models

# We're fancy today
from rich.traceback import install
install(show_locals=True)

# DONE: Migrate back to discord.py
# DONE: Rewrite bot with slash commands (and making actual use of discord.py)
# TODO: yt-dlp music support
# TODO: Somehow upload voicelines more easily (from discord voice message?), also need to be distributed to folders so no more than 25 lines per folder
# TODO: Reenable text/quote generation, allow uploading of training text files, allow switching "personalities" (/elon generates elon quote?)
# TODO: Zalgo generator

# IDs of the servers Heidi is used on
LINUS_GUILD = discord.Object(id=431154792308408340)
TEST_GUILD = discord.Object(id=821511861178204161)

class HeidiClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(status="Nur eine kann GNTM werden!", intents=intents)

        # Separate object that keeps all application command state
        self.tree = app_commands.CommandTree(self)

        # self.models = Models()  # scraped model list

        # automatic actions on all messages
        # auto_triggers is a map with tuples of two functions: (predicate, action)
        # if the predicate is true the action is performed
        self.auto_triggers = {
            # lambda m: m.author.nick.lower() in self.models.get_in_names(): self.autoreact_to_girls,
            lambda m: "jeremy" in m.author.nick.lower(): self._autoreact_to_jeremy
        }

    # Synchronize commands to guilds
    async def setup_hook(self):
        self.tree.copy_global_to(guild=LINUS_GUILD)
        await self.tree.sync(guild=LINUS_GUILD)

        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync(guild=TEST_GUILD)

    # Commands -----------------------------------------------------------------------------------

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

# Events -----------------------------------------------------------------------------------------
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

# Commands ---------------------------------------------------------------------------------------

@client.tree.command(name="heidi", description="Heidi!")
async def heidi_exclaim(interaction: discord.Interaction):
    messages = [
        "Die sind doch fast 18!",
        "Heidi!",
        "Du bist raus hihi :)",
        "Dann zieh dich mal aus!",
        "Warum denn so schüchtern?",
        "Im TV ist das legal!",
        "Das Stroh ist nur fürs Shooting!"
    ]
    await interaction.response.send_message(random.choice(messages))

@client.tree.command(name="miesmuschel", description="Was denkt Heidi?")
@app_commands.rename(question = "frage")
@app_commands.describe(question = "Heidi wird es beantworten!")
async def magic_shell(interaction: discord.Interaction, question: str):
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
    question = question.strip()
    question_mark = "" if question[-1] == "?" else "?"
    await interaction.response.send_message(f"{question}{question_mark}\nHeidi sagt: {random.choice(choices)}")

# TODO: Allow , separated varargs, need to parse manually as slash commands don't support varargs
@client.tree.command(name="wähle", description="Heidi trifft die Wahl!")
@app_commands.rename(option_a = "entweder")
@app_commands.describe(option_a = "Ist es vielleicht dies?")
@app_commands.rename(option_b = "oder")
@app_commands.describe(option_b = "Oder doch eher das?")
async def choose(interaction: discord.Interaction, option_a: str, option_b: str):
    options = [option_a.strip(), option_b.strip()]
    await interaction.response.send_message(f"{options[0]} oder {options[1]}?\nHeidi sagt: {random.choice(options)}")

@client.tree.command(name = "giblinkbruder", description = "Heidi hilft mit dem Link zu deiner Lieblingsshow im Qualitätsfernsehen.")
async def show_link(interaction: discord.Interaction):
    link_pro7 = "https://www.prosieben.de/tv/germanys-next-topmodel/livestream"
    link_joyn = "https://www.joyn.de/serien/germanys-next-topmodel"

    await interaction.response.send_message(f"ProSieben: {link_pro7}\nJoyn: {link_joyn}")

# SOUNDDIR: str = "./voicelines/" # Local
SOUNDDIR: str = "/sounds/" # Docker

# Example: https://discordpy.readthedocs.io/en/latest/interactions/api.html?highlight=autocomplete#discord.app_commands.autocomplete
# NOTE: Only 25 items can be autocompleted
# TODO: Generate autocomplete + say function pairs automatically for different sound folders so we can have more than 25 sound files
async def sound_autocomplete(interaction: discord.Interaction, current: str) -> list[Choice[str]]:
    sounds = map(lambda x: x.split(".")[0], os.listdir(SOUNDDIR))
    return [Choice(name=sound, value=sound) for sound in sounds]

@client.tree.command(name = "sag", description = "Heidi drückt den Knopf auf dem Soundboard.")
@app_commands.describe(sound = "Was soll Heidi sagen?")
@app_commands.autocomplete(sound = sound_autocomplete)
async def say_voiceline(interaction: discord.Interaction, sound: str):
    # Only Members can access voice channels
    if not isinstance(interaction.user, discord.Member):
        print("User not a member")
        await interaction.response.send_message("Heidi sagt: Komm in die Gruppe!")
        return

    member: discord.Member = interaction.user

    # Member needs to be in voice channel to hear audio (Heidi needs to know the channel to join)
    if (not member.voice) or (not member.voice.channel) or (not isinstance(member.voice.channel, discord.VoiceChannel)):
        print("User not in (valid) voice channel!")
        await interaction.response.send_message("Heidi sagt: Komm in den Channel!")
        return

    voice_channel: discord.VoiceChannel = member.voice.channel

    try:
        open(SOUNDDIR + sound + ".mp3")
    except IOError:
        print("Error: Invalid soundfile!")
        await interaction.response.send_message(f"Heidi sagt: \"{sound}\" kanninich finden bruder")
        return

    await interaction.response.send_message(f"Heidi sagt: \"{sound}\"")

    audio_source = discord.FFmpegPCMAudio(SOUNDDIR + sound + ".mp3")  # only works from docker
    voice_client = await voice_channel.connect()
    voice_client.play(audio_source)

    while voice_client.is_playing():
        await asyncio.sleep(1)

    await voice_client.disconnect()

# TODO: More insults
# Callable on members
@client.tree.context_menu(name="beleidigen")
async def insult(interaction: discord.Interaction, member: discord.Member): # with message: discord.Message this can be called on a message
    if not member.dm_channel:
        await member.create_dm()

    if not member.dm_channel:
        print("Error creating DMChannel!")
        await interaction.response.send_message("Heidi sagt: Gib mal DM Nummer süße*r!")
        return

    insults = [
        "Du kleiner Hurensohn!",
        "Fick dich!"
    ]

    await member.dm_channel.send(random.choice(insults))
    await interaction.response.send_message("Anzeige ist raus!") # with ephemeral = True only the caller can see the answer

# ------------------------------------------------------------------------------------------------

# Used to start the bot locally, for docker the variables have to be set when the container is run
load_dotenv()
TOKEN: str = os.getenv("DISCORD_TOKEN") or ""

# Start client if TOKEN valid
if TOKEN != "":
    client.run(TOKEN, log_handler=handler)
else:
    print("DISCORD_TOKEN not found, exiting...")
