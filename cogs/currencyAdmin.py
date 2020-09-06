import discord
from discord.ext import commands
from modules import accessToDB
import aiosqlite


class CurrencyAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="서버등록")
    async def serverRes(self, ctx: commands.Context):
        try:
            await accessToDB.newServer(ctx.guild.id, 0)
            await ctx.send("서버 등록 완료!")
        except aiosqlite.OperationalError as err:
            if str(err) == f'table "{ctx.guild.id}" already exists':
                await ctx.send("이미 등록되어 있습니다.")

def setup(bot):
    bot.add_cog(CurrencyAdmin(bot))