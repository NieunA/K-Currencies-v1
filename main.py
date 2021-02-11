import discord
from discord.ext import commands
import os
import dbkrpy
from cogs import *
from modules import accessToDB

tokens = {
    "release": "token",
    "beta": "token"
}


async def get_prefix(bot, message):
    return commands.when_mentioned_or(f"!KC{'B' if mode == 'beta' else ''} ")(bot, message)


bot = commands.Bot(command_prefix=get_prefix, help_command=None, intents=discord.Intents.all())

dbkrpy.UpdateGuilds(bot=bot, token="token")

mode = "release"  # release or beta

passFiles = {
    "release": ["error"],
    "beta": ["error"]
}

[bot.load_extension(f"cogs.{x.replace('.py', '')}") for x in os.listdir("./cogs") if x.endswith('.py') and x[:-3] not in passFiles[mode]]

bot.run(tokens[mode])
