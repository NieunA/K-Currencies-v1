import discord
from discord.ext import commands
import time

from modules import accessToDB, customErrors

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chatReward = {}
        self.lastTime = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            try:
                guildData = await accessToDB.getServerData(guild.id)
                self.chatReward[guild.id] = guildData["chatReward"]
                self.lastTime[guild.id] = {}
            except:
                pass


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        try:
            if self.chatReward[message.guild.id] == 0:
                return
        except KeyError:
            return
        if message.guild is None or message.author.bot:
            return
        if "KC-채팅보상X" in str(message.channel.topic):
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



def setup(bot):
    bot.add_cog(Events(bot))