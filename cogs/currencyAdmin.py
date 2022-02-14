import discord
from discord.ext import commands
from modules import accessToDB, customErrors, log
from cogs import events
import asyncio
import aiosqlite
from typing import Union


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

    @commands.command(name="지급", aliases=["회수"])
    async def giveMoney(self, ctx: commands.Context, memberOrRole: Union[discord.Member, discord.Role, str], amount: float):
        if amount == 0:
            return
        if ctx.invoked_with == "회수":
            amount = -amount
        isGive = amount > 0
        usedCommand = "지급" if isGive else "회수"
        unsignedAmount = abs(amount)
        if type(memberOrRole) == discord.Member:
            member = memberOrRole
            userData = await accessToDB.getUserData(ctx.guild.id, member.id)
            userData["money"] += amount
            await accessToDB.setUserData(ctx.guild.id, member.id, userData)
            money = await accessToDB.getMoney(ctx.guild.id, userData['money'])
            try:
                await log.log(self.bot, ctx.guild.id,
                              f"화폐 {usedCommand}",
                              f"{ctx.author.mention}님이 {member.mention}님{'께' if isGive else '의'} {await accessToDB.getMoney(ctx.guild.id, unsignedAmount)} {usedCommand}")
            except AttributeError:
                pass
            await ctx.send(f"{usedCommand} 완료!: 현재 유저의 보유 금액: `{money}`")
        elif type(memberOrRole) == discord.Role:
            role = memberOrRole
            for member in role.members:
                userData = await accessToDB.getUserData(ctx.guild.id, member.id)
                userData["money"] += amount
                await accessToDB.setUserData(ctx.guild.id, member.id, userData)
            try:
                await log.log(self.bot, ctx.guild.id,
                              f"역할 화폐 {usedCommand}",
                              f"{ctx.author.mention}님이 {role.mention} 역할을 가지신 분들{'께' if isGive else '의'} {await accessToDB.getMoney(ctx.guild.id, unsignedAmount)} {usedCommand}")
            except AttributeError:
                pass
            await ctx.send(f"{usedCommand} 완료!")
        else:
            if memberOrRole in ["전체", "모두", "everyone"]:
                for member in ctx.guild.members:
                    userData = await accessToDB.getUserData(ctx.guild.id, member.id)
                    userData["money"] += amount
                    await accessToDB.setUserData(ctx.guild.id, member.id, userData)
                try:
                    await log.log(self.bot, ctx.guild.id,
                                  f"전체 화폐 {usedCommand}",
                                  f"{ctx.author.mention}님이 모두에게 {await accessToDB.getMoney(ctx.guild.id, unsignedAmount)} {usedCommand}")
                except AttributeError:
                    pass
                await ctx.send(f"{usedCommand} 완료!")


    @commands.command(name="보유금설정", aliases=["보유금", "소유금설정", "소유금", "초기화",])
    async def setMoney(self, ctx, memberOrRole: Union[discord.Member, discord.Role], amount: float):
        if type(memberOrRole) == discord.Member:
            member = memberOrRole
            userData = await accessToDB.getUserData(ctx.guild.id, member.id)
            userData["money"] = amount
            await accessToDB.setUserData(ctx.guild.id, member.id, userData)
            money = await accessToDB.getUsersMoney(ctx.guild.id, member.id)
            try:
                await log.log(self.bot, ctx.guild.id,
                              "소유 금액 설정/초기화",
                              f"{ctx.author.mention}님이 {member.mention}님의 소유 금액을 {await accessToDB.getMoney(ctx.guild.id, amount)}로 설정")
            except AttributeError:
                pass
            await ctx.send(f"설정 완료!: 현재 유저의 보유 금액: `{money}`")
        elif type(memberOrRole) == discord.Role:
            role = memberOrRole
            for member in role.members:
                userData = await accessToDB.getUserData(ctx.guild.id, member.id)
                userData["money"] = amount
                await accessToDB.setUserData(ctx.guild.id, member.id, userData)
            try:
                await log.log(self.bot, ctx.guild.id,
                              "역할 소유 금액 설정/초기화",
                              f"{ctx.author.mention}님이 {role.mention} 역할을 가진 유저의 소유 금액을 {await accessToDB.getMoney(ctx.guild.id, amount)}로 설정")
            except AttributeError:
                pass
            await ctx.send(f"설정 완료!")
        else:
            if memberOrRole in ["전체", "모두", "everyone"]:
                for member in ctx.guild.members:
                    userData = await accessToDB.getUserData(ctx.guild.id, member.id)
                    userData["money"] = amount
                    await accessToDB.setUserData(ctx.guild.id, member.id, userData)
                try:
                    await log.log(self.bot, ctx.guild.id,
                                  "전체 소유 금액 설정/초기화",
                                  f"{ctx.author.mention}님이 모두의 소유 금액을 {await accessToDB.getMoney(ctx.guild.id, amount)}로 설정")
                except AttributeError:
                    pass
                await ctx.send(f"설정 완료!")

    @commands.command(name="서버초기화")
    async def serverReset(self, ctx: commands.Context):
        await ctx.send("서버 초기화는 지원 서버에서 문의해주세요."
                       "지원 서버 링크: https://discord.gg/wThxdtB")

# ----------------------------------------------------------------------------------------------------------------------

    @commands.group(name="설정")
    async def setting(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            data = await accessToDB.getServerData(ctx.guild.id)
            embed = discord.Embed(title=f"{ctx.guild.name} 설정",
                                  description=f"서버 ID: `{ctx.guild.id}`\n"
                                              f"설정 방법은 `{ctx.prefix}도움 명령어 관리` 명령어를 참고해주세요.")
            embed.add_field(name="화폐명", value=data['currency'], inline=False)
            embed.add_field(name="위치", value="왼쪽" if data['locate'] == 0 else "오른쪽", inline=False)
            controlRole = ctx.guild.get_role(data['controlRoleID'])
            if controlRole is None:
                embed.add_field(name="관리 역할", value="역할이 없어요!")
            else:
                embed.add_field(name="관리 역할", value=f"{controlRole.mention}\nID: `{controlRole.id}`")
            logChannel = ctx.guild.get_channel(data['logChannelID'])
            if logChannel is None:
                embed.add_field(name="로그 채널", value="로그 채널이 없어요!")
            else:
                embed.add_field(name="로그 채널", value=f"{logChannel.mention}\n ID: `{logChannel.id}`")
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="채팅 보상 (1분마다)", value=f"{data['chatReward']}")
            embed.add_field(name="순위 기능", value="활성화" if data['showRanking'] == 1 else "비활성화")
            embed.add_field(name="송금 기능", value="활성화" if data['sendMoney'] == 1 else "비활성화")
            await ctx.send(embed=embed)

    @setting.group(name="화폐", invoke_without_command=False)
    async def currency(self, ctx: commands.Context):
        await ctx.send("세부항목이 올바르지 않아요!\n"
                       f"{', '.join(self.currency.commands)} 중 하나를 입력해주세요.")

    @currency.command(name="이름", aliases=["단위"])
    async def curName(self, ctx: commands.Context, *, name: str = None):
        if name is None:
            name = ""
        if len(name) > 20:
            await ctx.send("화폐 단위의 길이는 최대 20을 넘을 수 없습니다.")
            return
        await accessToDB.setServerData(ctx.guild.id, {"currency": name})
        if name == "":
            name = "(없음)"
        await ctx.send(f"화폐 단위를 `{name}`(으)로 변경 완료!")
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

    @setting.command(name="로그채널")
    async def logChannel(self, ctx: commands.Context, channel: discord.TextChannel):
        await accessToDB.setServerData(ctx.guild.id, {"logChannelID": channel.id})
        await ctx.send(f"로그 채널을 {channel.mention}(으)로 설정 완료!")

    @setting.group(name="보상")
    async def reward(self, ctx):
        pass

    @reward.command(name="채팅")
    async def chatReward(self, ctx: commands.Context, amount: float):
        await accessToDB.setServerData(ctx.guild.id, {"chatReward": amount})
        await self.bot.get_cog("Events").addServer(ctx.guild)
        await ctx.send(f"채팅 시 보상을 {await accessToDB.getMoney(ctx.guild.id, amount)}(으)로 설정 완료!")

    @setting.group(name="기능")
    async def feature(self, ctx: commands.Context, item: str, answer: str = None):
        aliases = {}
        kinds = {
            "순위": {
                "column": "showRanking",
                "default": 1
            },
            "송금": {
                "column": "sendMoney",
                "default": 0
            },
            "재가입시초기화": {
                "column": "reregisterReset",
                "default": 0
            },
        }
        if item in aliases.keys():
            item = aliases[item]
        if item in kinds.keys():
            featureData = kinds[item]
        else:
            await ctx.send("설정할 기능의 이름을 확인해주세요 !")
            return
        if answer is None:
            serverData = await accessToDB.read(f'SELECT {featureData["column"]} FROM "serversData" WHERE serverID=?',
                                               (ctx.guild.id,))
            if serverData[0][featureData["column"]] == 0:
                final = 1
            else:
                final = 0
        else:
            answer = answer.lower()
            if answer in ["true", "o", "1", "활성화", "on", "켜기"]:
                final = 1
            elif answer in ["false", "x", "0", "비활성화", "off", "끄기"]:
                final = 0
            elif answer in ["default", "기본", "기본값", "초기화", "reset"]:
                final = featureData["default"]
            else:
                await ctx.send("o 또는 x로 입력해주세요 !")
                return
        await accessToDB.setServerData(ctx.guild.id, {featureData["column"]: final})
        await ctx.send(f"{item} 기능이 {'활성화' if final == 1 else '비활성화'}되었어요 !")




# unused command
"""
    @feature.command(name="순위", aliases=["랭킹"])
    async def setShowRanking(self, ctx: commands.Context, answer: str = None):
        if answer is None:
            serverData = await accessToDB.read(f'SELECT showRanking FROM "serversData" WHERE serverID=?',
                                               (ctx.guild.id,))
            if serverData[0]['showRanking'] == 0:
                final = 1
            else:
                final = 0
        else:
            answer = answer.lower()
            if answer in ["true", "o", "1", "활성화", "on", "켜기"]:
                final = 1
            elif answer in ["false", "x", "0", "비활성화", "off", "끄기"]:
                final = 0
            else:
                await ctx.send("다시 입력해주세요.")
                return
        await accessToDB.setServerData(ctx.guild.id, {"showRanking": final})
        await ctx.send(f"순위 기능이 {'활성화' if final == 1 else '비활성화'}되었어요 !")
"""





def setup(bot):
    bot.add_cog(CurrencyAdmin(bot))
