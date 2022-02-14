import discord
from discord.ext import commands
from modules import accessToDB, customErrors
import aiosqlite, math, asyncio


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
        return True

    @commands.command(name="송금")
    async def sendMoney(self, ctx: commands.Context, member: discord.Member, amount: float):
        serverData = await accessToDB.read(f'SELECT sendMoney FROM "serversData" WHERE serverID=?', (ctx.guild.id,))
        if amount <= 0:
            await ctx.send("0 이하의 금액은 보낼 수 없어요 !")
            return
        elif serverData[0]['sendMoney'] == 0:
            await ctx.send("이 서버에서는 송금 기능이 비활성화되어 있어요 !")
            return
        authorData = await accessToDB.getUserData(ctx.guild.id, ctx.author.id)
        authorData["money"] -= amount
        if authorData['money'] < 0:
            await ctx.send(f"화폐가 `{await accessToDB.getMoney(ctx.guild.id, -authorData['money'])}` 부족해요 !")
            return
        await accessToDB.setUserData(ctx.guild.id, ctx.author.id, authorData)
        userData = await accessToDB.getUserData(ctx.guild.id, member.id)
        userData["money"] += amount
        await accessToDB.setUserData(ctx.guild.id, member.id, userData)
        await ctx.send(f"송금 완료! `{str(ctx.author)}`님의 남은 금액은 `{await accessToDB.getMoney(ctx.guild.id, authorData['money'])}`입니다.")

    @commands.command(name="지갑")
    async def wallet(self, ctx: commands.Context, member: discord.Member = None):
        if member is None:
            member = ctx.author
        money = await accessToDB.getUsersMoney(ctx.guild.id, member.id)
        await ctx.send(f"`{member.name}#{member.discriminator}`님의 보유 금액은 `{money}`입니다.")

    @commands.command(name="순위", aliases=["rank", "랭킹"])
    async def ranking(self, ctx: commands.Context, num: int = 5):
        serverData = await accessToDB.read(f'SELECT showRanking FROM "serversData" WHERE serverID=?', (ctx.guild.id, ))
        if serverData[0]['showRanking'] == 0:
            await ctx.send("이 서버에서는 순위 기능이 비활성화되어 있어요 !")
        else:
            usersRawL = await accessToDB.read(f'SELECT userID, money, items FROM "{ctx.guild.id}" ORDER BY money DESC',
                                              ())
            usersL = []
            for user in usersRawL:
                member: discord.Member = ctx.guild.get_member(user['userID'])
                if member is not None:
                    if not member.bot:
                        user['name'] = str(member)
                        usersL.append(user)

            pages = math.ceil(len(usersL) / num)
            nowPage = 0
            embedPages = []
            sData = await accessToDB.getServerData(ctx.guild.id)
            for i in range(pages):
                embed = discord.Embed(
                    title=f"화폐 보유 순위",
                    description=f"{i + 1} / {pages} 페이지\n"
                                f"서버 : {ctx.guild.name}"
                )
                for j in range(num):
                    try:
                        userD = usersL[i * num + j]
                        userID = userD['userID']
                        embed.add_field(name=f"{i * num + j + 1}위 : {userD['name']}",
                                        value=f"보유 금액: {await accessToDB.getMoney(ctx.guild.id, userD['money'], sData)}",
                                        inline=False)
                    except IndexError:
                        continue
                if i + 1 == pages:
                    embed.add_field(name="마지막 페이지입니다.",
                                    value="찾으시는 유저가 없다면 `!KC 지갑 (유저)` 명령어를 사용해보세요 !",
                                    inline=False)
                embedPages.append(embed)
            if not embedPages:
                await ctx.send("아직 유저가 없어요.")
                return None
            embedMessage = await ctx.send(embed=embedPages[0])
            def check(reaction, user):
                return str(reaction) in ["⬅", "➡"] and user == ctx.author and reaction.message.id == embedMessage.id

            if len(usersL) < num:
                pass
            else:
                await embedMessage.add_reaction("⬅")
                await embedMessage.add_reaction("➡")
                while True:
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=15)
                        if str(reaction) == "⬅":
                            if nowPage == 0:
                                await ctx.send("첫 페이지입니다.")
                            else:
                                nowPage -= 1
                                await embedMessage.edit(embed=embedPages[nowPage])
                        else:
                            if nowPage == pages - 1:
                                await ctx.send("마지막 페이지입니다.")
                            else:
                                nowPage += 1
                                await embedMessage.edit(embed=embedPages[nowPage])
                    except asyncio.TimeoutError:
                        await embedMessage.edit(content="시간이 초과되었습니다. 다시 시작해주세요.", embed=embedPages[nowPage])
                        return None


def setup(bot):
    bot.add_cog(CurrencyUser(bot))