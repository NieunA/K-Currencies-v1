import discord
from discord.ext import commands

categories = {
    "등록": {
        "desc": None,
        "commands": {
            "서버등록":
                "서버를 데이터베이스에 등록하고, \n"
                "화폐 관리 역할(기본적으로 '은행원'이라는 이름으로 생성됩니다)를 생성합니다. \n"
                "(관리자 권한 필요)",
            "역할재설정":
                "화폐 관리 역할을 리셋합니다. \n"
                "(역할을 가진 유저, 색, 이름 등이 모두 초기화됩니다.)"
                "(관리자 권한 필요)"
        }
    },
    "관리": {
        "desc": "이 명령어들은 화폐 관리 역할이 필요합니다.",
        "commands": {
            "지급 [유저(멘션)] [금액]":
                "[금액]의 화폐를 [유저]에게 지급합니다.",
            "관리역할 [역할 이름]":
                "관리 역할의 이름을 [역할 이름]으로 변경합니다. \n"
                "(수동으로 이름을 변경하실 시, 오류의 위험이 있으니 절대 하지 말아주세요.",
            "화폐설정 단위 [단위]":
                "화폐 단위를 [단위]로 지정합니다. \n"
                "단, [단위]의 길이는 20을 넘을 수 없어요!",
            "화폐설정 위치":
                "화폐 표기 시 단위의 위치를 지정합니다. \n"
                "왼쪽, 오른쪽 중 이모지를 클릭하여 지정할 수 있습니다.",
            "로그채널 [채널(멘션)]":
                "[채널]을 로그 채널로 설정합니다."
        }
    },
    "화폐": {
        "desc": None,
        "commands": {
            "지갑 (유저(멘션), 명령어 사용 유저)":
                "(유저)의 보유 금액을 보여줍니다."
        }
    },
    "기타": {
        "desc": None,
        "commands": {
            "링크":
                "봇 초대 링크, 공식 서버 링크 등 다양한 링크를 보여줍니다."
        }
    }
}


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="도움", aliases=["도움말", "help"])
    async def help(self, ctx: commands.Context, *, kind: str = None):
        if kind is None:
            embed = discord.Embed(title="K-Currencies 기본 도움말")
            embed.add_field(name="기본 소개",
                            value="K-C봇은 K-POP, K-방역과 같이 한국의 화폐 관리 봇이라는 뜻을 담고 있습니다. \n"
                                  "K-C봇을 통해 서버 전용 화폐를 만들고 관리하실 수 있습니다. \n"
                                  f"K-C봇의 접두사(prefix)는 `{ctx.prefix}`입니다.", inline=False)
            embed.add_field(name="기본 작동 메커니즘",
                            value="K-C봇은 서버별 데이터베이스를 생성하여 화폐 데이터를 관리하면, \n"
                                  "화폐 관리 역할을 생성하여 역할을 가진 유저만 서버 데이터를 관리할 수 있습니다. \n"
                                  "K-C봇의 주요 기능을 사용하시려면 K-C봇에게 '역할 관리' 권한이 필요합니다. \n"
                                  "K-C봇을 처음 사용하신다면 서버를 등록하여야 하며, \n"
                                  f"자세한 내용은 `{ctx.prefix}도움 등록` 명령어를 참고하세요.", inline=False)
            embed.add_field(name="서버 관리 역할",
                            value="서버 데이터 관리 명령어는 이 역할을 가진 유저만이 사용할 수 있습니다. \n"
                                  "서버를 등록할 때 기본적으로 생성되며, 이름은 '은행원'입니다. \n"
                                 f"만약 역할의 이름을 바꾸고 싶으시다면, `{ctx.prefix}도움 관리` 명령어를 참고하세요.",
                            inline=False)
            embed.add_field(name="전체 명령어 목록",
                            value=f"`{ctx.prefix}도움 [카테고리]` 명령어를 사용하여 확인하세요. \n"
                                  f"카테고리 목록: `{'`, `'.join(categories.keys())}`", inline=False)
            embed.add_field(name='기타 문의사항',
                            value=f"건의, 문의사항이나 봇 사용 중 불편한 점이 있으시다면 "
                                  f"[Team EG 공식 디스코드 서버](https://discord.gg/wThxdtB)에서 말씀해주세요!", inline=False)
        elif kind in categories.keys():
            if categories[kind]['desc'] is None:
                embed = discord.Embed(title=f"K-Currencies 도움말 목록 - {kind}",
                                      description=f"[필수 입력 항목], (선택 입력 항목, 기본값)")
            else:
                embed = discord.Embed(title=f"K-Currencies 도움말 목록 - {kind}",
                                      description=f"{categories[kind]['desc']}, [필수 입력 항목], (선택 입력 항목, 기본값)")
            for key, value in categories[kind]['commands'].items():
                embed.add_field(name=key,
                                value=value,
                                inline=False)
        else:
            await ctx.send("입력하신 카테고리는 존재하지 않는 카테고리입니다. 다시 입력해주세요.")
            return
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
