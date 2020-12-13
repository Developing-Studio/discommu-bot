from discord import Embed, Color

from discord.errors import (
    Forbidden
)
from discord.ext.commands.errors import (
    CommandNotFound, BotMissingPermissions, NoPrivateMessage,
    UserNotFound, MissingPermissions, BadArgument,
    MissingRequiredArgument, ConversionError, NotOwner
)

from extension import BaseEvent


class Event(BaseEvent):
    async def trigger(self, ctx, e):
        if isinstance(e, CommandNotFound):
            cmd = ctx.message.content[len(self.bot.config.command_prefix): ctx.message.content.index(' ') if ' ' in ctx.message.content else len(ctx.message.content)]
            await ctx.send(embed = Embed(title = f'{cmd} 명령어를 찾을수 없습니다', color = Color.red()))

        elif isinstance(e, NotOwner):
            await ctx.send(embed = Embed(title = '오너가 아닙니다', color = Color.red()))

        elif isinstance(e, NoPrivateMessage):
            await ctx.send(embed = Embed(title = 'DM에서는 사용 불가한 명령어입니다', color = Color.red()))
        
        elif isinstance(e, (ConversionError, MissingRequiredArgument, BadArgument)):
            await ctx.send(embed = Embed(title = '양식이 잘못되었습니다', color = Color.red()))
        
        elif isinstance(e, BotMissingPermissions):
            try: await ctx.send(embed = Embed(title = '봇에게 권한이 부족합니다', color = Color.red()))
            except: return
        
        elif isinstance(e, MissingPermissions):
            try: await ctx.send(embed = Embed(title = '유저에게 권한이 부족합니다', color = Color.red()))
            except: return

        elif isinstance(e, Forbidden):
            try: await ctx.send(embed = Embed(title = '권한이 부족합니다', color = Color.red()))
            except: return
        
        elif isinstance(e, UserNotFound):
            await ctx.send(embed = Embed(title = '없는 유저입니다', color = Color.red()))
        
        else:
            await ctx.send(embed = Embed(title = 'ERRrOR가 발생했습니다', description = f'```\n{te.__name__}: {str(te)} ({repr(te)})\n```', color = Color.red()))