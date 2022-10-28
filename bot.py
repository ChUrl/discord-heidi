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
# DONE: Rewrite bot with slash commands (and making actual use of discord.py)
# TODO: yt-dlp music support
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

@client.tree.command(name="miesmuschel", description="Was denk Heidi?")
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
@client.tree.command(name="wähle", description="Heidi trifft die Wahl")
@app_commands.describe(option_a = "Erste möglichkeit")
@app_commands.describe(option_b = "Zweite möglichkeit")
async def choose(interaction: discord.Interaction, option_a: str, option_b: str):
    options = [option_a.strip(), option_b.strip()]
    await interaction.response.send_message(f"{options[0]} oder {options[1]}?\nHeidi sagt: {random.choice(options)}")

@client.tree.command(name="giblinkbruder", description="Heidi hilft mit dem Link zu deiner Lieblingsshow im Qualitätsfernsehen")
async def show_link(interaction: discord.Interaction):
    link_pro7 = "https://www.prosieben.de/tv/germanys-next-topmodel/livestream"
    link_joyn = "https://www.joyn.de/serien/germanys-next-topmodel"

    await interaction.response.send_message(f"ProSieben: {link_pro7}\nJoyn: {link_joyn}")





# Example
# Callable on members
@client.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')

# Example
# Callable on messages
@client.tree.context_menu(name='Report to Moderators')
async def report_message(interaction: discord.Interaction, message: discord.Message):
    # We're sending this response message with ephemeral=True, so only the command executor can see it
    await interaction.response.send_message(
        f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
    )

    # Handle report by sending it into a log channel
    log_channel = interaction.guild.get_channel(821511861178204164)  # replace with your channel id

    embed = discord.Embed(title='Reported Message')
    if message.content:
        embed.description = message.content

    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    embed.timestamp = message.created_at

    url_view = discord.ui.View()
    url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

    await log_channel.send(embed=embed, view=url_view)

# ------------------------------------------------------------------------------------------------

# Used to start the bot locally, for docker the variables have to be set when the container is run
load_dotenv()
TOKEN: str = os.getenv("DISCORD_TOKEN") or ""

# Start client if TOKEN valid
if TOKEN != "":
    client.run(TOKEN, log_handler=handler)
else:
    print("DISCORD_TOKEN not found, exiting...")
