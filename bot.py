# Example: https://github.com/Rapptz/discord.py/blob/master/examples/app_commands/basic.py

from ast import Call
import random, logging
from discord import DMChannel
from discord.app_commands import Choice
from typing import Awaitable, Dict, List, Optional, Union, Callable, Any
from rich.traceback import install

from heidi_client import *

# Install rich traceback
install(show_locals=True)


# @todo yt-dlp music support


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


class EntranceSoundSoundSelect(discord.ui.Select):
    def __init__(self, board: str, on_sound_select_callback):
        self.board = board
        self.on_sound_select_callback = on_sound_select_callback

        options: List[discord.SelectOption] = [
            discord.SelectOption(label=sound.split(".")[0], value=sound)
            for sound in os.listdir(f"{SOUNDDIR}/{board}")
        ]

        super().__init__(
            placeholder="Select Sound", min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: Interaction):
        await self.on_sound_select_callback(interaction, self.board, self.values[0])


class EntranceSoundSoundView(discord.ui.View):
    def __init__(self, board: str, on_sound_select_callback):
        super().__init__(timeout=600)

        self.add_item(EntranceSoundSoundSelect(board, on_sound_select_callback))


class EntranceSoundBoardSelect(discord.ui.Select):
    def __init__(self, on_sound_select_callback):
        self.on_sound_select_callback = on_sound_select_callback

        options: List[discord.SelectOption] = [
            discord.SelectOption(label=board, value=board)
            for board in os.listdir(f"{SOUNDDIR}")
        ]

        super().__init__(
            placeholder="Select Board", min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.send_message(
            f"Welchen sound willst du?",
            view=EntranceSoundSoundView(self.values[0], self.on_sound_select_callback),
            ephemeral=True,
        )


class EntranceSoundBoardView(discord.ui.View):
    def __init__(self, on_sound_select_callback):
        super().__init__(timeout=600)

        self.add_item(EntranceSoundBoardSelect(on_sound_select_callback))


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


@client.tree.command(
    name="userconfig",
    description="User-spezifische Heidi-Einstellungen (Heidi merkt sie sich in ihrem riesigen Gehirn).",
)
@app_commands.rename(config_key="option")
@app_commands.describe(config_key="Die Option, welche du ändern willst.")
@app_commands.autocomplete(config_key=user_config_key_autocomplete)
@enforce_channel(HEIDI_SPAM_ID)
async def user_config(interaction: Interaction, config_key: str) -> None:
    """
    Set a user config value for the calling user.
    """
    # Only Members can set settings
    if not isinstance(interaction.user, Member):
        print("User not a member")
        await interaction.response.send_message(
            "Heidi sagt: Komm in die Gruppe!", ephemeral=True
        )
        return

    member: Member = interaction.user

    async def on_sound_select_callback(interaction, board: str, sound: str):
        """
        This function is called, when an EntrySoundSoundSelect option is selected.
        """
        client.user_config[config_key][member.name] = f"{board}/{sound}"
        client.write_user_config()

        await interaction.response.send_message(
            f"Ok, ich schreibe {member.name}={board}/{sound} in mein fettes Gehirn!",
            ephemeral=True,
        )

    # Views for different user config options are defined here
    views = {"ENTRANCE.SOUND": (EntranceSoundBoardView, on_sound_select_callback)}

    view, select_callback = views[config_key]

    await interaction.response.send_message(
        f"Aus welchem Soundboard soll dein sound sein?",
        view=view(select_callback),
        ephemeral=True,
    )


# Commands ---------------------------------------------------------------------------------------


@client.tree.command(name="heidi", description="Heidi!")
@enforce_channel(HEIDI_SPAM_ID)
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
        "Jetzt sei doch mal sexy!",
        "Stell dich nicht so an!",
        "Models müssen da halt durch!",
        "Heul doch nicht!",
    ]
    await interaction.response.send_message(random.choice(messages))


@client.tree.command(name="miesmuschel", description="Was denkt Heidi?")
@app_commands.rename(question="frage")
@app_commands.describe(question="Heidi wird es beantworten!")
@enforce_channel(HEIDI_SPAM_ID)
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
        "Tom sagt Nein",
    ]
    question = question.strip()
    question_mark = "" if question[-1] == "?" else "?"
    await interaction.response.send_message(
        f"{question}{question_mark}\nHeidi sagt: {random.choice(choices)}"
    )


# @todo Allow , separated varargs, need to parse manually as slash commands don't support varargs
@client.tree.command(name="wähle", description="Heidi trifft die Wahl!")
@app_commands.rename(option_a="entweder")
@app_commands.describe(option_a="Ist es vielleicht dies?")
@app_commands.rename(option_b="oder")
@app_commands.describe(option_b="Oder doch eher das?")
@enforce_channel(HEIDI_SPAM_ID)
async def choose(interaction: Interaction, option_a: str, option_b: str) -> None:
    """
    Select an answer from two options.
    """
    options = [option_a.strip(), option_b.strip()]
    await interaction.response.send_message(
        f"{options[0]} oder {options[1]}?\nHeidi sagt: {random.choice(options)}"
    )


# Sounds -----------------------------------------------------------------------------------------


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
    sounds: List[str] = os.listdir(f"{SOUNDDIR}/{board}/")

    return [
        Choice(name=sound.split(".")[0], value=sound)
        for sound in sounds
        if sound.lower().startswith(current.lower())
    ]


@client.tree.command(
    name="sag", description="Heidi drückt den Knopf auf dem Soundboard."
)
@app_commands.describe(sound="Was soll Heidi sagen?")
@app_commands.autocomplete(board=board_autocomplete)
@app_commands.autocomplete(sound=sound_autocomplete)
@enforce_channel(HEIDI_SPAM_ID)
async def say_voiceline(interaction: Interaction, board: str, sound: str) -> None:
    """
    Play a voiceline in the calling member's current voice channel.
    """
    # Only Members can access voice channels
    if not isinstance(interaction.user, Member):
        print("User not a member")
        await interaction.response.send_message(
            "Heidi sagt: Komm in die Gruppe!", ephemeral=True
        )
        return

    member: Member = interaction.user

    await play_voice_line_for_member(interaction, member, board, sound)


class InstantButton(discord.ui.Button):
    def __init__(self, label: str, board: str, sound: str):
        super().__init__(style=discord.ButtonStyle.red, label=label)

        self.board = board
        self.sound = sound

    async def callback(self, interaction: Interaction):
        """
        Handle a press of the button.
        """
        if not isinstance(interaction.user, Member):
            await interaction.response.send_message(
                "Heidi mag keine discord.User, nur discord.Member!", ephemeral=True
            )
            return

        await play_voice_line_for_member(
            interaction, interaction.user, self.board, self.sound
        )


class InstantButtonsView(discord.ui.View):
    def __init__(self, board: str, timeout=None):
        super().__init__(timeout=timeout)

        sounds = os.listdir(f"{SOUNDDIR}/{board}")
        for sound in sounds:
            self.add_item(InstantButton(sound.split(".")[0], board, sound))


@client.tree.command(
    name="instantbuttons", description="Heidi malt Knöpfe für Sounds in den Chat."
)
@app_commands.describe(board="Welches Soundboard soll knöpfe bekommen?")
@app_commands.autocomplete(board=board_autocomplete)
@enforce_channel(HEIDI_SPAM_ID)
async def soundboard_buttons(interaction: Interaction, board: str) -> None:
    await interaction.response.send_message(
        f"Soundboard: {board.capitalize()}", view=InstantButtonsView(board)
    )


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
        await interaction.response.send_message(
            "Heidi sagt: Gib mal DM Nummer süße*r!", ephemeral=True
        )
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
        "Anzeige ist raus!", ephemeral=True
    )  # with ephemeral = True only the caller can see the answer


# ------------------------------------------------------------------------------------------------


# Used to start the bot locally, for docker the variables have to be set when the container is run
TOKEN: str = os.getenv("DISCORD_TOKEN") or ""

# Start client if TOKEN valid
if TOKEN != "":
    print(f"Running client with DOCKER={DOCKER}")
    client.run(TOKEN, log_handler=handler)
else:
    print("DISCORD_TOKEN not found, exiting...")
