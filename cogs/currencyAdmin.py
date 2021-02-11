import discord
from discord.ext import commands
from modules import accessToDB, customErrors, log
from cogs import events
import asyncio
import aiosqlite


class CurrencyAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

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
        except customErrors.NoServerData:
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
            await log.log(self.bot, ctx.guild.id, "관리역할 변경", f"{ctx.author.mention}님이 관리역할 변경")
        except commands.MissingPermissions:
            await ctx.send("'역할 관리' 권한이 필요해요!")

    @commands.command(name="지급")
    async def giveMoney(self, ctx, member: discord.Member, amount: float):
        userData = await accessToDB.getUserData(ctx.guild.id, member.id)
        userData["money"] += amount
        await accessToDB.setUserData(ctx.guild.id, member.id, userData)
        money = await accessToDB.getUsersMoney(ctx.guild.id, member.id)
        await log.log(self.bot, ctx.guild.id,
                      "화폐 지급",
                      f"{ctx.author.mention}님이 {member.mention}님께 {await accessToDB.getMoney(ctx.guild.id, amount)} 지급")
        await ctx.send(f"지급 완료!: 현재 유저의 보유 금액: `{money}`")

    @commands.group(name="화폐설정")
    async def currency(self, ctx):
        pass

    @currency.command(name="이름", aliases=["단위"])
    async def curName(self, ctx: commands.Context, *, name: str = None):
        if name is None:
            name = ""
        if len(name) > 20:
            await ctx.send("화폐 단위의 길이는 최대 20을 넘을 수 없습니다.")
            return
        await accessToDB.setServerData(ctx.guild.id, {"currency": name})
        if name is None:
            name = "(없음)"
        await ctx.send(f"화폐 단위를 `{name}`으로 변경 완료!")
        await log.log(self.bot, ctx.guild.id, "화폐 단위 변경", f"{ctx.author.mention}님이 화폐 단위를 {name}(으)로 변경")

    @currency.command(name="위치")
    async def curLoc(self, ctx: commands.Context):
        message = await ctx.send("화폐 표기 시의 화폐 단위 표기 위치를 지정해주세요. \n"
                                 "예) ⬅: $20, ➡: 20$")
        await message.add_reaction("⬅")
        await message.add_reaction("➡")

        def check(reaction, user):
            if user == ctx.author:
                if str(reaction) in ["⬅", "➡"]:
                    return True
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=15)
            if str(reaction) == "⬅":
                await accessToDB.setServerData(ctx.guild.id, {"locate": 0})
                await ctx.send("화폐 단위 표기 위치를 왼쪽으로 설정 완료!")
                await log.log(self.bot, ctx.guild.id, "화폐 단위 변경", f"{ctx.author.mention}님이 화폐 단위 표기 위치를 왼쪽으로 변경")
            elif str(reaction) == "➡":
                await accessToDB.setServerData(ctx.guild.id, {"locate": 1})
                await ctx.send("화폐 단위 표기 위치를 오른쪽으로 설정 완료!")
                await log.log(self.bot, ctx.guild.id, "화폐 단위 변경", f"{ctx.author.mention}님이 화폐 단위 표기 위치를 오른쪽으로 변경")
        except asyncio.TimeoutError:
            await ctx.send("입력 시간이 초과되었습니다.")

    @commands.command(name="로그채널")
    async def logChannel(self, ctx: commands.Context, channel: discord.TextChannel):
        await accessToDB.setServerData(ctx.guild.id, {"logChannelID": channel.id})
        await ctx.send(f"로그 채널을 {channel.mention}으로 설정 완료!")

    @commands.group(name="보상설정")
    async def reward(self, ctx):
        pass

    @reward.command(name="채팅")
    async def chatReward(self, ctx: commands.Context, amount: int):
        await accessToDB.setServerData(ctx.guild.id, {"chatReward": amount})
        self.bot.cogs["Events"].chatReward[ctx.guild.id] = amount
        await ctx.send(f"채팅 시 보상을 {await accessToDB.getMoney(ctx.guild.id, amount)}으로 설정 완료!")


def setup(bot):
    bot.add_cog(CurrencyAdmin(bot))
