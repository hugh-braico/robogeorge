# bot.py
import os
import discord
import csv
import datetime as dt
from sys import exit
from discord import User
from discord.ext import commands
from dotenv import load_dotenv

import yomocoins as yc
from yomocoins import coins_dict

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
SEAJAY = 202732983910793217

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


# print server connection info
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following server:\n'
        f'{guild.name} (id: {guild.id})\n'
    )


# george walk
@bot.command(name='walk')
async def walk_command(ctx):
    await ctx.send("https://cdn.discordapp.com/emojis/671277691755823104.gif")


# set someone's yomocoins
@bot.command(name='setcoins')
@commands.has_permissions(administrator=True)
async def number(ctx, user: User, coins: int):
    #member = await commands.MemberConverter().convert(ctx, username)
    if int(user.id) not in coins_dict: 
        await ctx.send(f"New user {user} ({user.id}) added to YomoCoin database.")
        coins_dict[user.id] = {}
    coins_dict[user.id]["coins"] = coins
    await ctx.send(f"{user}'s YomoCoins set to {coins}.")
    yc.save_coins_if_necessary("yomocoins.csv")


# save yomocoins
@bot.command(name='savecoins')
@commands.has_permissions(administrator=True)
async def number(ctx):
    yc.save_coins("yomocoins.csv")
    await ctx.send(f"YomoCoins saved!")
    

# list everyone's yomocoins
@bot.command(name='listcoins')
async def number(ctx):
    sorted_coins_list = '\n'.join([   
        f"""{bot.get_user(int(user_id)).name}: {coins_dict[user_id]["coins"]} coins.""" 
        for user_id 
        in sorted(coins_dict, key=lambda x: coins_dict[x]["coins"], reverse=True)
    ])
    await ctx.send(sorted_coins_list)
    yc.save_coins_if_necessary("yomocoins.csv")
    

# print just one person's yomocoins
@bot.command(name='coins')
async def number(ctx, user: User = None):
    if user is None: 
        user = ctx.author
    await ctx.send(f"""{user.name} has {coins_dict[user.id]["coins"]} coins.""")


# shoot the bot
@bot.command(name='bang')
async def number(ctx):
    if ctx.author.id == SEAJAY: 
        await ctx.send("https://cdn.discordapp.com/emojis/774135280206348290.png")
        await ctx.send("Shutting down...")
        yc.save_coins("yomocoins.csv")
        exit(0)
    else: 
        await ctx.send("Did you really think that would work?")



if __name__ == "__main__":

    yc.load_coins("yomocoins.csv")
    now = dt.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H%M")
    yc.save_coins(f"yomocoin_backups/yomocoins_{timestamp}.csv")

    # run bot
    bot.run(TOKEN)
