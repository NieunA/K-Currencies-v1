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
        "desc": "이 명령어들은 화폐 관리 역할이 필요합니다. \n"
                "멘션이 어려우신 경우 유저분의 닉네임 혹은 역할의 이름을 대신 입력할 수 있습니다.",
        "commands": {
            "지급 [유저(멘션/닉네임)/역할(멘션/이름)/'전체'] [금액]":
                "[금액]의 화폐를 [유저], [역할]을 가진 유저들 또는 유저 전체에게 지급합니다.\n",
            "회수 [유저(멘션/닉네임)/역할(멘션/이름)/'전체'] [금액]":
                "[금액]의 화폐를 [유저], [역할]을 가진 유저들 또는 유저 전체에게서 회수합니다.\n",
            "설정":
                "서버의 모든 설정 상태를 확인합니다.",
            "소유금설정 [유저(멘션/닉네임)/역할(멘션/이름)/'전체'] [금액]":
                "[유저], [역할]을 가진 유저들 또는 유저 전체의 소유 금액을 [금액]으로 설정합니다.\n",
            "관리역할 [역할 이름]":
                "관리 역할의 이름을 [역할 이름]으로 변경합니다. \n"
                "(수동으로 이름을 변경하실 시, 오류의 위험이 있으니 절대 하지 말아주세요.)",
            "화폐설정 단위 [단위]":
                "화폐 단위를 [단위]로 지정합니다. \n"
                "단, [단위]의 길이는 20을 넘을 수 없어요!",
            "화폐설정 위치":
                "화폐 표기 시 단위의 위치를 지정합니다. \n"
                "왼쪽, 오른쪽 중 이모지를 클릭하여 지정할 수 있습니다.",
            "로그채널 [채널(멘션)]":
                "[채널]을 로그 채널로 설정합니다.",
            "보상설정 채팅 [금액]":
                "1분마다 채팅 시 보상을 [금액]으로 설정합니다.",
            "기능설정 [기능] [O/X]":
                "서버에서 [기능]을 활성화/비활성화합니다. \n"
                "기능의 종류에는 `순위`, `송금`이 있어요!"
        }
    },
    "화폐": {
        "desc": None,
        "commands": {
            "지갑 (유저(멘션), 명령어 사용 유저)":
                "(유저)의 보유 금액을 보여줍니다.",
            "순위 (한 페이지에 보일 유저 수, 5)":
                "서버의 화폐 보유(부자) 순위를 보여줍니다.",
            "송금 (유저) (금액)":
                "(유저)에게 자신이 가진 화폐를 (금액)만큼 송금합니다.\n"
                "자신의 보유 금액을 초과해서 보낼 수 없어요!"
        }
    },
    "기타": {
        "desc": None,
        "commands": {
            "링크":
                "봇 초대 링크, 공식 서버 링크 등 다양한 링크를 보여줍니다.",
            "구독 (채널(멘션), 현재 채널)":
                "K-Currencies 공지를 (채널)에 보여줍니다.\n"
                "(관리자 권한 필요)"
        }
    }
}


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="도움", aliases=["도움말", "help"])
    async def help(self, ctx: commands.Context, kind: str = None, *, category: str = None):
        if kind is None:
            embed = discord.Embed(title="K-Currencies 기본 도움말", color=discord.Color.green())
            embed.add_field(name="기본 소개",
                            value="K-Currencies 봇은 K-POP, K-방역과 같이 한국의 화폐 관리 봇이라는 뜻을 담고 있습니다. \n"
                                  "KC봇을 통해 서버 전용 화폐를 만들고 관리하실 수 있습니다. \n"
                                  f"KC봇의 접두사(prefix)는 `!KC `, `!kc `. `!ㅏㅊ `입니다.", inline=False)
            embed.add_field(name="기본 작동 메커니즘",
                            value="KC봇은 서버별 데이터베이스를 생성하여 화폐 데이터를 관리하면, \n"
                                  "화폐 관리 역할을 생성하여 역할을 가진 유저만 서버 데이터를 관리할 수 있습니다. \n"
                                  "KC봇의 주요 기능을 사용하시려면 KC봇에게 '역할 관리' 권한이 필요합니다. \n"
                                  "KC봇을 처음 사용하신다면 서버를 등록하여야 하며, \n"
                                  f"자세한 내용은 `{ctx.prefix}도움 명령어 등록` 명령어를 참고하세요.", inline=False)
            embed.add_field(name="서버 관리 역할",
                            value="서버 데이터 관리 명령어는 이 역할을 가진 유저만이 사용할 수 있습니다. \n"
                                  "서버를 등록할 때 기본적으로 생성되며, 이름은 '은행원'입니다. \n"
                                 f"만약 역할의 이름을 바꾸고 싶으시다면, `{ctx.prefix}도움 명령어 관리` 명령어를 참고하세요.",
                            inline=False)
            embed.add_field(name="서버의 관리자이신가요?",
                            value=f"KC봇에는 채팅 시 보상, 로깅 기능 등 다양한 기능이 있습니다.\n"
                                  f"`{ctx.prefix}도움 특수기능` 명령어를 참고하여 보상 내용, 로깅 채널 등을 설정해주세요.",
                            inline=False)
            embed.add_field(name="전체 명령어 목록",
                            value=f"`{ctx.prefix}도움 명령어 [카테고리]` 명령어를 사용하여 확인하세요. \n"
                                  f"카테고리 목록: `{'`, `'.join(categories.keys())}`", inline=False)
            embed.add_field(name='공식 서버',
                            value=f"KC봇의 공지를 확인하거나 건의, 문의사항이나 봇 사용 중 불편한 점을 말씀해주시려면, \n"
                                  f"[CodeNU 공식 디스코드 서버](https://discord.gg/wThxdtB)에 들어와주세요!\n"
                                  f"(들어오시는 것을 추천드려요!)", inline=False)
            embed.add_field(name="혹시 KC봇에게 도움을 주고 싶으시다면",
                            value=f"KC봇을 위해 KOREANBOTS에서 ❤️를 눌러주세요! \n"
                                  f"[KOREANBOTS KC봇 페이지](https://koreanbots.dev/bots/752354433106706452)\n"
                                  f"또는 KC봇의 개발을 도와주세요! \n"
                                  f"[CodeNU 채용 서버](https://discord.gg/AuJakuguYw)"
                            )
        elif kind == "명령어":
            if category in categories.keys():
                if categories[category]['desc'] is None:
                    embed = discord.Embed(title=f"K-Currencies 도움말 목록 - {category}",
                                          description=f"[필수 입력 항목], (선택 입력 항목, 기본값)",
                                          color=discord.Color.green())
                else:
                    embed = discord.Embed(title=f"K-Currencies 도움말 목록 - {category}",
                                          description=f"{categories[category]['desc']}\n[필수 입력 항목], (선택 입력 항목, 기본값)",
                                          color=discord.Color.green())
                for key, value in categories[category]['commands'].items():
                    embed.add_field(name=key,
                                    value=value,
                                    inline=False)
            else:
                await ctx.send("입력하신 카테고리는 존재하지 않는 카테고리입니다. 다시 입력해주세요.")
                return
        elif kind == "특수기능":
            embed = discord.Embed(title="K-Currencies 특수기능 도움말", color=discord.Color.green())
            embed.add_field(name="로깅",
                            value="로깅 기능은 서버 데이터(예: 화폐 단위 변경)나\n"
                                  "유저 데이터(예: 보유 금액 설정) 등을 변경할 경우\n"
                                  "로그 채널에 알리는 기능입니다.\n"
                                 f"로그 채널 설정 방법은 `{ctx.prefix}도움 명령어 관리` 명령어를 확인해주세요.",
                            inline=False)
            embed.add_field(name="채팅 보상",
                            value="채팅 보상 기능은 유저가 채팅 시 지정한 금액을 지급하는 기능입니다.\n"
                                  "유저당 쿨타임은 1분이며(즉 계속 채팅 시 1분마다 금액이 지급됩니다.),\n"
                                  "채팅 보상 기능을 사용하고 싶지 않으시다면 채팅 보상을 0으로 설정하실 수 있습니다. \n"
                                  "특정 채널만 채팅 보상 기능을 사용하고 싶지 않으시다면\n 채널의 설명 란에 'KC-채팅보상X'를 입력하시면 됩니다.\n"
                                  f"보상 설정 방법은 `{ctx.prefix}도움 명령어 관리` 명령어를 확인해주세요.",
                            inline=False)
        else:
            return
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
