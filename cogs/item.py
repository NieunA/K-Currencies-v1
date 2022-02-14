import asyncio
import random

import discord
from discord import ui, utils
from discord.ext import commands
from modules import accessToDB, customErrors, log

"""
class TypeChoice(discord.ui.View):

    @ui.button(style=discord.ButtonStyle.secondary, label="수동", custom_id="manual", row=0)
    async def manual(self, button: discord.Button, ia: discord.Interaction):
        for c in self.children:
            c: discord.Button
            c.disabled = True
        await ia.edit_original_message(view=self)
"""


class KCLangCompileError(customErrors.CustomError):
    def __init__(self, line, message):
        super().__init__(f"{line + 1}번째 줄에서 오류가 발생했습니다.\n{message}")

class KCLangCompileForGuildError(KCLangCompileError):
    pass


# compiled codes :
# ['give' or 'take', 'role', id: int or name: str]
# ['give' or 'take', 'item' or 'currency', id: int or name: str, amount: int]
# ['message' or 'dm', message: str]
# ['wait', seconds: int]
# ['chance', percentage: int]
# ['else', percentage: Optional[int]]
# ['end']

def kcCompile(code: str, guild: discord.Guild):
    toReturn = {
        "type": "",
        "cooltime": 0
    }
    compiled = []
    probsStack = []
    probSum = [] # max 100
    toPass = []
    lines = code.split("\n")
    for i, line in enumerate(lines):
        if i in toPass:
            continue
        tokens = line.strip().split(" ")
        if tokens[0].startswith("#"):
            continue
        elif tokens[0] in ["지급", "회수"]:
            if len(tokens) < 2:
                raise KCLangCompileError(i, f"`{tokens[0]}` 뒤에는 `아이템`, `화폐`, `역할` 중 하나가 와야 합니다.")
            toGet = line.strip().split(maxsplit=2)[-1]
            comName = 'give' if tokens[0] == "지급" else 'take'
            if tokens[1] == "아이템":
                # connect to DB, and check if item whose name or id is toGet exists
                pass
            elif tokens[1] == "화폐":
                try:
                    toGet = round(float(toGet), ndigits=4)
                    compiled.append([comName, 'currency', toGet])
                except ValueError:
                    raise KCLangCompileError(i, "화폐는 숫자만 입력해주세요.")
            elif tokens[1] == "역할":
                role = utils.get(guild.roles, name=toGet) or utils.get(guild.roles, id=toGet) or utils.get(guild.roles, mention=toGet)
                if role:
                    compiled.append([comName, 'role', role.id])
                else:
                    raise KCLangCompileForGuildError(i, f"역할을 찾을 수 없습니다.\n역할: {toGet}")
            else:
                raise KCLangCompileError(i, f"`{tokens[0]}` 뒤에는 `아이템`, `화폐`, `역할` 중 하나가 와야 합니다.")
        elif tokens[0] in ['dm', "DM", "메시지"]:
            # content should be separated with """ or in the same line
            if tokens[0] in ['dm' or 'DM']:
                comName = 'dm'
            else:
                comName = 'message'
            content = ""
            if tokens[1] == '"""':
                for j, more in enumerate(lines[i + 1:]):
                    if more.strip().endswith('"""'):
                        content += more.strip()[:-3] + "\n"
                        toPass.append(i + j + 1)
                        break
                    else:
                        toPass.append(i + j + 1)
                        content += more + "\n"
            else:
                content = line.strip().split(maxsplit=1)[-1]
            content = content.strip()
            compiled.append([comName, content])
        elif tokens[0] in ['기다리기', '시간', '지연']:
            if len(tokens) == 1:
                raise KCLangCompileError(i, f"`{tokens[0]}` 뒤에 시간을 입력해주세요.")
            if tokens[1].isdecimal():
                compiled.append(['wait', int(tokens[1])])
            else:
                raise KCLangCompileError(i, "시간은 숫자만 입력해주세요.")
        elif tokens[0] in ['확률']:
            if len(tokens) < 2:
                raise KCLangCompileError(i, f"`{tokens[0]}` 뒤에 확률을 입력해주세요.")
            if tokens[1].isdecimal():
                probsStack.append(i)
                probSum.append(int(tokens[1]))
                compiled.append(['chance', int(tokens[1])])
            else:
                raise KCLangCompileError(i, "확률은 숫자만 입력해주세요.")
        elif tokens[0] in ['아니면']:
            if len(probsStack) == 0:
                raise KCLangCompileError(i, "`아니면`은 `확률` 이후에 와야 합니다.")
            if len(tokens) < 2:
                compiled.append(['else', 100 - probSum[-1]])
            else:
                if tokens[1].isdecimal():
                    if probSum[-1] + int(tokens[1]) > 100:
                        raise KCLangCompileError(i, "확률의 합이 100을 넘어요.")
                    probSum[-1] += int(tokens[1])
                    compiled.append(['else', int(tokens[1])])
                else:
                    raise KCLangCompileError(i, "확률은 숫자만 입력해주세요.")
        elif tokens[0] in ["확률끝", "끝"]:
            try:
                probsStack = probsStack[0:-1]
                probSum = probSum[0:-1]
                compiled.append(['end'])
            except IndexError:
                raise KCLangCompileError(i, f"`{tokens[0]}`은 `확률` 이후에 와야 합니다.")
    return compiled

async def run(code: str, ctx: commands.Context, guild: discord.Guild):
    randomNumbers = []
    toPass = False
    for i, line in enumerate(code):
        if line[0] == 'chance':
            randomNumbers.append(random.randint(1, 100))
            if line[1] > randomNumbers[-1]:
                toPass = False
            else:
                randomNumbers[-1] += line[1]
                toPass = True
        elif line[0] == "else":
            if line[1] > randomNumbers[-1]:
                toPass = False
            else:
                toPass = True
        elif line[0] == 'end':
            # end of chance
            toPass = False
            del randomNumbers[-1]
        elif toPass:
            continue
        elif line[0] == 'dm':
            await ctx.author.send(line[1])
        elif line[0] == 'message':
            await ctx.send(line[1])
        elif line[0] == 'give':
            if line[1] == 'currency':
                await accessToDB.addUserMoney(guild.id, ctx.author.id, line[2])
            elif line[1] == 'item':
                pass
            elif line[1] == 'role':
                await ctx.author.add_roles(guild.get_role(line[2]), reason="아이템 사용")
        elif line[0] == 'wait':
            await asyncio.sleep(line[1])





class Item(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

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

    @commands.command(name="test")
    async def testc(self, ctx, *, code: str):
        await ctx.send(kcCompile(code, ctx.guild))

    @commands.group(name="아이템")
    async def g_item(self, ctx):
        if ctx.invoked_subcommand is None:
            # todo
            pass

    @g_item.command(name="추가", aliases=["생성"])
    async def add(self, ctx: commands.Context, *, code: str):
        try:
            compiled = kcCompile(code, ctx.guild)
        except KCLangCompileError as e:
            await ctx.send(str(e))
        else:
            embed = discord.Embed(title="아이템 추가", description="이름: \nID: ")
            await ctx.send(embed=embed)






def setup(bot):
    bot.add_cog(Item(bot))