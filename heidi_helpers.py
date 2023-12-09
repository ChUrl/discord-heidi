import asyncio
from typing import Union

import discord
from discord import Interaction, VoiceChannel, Member

from heidi_constants import *

print("Debug: Importing heidi_helpers.py")


# @todo Normalize volume when playing
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
        open(f"{SOUNDDIR}/{board}/{sound}")
    except IOError:
        print(f"Error: Invalid soundfile {SOUNDDIR}/{board}/{sound}!")
        if interaction is not None:
            await interaction.response.send_message(
                f'Heidi sagt: "{board}/{sound}" kanninich finden bruder'
            )
        return

    if interaction is not None:
        await interaction.response.send_message(f'Heidi sagt: "{board}/{sound}"')

    audio_source = discord.FFmpegPCMAudio(
        f"{SOUNDDIR}/{board}/{sound}"
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
