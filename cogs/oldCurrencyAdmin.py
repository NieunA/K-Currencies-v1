import discord
from discord.ext import commands
from modules import accessToDB, customErrors, log
from cogs import events
import asyncio
import aiosqlite
from typing import Union


class OldCurrencyAdmin(commands.Cog):
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


    @commands.group(name="화폐설정")
    async def oldCurrency(self, ctx):
        pass

    @oldCurrency.command(name="이름", aliases=["단위"])
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

    @oldCurrency.command(name="위치")
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
        await ctx.send(f"로그 채널을 {channel.mention}(으)로 설정 완료!")

    @commands.group(name="보상설정")
    async def reward(self, ctx):
        pass

    @reward.command(name="채팅")
    async def chatReward(self, ctx: commands.Context, amount: float):
        await accessToDB.setServerData(ctx.guild.id, {"chatReward": amount})
        await self.bot.get_cog("Events").addServer(ctx.guild)
        await ctx.send(f"채팅 시 보상을 {await accessToDB.getMoney(ctx.guild.id, amount)}(으)로 설정 완료!")

    @commands.group(name="기능설정")
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
    bot.add_cog(OldCurrencyAdmin(bot))
