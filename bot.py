# Example: https://github.com/Rapptz/discord.py/blob/master/examples/app_commands/basic.py

import os, re, random, logging, asyncio, discord, configparser
from discord import app_commands
from discord.app_commands import Choice
from functools import reduce
from dotenv import load_dotenv
from typing import Dict, List, Optional, Union, Callable, Any

# TODO: Reenable + extend textgen
# from textgen import textgen
# from textgen_markov import MarkovTextGenerator
# from textgen_lstm import LSTMTextGenerator

# TODO: Reenable + extend scraper
# from models import Models

# We're fancy today
from rich.traceback import install

install(show_locals=True)
load_dotenv()


# ================================================================================================ #
# ================================================================================================ #
# NOTE: Always set this correctly:
DOCKER = os.getenv("DOCKER") == "True"
# ================================================================================================ #
# ================================================================================================ #


# TODO: Only post in heidi-spam channel
# TODO: yt-dlp music support
# TODO: Somehow upload voicelines more easily (from discord voice message?)

# IDs of the servers Heidi is used on
LINUS_GUILD = discord.Object(id=431154792308408340)
TEST_GUILD = discord.Object(id=821511861178204161)

CONFIGPATH = "/config" if DOCKER else "."
USERCONFIGNAME = "Heidi_User.conf"


class HeidiClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(status="Nur eine kann GNTM werden!", intents=intents)

        # Separate object that keeps all application command state
        self.tree = app_commands.CommandTree(self)

        # Handle persistent user configuration
        self.user_config = configparser.ConfigParser()
        if not os.path.exists(f"{CONFIGPATH}/{USERCONFIGNAME}"):
            os.mknod(f"{CONFIGPATH}/{USERCONFIGNAME}")
        self.user_config.read(f"{CONFIGPATH}/{USERCONFIGNAME}")
        self.update_to_default_user_config()
        self.print_user_config()

        # self.models = Models()  # scraped model list

        # automatic actions on all messages
        # on_message_triggers is a map with tuples of two functions: (predicate, action)
        # the predicate receives the message as argument
        # if the predicate is true the action is performed
        self.on_message_triggers = {
            # lambda m: m.author.nick.lower() in self.models.get_in_names(): self.autoreact_to_girls,
            lambda m: "jeremy" in m.author.nick.lower(): self._autoreact_to_jeremy,
            lambda m: "kardashian" in m.author.nick.lower()
            or "jenner" in m.author.nick.lower(): self._autoreact_to_kardashian,
        }

        # automatic actions on voice state changes
        # on_voice_state_triggers is a map with tuples of two functions: (predicate, action)
        # the predicate receives the member, before- and after-state as arguments
        # if the predicate is true, the action is performed
        self.on_voice_state_triggers = {
            lambda m, b, a: b.channel != a.channel
            and a.channel is not None
            and isinstance(a.channel, discord.VoiceChannel): self._play_entrance_sound,
        }

        # Textgen
        # self.textgen_models: dict[str, textgen] = {
        #     # The name must correspond to the name of the training text file
        #     "kommunistisches_manifest": LSTMTextGenerator(10),
        #     "musk": LSTMTextGenerator(10),
        #     "bibel": LSTMTextGenerator(10)
        #     "bibel": MarkovTextGenerator(3), # Prefix length of 3
        #     "kommunistisches_manifest": MarkovTextGenerator(3),
        #     "musk": MarkovTextGenerator(3)
        # }

        # for name, model in self.textgen_models.items():
        #     model.init(name)  # Loads the textfile

        #     if os.path.exists(f"weights/{name}_lstm_model.pt"):
        #         model.load()
        #     elif not DOCKER:
        #         model.train()
        #     else:
        #         print("Error: Can't load model", name)

        #     print("Generating test sentence for", name)
        #     self.textgen_models[name].generate_sentence()

    # Synchronize commands to guilds
    async def setup_hook(self):
        self.tree.copy_global_to(guild=LINUS_GUILD)
        await self.tree.sync(guild=LINUS_GUILD)

        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync(guild=TEST_GUILD)

    def update_to_default_user_config(self) -> None:
        """
        Adds config keys to the config, if they don't exist yet.
        """
        user_config_sections = ["ENTRANCE.SOUND"]

        for section in user_config_sections:
            if section not in self.user_config:
                print(f"Adding section {section} to {CONFIGPATH}/{USERCONFIGNAME}")
                self.user_config[section] = dict()

        self.write_user_config()

    def print_user_config(self) -> None:
        print("Read persistent configuration:\n")

        for section in self.user_config.sections():
            print(f"[{section}]")
            for key in self.user_config[section]:
                print(f"{key}={self.user_config[section][key]}")

        print("")

    def write_user_config(self) -> None:
        if not os.path.exists(f"{CONFIGPATH}/{USERCONFIGNAME}"):
            print(f"Error: {CONFIGPATH}/{USERCONFIGNAME} doesn't exist!")
            return

        print(f"Writing {CONFIGPATH}/{USERCONFIGNAME}")

        with open(f"{CONFIGPATH}/{USERCONFIGNAME}", "w") as file:
            self.user_config.write(file)

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
    async def _autoreact_to_jeremy(message: discord.Message) -> None:
        """
        🧀 Jeremy
        """
        await message.add_reaction("🧀")

    @staticmethod
    async def _autoreact_to_kardashian(message: discord.Message) -> None:
        """
        💄 Kardashian
        """
        await message.add_reaction("💄")

    async def _play_entrance_sound(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        soundpath: Union[str, None] = self.user_config["ENTRANCE.SOUND"].get(
            member.name, None
        )

        if soundpath is None:
            print(f"User {member.name} has not set an entrance sound")
            return

        board, sound = soundpath.split("/")

        # Wait a bit to not have simultaneous joins
        await asyncio.sleep(1)

        await play_voice_line_for_member(None, member, board, sound)


# ------------------------------------------------------------------------------------------------

# Log to file
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

# Intents specification is no longer optional
intents = discord.Intents.default()
intents.members = True  # Allow to react to member join/leave etc
intents.message_content = True  # Allow to read message content from arbitrary messages
intents.voice_states = True  # Allow to process on_voice_state_update

# Setup our client
client = HeidiClient(intents=intents)

# Events -----------------------------------------------------------------------------------------
# NOTE: I defined the events outside of the Client class, don't know if I like it or not...


@client.event
async def on_ready() -> None:
    if client.user is not None:
        print(f"{client.user} (id: {client.user.id}) has connected to Discord!")
    else:
        print("client.user is None!")


@client.event
async def on_message(message: discord.Message) -> None:
    # Skip Heidis own messages
    if message.author == client.user:
        return

    # Automatic actions for all messages
    # python iterates over the keys of a map
    for predicate in client.on_message_triggers:
        if predicate(message):
            action = client.on_message_triggers[predicate]
            print(f"on_message: calling {action.__name__}")
            await action(message)


@client.event
async def on_voice_state_update(
    member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
) -> None:
    # Skip Heidis own voice state updates (e.g. on /say)
    if member._user == client.user:
        return

    # Automatic acions for all voice state changes
    # python iterates over the keys of a map
    for predicate in client.on_voice_state_triggers:
        if predicate(member, before, after):
            action: Callable = client.on_voice_state_triggers[predicate]
            print(f"on_voice_state_update: calling {action.__name__}")
            await action(member, before, after)


# Config Commands --------------------------------------------------------------------------------


async def user_config_key_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    return [
        Choice(name=key, value=key)
        for key in client.user_config.sections()
        if key.lower().startswith(current.lower())
    ]


async def user_config_value_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    """
    Calls an autocomplete function depending on the entered config_key.
    """
    autocompleters = {"ENTRANCE.SOUND": user_entrance_sound_autocomplete}
    autocompleter = autocompleters[interaction.namespace.option]

    print(f"config_value_autocomplete: calling {autocompleter.__name__}")

    return autocompleter(interaction, current)


def user_entrance_sound_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    """
    Generates autocomplete options for the ENTRANCE.SOUND config key.
    """
    boards: List[str] = os.listdir(SOUNDDIR)
    all_sounds: Dict[str, List[str]] = {
        board: list(map(lambda x: x.split(".")[0], os.listdir(f"{SOUNDDIR}/{board}/")))
        for board in boards
    }  # These are all sounds, organized per board

    completions: List[Choice[str]] = []
    for (
        board,
        board_sounds,
    ) in all_sounds.items():  # Iterate over all sounds, organized per board
        for sound in board_sounds:  # Iterate over board specific sounds
            soundpath = f"{board}/{sound}"
            if soundpath.lower().startswith(current.lower()):
                completions += [Choice(name=soundpath, value=soundpath)]

    return completions


@client.tree.command(
    name="userconfig",
    description="User-spezifische Heidi-Einstellungen (Heidi merkt sie sich in ihrem riesigen Gehirn).",
)
@app_commands.rename(config_key="option")
@app_commands.describe(config_key="Die Option, welche du ändern willst.")
@app_commands.autocomplete(config_key=user_config_key_autocomplete)
@app_commands.rename(config_value="wert")
@app_commands.describe(
    config_value="Der Wert, auf welche die Option gesetzt werden soll."
)
@app_commands.autocomplete(config_value=user_config_value_autocomplete)
async def user_config(
    interaction: discord.Interaction, config_key: str, config_value: str
) -> None:
    # Only Members can set settings
    if not isinstance(interaction.user, discord.Member):
        print("User not a member")
        await interaction.response.send_message("Heidi sagt: Komm in die Gruppe!")
        return

    member: discord.Member = interaction.user

    client.user_config[config_key][member.name] = config_value
    client.write_user_config()

    await interaction.response.send_message(
        f"Ok, ich schreibe {member.name}={config_value} in mein fettes Gehirn!"
    )


# Commands ---------------------------------------------------------------------------------------


@client.tree.command(
    name="giblinkbruder",
    description="Heidi hilft mit dem Link zu deiner Lieblingsshow im Qualitätsfernsehen.",
)
async def show_link(interaction: discord.Interaction) -> None:
    link_pro7 = "https://www.prosieben.de/tv/germanys-next-topmodel/livestream"
    link_joyn = "https://www.joyn.de/serien/germanys-next-topmodel"

    await interaction.response.send_message(
        f"ProSieben: {link_pro7}\nJoyn: {link_joyn}"
    )


@client.tree.command(name="heidi", description="Heidi!")
async def heidi_exclaim(interaction: discord.Interaction) -> None:
    messages = [
        "Die sind doch fast 18!",
        "Heidi!",
        "Du bist raus hihi :)",
        "Dann zieh dich mal aus!",
        "Warum denn so schüchtern?",
        "Im TV ist das legal!",
        "Das Stroh ist nur fürs Shooting!",
    ]
    await interaction.response.send_message(random.choice(messages))


@client.tree.command(name="miesmuschel", description="Was denkt Heidi?")
@app_commands.rename(question="frage")
@app_commands.describe(question="Heidi wird es beantworten!")
async def magic_shell(interaction: discord.Interaction, question: str) -> None:
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
    await interaction.response.send_message(
        f"{question}{question_mark}\nHeidi sagt: {random.choice(choices)}"
    )


# TODO: Allow , separated varargs, need to parse manually as slash commands don't support varargs
@client.tree.command(name="wähle", description="Heidi trifft die Wahl!")
@app_commands.rename(option_a="entweder")
@app_commands.describe(option_a="Ist es vielleicht dies?")
@app_commands.rename(option_b="oder")
@app_commands.describe(option_b="Oder doch eher das?")
async def choose(interaction: discord.Interaction, option_a: str, option_b: str) -> None:
    options = [option_a.strip(), option_b.strip()]
    await interaction.response.send_message(
        f"{options[0]} oder {options[1]}?\nHeidi sagt: {random.choice(options)}"
    )


# TextGen ----------------------------------------------------------------------------------------


# async def quote_model_autocomplete(interaction: discord.Interaction, current: str) -> list[Choice[str]]:
#     models = client.textgen_models.keys()
#     return [Choice(name=model, value=model) for model in models]

# @client.tree.command(name="zitat", description="Heidi zitiert!")
# @app_commands.rename(quote_model = "style")
# @app_commands.describe(quote_model = "Woraus soll Heidi zitieren?")
# @app_commands.autocomplete(quote_model = quote_model_autocomplete)
# async def quote(interaction: discord.Interaction, quote_model: str):
#     generated_quote = client.textgen_models[quote_model].generate_sentence()
#     joined_quote = " ".join(generated_quote)
#     await interaction.response.send_message(f"Heidi zitiert: \"{joined_quote}\"")

# @client.tree.command(name="vervollständige", description="Heidi beendet den Satz!")
# @app_commands.rename(prompt = "satzanfang")
# @app_commands.describe(prompt = "Der Satzanfang wird vervollständigt.")
# @app_commands.rename(quote_model = "style")
# @app_commands.describe(quote_model = "Woraus soll Heidi vervollständigen?")
# @app_commands.autocomplete(quote_model = quote_model_autocomplete)
# async def complete(interaction: discord.Interaction, prompt: str, quote_model: str):
#     prompt = re.sub(r"[^a-zäöüß'.,]+", " ", prompt.lower()) # only keep valid chars
#     generated_quote = client.textgen_models[quote_model].complete_sentence(prompt.split())
#     joined_quote = " ".join(generated_quote)
#     await interaction.response.send_message(f"Heidi sagt: \"{joined_quote}\"")


# Sounds -----------------------------------------------------------------------------------------


SOUNDDIR: str = "/sounds" if DOCKER else "./heidi-sounds"


# Example: https://discordpy.readthedocs.io/en/latest/interactions/api.html?highlight=autocomplete#discord.app_commands.autocomplete
async def board_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    boards: List[str] = os.listdir(SOUNDDIR)

    return [
        Choice(name=board, value=board)
        for board in boards
        if board.lower().startswith(current.lower())
    ]


async def sound_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    board: str = interaction.namespace.board
    sounds: List[str] = list(
        map(lambda x: x.split(".")[0], os.listdir(f"{SOUNDDIR}/{board}/"))
    )

    return [
        Choice(name=sound, value=sound)
        for sound in sounds
        if sound.lower().startswith(current.lower())
    ]


@client.tree.command(
    name="sag", description="Heidi drückt den Knopf auf dem Soundboard."
)
@app_commands.describe(sound="Was soll Heidi sagen?")
@app_commands.autocomplete(board=board_autocomplete)
@app_commands.autocomplete(sound=sound_autocomplete)
async def say_voiceline(interaction: discord.Interaction, board: str, sound: str) -> None:
    # Only Members can access voice channels
    if not isinstance(interaction.user, discord.Member):
        print("User not a member")
        await interaction.response.send_message("Heidi sagt: Komm in die Gruppe!")
        return

    member: discord.Member = interaction.user

    await play_voice_line_for_member(interaction, member, board, sound)


# Contextmenu ------------------------------------------------------------------------------------


# Callable on members
@client.tree.context_menu(name="beleidigen")
async def insult(
    interaction: discord.Interaction, member: discord.Member
) -> None:  # with message: discord.Message this can be called on a message
    if not member.dm_channel:
        await member.create_dm()

    if not member.dm_channel:
        print("Error creating DMChannel!")
        await interaction.response.send_message("Heidi sagt: Gib mal DM Nummer süße*r!")
        return

    insults = [
        "Du kleiner Hurensohn!",
        "Fick dich!",
        "Fotze!",
        "Du Sohn einer Dirne!",
        "Ipp hat gesagt du stinkst!",
        "Ich furze in den Bart deines Vaters!",
        "Geh auf der Autobahn spielen!",
        "Du Bananenbieger!",
        "Du kommst bei mir nichtmal durch die Vorauswahl!",
        "Opfer!",
        "Du miese Raupe!",
        "Geh Steckdosen befruchten!",
        "Richtiger Gesichtsgünther ey!",
    ]

    await member.dm_channel.send(random.choice(insults))
    await interaction.response.send_message(
        "Anzeige ist raus!"
    )  # with ephemeral = True only the caller can see the answer


# Helpers ----------------------------------------------------------------------------------------


async def play_voice_line(
    interaction: Union[discord.Interaction, None],
    voice_channel: discord.VoiceChannel,
    board: str,
    sound: str,
) -> None:
    try:
        open(f"{SOUNDDIR}/{board}/{sound}.mkv")
    except IOError:
        print("Error: Invalid soundfile!")
        if interaction is not None:
            await interaction.response.send_message(
                f'Heidi sagt: "{board}/{sound}" kanninich finden bruder'
            )
        return

    if interaction is not None:
        await interaction.response.send_message(f'Heidi sagt: "{board}/{sound}"')

    audio_source = discord.FFmpegPCMAudio(
        f"{SOUNDDIR}/{board}/{sound}.mkv"
    )  # only works from docker
    voice_client = await voice_channel.connect()
    voice_client.play(audio_source)

    while voice_client.is_playing():
        await asyncio.sleep(1)

    await voice_client.disconnect()


async def play_voice_line_for_member(
    interaction: Union[discord.Interaction, None],
    member: discord.Member,
    board: str,
    sound: str,
) -> None:
    # Member needs to be in voice channel to hear audio (Heidi needs to know the channel to join)
    if (
        member is None
        or member.voice is None
        or member.voice.channel is None
        or not isinstance(member.voice.channel, discord.VoiceChannel)
    ):
        print("User not in (valid) voice channel!")
        if interaction is not None:
            await interaction.response.send_message("Heidi sagt: Komm in den Channel!")
        return

    voice_channel: discord.VoiceChannel = member.voice.channel

    await play_voice_line(interaction, voice_channel, board, sound)


# ------------------------------------------------------------------------------------------------


# Used to start the bot locally, for docker the variables have to be set when the container is run
TOKEN: str = os.getenv("DISCORD_TOKEN") or ""

# Start client if TOKEN valid
if TOKEN != "":
    print(f"Running client with DOCKER={DOCKER}")
    client.run(TOKEN, log_handler=handler)
else:
    print("DISCORD_TOKEN not found, exiting...")
