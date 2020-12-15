from discord import Embed, Color
from discord.ext.commands import command, group, MissingRequiredArgument

from os.path import splitext
from asyncio import TimeoutError
from EZPaginator import Paginator
from re import sub

from extension import BaseCommand

def divide(l: list, n: int = 5):
    return [l[i * n:(i + 1) * n] for i in range((len(l) + n - 1) // n )] 

class Command(BaseCommand):
    name = '글'
    description = '글 관련 명령어들입니다'


    def __init__(self, bot):
        super().__init__(bot)

        for cmd in self.get_commands():
            cmd.add_check(self.bot.check_registered)
            if 'commands' in dir(cmd):
                for child_cmd in cmd.commands:
                    child_cmd.add_check(self.bot.check_registered)

    @group(name = '글', aliases = ['post'], help = '글 명령어 그룹입니다')
    async def post(self, ctx):
        if not ctx.invoked_subcommand:
            await self.list_post(ctx)

    @post.command(name = '작성', usage = '작성 [제목]', aliases = ['write'], help = '글을 작성합니다')
    async def add_post(self, ctx, *, title: str):
        if len(list(self.bot.postCollection.find({'title': title}))):
            await ctx.send(embed = Embed(title = '같은 이름을 가진 글이 이미 존재합니다', color = Color.red()))
            return

        msg = await ctx.send(embed = Embed(title = '카테고리', description = '이 글의 카테고리를 무엇으로 할까요?', color = Color.orange()))

        try:
            category = (await self.bot.wait_for('message', check = (lambda m: (m.channel == ctx.channel) and (m.author == ctx.author)), timeout = 60)).content
        except TimeoutError:
            await msg.edit(embed = Embed(title = '글 작성이 취소되었습니다', color = Color.green()))
            return

        if not len(list(self.bot.categoryCollection.find({'name': category}))):
            await ctx.send(embed = Embed(title = '그런 이름을 가진 카테고리가 없습니다', color = Color.red()))
            return

        msg = await ctx.send(embed = Embed(title = '태그', description = '이 글의 태그를 무엇으로 할까요?(`/`로 분리하면 여러개가 됩니다)', color = Color.orange()))

        try:
            tags = (await self.bot.wait_for('message', check = (lambda m: (m.channel == ctx.channel) and (m.author == ctx.author)), timeout = 60)).content.split('/')
        except TimeoutError:
            await msg.edit(embed = Embed(title = '글 작성이 취소되었습니다', color = Color.green()))
            return

        msg = await ctx.send(embed = Embed(title = '내용', description = '이 글의 내용을 작성해주세요', color = Color.orange()))

        try:
            msg = (await self.bot.wait_for('message', check = (lambda m: (m.channel == ctx.channel) and (m.author == ctx.author)), timeout = 600))
        except TimeoutError:
            await msg.edit(embed = Embed(title = '글 작성이 취소되었습니다', color = Color.green()))
            return

        content = msg.content
        if msg.attachments:
            if splitext(msg.attachments[0].filename)[1][1:] in ['png', 'jpg', 'jpeg', 'gif']:
                content += f'\n![Image]({msg.attachments[0].url})'

        try:
            msg = await ctx.send(embed = Embed(title = '글 작성', description = f'**제목:** `{title}`\n**내용:** `{content}`\n**카테고리:** `{category}`\n**태그 목록:** {"**,** ".join([f"`{tag}`" for tag in tags])}', color = Color.orange()))
        except:
            await ctx.send(embed = Embed(title = '글 작성', description = '정말로 글을 작성하시겠습니까?', color = Color.orange()))

        await msg.add_reaction('⭕')
        await msg.add_reaction('❌')

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check = (lambda r, u: (str(r.emoji) in ('⭕', '❌')) and (r.message.channel == ctx.channel) and (u == ctx.author)), timeout = 30)
        except TimeoutError:
            await msg.edit(embed = Embed(title = '글 작성을 취소했습니다', color = Color.green()))
            return

        if str(reaction) == '❌':
            await msg.edit(embed = Embed(title = '글 작성을 취소했습니다', color = Color.green()))
            return

        self.bot.postCollection.insert({
            'authorID': str(ctx.author.id),
            'title': title,
            'content': content,
            'category': category,
            'tag': tags,
            'hearts': [],
            'comments': []
        })
        await msg.edit(embed = Embed(title = '글을 작성했습니다', color = Color.green()))

    @post.command(name = '삭제', usage = '삭제 [제목]', aliases = ['del', 'delete', 'remove'], help = '글을 삭제합니다')
    async def del_post(self, ctx, *, title: str):
        if not len(list(self.bot.postCollection.find({'title': title}))):
            await ctx.send(embed = Embed(title = '그런 제목을 가진 글이 없습니다', color = Color.red()))
            return

        post = self.bot.postCollection.find_one({'title': title})
        if post['authorID'] != str(ctx.author.id):
            await ctx.send(embed = Embed(title = '님이 만드신 글만 삭제 가능합니다', color = Color.red()))
            return

        msg = await ctx.send(embed = Embed(title = '글 삭제', description = f'정말 글 `{title}`를 삭제하시겠습니까?', color = Color.orange()))

        await msg.add_reaction('⭕')
        await msg.add_reaction('❌')

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check = (lambda r, u: (str(r.emoji) in ('⭕', '❌')) and (r.message.channel == ctx.channel) and (u == ctx.author)), timeout = 30)
        except TimeoutError:
            await msg.edit(embed = Embed(title = '글 삭제를 취소했습니다', color = Color.green()))
            return

        if str(reaction) == '❌':
            await msg.edit(embed = Embed(title = '글 삭제를 취소했습니다', color = Color.green()))
            return

        self.bot.postCollection.remove({
            'authorID': str(ctx.author.id),
            'title': title
        })
        await msg.edit(embed = Embed(title = '글을 삭제했습니다', color = Color.green()))

    @post.command(name = '수정', usage = '수정 [제목]', aliases = ['edit', 'update'], help = '글 내용을 수정합니다')
    async def edit_post(self, ctx, *, title: str):
        if not len(list(self.bot.postCollection.find({'title': title}))):
            await ctx.send(embed = Embed(title = '그런 제목을 가진 글이 없습니다', color = Color.red()))
            return

        post = self.bot.postCollection.find_one({'title': title})
        if post['authorID'] != str(ctx.author.id):
            await ctx.send(embed = Embed(title = '님이 만드신 글만 수정 가능합니다', color = Color.red()))
            return

        await ctx.send(embed = Embed(title = '글 수정', description = f'글 `{title}`의 내용을 수정하세요? (10분이 지나면 자동으로 취소됩니다)', color = Color.orange()))

        try:
            msg = await self.bot.wait_for('message', check = (lambda m: (m.channel == ctx.channel) and (m.author == ctx.author)), timeout = 600)
        except TimeoutError:
            await msg.edit(embed = Embed(title = '글 수정을 취소했습니다', color = Color.green()))
            return

        content = msg.content
        if msg.attachments:
            if splitext(msg.attachments[0].filename)[1][1:] in ['png', 'jpg', 'jpeg', 'gif']:
                content += f'\n![Image]({msg.attachments[0].url})'

        msg = await ctx.send(embed = Embed(title = '글 수정', description = f'정말 카테고리 `{title}`를 수정하겠습니까?', color = Color.orange()))

        await msg.add_reaction('⭕')
        await msg.add_reaction('❌')

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check = (lambda r, u: (str(r.emoji) in ('⭕', '❌')) and (r.message.channel == ctx.channel) and (u == ctx.author)), timeout = 30)
        except TimeoutError:
            await msg.edit(embed = Embed(title = '글 수정을 취소했습니다', color = Color.green()))
            return

        if str(reaction) == '❌':
            await msg.edit(embed = Embed(title = '글 수정을 취소했습니다', color = Color.green()))
            return

        self.bot.postCollection.update_one({
            'authorID': str(ctx.author.id),
            'title': title
        },
        {
            '$set': {
                'content': content
            }
        })
        await msg.edit(embed = Embed(title = '글 내용을 수정했습니다', color = Color.green()))

    @post.command(name = '보기', usage = '보기 [제목]', help = '글을 보여줍니다')
    async def info_post(self, ctx, *, title: str):
        if not len(list(self.bot.postCollection.find({'title': title}))):
            await ctx.send(embed = Embed(title = '그런 제목을 가진 글이 없습니다', color = Color.red()))
            return

        post = self.bot.postCollection.find_one({'title': title})
        await ctx.send(embed = Embed(
            title = title,
            description = f'{self.bot.format_post(post["content"])}\n\n**작성자:** {self.bot.get_user(int(post["authorID"]))}\n**카테고리:** `{post["category"]}`\n**태그:** {"**,** ".join([f"`{tag}`" for tag in post["tag"]])}\n\n:heart: `{len(post["hearts"])}`\n:speech_balloon: `{len(post["comments"])}`',
            color = Color.green()
        ))

    @post.command(name = '검색', aliases = ['search'], help = '글을 검색합니다(검색어가 없으면 모두 다 표시)')
    async def list_post(self, ctx, *, query: str = None):
        if not query:
            postlist = list(self.bot.postCollection.find())
            title = '글 목록'
            no_description = '글이 없습니다'
        else:
            postlist = []
            _idlist = []

            _postlist = list(self.bot.postCollection.find({'title': {'$regex': f'.*{query}.*'}}))
            _postlist.extend(list(self.bot.postCollection.find({'content': {'$regex': f'.*{query}.*'}})))

            for data in _postlist:
                if data['_id'] in _idlist:
                    continue
                _idlist.append(data['_id'])
                postlist.append(data)

            title = f'"{query}" 검색 결과'
            no_description = '검색 결과가 없습니다'

        embeds = []

        for categories in divide(postlist, 10):
            embed = Embed(
                title = title,
                color = Color.green()
            )

            for post in categories:
                embed.add_field(name = post["title"], value = f'by `{self.bot.get_user(int(post["authorID"]))}` :heart: `{len(post["hearts"])}` :speech_balloon: `{len(post["comments"])}`', inline = False)

            embeds.append(embed)

        if embeds:
            msg = await ctx.send(embed = embeds[0])
            await Paginator(self.bot, msg, embeds = embeds).start()
        else:
            await ctx.send(embed = Embed(title = title, description = no_description, color = Color.green()))