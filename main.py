import discord
from discord.ext import commands
import os
import dbkrpy
from cogs import *
from modules import accessToDB

tokens = {
    "release": "NzUyMzU0NDMzMTA2NzA2NDUy.X1Waqg.UcEeM0OG-SJSU8BdPTElDIipudc",
    "beta": "NzUyNzE1NzE4OTk4MzYwMDk0.X1brJA.qp1S7trqFN0YEqKv6CBl_tLj60Y"
}


async def get_prefix(bot, message):
    return commands.when_mentioned_or(f"!KC{'B' if mode == 'beta' else ''} ")(bot, message)


bot = commands.Bot(command_prefix=get_prefix, help_command=None)

dbkrpy.UpdateGuilds(bot=bot, token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijc"
                                   "1MjM1NDQzMzEwNjcwNjQ1MiIsImlhdCI6MTU5OTYxMTc5Miw"
                                   "iZXhwIjoxNjMxMTY5MzkyfQ.Y_Gl_uspPk-xZ3R3jl7-HoCX"
                                   "TuNHK2icKuFV6DWVggm6OD4QuG6OQLZdb_tnLhTGHk3MzcNX"
                                   "KtEKsXFIHjcun3QpYb3rRrVHjLDu-2mYAOoUxoLZimnoPAGR"
                                   "p9c8SCzxVV3BiGPby2ckMjj6Zycra8OwELZYKb1RAYtujTMAdCE")


mode = "release"  # release or beta

passFiles = {
    "release": ["error"],
    "beta": ["error"]
}

[bot.load_extension(f"cogs.{x.replace('.py', '')}") for x in os.listdir("./cogs") if x.endswith('.py') and x[:-3] not in passFiles[mode]]

bot.run(tokens[mode])
