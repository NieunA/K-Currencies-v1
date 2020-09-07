import discord
from discord.ext import commands

class Others(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(f"{len(self.bot.guilds)}곳의 서버에서 돈 계산"))

    @commands.command(name="정보")
    async def info(self, ctx: commands.Context):
        await ctx.send(f"{len(self.bot.guilds)}곳의 서버에서"
                       f" {len(list(self.bot.get_all_members()))}분의 유저와 함께하는 K-Currencies 봇입니다!")

    @commands.command(name="hellothisisverification")
    async def htivc(self, ctx: commands.Context):
        await ctx.send("GPM567#3006")

def setup(bot):
    bot.add_cog(Others(bot))