import discord
from discord.ext import commands
import aiosqlite
from cogs import *
from modules import accessToDB

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

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

    @commands.group(name="cog")
    async def cogCommands(self, ctx: commands.Context):
        pass

    @cogCommands.command(name="load")
    async def load(self, ctx, name):
        try:
            self.bot.load_extension(f"cogs.{name}")
        except commands.ExtensionNotFound:
            await ctx.send(f"{name} 모듈을 찾지 못했어요.")
            return
        await ctx.send(f"{name} 모듈을 로드 완료!")

    @cogCommands.command(name="reload")
    async def reload(self, ctx, name):
        try:
            self.bot.reload_extension(f"cogs.{name}")
        except commands.ExtensionNotLoaded:
            await ctx.send(f"{name} 모듈을 찾지 못했어요.")
            return
        await ctx.send(f"{name} 모듈을 리로드 완료!")

    @cogCommands.command(name="unload")
    async def unload(self, ctx, name):
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except commands.ExtensionNotLoaded:
            await ctx.send(f"{name} 모듈을 찾지 못했어요.")
            return
        await ctx.send(f"{name} 모듈을 언로드 완료!")


def setup(bot: commands.Bot):
    bot.add_cog(Dev(bot))