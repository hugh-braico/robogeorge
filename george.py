# bot.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

# print server connection info
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following server:\n'
        f'{guild.name} (id: {guild.id})\n'
    )


# test a command 
@bot.command(name='walk', help='Posts a gif of George walking')
async def walk_command(ctx):
    print(f"User {ctx.author} used the !walk command in channel {ctx.channel}")
    await ctx.send("https://cdn.discordapp.com/emojis/671277691755823104.gif")


# test a command 
@bot.command(name='number', help='Test thing')
async def number(ctx, arg: int):
    print(f"User {ctx.author} used the !number command in channel {ctx.channel}")
    await ctx.send(f"You sent the number {arg}.")


if __name__ == "__main__":
    bot.run(TOKEN)
