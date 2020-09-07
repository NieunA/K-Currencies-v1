import discord
from discord.ext import commands
import os
from cogs import *
from modules import accessToDB

tokens = {
    "release": "NzUyMzU0NDMzMTA2NzA2NDUy.X1Waqg.UcEeM0OG-SJSU8BdPTElDIipudc",
    "canary": "NzUyMzU0NDMzMTA2NzA2NDUy.X1Waqg.UcEeM0OG-SJSU8BdPTElDIipudc"
}


async def get_prefix(bot, message):
    return commands.when_mentioned_or("!KC ")(bot, message)


bot = commands.Bot(command_prefix=get_prefix, help_command=None)

mode = "canary"  # release or canary

passFiles = {
    "release": [],
    "canary": ["error"]
}

[bot.load_extension(f"cogs.{x.replace('.py', '')}") for x in os.listdir("./cogs") if x.endswith('.py') and x[:-3] not in passFiles[mode]]

bot.run(tokens[mode])
