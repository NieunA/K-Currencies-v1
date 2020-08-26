import discord
from discord.ext import commands
import os

releaseToken = "Njk3Njc2NTcwNDI4NDQwNTg2.XsSIpA.YWkZZ9g25ybZn8HvjqRkcgzBZhI"
canaryToken = "NzAzMjQwOTg4NjI5NjYzNzg0.XqLuPA.Uvmj20wkag0s3oCEvfSJpWg2UMk"


async def get_prefix(bot, message):
    return commands.when_mentioned_or("!CM ")(bot, message)


bot = commands.Bot(command_prefix=get_prefix, help_command=None)

isRelease = False

releasePassFiles = []
canaryPassFiles = []

if isRelease:
    passFile = releasePassFiles
else:
    passFile = canaryPassFiles

[bot.load_extension(f"cogs.{x.replace('.py', '')}") for x in os.listdir("./cogs") if x.endswith('.py') and x not in passFile]

if isRelease:
    token = releaseToken
else:
    token = canaryToken
bot.run(token)
