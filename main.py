import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
import random
import config
import util


load_dotenv() 
token = os.getenv('TOKEN')
app_id = os.getenv('APP_ID')
guild_id = os.getenv('GUILD_ID')
KNS = discord.Object(id=guild_id)

description = '''An example bot to showcase the discord.ext.commands extension module.
There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = discord.Client(command_prefix='/', description=description, intents=intents)
# bot = commands.Bot(command_prefix='/', description=description, intents=intents)
tree = app_commands.CommandTree(bot)


@tree.command(name = "ping", description = "pong!", guild = KNS)
async def ping(ctx):
    await ctx.response.send_message("pong!")

@tree.command(name = "weekreport", description = "get bunch of best traders this week!", guild = KNS)
async def weekreport(ctx, uid: str):
    await ctx.response.send_message("We're working on it...")

@tree.command(name = "performance", description = "Show performance of specific trader", guild = KNS)
async def performance(ctx, uid: str):
    resData = util.get_trader_drawdown(uid)
    await ctx.response.send_message("traderName:\n"+ resData['traderName'] + "\nlast month PNL:\n" + str(resData['pnlInDays']))


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    await tree.sync(guild=discord.Object(id = guild_id))
    print('------')



bot.run(token)