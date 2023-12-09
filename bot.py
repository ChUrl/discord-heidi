# Example: https://github.com/Rapptz/discord.py/blob/master/examples/app_commands/basic.py

import os, re, random, logging, asyncio, discord, configparser
from discord import app_commands, Member, VoiceState, VoiceChannel, Message, Interaction
from discord.app_commands import Choice
from functools import reduce
from dotenv import load_dotenv
from typing import Dict, List, Optional, Union, Callable, Any

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
            and isinstance(a.channel, VoiceChannel): self._play_entrance_sound,
        }

    # Synchronize commands to guilds
    async def setup_hook(self):
        self.tree.copy_global_to(guild=LINUS_GUILD)
        await self.tree.sync(guild=LINUS_GUILD)

        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync(guild=TEST_GUILD)

    def update_to_default_user_config(self) -> None:
        """
        Adds config keys to the config, if they don't exist yet.
        This writes the user config file.
        """
        user_config_sections = ["ENTRANCE.SOUND"]

        for section in user_config_sections:
            if section not in self.user_config:
                print(f"Adding section {section} to {CONFIGPATH}/{USERCONFIGNAME}")
                self.user_config[section] = dict()

        self.write_user_config()

    def print_user_config(self) -> None:
        """
        Print the current user config from memory.
        This does not read the user config file.
        """
        print("Heidi User Config:\n")

        for section in self.user_config.sections():
            print(f"[{section}]")
            for key in self.user_config[section]:
                print(f"{key}={self.user_config[section][key]}")

        print("")

    def write_user_config(self) -> None:
        """
        Write the current configuration to disk.
        """
        if not os.path.exists(f"{CONFIGPATH}/{USERCONFIGNAME}"):
            print(f"Error: {CONFIGPATH}/{USERCONFIGNAME} doesn't exist!")
            return

        print(f"Writing {CONFIGPATH}/{USERCONFIGNAME}")

        with open(f"{CONFIGPATH}/{USERCONFIGNAME}", "w") as file:
            self.user_config.write(file)

    # Automatic Actions ------------------------------------------------------------------------------

    @staticmethod
    async def _autoreact_to_jeremy(message: Message) -> None:
        """
        🧀 Jeremy.
        This function is set in on_message_triggers and triggered by the on_message event.
        """
        await message.add_reaction("🧀")

    @staticmethod
    async def _autoreact_to_kardashian(message: Message) -> None:
        """
        💄 Kardashian.
        This function is set in on_message_triggers and triggered by the on_message event.
        """
        await message.add_reaction("💄")

    async def _play_entrance_sound(
        self,
            member: Member,
            before: VoiceState,
            after: VoiceState,
    ) -> None:
        """
        Play a sound when a member joins a voice channel.
        This function is set in on_voice_state_triggers and triggered by the on_voice_state_update event.
        """
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

# Set up our client
client = HeidiClient(intents=intents)


# Events -----------------------------------------------------------------------------------------
# NOTE: I defined the events outside the Client class, don't know if I like it or not...


@client.event
async def on_ready() -> None:
    """
    This event triggers when the Heidi client has finished connecting.
    """
    if client.user is not None:
        print(f"{client.user} (id: {client.user.id}) has connected to Discord!")
    else:
        print("client.user is None!")


@client.event
async def on_message(message: Message) -> None:
    """
    This event triggers when a message is sent in any text channel.
    """
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
    member: Member, before: VoiceState, after: VoiceState
) -> None:
    """
    This event triggers when a member joins/changes/leaves a voice channel or mutes/unmutes.
    """
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
    interaction: Interaction, current: str
) -> List[Choice[str]]:
    """
    Suggest a value from the user config keys (each .conf section is a key).
    """
    return [
        Choice(name=key, value=key)
        for key in client.user_config.sections()
        if key.lower().startswith(current.lower())
    ]


async def user_config_value_autocomplete(
    interaction: Interaction, current: str
) -> List[Choice[str]]:
    """
    Calls an autocomplete function depending on the entered config_key.
    """
    autocompleters = {"ENTRANCE.SOUND": user_entrance_sound_autocomplete}
    autocompleter = autocompleters[interaction.namespace.option]

    print(f"config_value_autocomplete: calling {autocompleter.__name__}")

    return autocompleter(interaction, current)


def user_entrance_sound_autocomplete(
    interaction: Interaction, current: str
) -> List[Choice[str]]:
    """
    Generates autocomplete options for the ENTRANCE.SOUND config key.
    """
    boards: List[str] = os.listdir(SOUNDDIR)
    all_sounds: Dict[str, List[str]] = {
        board: list(map(lambda x: x.split(".")[0], os.listdir(f"{SOUNDDIR}/{board}/")))
        for board in boards
    }  # These are all sounds, organized per board

    # TODO: Initially only suggest boards, because there are too many sounds to show them all
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
    interaction: Interaction, config_key: str, config_value: str
) -> None:
    """
    Set a user config value for the calling user.
    """
    # Only Members can set settings
    if not isinstance(interaction.user, Member):
        print("User not a member")
        await interaction.response.send_message("Heidi sagt: Komm in die Gruppe!")
        return

    member: Member = interaction.user

    client.user_config[config_key][member.name] = config_value
    client.write_user_config()

    await interaction.response.send_message(
        f"Ok, ich schreibe {member.name}={config_value} in mein fettes Gehirn!"
    )


# Commands ---------------------------------------------------------------------------------------


@client.tree.command(name="heidi", description="Heidi!")
async def heidi_exclaim(interaction: Interaction) -> None:
    """
    Print a random Heidi quote.
    """
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
async def magic_shell(interaction: Interaction, question: str) -> None:
    """
    Answer a yes/no question.
    """
    # Should be equal amounts of yes/no answers, to have a 50/50 chance.
    choices = [
        "Ja!",
        "Jo",
        "Total!",
        "Natürlich",
        "Klaro Karo",
        "Offensichtlich Sherlock",
        "Tom sagt Ja",

        "Nein!",
        "Nö.",
        "Nä.",
        "Niemals!",
        "Nur über meine Leiche du Hurensohn!",
        "In deinen Träumen.",
        "Tom sagt Nein"
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
async def choose(interaction: Interaction, option_a: str, option_b: str) -> None:
    """
    Select an answer from two options.
    """
    options = [option_a.strip(), option_b.strip()]
    await interaction.response.send_message(
        f"{options[0]} oder {options[1]}?\nHeidi sagt: {random.choice(options)}"
    )


# Sounds -----------------------------------------------------------------------------------------


SOUNDDIR: str = "/sounds" if DOCKER else "./heidi-sounds"


async def board_autocomplete(
    interaction: Interaction, current: str
) -> List[Choice[str]]:
    """
    Suggest a sound board.
    """
    boards: List[str] = os.listdir(SOUNDDIR)

    return [
        Choice(name=board, value=board)
        for board in boards
        if board.lower().startswith(current.lower())
    ]


async def sound_autocomplete(
    interaction: Interaction, current: str
) -> List[Choice[str]]:
    """
    Suggest a sound from an already selected board.
    """
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
async def say_voiceline(interaction: Interaction, board: str, sound: str) -> None:
    """
    Play a voiceline in the calling member's current voice channel.
    """
    # Only Members can access voice channels
    if not isinstance(interaction.user, Member):
        print("User not a member")
        await interaction.response.send_message("Heidi sagt: Komm in die Gruppe!")
        return

    member: Member = interaction.user

    await play_voice_line_for_member(interaction, member, board, sound)


# Contextmenu ------------------------------------------------------------------------------------


# Callable on members
@client.tree.context_menu(name="beleidigen")
async def insult(
    interaction: Interaction, member: Member
) -> None:  # with message: discord.Message this can be called on a message
    """
    Send an insult to a member via direct message.
    """
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
    interaction: Union[Interaction, None],
    voice_channel: VoiceChannel,
    board: str,
    sound: str,
) -> None:
    """
    Play a voice line in the specified channel.
    """
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
    interaction: Union[Interaction, None],
    member: Member,
    board: str,
    sound: str,
) -> None:
    """
    Play a voice line in the member's current channel.
    """
    # Member needs to be in voice channel to hear audio (Heidi needs to know the channel to join)
    if (
        member is None
        or member.voice is None
        or member.voice.channel is None
        or not isinstance(member.voice.channel, VoiceChannel)
    ):
        print("User not in (valid) voice channel!")
        if interaction is not None:
            await interaction.response.send_message("Heidi sagt: Komm in den Channel!")
        return

    voice_channel: VoiceChannel = member.voice.channel

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
