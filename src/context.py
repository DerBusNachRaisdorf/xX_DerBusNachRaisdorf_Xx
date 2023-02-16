import discord

from settings import Settings
from utility.parsing import tokenize_argv


class Context:

    def __init__(self, message, client, settings):
        self.message: discord.Message = message
        self.client: discord.Client = client
        # tokenize content
        self.argv: list[str] = tokenize_argv(message.content)
        # save command
        self.command: str = self.argv[0].lower()
        self.settings: Settings = settings
