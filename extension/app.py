from discord import Status, Embed, Color
from discord.ext.commands import Bot

from discordex.utils.node import File

from asyncio import sleep
from pymongo import MongoClient
from re import compile

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

    async def check_registered(self, ctx):
        if not len(list(self.userCollection.find({'discordID': str(ctx.author.id)}))):
            await ctx.send(embed = Embed(title = '가입이 안되있습니다', color = Color.red()))
            return False
        return True

    async def check_owner(self, ctx):
        if str(ctx.author.id) not in self.config.owners:
            await ctx.send(embed = Embed(title = '오너가 아닙니다', color = Color.red()))
            return False
        return True

    def format_post(self, string: str):
        url_compiled = compile(r'!\[.+\]\((?P<url>.+)\)')
        for i in url_compiled.finditer(string):
            string = string.replace(i.group(), f'[사진]({i.group("url")})')
        return string