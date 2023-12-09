import os
import discord
from dotenv import load_dotenv

# This is run when this file is imported
load_dotenv()

print("Debug: Importing heidi_constants.py")


# ================================================================================================ #
# ================================================================================================ #
# NOTE: Always set this correctly:
DOCKER = os.getenv("DOCKER") == "True"
# ================================================================================================ #
# ================================================================================================ #

# Constants
CONFIGPATH = "/config" if DOCKER else "."
USERCONFIGNAME = "Heidi_User.conf"

SOUNDDIR: str = "/sounds" if DOCKER else "./heidi-sounds"

# IDs of the servers Heidi is used on
LINUS_GUILD = discord.Object(id=431154792308408340)
TEST_GUILD = discord.Object(id=821511861178204161)
