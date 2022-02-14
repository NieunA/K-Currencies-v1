import discord
from discord.ext import commands, tasks
import asyncio
import json
import datetime
from modules import accessToDB

with open("data/mainData.json", "r") as f:
    mainData = json.load(f)

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.changePre.start()

    @tasks.loop(seconds=30)
    async def changePre(self):
        await self.bot.change_presence(activity=discord.Game(f"!KC 도움 | {len(self.bot.guilds)}곳의 서버에서 돈 계산"))

    @changePre.before_loop
    async def before_loop_start(self):
        await self.bot.wait_until_ready()

    """
    @tasks.loop(hours=24)
    async def deleteG(self):
        with open("../data/serverToDel.json", 'r') as f:
            data = json.load(f)  # [[serverID, 1632300716.1497636], [serverID, 1632300756.174678], ...]
        while True:
            # compare earliest request with 30 days ago
            if datetime.date.today() - datetime.date.fromtimestamp(data[0][1]) > datetime.timedelta(days=30):
                await accessToDB.run(f"DROP TABLE IF EXISTS {data[0][0]};")
                await accessToDB.run(f"DELETE FROM 'serversData' WHERE serverID='?'", (data[0][0], ))
                del data[0]
            else: break
        with open("../data/serverToDel.json", 'w') as f:
            json.dump(data, f) 
    """


def setup(bot):
    bot.add_cog(Tasks(bot))