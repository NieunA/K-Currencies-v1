import discord
from discord.ext import commands
import pytz, datetime
from modules import accessToDB, customErrors

async def log(bot: commands.Bot, serverID, title, description):
    data = await accessToDB.getServerData(serverID)
    logChannelID = data["logChannelID"]
    embed = discord.Embed(title=title, description=description, timestamp=datetime.datetime.now(pytz.timezone("Asia/Seoul")))
    await bot.get_guild(serverID).get_channel(logChannelID).send(embed=embed)