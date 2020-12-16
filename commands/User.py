from discord import Embed, Color, Member
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

    @command(name = '유저정보', usage = '유저정보 [유저]', aliases = ['정보', 'info'], help = '유저의 정보를 보여줍니다')
    async def user_info(self, ctx, user: Member = None):
        if not len(list(self.bot.userCollection.find({'discordID': str(ctx.author.id)}))):
            await ctx.send(embed = Embed(title = '가입이 안되있습니다', color = Color.red()))
            return

        if not user:
            user = ctx.author

        user_db = self.bot.userCollection.find_one({'discordID': str(user.id)})
        if not user_db:
            await ctx.send(embed = Embed(title = '가입이 되지 않은 유저입니다', color = Color.red()))
            return

        embed = Embed(
            title = f'{user.name}님 정보',
            color = Color.green()
        )

        following = user_db["following"]
        embed.add_field(name = '팔로우중', value = f'{", ".join(map(lambda u: u.mention, map(lambda id: self.bot.get_user(int(id)), following[:2] if len(following) >= 2 else following)))} ({len(following)}명)')

        followers = len(list(filter(lambda u: str(user.id) in u["following"], self.bot.userCollection.find())))
        embed.add_field(name = '팔로워', value = f'{followers}명')

        hearts = len(list(filter(lambda u: str(user.id) in u["hearts"], self.bot.postCollection.find())))
        embed.add_field(name = '하트', value = f'{hearts}개')

        posts = len(list(self.bot.postCollection.find({'authorID': str(user.id)})))
        embed.add_field(name = '작성 글', value = f'{posts}개')

        await ctx.send(embed = embed)

    @command(name = '팔로우', usage = '팔로우 [유저]', aliases = ['follow', '팔로우취소'], help = '유저를 팔로우합니다')
    async def follow(self, ctx, user: Member):
        if not len(list(self.bot.userCollection.find({'discordID': str(ctx.author.id)}))):
            await ctx.send(embed = Embed(title = '가입이 안되있습니다', color = Color.red()))
            return

        if not user:
            await ctx.send(embed = Embed(title = '유저를 맨션해주세요', color = Color.red()))
            return

        if not self.bot.userCollection.find_one({'discordID': str(user.id)}):
            await ctx.send(embed = Embed(title = '가입이 되지 않은 유저입니다', color = Color.red()))
            return

        if user == ctx.author:
            await ctx.send(embed = Embed(title = '나 자신은 영원한 인생의 친구입니다(라고 쓰라고 디켑님이 시킴)', color = Color.green()))
            return

        user_db = self.bot.userCollection.find_one({'discordID': str(ctx.author.id)})
        if str(user.id) in user_db["following"]:
            user_db['following'].remove(str(user.id))
            self.bot.userCollection.update({'discordID': str(ctx.author.id)}, {'$set': {'following': user_db["following"]}})
            await ctx.send(embed = Embed(title = '팔로우 취소를 했습니다', color = Color.green()))
        else:
            self.bot.userCollection.update({'discordID': str(ctx.author.id)}, {'$set': {'following': user_db["following"] + [str(user.id)]}})
            await ctx.send(embed = Embed(title = '팔로우를 했습니다', color = Color.green()))