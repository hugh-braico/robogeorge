import os
import discord
import csv
import datetime as dt
import sys
import traceback
from discord import User
from discord.ext import commands
from dotenv import load_dotenv
import yomocoins

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SEAJAY = int(os.getenv('SEAJAY'))
intents = discord.Intents.default()
intents.members = True
daily_amount = 25
bot = commands.Bot(command_prefix='!', intents=intents)
yc = yomocoins.YomoCoins()

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
@bot.command(name='bang', aliases=['kill'])
@commands.guild_only()
async def bang(ctx):
    if ctx.author.id == SEAJAY: 
        await ctx.send("https://cdn.discordapp.com/emojis/774135280206348290.png")
        await ctx.send("🖥️ Saving YomoCoins database and shutting down...")
        yc.save_coins("yomocoins.csv")
        sys.exit(0)
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
        await ctx.send(f'⚠️ {ctx.command} has been disabled.')
    elif isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        except discord.HTTPException:
            pass
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("⚠️ I don't recognise that command. Try `!help` for a list of all commands.")
    elif isinstance(error, commands.BadArgument):
        if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
            await ctx.send('⚠️ I could not find that member. Please try again.')
        else:
            await ctx.send('⚠️ Invalid command arguments. Maybe try `!help <command>`.')
    else:
        await ctx.send('⚠️ Something went wrong. If you formed your command properly, get CJ to fix his shitty python code.')
        # All other Errors not returned come here. And we can just print the default TraceBack.
        print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


################################################################################
#
### YomoCoins


# opt into the YomoCoins system
@bot.command(name='optin', aliases=['opt_in'])
@commands.guild_only()
async def optin(ctx):
    if yc.get_coins(ctx.author.id) is None:
        yc.set_coins(ctx.author.id, 310)
        await ctx.send(f"🪙 Welcome to YomoCoins! You have been given 310 starting YomoCoins.")
    else: 
        await ctx.send(f"❌ You have already opted in.")
    yc.save_coins_if_necessary("yomocoins.csv")


# set someone's yomocoins (admin only, obviously)
@bot.command(name='set', aliases=['setcoins', 'set_coins'])
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def set(ctx, user: User, coins: int):
    yc.set_coins(user.id, coins)
    await ctx.send(f"🪙 {user}'s YomoCoins set to {coins}.")
    yc.save_coins_if_necessary("yomocoins.csv")


# give someone yomocoins
@bot.command(name='give', aliases=['givecoins', 'give_coins', 'givecoin', 'give_coin'])
@commands.guild_only()
async def give(ctx, recipient: User, coins: int):
    giver = ctx.author
    giver_coins = yc.get_coins(giver.id)
    recipient_coins = yc.get_coins(recipient.id)

    if giver_coins is None:
        await ctx.send(f"❌ You don't appear to be in the YomoCoins system yet.")
    elif recipient_coins is None: 
        await ctx.send(f"❌ {recipient.name} doesn't appear to be in the YomoCoins system yet.")
    elif recipient.id == giver.id: 
        await ctx.send(f"❌ You can't give yourself YomoCoins.")
    elif coins <= 0: 
        await ctx.send(f"❌ Invalid amount of YomoCoins.")
    elif giver_coins < coins: 
        await ctx.send(f"https://cdn.discordapp.com/emojis/780232729173164112.png")
        if giver_coins == 0: 
            await ctx.send(f"❌ You don't have any YomoCoins to give.")
        elif giver_coins == 1:
            await ctx.send(f"❌ You only have 1 YomoCoin to give.")
        else:
            await ctx.send(f"❌ You only have {giver_coins} YomoCoins to give.")
    else: 
        yc.set_coins(giver.id, giver_coins - coins)
        yc.set_coins(recipient.id, recipient_coins + coins)
        await ctx.send(f"🪙 You have given {recipient.name} {coins} YomoCoins.")
    yc.save_coins_if_necessary("yomocoins.csv")


# award someone yomocoins (admin only)
@bot.command(name='award', aliases=['awardcoins', 'award_coins', 'awardcoin', 'award_coin'])
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def award(ctx, recipient: User, coins: int):
    recipient_coins = yc.get_coins(recipient.id)
    if recipient_coins is None: 
        await ctx.send(f"❌ {recipient.name} doesn't appear to be in the YomoCoins system yet.")
    elif coins <= 0: 
        await ctx.send(f"❌ Invalid amount of YomoCoins.")
    else: 
        if ctx.author.id == recipient.id: 
            await ctx.send("https://i.kym-cdn.com/entries/icons/facebook/000/030/329/cover1.jpg")
        yc.set_coins(recipient.id, recipient_coins + coins)
        await ctx.send(f"🪙 Awarded {recipient.name} {coins} YomoCoins.")
    yc.save_coins_if_necessary("yomocoins.csv")


# save yomocoins
@bot.command(name='save', aliases=['savecoins', 'save_coins', 'savecoin', 'save_coin'])
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def save(ctx):
    yc.save_coins("yomocoins.csv")
    await ctx.send(f"🪙 YomoCoins saved!")
    

# list everyone's yomocoins
@bot.command(name='list', aliases=['listcoins', 'list_coins', 'listcoin', 'list_coin'])
@commands.guild_only()
async def list(ctx):
    coins_list = '\n'.join([   
        f"""🪙 **{bot.get_user(int(user_id)).name}**: {yc.get_coins(user_id)} YomoCoins.""" 
        for user_id in yc.sorted_coins_list()
    ])
    await ctx.send(coins_list)
    

# print one person's yomocoins
@bot.command(name='coins', aliases=['mycoins', 'my_coins', 'check', 'checkcoins', 'check_coins', 'getcoins', 'get_coins'])
@commands.guild_only()
async def single_coins(ctx, user: User = None):
    if user is None: 
        user = ctx.author
    coins = yc.get_coins(user.id)
    if coins is None:
        await ctx.send(f"""❌ Invalid user, or user is not in the YomoCoins database yet.""")
    else: 
        await ctx.send(f"""🪙 {user.name} has {coins} coins.""")
    

# claim daily coins 
@bot.command(name='centrelink', aliases=['dailycoins', 'dole', 'daily', 'daily_coins', 'freecoins', 'free_coins'])
@commands.guild_only()
async def centrelink(ctx):
    recipient_id = ctx.author.id
    recipient_coins = yc.get_coins(recipient_id)
    if recipient_coins == None:
        await ctx.send(f"❌ You don't appear to be in the YomoCoins system yet.")
    elif not yc.check_daily_eligibility(recipient_id):
        await ctx.send(f"❌ You have already claimed today's free daily YomoCoins.")
    else: 
        recipient_coins = yc.get_coins(recipient_id)
        global daily_amount
        yc.set_coins(recipient_id, recipient_coins + daily_amount)
        await ctx.send(f"🪙 Claimed {daily_amount} daily YomoCoins. Come back tomorrow for more.")
    yc.save_coins_if_necessary("yomocoins.csv")


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
