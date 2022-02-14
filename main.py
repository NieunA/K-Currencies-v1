import discord
from discord.ext import commands
import os
import koreanbots
import jishaku
import json
import logging
from cogs import *
from modules import accessToDB

with open("data/mainData.json", "r") as f:
    mainData = json.load(f)

mode = mainData['bot']['mode']

prefixes = [
    f"!KC{'B' if mode == 'beta' else ''} ",
    f"!kc{'b' if mode == 'beta' else ''} ",
    f"!ㅏ{'츄' if mode == 'beta' else 'ㅊ'} ",
]

passFiles = {
    "release": ["error"],
    "beta": ["error"]
}

async def get_prefix(bot, message):
    return commands.when_mentioned_or(*prefixes)(bot, message)

intents: discord.Intents = discord.Intents.all()

bot = commands.Bot(command_prefix=get_prefix, help_command=None, intents=intents, owner_ids=[288302173912170497, 665450122926096395, 868164373548531712])
tokens = mainData["bot"]["token"]

[bot.load_extension(f"cogs.{x.replace('.py', '')}") for x in os.listdir("cogs") if x.endswith('.py') and x[:-3] not in passFiles[mode]]
bot.load_extension("jishaku")

bot.run(tokens[mode])
