import discord
from discord.ext import commands
import aiosqlite
from cogs import *
from modules import accessToDB

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.id in [288302173912170497, 665450122926096395]


    @commands.command(name="eval")
    async def comEval(self, ctx, *, command: str):
        try:
            await ctx.send(f"실행 결과: `{eval(command)}`")
        except Exception as e:
            await ctx.send(f"오류 발생: `{e}`")

    @commands.command(name="awaitEval")
    async def comAwaitEval(self, ctx, *, command: str):
        try:
            await ctx.send(f"실행 결과: `{await eval(command)}`")
        except Exception as e:
            await ctx.send(f"오류 발생: `{e.__class__.__name__}: {e}`")


def setup(bot: commands.Bot):
    bot.add_cog(Dev(bot))