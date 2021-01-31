import discord
from discord.ext import commands
from modules import accessToDB, customErrors
import aiosqlite


class CurrencyUser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if type(ctx.channel) == discord.DMChannel:
            await ctx.send("이 명령어는 DM 채널에서는 사용하실 수 없어요!")
            return False
        try:
            await accessToDB.getUserData(ctx.guild.id, ctx.author.id)
        except customErrors.NoServerData:
            await ctx.send(f"먼저 서버의 관리자에게 요청해 서버를 등록해주세요. \n"
                           f"서버 등록 명령어는 `{ctx.prefix}서버등록`입니다.")
            return False
        except customErrors.NoUserData:
            await ctx.send(f"등록되어 있지 않습니다. 먼저 등록해주세요. \n"
                           f"등록 명령어는 `{ctx.prefix}유저등록`입니다.")
            return False
        return True


    @commands.command(name="지갑")
    async def wallet(self, ctx: commands.Context, member: discord.Member=None):
        if member is None:
            member = ctx.author
        try:
            money = await accessToDB.getUsersMoney(ctx.guild.id, member.id)
            await ctx.send(f"`{member.name}#{member.discriminator}`님의 보유 금액은 `{money}`입니다.")
        except customErrors.NoUserData:
            await ctx.send(f"등록되어 있지 않은 유저입니다. 먼저 등록해주세요. \n"
                           f"등록 명령어는 `{ctx.prefix}유저등록`입니다.")

def setup(bot):
    bot.add_cog(CurrencyUser(bot))