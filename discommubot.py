from discord import Game

from extension import Discommu

bot = Discommu()

@bot.event
async def on_ready():
    print(f'{bot.user.name} 준비 완료')
    await bot.change_presence_loop(presences = [lambda: Game(f'{len(list(bot.userCollection.find()))}명의 유저가 있어요..!')])

bot.run()