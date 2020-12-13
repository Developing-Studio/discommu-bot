from discord import Embed, Color
from discord.ext.commands import command

from EZPaginator import Paginator

from extension import BaseCommand

def divide(l: list, n: int = 5):
    return [l[i * n:(i + 1) * n] for i in range((len(l) + n - 1) // n )] 

class Command(BaseCommand):
    name = '일반'
    description = '가입 없이 사용될수 있는 일반 명령어들입니다'


    @command(name = '도움', aliases = ['help'], help = '도움 명령어입니다')
    async def 도움(self, ctx):
        embeds = [
            Embed(title = '도움', description = '이모지로 페이지를 넘기세요', color = Color.green())
        ]

        for i in range(len(self.bot.cogs)):
            cog = self.bot.cogs[list(self.bot.cogs.keys())[i]]
            embeds[0].add_field(name = f'{i + 1}페이지  |  {cog.name}', value = f'`{cog.description}`', inline = True)

            for cmds in divide(cog.get_commands(), 10):
                embed = Embed(title = f'{cog.name} 도움', color = Color.green())
                embed.set_footer(text = f'Page {i + 1}')
                for cmd in cmds: embed.add_field(name = f'{self.bot.command_prefix}{cmd.name}' if not cmd.usage else f'{self.bot.command_prefix}{cmd.usage}', value = cmd.help, inline = True)
                embeds.append(embed)

        msg = await ctx.send(embed = embeds[0])
        await Paginator(self.bot, msg, embeds = embeds).start()