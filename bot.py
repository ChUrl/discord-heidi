#!/usr/bin/env python3

import os
import re
import random
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")  # Zocken mit Heidi

client = discord.Client()


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")

    guild = discord.utils.get(client.guilds, name=GUILD)
    print(f"{client.user} is connected to the following guild:")
    print(f"{guild.name} (id: {guild.id})")


heidis_girls = ["Ana", "Soulin", "Alysha", "Luca", "Maria"]

cmd_prefix = "^Heidi, "
cmd_listing = {"HEIDI!": "Ich sage enthusiastisch meinen Namen", "*?": "Ich beantworte eine Frage"}


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    ### Passive Actions ----------------------------------------------------------------------------

    # React to girls message
    if message.author.nick in heidis_girls:
        await message.add_reaction("❤")

    ### Commands -----------------------------------------------------------------------------------

    # Help: Heidi, Hilfe
    if re.match(cmd_prefix + "Hilfe$", message.content):
        response = "Befehle für Heidi:\n" + str(cmd_listing)
        await message.channel.send(response)

    # Say my name: Heidi, Heidi!
    elif re.match(cmd_prefix + "Heidi!$", message.content):
        response = "HEIDI!"
        await message.channel.send(response)

    # Magic Conch Shell
    elif re.match(cmd_prefix + ".+\\?$", message.content):
        choices = ["Ja!", "Jo.", "Total!", "Hab ich selbst gesehen!", "Nein!", "Nö.", "Nä.", "Niemals!", "Twitch Prime?"]
        response = choices[random.randint(0, len(choices) - 1)]
        await message.channel.send(response)


client.run(TOKEN)
