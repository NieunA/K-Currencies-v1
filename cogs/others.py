import discord
from discord.ext import commands

class Others(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(f"!KC 도움 | {len(self.bot.guilds)}곳의 서버에서 돈 계산"))

    @commands.command(name="정보")
    async def info(self, ctx: commands.Context):
        await ctx.send(f"{len(self.bot.guilds)}곳의 서버에서"
                       f" {len(list(self.bot.get_all_members()))}분의 유저와 함께하는 K-Currencies 봇입니다!")

    @commands.command(name="hellothisisverification")
    async def htivc(self, ctx: commands.Context):
        await ctx.send("GPM567#3006")

    @commands.command(name="링크", aliases=("초대링크", "공식서버"))
    async def link(self, ctx: commands.Context):
        embed = discord.Embed(title="유용한 링크")
        embed.add_field(name="KC봇 초대 링크",
                        value="[KC봇 초대](https://discord.com/api/oauth2/authorize"
                              "?client_id=752354433106706452&permissions=8&scope=bot)", inline=False)
        embed.add_field(name="KOREANBOTS 페이지 링크",
                        value="❤️를 눌러주세요! \n"
                              "[KOREANBOTS KC봇 페이지](https://koreanbots.dev/bots/752354433106706452)",
                        inline=False)
        embed.add_field(name="CodeNU 공식 서버 링크",
                        value="[CodeNU 공식 서버](https://discord.gg/wThxdtB)",
                        inline=False)
        embed.add_field(name="CodeNU 채용 서버 링크",
                        value="[CodeNU 채용 서버](https://discord.gg/bw5sR7mDAZ)",
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="구독")
    @commands.has_guild_permissions(administrator=True)
    async def subscribe(self, ctx: commands.Context, channel: discord.TextChannel = None):
        byChannel: discord.TextChannel = self.bot.get_channel(892421007955079218)
        await byChannel.follow(destination=ctx.channel if channel is None else channel)

def setup(bot):
    bot.add_cog(Others(bot))