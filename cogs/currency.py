import discord
from discord.ext import commands
from modules import accessToDB
import aiosqlite


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="유저등록")
    async def register(self, ctx: commands.Context):
        try:
            await accessToDB.newUser(ctx.guild.id, ctx.author.id)
            await ctx.send("유저 등록 완료!")
        except aiosqlite.OperationalError as err:
            if str(err) == f'no such table: {ctx.guild.id}':
                await ctx.send("아직 서버가 등록되어 있지 않습니다. \n"
                               "!KC 서버등록 명령어를 이용해 서버를 등록하세요.")


def setup(bot):
    bot.add_cog(Currency(bot))