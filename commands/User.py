from discord import Embed, Color
from discord.ext.commands import command

from asyncio import TimeoutError

from extension import BaseCommand

class Command(BaseCommand):
    name = '유저'
    description = '유저 관련 명령어들입니다'


    @command(name = '가입', aliases = ['register'], help = '서비스에 가입합니다')
    async def register(self, ctx):
        if len(list(self.bot.userCollection.find({'discordID': str(ctx.author.id)}))):
            await ctx.send(embed = Embed(title = '이미 가입되셨습니다', color = Color.red()))
            return

        msg = await ctx.send(embed = Embed(title = '정말 가입하시겠습니까?', description = 'DB에는 사용자의 정보중 `ID`만 저장합니다\n정말 가입을 하실거면 `네넹` 이라고 보내주세요(30초 동안 `네넹`을 안보내시면 자동으로 취소됩니다)', color = Color.orange()))

        try:
            await self.bot.wait_for('message', check = (lambda m: (m.content == '네넹') and (m.channel == ctx.channel) and (m.author == ctx.author)), timeout = 30)
        except TimeoutError:
            await msg.edit(embed = Embed(title = '가입을 취소했습니다', color = Color.green()))
            return

        self.bot.userCollection.insert({
            'discordID': str(ctx.author.id),
            'point': 0,
            'permissions': [],
            'following': []
        })
        await msg.edit(embed = Embed(title = '가입을 했습니다', color = Color.green()))

    @command(name = '탈퇴', aliases = ['unregister'], help = '서비스에 탈퇴합니다')
    async def unregister(self, ctx):
        if not len(list(self.bot.userCollection.find({'discordID': str(ctx.author.id)}))):
            await ctx.send(embed = Embed(title = '가입이 안되있습니다', color = Color.red()))
            return

        msg = await ctx.send(embed = Embed(title = '정말 탈퇴하시겠습니까?', description = '정말 가입을 하실거면 `네넹` 이라고 보내주세요(30초 동안 `네넹`을 안보내시면 자동으로 취소됩니다)', color = Color.orange()))

        try:
            await self.bot.wait_for('message', check = (lambda m: (m.content == '네넹') and (m.channel == ctx.channel) and (m.author == ctx.author)), timeout = 30)
        except TimeoutError:
            await msg.edit(embed = Embed(title = '탈퇴를 취소했습니다', color = Color.green()))
            return

        self.bot.userCollection.remove({'discordID': str(ctx.author.id)})
        await msg.edit(embed = Embed(title = '탈퇴를 했습니다', color = Color.green()))