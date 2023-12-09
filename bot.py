# Example: https://github.com/Rapptz/discord.py/blob/master/examples/app_commands/basic.py

import random, logging
from discord.app_commands import Choice
from typing import Dict, List, Optional, Union, Callable, Any
from rich.traceback import install

from heidi_client import *

# Install rich traceback
install(show_locals=True)


# @todo Only post in heidi-spam channel
# @todo yt-dlp music support
# @todo Somehow upload voicelines more easily (from discord voice message?)


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
    }  # These are all sounds, organized per board, without file extension

    # @todo Initially only suggest boards, because there are too many sounds to show them all
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
        "Jetzt sei doch mal sexy!",
        "Stell dich nicht so an!",
        "Models müssen da halt durch!",
        "Heul doch nicht!"
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


# ------------------------------------------------------------------------------------------------


# Used to start the bot locally, for docker the variables have to be set when the container is run
TOKEN: str = os.getenv("DISCORD_TOKEN") or ""

# Start client if TOKEN valid
if TOKEN != "":
    print(f"Running client with DOCKER={DOCKER}")
    client.run(TOKEN, log_handler=handler)
else:
    print("DISCORD_TOKEN not found, exiting...")
