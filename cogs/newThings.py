import discord
import aiosqlite
from discord.ext import commands
from modules import accessToDB, customErrors


class NewThings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        if type(ctx.channel) == discord.DMChannel:
            await ctx.send("이 명령어는 DM 채널에서는 사용하실 수 없어요!")
            return False

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            await accessToDB.newUser(member.guild.id, member.id)
        except customErrors.UserAlreadyRegistered:
            pass
        except customErrors.NoServerData:
            pass

    @commands.command(name="유저등록")
    async def register(self, ctx: commands.Context):
        try:
            await accessToDB.newUser(ctx.guild.id, ctx.author.id)
            await ctx.send("유저 등록 완료!")
        except customErrors.NoServerData:
            await ctx.send(f"먼저 서버의 관리자에게 요청해 서버를 등록해주세요. \n"
                           f"서버 등록 명령어는 `{ctx.prefix}서버등록`입니다.")

    @commands.command(name="서버등록")
    @commands.has_guild_permissions(administrator=True)
    async def serverReg(self, ctx: commands.Context):
        try:
            role = await ctx.guild.create_role(name="은행원", color=discord.Color.green())
            await accessToDB.newServer(ctx.guild.id, role.id)
            for member in ctx.guild.members:
                await accessToDB.newUser(ctx.guild.id, member.id)
            await ctx.send("서버 등록 완료!")
        except customErrors.ServerAlreadyRegistered:
            await ctx.send("이미 등록되어 있습니다.")
        except commands.MissingPermissions:
            await ctx.send("'역할 관리' 권한이 필요해요!")

    @commands.command(name="역할재설정")
    @commands.has_guild_permissions(administrator=True)
    async def roleReset(self, ctx: commands.Context):
        try:
            try:
                data = await accessToDB.getServerData(ctx.guild.id)
                oldRole = ctx.guild.get_role(data["controlRoleID"])
                if oldRole is None:
                    pass
                else:
                    await oldRole.delete()
            except customErrors.NoServerData:
                await ctx.send(f"먼저 서버의 관리자에게 요청해 서버를 등록해주세요. \n"
                               f"서버 등록 명령어는 `{ctx.prefix}서버등록`입니다.")
            role = await ctx.guild.create_role(name="은행원", color=discord.Color.green())
            await accessToDB.setServerData(ctx.guild.id, {"controlRoleID": role.id})
            await ctx.send("역할 재설정 완료!")
        except commands.MissingPermissions:
            await ctx.send("'역할 관리' 권한이 필요해요!")


def setup(bot):
    bot.add_cog(NewThings(bot))