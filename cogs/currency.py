import discord
from discord.ext import commands

class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="지갑")
    async def wallet(self, ctx: commands.Context):
        await ctx.send("test")


def setup(bot):
    bot.add_cog(Currency(bot))