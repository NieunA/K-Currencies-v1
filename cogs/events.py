import discord
from discord.ext import commands
import time
import json
import datetime
import koreanbots
from koreanbots.integrations.discord import DiscordpyKoreanbots

from modules import accessToDB, customErrors

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chatReward = {}
        self.lastTime = {}


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Bot {str(self.bot.user)}, Ready.")
        await self.bot.change_presence(activity=discord.Game(f"!KC 도움 | {len(self.bot.guilds)}곳의 서버에서 돈 계산"))
        for guild in self.bot.guilds:
            try:
                await self.addServer(guild)
            except:
                pass
        with open("data/mainData.json", "r") as f:
            mainData = json.load(f)
        if self.bot.user.id == 752354433106706452:
            self.krb = DiscordpyKoreanbots(self.bot, mainData["koreanbots"]['release']["token"], run_task=True)

    async def addServer(self, guild):
        guildData = await accessToDB.getServerData(guild.id)
        self.chatReward[guild.id] = guildData["chatReward"]
        self.lastTime[guild.id] = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel):
            return
        try:
            if self.chatReward[message.guild.id] == 0:
                return
        except KeyError:
            return
        if message.guild is None:
            return
        if message.author.bot:
            return
        if isinstance(message.channel, discord.Thread):
            if "KC-채팅보상X" in message.channel.parent.topic:
                return
        elif "KC-채팅보상X" in str(message.channel.topic):
            return
        now = time.time()
        guildID = message.guild.id
        userID = message.author.id
        serverData = await accessToDB.getServerData(guildID)

        if userID not in self.lastTime[guildID].keys():
            self.lastTime[guildID][userID] = now
            userData = await accessToDB.getUserData(guildID, userID)
            userData["money"] += serverData["chatReward"]
            await accessToDB.setUserData(guildID, userID, userData)

        elif self.lastTime[message.guild.id][message.author.id] + 60 < now:
            self.lastTime[guildID][userID] = now
            userData = await accessToDB.getUserData(guildID, userID)
            userData["money"] += serverData["chatReward"]
            await accessToDB.setUserData(guildID, userID, userData)

    """
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        
        with open("../data/serverToDel.json", 'r') as f:
            data = json.load(f)
            data.append([guild.id, time.time()])

        with open("../data/serverToDel.json", 'w') as f:
            json.dump(data, f)
        

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        
        toRemove = []
        with open("../data/serverToDel.json", 'r') as f:
            data = json.load(f)
        for i, item in data:
            if guild.id == data[0]:
                toRemove.append(i)
        for i in toRemove:
            del data[i]
        if toRemove:
            with open("../data/serverToDel.json", 'w') as f:
                json.dump(data, f)
    """



def setup(bot):
    bot.add_cog(Events(bot))