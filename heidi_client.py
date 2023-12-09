import configparser
from discord import app_commands, Message, VoiceState

from heidi_constants import *
from heidi_helpers import *


class HeidiClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(status="Nur eine kann GNTM werden!", intents=intents)

        # Separate object that keeps all application command state
        self.tree = app_commands.CommandTree(self)

        # Handle persistent user configuration
        self.user_config = configparser.ConfigParser()
        if not os.path.exists(f"{CONFIGPATH}/{USERCONFIGNAME}"):
            open(f"{CONFIGPATH}/{USERCONFIGNAME}", "x")
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
