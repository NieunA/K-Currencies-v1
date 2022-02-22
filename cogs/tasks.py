from typing import Union

import discord
from discord.ext import commands, tasks
from discord.ext.commands import AutoShardedBot, Bot


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=30)
    async def update_activity(self):
        await self.bot.change_presence(activity=discord.Game(f"!KC 도움 | {len(self.bot.guilds)}곳의 서버에서 돈 계산"))

    @update_activity.before_loop
    async def before_loop_start(self):
        await self.bot.wait_until_ready()


def setup(bot: Union[Bot, AutoShardedBot]):
    cog = Tasks(bot)
    cog.update_activity.start()
    bot.add_cog(cog)
