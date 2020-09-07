import discord
from discord.ext import commands, tasks
import asyncio


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.changePre.start()

    @tasks.loop(seconds=30)
    async def changePre(self):
        await self.bot.change_presence(activity=discord.Game(f"{len(self.bot.guilds)}곳의 서버에서 돈 계산"))


def setup(bot):
    bot.add_cog(Tasks(bot))