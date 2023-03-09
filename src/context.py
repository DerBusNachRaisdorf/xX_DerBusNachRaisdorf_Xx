import discord
import raisdorf_gpt

from settings import Settings
from utility.parsing import tokenize_argv
from utility.bifo import StrBIFO


class Context:

    def __init__(self, message, client, settings, deutschlehrer: StrBIFO, raisgpt: raisdorf_gpt.RaisdorfGPT):
        self.message: discord.Message = message
        self.client: discord.Client = client
        # tokenize content
        self.argv: list[str] = tokenize_argv(message.content)
        # save command
        self.command: str = self.argv[0][1:].lower() if len(self.argv) and self.argv[0][0] == '!' else None
        self.settings: Settings = settings
        self.deutschlehrer = deutschlehrer
        self.raisdorf_gpt = raisgpt
