import json
import os

import discord
from discord.ext import commands

with open('data/mainData.json', 'r') as f:
    config = json.load(f)

mode = config['mode']
bot_config = config[mode]['bot']

excludes = ['error']


async def get_prefix(_bot, message):
    return commands.when_mentioned(_bot, message) + bot_config['prefixes']


def load_cogs(_bot):
    _bot.load_extension("jishaku")
    for cog in os.listdir('cogs'):
        (name, ext) = os.path.splitext(cog)
        if ext != '.py' or name in ['error']:
            continue
        _bot.load_extension(f'cogs.{name}')
        print(f'Loading the cog: {name}')


intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, help_command=None, intents=intents, owner_ids=bot_config['owners'])
load_cogs(bot)
bot.run(bot_config['token'])
