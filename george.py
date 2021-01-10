import os
import discord
import csv
import datetime as dt
from sys import exit
from discord import User
from discord.ext import commands
from dotenv import load_dotenv
import yomocoins as yc

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SEAJAY = int(os.getenv('SEAJAY'))
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

################################################################################
#
### Bot maintenance

# print server connection info
@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following server(s):\n')
    for guild in bot.guilds:
        print(f'{guild.name} (id: {guild.id})\n')


# simple ping test
@bot.command(name='ping')
@commands.guild_only()
async def ping(ctx):
    await ctx.send(f"🏓 approx. latency = {round(bot.latency, 3)}s");
    

# shoot the bot
@bot.command(name='bang')
@commands.guild_only()
async def bang(ctx):
    if ctx.author.id == SEAJAY: 
        await ctx.send("https://cdn.discordapp.com/emojis/774135280206348290.png")
        await ctx.send("Shutting down...")
        yc.save_coins("yomocoins.csv")
        exit(0)
    else: 
        await ctx.send("https://cdn.discordapp.com/emojis/748106041711001742.png")


# basic error handling
@bot.event
async def on_command_error(ctx, error):      
    # This prevents any commands with local handlers being handled here
    if hasattr(ctx.command, 'on_error'):
        return

    # Allows us to check for original exceptions raised and sent to CommandInvokeError.
    # If nothing is found. We keep the exception passed to on_command_error.
    error = getattr(error, 'original', error)

    if isinstance(error, commands.DisabledCommand):
        await ctx.send(f'{ctx.command} has been disabled.')

    elif isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        except discord.HTTPException:
            pass

    # For this error example we check to see where it came from...
    elif isinstance(error, commands.BadArgument):
        if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
            await ctx.send('I could not find that member. Please try again.')
        else:
            await ctx.send('Invalid command arguments.')

    else:
        await ctx.send('Something went wrong.')
        # All other Errors not returned come here. And we can just print the default TraceBack.
        print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


################################################################################
#
### YomoCoins

# set someone's yomocoins (admin only, obviously)
@bot.command(name='set')
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def set(ctx, user: User, coins: int):
    yc.set_coins(user.id, coins)
    await ctx.send(f"{user}'s YomoCoins set to {coins}.")
    yc.save_coins_if_necessary("yomocoins.csv")


# give someone yomocoins
@bot.command(name='give')
@commands.guild_only()
async def give(ctx, recipient: User, coins: int):
    giver = ctx.author
    giver_coins = yc.get_coins(giver.id)
    recipient_coins = yc.get_coins(recipient.id)

    if giver_coins is None:
        await ctx.send(f"You don't appear to be in the YomoCoins system yet.")
    elif recipient_coins is None: 
        await ctx.send(f"{recipient.name} doesn't appear to be in the YomoCoins system yet.")
    elif recipient.id == giver.id: 
        await ctx.send(f"You can't give yourself YomoCoins.")
    elif coins <= 0: 
        await ctx.send(f"Invalid amount of YomoCoins.")
    elif giver_coins < coins: 
        await ctx.send(f"https://cdn.discordapp.com/emojis/780232729173164112.png")
        await ctx.send(f"You only have {giver_coins} YomoCoins to give.")
    else: 
        yc.set_coins(giver.id, giver_coins - coins)
        yc.set_coins(recipient.id, recipient_coins + coins)
        await ctx.send(f"You have given {recipient.name} {coins} YomoCoins.")
    yc.save_coins_if_necessary("yomocoins.csv")


# award someone yomocoins (admin only)
@bot.command(name='award')
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def award(ctx, recipient: User, coins: int):
    recipient_coins = yc.get_coins(recipient.id)
    if recipient_coins is None: 
        await ctx.send(f"{recipient.name} doesn't appear to be in the YomoCoins system yet.")
    elif coins <= 0: 
        await ctx.send(f"Invalid amount of YomoCoins.")
    else: 
        if ctx.author.id == recipient.id: 
            await ctx.send("https://i.kym-cdn.com/entries/icons/facebook/000/030/329/cover1.jpg")
        yc.set_coins(recipient.id, recipient_coins + coins)
        await ctx.send(f"Awarded {recipient.name} {coins} YomoCoins.")
    yc.save_coins_if_necessary("yomocoins.csv")


# save yomocoins
@bot.command(name='save')
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def save(ctx):
    yc.save_coins("yomocoins.csv")
    await ctx.send(f"YomoCoins saved!")
    

# list everyone's yomocoins
@bot.command(name='list')
@commands.guild_only()
async def list(ctx):
    coins_list = '\n'.join([   
        f"""{bot.get_user(int(user_id)).name}: {yc.get_coins(user_id)} YomoCoins.""" 
        for user_id in yc.sorted_coins_list()
    ])
    await ctx.send(coins_list)
    

# print one person's yomocoins
@bot.command(name='coins')
@commands.guild_only()
async def single_coins(ctx, user: User = None):
    if user is None: 
        user = ctx.author
    coins = yc.get_coins(user.id)
    if coins is None:
        await ctx.send(f"""Invalid user, or user is not in the YomoCoins database yet.""")
    else: 
        await ctx.send(f"""{user.name} has {coins} coins.""")


################################################################################
#
### Betting

# start betting round

# cancel betting round

# report betting round

# make a bet 


# main function
if __name__ == "__main__":
    yc.load_coins("yomocoins.csv")
    now = dt.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H%M")
    yc.save_coins(f"yomocoin_backups/yomocoins_{timestamp}.csv")
    bot.run(TOKEN)
