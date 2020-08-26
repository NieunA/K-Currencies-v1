import discord
from discord.ext import commands
import os

releaseToken = "Njk3Njc2NTcwNDI4NDQwNTg2.XsSIpA.YWkZZ9g25ybZn8HvjqRkcgzBZhI"
canaryToken = "NzAzMjQwOTg4NjI5NjYzNzg0.XqLuPA.Uvmj20wkag0s3oCEvfSJpWg2UMk"

bot = commands.Bot(command_prefix="!CM ", help_command=None)

isRelease = False

releasePassFiles = []
canaryPassFiles = []

for filename in os.listdir("./cogs"):
    if isRelease:
        passFile = releasePassFiles
    else:
        passFile = canaryPassFiles
    if not filename in passFile:
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

if isRelease:
    token = releaseToken
else:
    token = canaryToken
bot.run(token)