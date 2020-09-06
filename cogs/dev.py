import discord
from discord.ext import commands
import aiosqlite
from cogs import *
from modules import accessToDB

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            await ctx.send(f"오류 발생: `{e}`")

    @commands.command(name="getServerData")
    async def comGetServerData(self, ctx):
        a: aiosqlite.Row = await accessToDB.getServerData(ctx.guild.id)
        await ctx.send(a.keys())

def setup(bot: commands.Bot):
    bot.add_cog(Dev(bot))