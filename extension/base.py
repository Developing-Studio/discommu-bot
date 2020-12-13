from discord.ext.commands import Cog

from .app import Discommu


class BaseEvent:
    bot: Discommu

    def __init__(self, bot):
        self.bot: Discommu = bot


class BaseCommand(Cog):
    bot: Discommu

    def __init__(self, bot):
        self.bot: Discommu = bot
