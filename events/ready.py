from discord import Game

from extension import BaseEvent


class Event(BaseEvent):
    async def trigger(self):
        print(f'''
        ==========================================
        BotID: {self.bot.user.id}
        BotName: {self.bot.user}
        BotToken: {self.bot.config.token[:10] + "*" * (len(self.bot.config.token) - 10)}
        ==========================================
        ''')

        await self.bot.change_presence_loop(presences = [lambda: Game(f'{len(list(self.bot.userCollection.find()))}명의 유저가 있어요..!')])