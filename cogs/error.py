import discord
import json
from discord.ext import commands


class Error(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(Error(bot))
