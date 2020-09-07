import discord
from discord.ext import commands
from modules import accessToDB, customErrors
import aiosqlite


class CurrencyAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        if type(ctx.channel) == discord.DMChannel:
            await ctx.send("이 명령어는 DM 채널에서는 사용하실 수 없어요!")
            return False
        try:
            serverData = await accessToDB.getServerData(ctx.guild.id)
            guild: discord.Guild = ctx.guild
            role: discord.Role = guild.get_role(serverData["controlRoleID"])
            if role is None:
                role: discord.Role = await guild.create_role(name="은행원", color=discord.Color.green())
                await accessToDB.setServerData(ctx.guild.id, {"controlRoleID": role.id})
            if role in ctx.author.roles:
                return True
            else:
                await ctx.send(f"`{role.name}`(`{role.id}`) 역할이 없어요!")
                return False
        except IndexError:
            await ctx.send(f"먼저 서버의 관리자에게 요청해 서버를 등록해주세요. \n"
                           f"서버 등록 명령어는 `{ctx.prefix}서버등록`입니다.")

    @commands.command(name="관리역할")
    async def roleNameChange(self, ctx: commands.Context, newName: str):
        try:
            serverData = await accessToDB.getServerData(ctx.guild.id)
            oldRole: discord.Role = ctx.guild.get_role(serverData["controlRoleID"])
            newRole = await ctx.guild.create_role(name=newName, color=oldRole.color)
            for member in oldRole.members:
                member: discord.Member
                await member.add_roles(newRole)
            guild: discord.Guild = ctx.guild
            await accessToDB.setServerData(ctx.guild.id, {"controlRoleID": newRole.id})
            await oldRole.delete()
            await ctx.send("변경 완료!")
        except commands.MissingPermissions:
            await ctx.send("'역할 관리' 권한이 필요해요!")

    @commands.command(name="지급")
    async def giveMoney(self, ctx, member: discord.Member, amount: float):
        try:
            userData = await accessToDB.getUserData(ctx.guild.id, member.id)
            userData["money"] += amount
            await accessToDB.setUserData(ctx.guild.id, member.id, userData)
            money = await accessToDB.getMoney(ctx.guild.id, member.id)
            await ctx.send(f"지급 완료!: 현재 유저의 보유 금액: `{money}`")
        except customErrors.NoUserData:
            await ctx.send(f"등록되어 있지 않은 유저입니다. 먼저 등록해주세요. \n"
                           f"등록 명령어는 `{ctx.prefix}유저등록`입니다.")


def setup(bot):
    bot.add_cog(CurrencyAdmin(bot))