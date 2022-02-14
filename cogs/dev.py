import discord
from discord.ext import commands
import aiosqlite
import logging
from cogs import *
from modules import accessToDB

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.cache = {}
        self.embed = None

    async def cog_check(self, ctx):
        return ctx.author.id in [288302173912170497, 665450122926096395, 868164373548531712]

    async def addToCache(self, key, value):
        self.cache[key] = value

    @commands.command(name="eval")
    async def comEval(self, ctx, *, command: str):
        bot = self.bot
        cache = self.cache
        try:
            await ctx.send(f"실행 결과: `{eval(command)}`")
        except Exception as e:
            await ctx.send(f"오류 발생: `{e}`")

    @commands.command(name="addToCache", aliases=["ac"])
    async def addToCacheEv(self, ctx, name: str, *, command: str):
        self.cache[name] = await eval(command)

    @commands.command(name="exec")
    async def execCom(self, ctx, *, command: str):
        exec(command)

    @commands.group(name="await")
    async def group1(self, ctx):
        pass

    @group1.command(name="eval")
    async def comAwaitEval(self, ctx, *, command: str):
        bot = self.bot
        cache = self.cache
        try:
            await ctx.send(f"실행 결과: `{await eval(command)}`")
        except Exception as e:
            await ctx.send(f"오류 발생: `{e.__class__.__name__}: {e}`")

    @commands.command(name="임베드추가")
    async def addEmbed(self, ctx, *, text: str):
        texts = text.split("\n", 1)
        if self.embed:
            self.embed.add_field(name=texts[0], value=text[1])
        else:
            self.embed = discord.Embed(title=text[0], description=text[1])

    @commands.command(name="공지")
    async def notice(self, ctx, *, text: str):
        if "withoutMention" in text:
            text.replace("withoutMention", "")
        else:
            text = text + "\n||" + self.bot.get_guild(653865550157578251).get_role(893056157265063996).mention + "||"
        message: discord.Message = await self.bot.get_guild(653865550157578251).get_channel(892421007955079218).send(
            text,
            embed=self.embed
        )
        await message.add_reaction("👍")
        await message.add_reaction("👎")
        await ctx.send(f"공지가 전송되었어요 !")

    @commands.command(name="수동공지", aliases=["수공"])
    async def notice(self, ctx, id: int):
        message = await self.bot.get_guild(653865550157578251).get_channel(892421007955079218).fetch_message(id)
        if message is None:
            await ctx.send("메시지를 찾을 수 없어요 !")
        else:
            await message.add_reaction("👍")
            await message.add_reaction("👎")
            await ctx.send("반응을 추가했어요 !")

    @commands.command(name="공지수정")
    async def editNotice(self, ctx, id: int, *, text: str):
        message: discord.Message = await self.bot.get_guild(653865550157578251).get_channel(892421007955079218).fetch_message(id)
        await ctx.send(f"실행 결과: {await eval(text)}")


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