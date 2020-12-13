from discord.ext.commands import Cog


class BaseEvent:
    def __init__(self, bot):
        self.bot = bot


class BaseCommand(Cog):
    def __init__(self, bot):
        self.bot = bot
