from discord import Status
from discord.ext.commands import Bot

from discordex.utils.node import File

from asyncio import sleep
from pymongo import MongoClient

from .cmdmanager import gather_events, gather_commands

class Discommu(Bot):
    def __init__(self, **kwargs):
        self.config = File('config.json')
        self.db = MongoClient(f'mongodb+srv://admin:{self.config.db.password}@{self.config.db.url}/discommu?retryWrites=true&w=majority')['discommu']

        self.userCollection = self.db['users']
        self.postCollection = self.db['posts']
        self.categoryCollection = self.db['categories']

        super().__init__(self.config.command_prefix, **kwargs)
        self.remove_command('help')

        gather_events(self)
        gather_commands(self)

    def run(self):
        super().run(self.config.token)

    async def change_presence_loop(self, *, presences, wait: int = 60, status = Status.online, **kwargs):
        await self.wait_until_ready()

        while not self.is_closed():
            for _presence in presences:
                presence = _presence() if callable(_presence) else _presence
                await self.change_presence(status=status, activity=presence, **kwargs)
                await sleep(wait)