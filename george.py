import os
import discord
import csv
import datetime as dt
import sys
import random
import traceback
import asyncio
import aiohttp
from dotenv import load_dotenv

from discord import User
from discord.ext import commands

import yomocoins
import betting
import dueling

# logging stuff
import logging
log = logging.getLogger("yomo")
log.setLevel(logging.DEBUG)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
fh = logging.FileHandler("yomocoin_logs/" + dt.datetime.now().strftime("%Y-%m-%d %H%M") + ".log")
fh.setLevel(logging.DEBUG)
log.addHandler(fh)

# load environment variables
load_dotenv()
TOKEN           = os.getenv('DISCORD_TOKEN')
SEAJAY          = int(os.getenv('SEAJAY'))
BETTING_CHANNEL = int(os.getenv('BETTING_CHANNEL'))
SPAM_CHANNEL    = int(os.getenv('SPAM_CHANNEL'))

# let the bot cache member information and such
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# initialize yomocoins and betting modules
yc = yomocoins.YomoCoins()
betting = betting.Betting()
dueling = dueling.Dueling()

# funny mmr maps between userid and a datetime (when to next generate a mmr change) 
mmr_dict = {}


################################################################################
#
### Bot maintenance

# print server connection info
@bot.event
async def on_ready():
    log.info(f'{bot.user} is connected to the following server(s):')
    for guild in bot.guilds:
        log.info(f'    {guild.name} (id: {guild.id})')


# simple ping test
@bot.command(name='ping', aliases=['pong'], help='Ping test')
@commands.guild_only()
async def ping(ctx):
    await ctx.send(f"🏓 approx. latency = {round(bot.latency, 3)}s");


# cum
@bot.command(name='cum', aliases=['kum'], help='Ping test')
@commands.guild_only()
async def cum(ctx):
    await ctx.send(f"`* But nobody came.`");


# simple ping test
@bot.command(name='coinflip', help='Flips a coin')
@commands.guild_only()
async def coinflip(ctx, option1: str = "heads", option2: str = "tails"):
    await ctx.send(f"Flipping...");
    await asyncio.sleep(1)
    flip_result = random.randint(1,2)
    if flip_result == 1: 
        await ctx.send(f"🪙 Coin landed on **heads**. {option1} it is!");
    else: 
        await ctx.send(f"🪙 Coin landed on **tails**. {option2} it is!");


# shoot the bot
@bot.command(name='kill', aliases=['bang'], help='Kills the bot (SeaJay only)')
@commands.guild_only()
async def bang(ctx):
    if ctx.author.id == SEAJAY: 
        if betting.is_active(): 
            await ctx.send("❌ `!cancel` or `!winner` the current betting round before shutting down.")
        else:
            await ctx.send("<:sadcat:712998237975478282> Saving YomoCoins database and shutting down...")
            yc.save_coins("yomocoins.csv")
            yc.backup_coins()
            log.info("Shutting down (responding to !kill command)")
            await bot.close()
    else: 
        await ctx.send("<:squint:749549668954013696> You don't have the right permissions to do that.")


# funny meme mmr command
@bot.command(name='mmr', aliases=["MMR"], help='Check how your MMR is doing')
@commands.guild_only()
async def mmr(ctx):
    user_id = ctx.author.id
    now = dt.datetime.now()
    if user_id not in mmr_dict or mmr_dict[user_id] < now:
        flip_result = random.randint(1,2)
        if flip_result == 1: 
            await ctx.send("📈 Your MMR has gone up!")
        else:
            await ctx.send("📉 Your MMR has gone down...")
        # Add a somewhat random amount of minutes between changes
        random_minutes = random.randint(30,300)
        mmr_dict[user_id] = now + dt.timedelta(minutes=random_minutes)
    else: 
        await ctx.send("Your MMR has not changed since you last checked.")


# basic error handling
@bot.event
async def on_command_error(ctx, error):      
    # Prevents any commands with local handlers being handled here
    if hasattr(ctx.command, 'on_error'):
        return
    error = getattr(error, 'original', error)
    if isinstance(error, commands.DisabledCommand):
        await ctx.send(f'<:squint:749549668954013696> {ctx.command} has been disabled.')
    elif isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        except discord.HTTPException:
            pass
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("<:squint:749549668954013696> I don't recognise that command. Try `!help` for a list of all commands.")
    elif isinstance(error, commands.BadArgument):
        if ctx.command.qualified_name == 'tag list':
            await ctx.send('<:squint:749549668954013696> I could not find that member. Please try again.')
        else:
            await ctx.send('<:squint:749549668954013696> Invalid command arguments. Maybe try `!help <command>`.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("<:squint:749549668954013696> Looks like you didn't supply enough arguments. Maybe try `!help <command>`.")
    elif isinstance(error, commands.ExpectedClosingQuoteError) or isinstance(error, commands.UnexpectedQuoteError):
        await ctx.send("<:squint:749549668954013696> Looks like you didn't close your double quotes properly.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("<:squint:749549668954013696> You don't have the right permissions to do that.")
    elif isinstance(error, aiohttp.client_exceptions.ClientConnectorError):
        log.info("!save: DISCONNECT DETECTED - saving coins and closing")
        yc.save_coins("yomocoins.csv")
        yc.backup_coins()
        await bot.close()
    else:
        await ctx.send('<:squint:749549668954013696> An unknown error occurred. CJ needs to check the server log and fix it.')
        print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def get_username(user_id: int): 
    try:
        ret = bot.get_user(user_id).name
    except:
        ret = "Missing user"
    return ret


################################################################################
#
### YomoCoins

# opt into the YomoCoins system
@bot.command(name='optin', aliases=['opt_in'], help='Opt into YomoCoins, get 310 starting coins')
@commands.guild_only()
async def optin(ctx):
    if yc.get_coins(ctx.author.id) is None:
        yc.set_coins(ctx.author.id, 310, ctx.author.name)
        log.info(f"!optin: adding {ctx.author.name} to YomoCoins")
        await ctx.send(f"🪙 Welcome to YomoCoins! You have been given 310 starting YomoCoins.")
    else: 
        await ctx.send(f"<:squint:749549668954013696> You have already opted in.")
    yc.save_coins_if_necessary("yomocoins.csv")


# set someone's yomocoins
@bot.command(name='set', help="Set a user's coins (admin only)")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def set(ctx, user: User, coins: int):
    log.info(f"!set: admin {ctx.author.name} setting {user.name}'s coins to {coins}")
    yc.set_coins(user.id, coins, user.name)
    await ctx.send(f"🪙 {user.name}'s YomoCoins set to {coins}.")
    yc.save_coins_if_necessary("yomocoins.csv")


# give someone yomocoins
@bot.command(name='give', help="Give some of your coins to another user")
@commands.guild_only()
async def give(ctx, recipient: User, coins: int):
    giver = ctx.author
    giver_coins = yc.get_coins(giver.id)
    recipient_coins = yc.get_coins(recipient.id)

    if giver_coins is None:
        await ctx.send(f"<:squint:749549668954013696> You don't appear to be in the YomoCoins system yet. Use `!optin`")
    elif recipient_coins is None: 
        await ctx.send(f"<:squint:749549668954013696> {recipient.name} doesn't appear to be in the YomoCoins system yet. Use `!optin`")
    elif recipient.id == giver.id: 
        await ctx.send(f"<:squint:749549668954013696> You can't give yourself YomoCoins.")
    elif coins <= 0: 
        await ctx.send(f"<:squint:749549668954013696> Invalid amount of YomoCoins.")
    elif giver_coins < coins: 
        if giver_coins == 0: 
            await ctx.send(f"<:squint:749549668954013696> You don't have any YomoCoins to give. Maybe try `!centrelink`?")
        elif giver_coins == 1:
            await ctx.send(f"<:squint:749549668954013696> You only have 1 YomoCoin to give. Maybe try `!centrelink`?")
        else:
            await ctx.send(f"<:squint:749549668954013696> You only have {giver_coins} YomoCoins to give.")
    else: 
        log.info(f"!give: {giver.name} giving {recipient.name} {coins} coins")
        yc.set_coins(giver.id, giver_coins - coins, giver.name)
        yc.set_coins(recipient.id, recipient_coins + coins, recipient.name)
        if coins == 1:
            await ctx.send(f"🪙 You have given {recipient.name} a single YomoCoin. They now have {recipient_coins + coins}.")
        else:
            await ctx.send(f"🪙 You have given {recipient.name} {coins} YomoCoins. They now have {recipient_coins + coins}.")
    yc.save_coins_if_necessary("yomocoins.csv")


# award someone yomocoins (admin only)
@bot.command(name='treat', aliases=['award'], help="Award coins as a treat (admin only)")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def award(ctx, recipient: User, coins: int):
    recipient_coins = yc.get_coins(recipient.id)
    if recipient_coins is None: 
        await ctx.send(f"<:squint:749549668954013696> {recipient.name} doesn't appear to be in the YomoCoins system yet. Use `!optin`")
    elif coins == 0: 
        await ctx.send(f"https://www.youtube.com/watch?v=M5QGkOGZubQ")
    elif coins < 0 and (recipient_coins + coins) < 0: 
        await ctx.send(f"<:squint:749549668954013696> {recipient.name} only has {recipient_coins} YomoCoins to lose.")
    else: 
        log.info(f"!treat: admin {ctx.author.name} awarding {recipient.name} {coins} coins")
        if ctx.author.id == recipient.id:
            if coins > 0: 
                await ctx.send("https://i.kym-cdn.com/entries/icons/facebook/000/030/329/cover1.jpg")
            else: 
                await ctx.send("https://cdn.discordapp.com/attachments/396643053600899084/801071689337274388/trust_nobody.png")
        yc.set_coins(recipient.id, recipient_coins + coins, recipient.name)
        if coins == 1:
            await ctx.send(f"🪙 {recipient.name} can have a YomoCoin, as a treat. They now have {recipient_coins + coins}.")
        elif coins < 0:
            await ctx.send(f"🪙 {recipient.name} had {-coins} of their YomoCoins revoked. They now have {recipient_coins + coins}.")
        else: 
            await ctx.send(f"🪙 {recipient.name} can have {coins} YomoCoins, as a treat. They now have {recipient_coins + coins}.")
    yc.save_coins_if_necessary("yomocoins.csv")


# save yomocoins
@bot.command(name='save', help="Manually save the coin database (admin only)")
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def save(ctx):
    log.info("!save: saving coins")
    yc.save_coins("yomocoins.csv")
    yc.backup_coins()
    await ctx.send(f"💰 YomoCoins saved!")
    

# list everyone's yomocoins
@bot.command(name='list', aliases=['listcoins', 'list_coins', 'listcoin', 'list_coin'], help="List how many coins everyone has")
async def list(ctx, options: str ="default"):
    if options == "all":
        if ctx.channel.id != BETTING_CHANNEL:
            total_coins = sum([yc.get_coins(user_id) for user_id in yc.sorted_coins_list()])
            await ctx.send('\n'.join([   
                f"""🪙 {placing}. **{get_username(user_id)}**: {yc.get_coins(user_id)} YomoCoins.""" 
                for (placing, user_id) in enumerate(yc.sorted_coins_list(), 1)
            ]))
        else:  
            await ctx.send(f"""❌ That command is only allowed in {bot.get_channel(SPAM_CHANNEL).mention} or in DMs.""")
    elif options == "winrate": 
        if ctx.channel.id != BETTING_CHANNEL:
            await ctx.send('\n'.join([   
                f"""🪙 {placing}. **{get_username(user_id)}**: {winrate:.2f}%.""" 
                for (placing, (user_id, winrate)) in enumerate(yc.sorted_winrate_list(), 1)
            ]))
        else:  
            await ctx.send(f"""❌ That command is only allowed in {bot.get_channel(SPAM_CHANNEL).mention} or in DMs.""")
    elif options == "default":
        coins_list = yc.sorted_coins_list()
        top5_list = coins_list[:5]
        bottom5_list = coins_list[-5:]

        top5_message = '\n'.join([   
            f"""🪙 {placing}. **{get_username(user_id)}**: {yc.get_coins(user_id)} YomoCoins.""" 
            for (placing, user_id) in enumerate(top5_list, 1)
        ])

        user_id = ctx.author.id
        user_coins = yc.get_coins(user_id)
        user_in_top5    = any(u == user_id for u in    top5_list)
        user_in_bottom5 = any(u == user_id for u in bottom5_list)

        if user_coins is None or user_in_top5 or user_in_bottom5:
            user_message = ""
        else:
            user_placing = coins_list.index(user_id) + 1
            user_message = f"""🪙 {user_placing}. **{ctx.author.name}**: {user_coins} YomoCoins.\n...\n"""

        # placing of the 5th last user, for numbering display 
        bottom5_start_placing = len(coins_list) - 4

        bottom5_message = '\n'.join([   
            f"""🪙 {placing}. **{get_username(user_id)}**: {yc.get_coins(user_id)} YomoCoins.""" 
            for (placing, user_id) in enumerate(bottom5_list, bottom5_start_placing)
        ])

        await ctx.send(top5_message + "\n...\n" + user_message + bottom5_message)

    else:
        await ctx.send(f"""<:squint:749549668954013696> The only valid options are `all` or no option.""")

    
# print one person's yomocoins
@bot.command(name='coins', aliases=['coin', 'balance', 'mycoins', 'my_coins', 'checkcoins', 'check_coins'], help="List how many coins you have, or a specific user")
async def single_coins(ctx, user: User = None):
    if user is None: 
        user = ctx.author
    coins = yc.get_coins(user.id)
    if coins is None:
        await ctx.send(f"""<:squint:749549668954013696> Invalid user, or user is not in the YomoCoins database yet. If the latter, use `!optin`""")
    elif coins == 0:
        await ctx.send(f"""<:hmmge:798436267435884584> {user.name} is **totally bankrupt.**""")
    elif coins == 1:
        await ctx.send(f"""<:hmmge:798436267435884584>🪙 {user.name} has **1** YomoCoin.""")
    else: 
        await ctx.send(f"""🪙 {user.name} has **{coins}** YomoCoins.""")


# print all yomocoins in circulation
@bot.command(name='totalcoins', aliases=['allcoins', 'economy'], help="Calculate total number of coins in circulation")
async def totalcoins(ctx):
    total_coins = sum([yc.get_coins(uid) for uid in yc.sorted_coins_list()])
    await ctx.send(f"""🪙 Total number of coins in circulation: **{total_coins}** YomoCoins.""")

    
# print one person's betting stats
@bot.command(name='stats', help="Betting statistics for yourself (or a specific user)")
async def betting_stats(ctx, user: User = None):
    if user is None: 
        user = ctx.author
    user_id = user.id
    coins = yc.get_coins(user_id)
    if coins is None:
        await ctx.send(f"""<:squint:749549668954013696> Invalid user, or user is not in the YomoCoins database yet. If the latter, use `!optin`""")
    else: 
        wins         = yc.get_wins(user_id)
        losses       = yc.get_losses(user_id)
        total_bets   = wins + losses
        streak       = yc.get_streak(user_id)
        best_streak  = yc.get_best_streak(user_id)
        biggest_win  = yc.get_biggest_win(user_id)
        biggest_loss = yc.get_biggest_loss(user_id)

        # watch out for funny divide-by-zero pitfall
        if total_bets > 0: 
            win_float = float(100 * wins / total_bets)
            win_rate = f"{win_float:.2f}%"
        else:
            win_rate = "N/A"

        if win_float >= 50.0: 
            display_emote = "📈"
        else:
            display_emote = "📉"

        await ctx.send(
            display_emote + f" **{user.name}**'s betting stats:\n" + 
            f"**Wins:** {wins}/{total_bets}\n" + 
            f"**Win rate:** {win_rate}\n" + 
            f"**Current win streak:** {streak}\n" + 
            f"**Best win streak:** {best_streak}\n" + 
            f"**Biggest win:** {biggest_win}\n" + 
            f"**Biggest loss:** {biggest_loss}" 
        ) 
    

# claim daily coins 
@bot.command(name='centrelink', aliases=['cenno', "cenny", "gimme", "newstart", "jobkeeper", "jobseeker", "dole", "youthallowance"], help="Claim a daily 25 coins")
@commands.guild_only()
async def centrelink(ctx, option: str=None):
    recipient_id = ctx.author.id
    recipient_coins = yc.get_coins(recipient_id)
    if recipient_coins == None:
        await ctx.send(f"<:squint:749549668954013696> You don't appear to be in the YomoCoins system yet. Use `!optin`")
    elif yc.get_daily_claimed(recipient_id) and not (option == "--force" and ctx.author.guild_permissions.administrator):
        if option == "--force": 
            await ctx.send("<:squint:749549668954013696> You don't have the right permissions to do that.")
        else:
            await ctx.send(f"<:squint:749549668954013696> You have already claimed today's free daily YomoCoins.")
    elif recipient_coins >= 2023:
        await ctx.send(f"❌ You have failed the means test, so your Centrelink payments have been cancelled.")
    elif yc.is_richest_yomofan(recipient_id):
        await ctx.send(f"❌ You are the richest YomoFan, so your Centrelink payments have been cancelled.")
    elif betting.bet_exists(recipient_id):
        await ctx.send(f"❌ Can't claim Centrelink while betting (or you would be able to cheat the means test).")
    elif dueling.is_active() and dueling.get_challenger() == recipient_id:
        await ctx.send(f"❌ Can't claim Centrelink while dueling (or you would be able to cheat the means test).")
    else:
        recipient_coins = yc.get_coins(recipient_id)
        if recipient_coins < 87: 
            daily_amount = 50
        elif recipient_coins < 135:
            daily_amount = int(93 - recipient_coins/2)
        elif recipient_coins < 1975:
            daily_amount = 25
        elif recipient_coins < 2023:
            daily_amount = int(1012 - recipient_coins/2)
        else: 
            daily_amount = 0
        log.info(f"!centrelink: {ctx.author.name} claiming {daily_amount} coins") 
        yc.set_coins(recipient_id, recipient_coins + daily_amount, ctx.author.name)
        yc.set_daily_claimed(recipient_id)
        if option == "--force":
            await ctx.send(f"⚠️ Bypassing Centrelink daily quota. This should only be used for testing purposes!")
        await ctx.send(f"🪙 Claimed {daily_amount} daily YomoCoins. You now have {recipient_coins + daily_amount}.")
        yc.save_coins_if_necessary("yomocoins.csv")


# spend 100 coins to remove rand(5,15) of someone else's (they will always hold onto their last coin though)
@bot.command(name='slap', help="Spend 200 coins to take away ~10 of someone's coins")
@commands.guild_only()
async def slap(ctx, victim: User):
    slapper = ctx.author
    slapper_coins = yc.get_coins(slapper.id)
    victim_coins = yc.get_coins(victim.id)
    slap_cost = 200
    slap_amount = random.randint(10,15)
    crit_chance = 0.02

    if slapper_coins is None:
        await ctx.send(f"<:squint:749549668954013696> You don't appear to be in the YomoCoins system yet. Use `!optin`")
    elif victim_coins is None: 
        await ctx.send(f"<:squint:749549668954013696> **{victim.name}** doesn't appear to be in the YomoCoins system yet. Use `!optin`")
    elif slapper.id == victim.id: 
        await ctx.send(f"❌ You can't slap yourself.\n<:squint:749549668954013696> ...Well, you can, but why the fuck would you do that.")
    elif slapper_coins < slap_cost: 
        if slapper_coins == 0:
            await ctx.send(f"<:squint:749549668954013696> You are flat broke, you can't afford to slap anybody.")
        elif slapper_coins == 1:
            await ctx.send(f"<:squint:749549668954013696> You only have 1 YomoCoin, you can't afford to slap anybody.")
        else:
            await ctx.send(f"<:squint:749549668954013696> You only have {slapper_coins} YomoCoins, you can't afford to slap anybody.")
    elif victim_coins <= 1: 
        await ctx.send(f"<:squint:749549668954013696> **{victim.name}** is too poor for it to be worth slapping them.")
    else: 
        # funny critical hit
        crit_roll = random.random() 
        if crit_roll < crit_chance: 
            slap_amount *= 12
            is_critical = True
        else:
            is_critical = False

        log.info(f"!slap: {slapper.name} spending {slap_cost} to remove {slap_amount} of {victim.name}'s coins")
        log.info(f"!slap: crit_roll = {crit_roll}, is_critical = {is_critical}")

        yc.set_coins(slapper.id, slapper_coins - slap_cost, slapper.name)

        await ctx.send(f"💥👏 You paid a hitman {slap_cost} YomoCoins to slap **{victim.name}**.\n")
        if is_critical: 
            await ctx.send("https://cdn.discordapp.com/attachments/396643053600899084/799859207620657152/critical_hit.png \n")

        if victim_coins > slap_amount: 
            yc.set_coins(victim.id, victim_coins - slap_amount, victim.name)
            await ctx.send( 
                f"🪙 **{slap_amount}** YomoCoins fell out of {victim.name}'s pocket and into the gutter!\n" +
                f"🪙 {victim.name} now has {victim_coins - slap_amount} YomoCoins."
            )
        else:
            yc.set_coins(victim.id, 1, victim.name)
            await ctx.send( 
                f"🪙 **{victim_coins - 1}** YomoCoins fell out of {victim.name}'s pocket and into the gutter!\n" +
                f"🪙 They managed to hold onto **their last YomoCoin** as they reeled from the impact.\n" + 
                f"<:hmmge:798436267435884584> 🪙"
            )
        yc.save_coins_if_necessary("yomocoins.csv")


################################################################################
#
### Betting

# start betting round
@bot.command(name='start', aliases=['startbets'], help="Start a new betting round")
@commands.guild_only()
async def startbets(ctx, *teams):

    # unpack teams tuple into a list
    teamlist = [team for team in teams]   

    # unpack the noping flag
    ping = True
    if "noping" in teamlist: 
        teamlist.remove("noping")
        ping = False

    # default teams if none are given
    if not teamlist:
        teamlist = ["radiant", "dire"]

    # Check for existing betting round
    if betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is already an active betting round.\n" + 
            f"Either `!cancel` or `!winner` this round before starting another one.")

    # Check for duplicates (case insensitive)
    elif len(teamlist) < 2 or len(teamlist) > 10:
        await ctx.send(f"❌ There can only be between 2 and 10 teams.")

    # Check for duplicates (case insensitive)
    #elif len(teamlist) != len(set(map(lambda t: t.lower(), teamlist))):
    elif len(teamlist) != len({team.lower() for team in teamlist}):
        await ctx.send(f"❌ Can't use duplicate team names.")

    # Check for team names that are just whitespace or not printable characters
    elif any([t.isspace() or not t.isprintable() for t in teamlist]): 
        await ctx.send(f"<:squint:749549668954013696> Those team names don't look very readable.")

    # Check for team names that are numbers but do not correspond to the shorthand
    # fuck you python 3 for taking away tuple unpacking in lambdas
    elif any([t.isdigit() and int(t) != n for (n,t) in enumerate(teamlist, 1)]): 
        await ctx.send(f"<:squint:749549668954013696> If a team name is a number, it has to be the same number as the shorthand.")

    # Teams can be no longer than 30 characters long 
    elif any([len(t) > 30 for t in teamlist]): 
        await ctx.send(f"<:squint:749549668954013696> Those team names are a bit too long.")

    # Bets have to be started in the betting channel (unless you're an admin)    
    elif ctx.channel.id != BETTING_CHANNEL and not ctx.author.guild_permissions.administrator:
        await ctx.send(f"""❌ That command is only allowed in {bot.get_channel(BETTING_CHANNEL).mention}.""")

    else:
        log.info(f"!start: {ctx.author.name} started bet with teams {teamlist}")
        betting.start(teamlist)
        if ping:
            gamblers_role = discord.utils.get(ctx.guild.roles, name='yomocoin-gamblers')
            gamblers_ping = f"{gamblers_role.mention}\n"
        else: 
            gamblers_ping = "\n"

        await ctx.send(
            f"💰 Betting has started! Who will reign supreme? " + gamblers_ping + 
            "\n".join([
                f"To bet on **{t}**, type `!bet \"{t}\" <amount>` or simply `!bet {n} <amount>`."
                for (n,t)
                in enumerate(teamlist, 1)
            ]) + 
            f"\nTo report the outcome, type `!winner <team name>` or `!winner <team number>`.\n" +
            f"To cancel the round, type `!cancel`."
        )
    yc.save_coins_if_necessary("yomocoins.csv")


# cancel betting round
@bot.command(name='cancel', help="Cancel the current betting round")
@commands.guild_only()
async def cancel(ctx):
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening. Use `!start team1 team2` to start one.")
        return
    # Confirmation process
    canceller = betting.get_canceller()
    author_id = ctx.author.id

    # Cancelling is allowed if:
    # 1. there are no bets
    # OR
    # 2. it has already been proposed AND this person is a valid approver
    # A valid approver is either an administrator, or simply any user that wasn't the original approver. 
    if betting.is_empty() or (canceller != None and (canceller != author_id or ctx.author.guild_permissions.administrator)):
        log.info(f"!cancel: user {ctx.author.name} is cancelling bet")
        bets = betting.get_bets_list()
        for bet in bets:
            user_id, team, amount, display_emote = bet
            user_name = get_username(user_id)
            log.info(f"!cancel: refunding {user_name} {amount} coins")
            yc.set_coins(user_id, yc.get_coins(user_id) + amount, user_name)
        betting.cancel()
        await ctx.send(f"✅ Round cancelled. All bet amounts have been returned.")
    # If there has been no proposal yet, make one
    elif betting.get_canceller() is None:
        await ctx.send(f"⚠️ A cancel of the current round has been proposed. One other person must confirm by also typing `!cancel`.")
        betting.set_canceller(author_id)
    # Case where someone tries to approve their own cancel
    elif betting.get_canceller() == author_id:
        await ctx.send(f"<:squint:749549668954013696> You can't confirm your own cancellation proposal.")
    yc.save_coins_if_necessary("yomocoins.csv")


# lock betting round
@bot.command(name='lock', help="Stop any further bets from being made in this round. Can be on a timer")
@commands.guild_only()
async def lock_bets(ctx, timer: int=0):
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening. Use `!start team1 team2` to start one.")
    elif betting.is_locked(): 
        await ctx.send(f"<:squint:749549668954013696> Betting is already locked.")
    elif timer > 600 or timer < 0:
        await ctx.send(f"<:squint:749549668954013696> Invalid timer value (restricted to 0-600 seconds)")
    elif timer > 0 and betting.get_autolock():
        await ctx.send(f"<:squint:749549668954013696> There is already an auto lock scheduled.")
    else:
        # autolock timing logic
        if timer > 0:
            now = dt.datetime.now()
            betting.set_autolock(now)

            log.info(f"!lock: user {ctx.author.name} scheduled auto lock in {timer} seconds")

            # different display formats for time remaining
            if timer < 60:
                time_display = f"{timer} seconds"
            elif timer == 60:
                time_display = f"1 minute" 
            elif timer < 120: 
                time_display = f"1 minute {timer-60} seconds"
            elif timer % 60 == 0: 
                time_display = f"{int(timer/60)} minutes"
            else: 
                time_display = f"{int(timer/60)} minutes {timer % 60} seconds"

            # for long timers sleep until the 30 second mark and then give a warning
            if timer > 30: 
                await ctx.send(f"⏱️ Auto lock will occur in **" + time_display + "**. There will be a warning at 30s remaining.")
                await asyncio.sleep(timer-30)
                # check for manual locks, autolock cancels, and whole-ass cancels
                if not betting.is_active() or betting.is_locked() or betting.get_autolock() != now:
                    return
                await ctx.send(f"⚠️ **Locking in 30 seconds!** ⚠️")
                await asyncio.sleep(30)
            else: 
                await ctx.send(f"⚠️ **Locking in {time_display}!**")
                await asyncio.sleep(timer)
            # check for manual locks, autolock cancels, and whole-ass cancels
            if not betting.is_active() or betting.is_locked() or betting.get_autolock() != now:
                return
            betting.set_autolock(None)

        betting.lock()
        log.info(f"!lock: user {ctx.author.name} locked the bet")
        yc.save_coins("yomocoins.csv")
        yc.backup_coins()
        await ctx.send(f"🔒 Betting is now locked. No more bets can be made until the round is cancelled or reported.")


@bot.command(name='autolock', help="Alias for !lock 180")
@commands.guild_only()
async def autolock(ctx, timer: int=180):
    await lock_bets(ctx, timer)


# cancel auto lock 
@bot.command(name='stopautolock', aliases=['noautolock', 'cancelautolock'], help="Cancel autolock timer")
@commands.guild_only()
async def stopautolock(ctx):
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening. Use `!start team1 team2` to start one.")
    elif betting.is_locked(): 
        await ctx.send(f"<:squint:749549668954013696> Betting is already locked.")
    elif not betting.get_autolock():
        await ctx.send(f"<:squint:749549668954013696> There is no auto lock scheduled.")
    else:
        betting.set_autolock(False)
        await ctx.send(f"⏱️ Auto lock has been stopped.")


# unlock betting round
@bot.command(name='unlock', help="Opposite of lock (admin only)")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def unlock_bets(ctx):
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening. Use `!start team1 team2` to start one.")
    elif not betting.is_locked(): 
        await ctx.send(f"<:squint:749549668954013696> Betting is not locked.")
    else:
        log.info(f"!lock: administrator {ctx.author.name} unlocked the bet")
        betting.unlock()
        await ctx.send(f"🔓 Betting has been unlocked.")


# report betting round winning team
@bot.command(name='winner', help="Report the winner of a round")
@commands.guild_only()
async def winner(ctx, team: str):
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening. Use `!start team1 team2` to start one.")
    elif betting.is_empty():
        await ctx.send(f"Betting is now over, but nobody placed any bets... <:soulless:681461973761654790>")
        betting.cancel()
    else:
        teamlist = betting.get_teamlist()

        if team in teamlist:
            winning_team = team
        elif team.isdigit() and int(team) > 0 and int(team) <= len(teamlist):
            winning_team = teamlist[int(team)-1]
        else:
            await ctx.send(f"<:vic:792318295709581333> That's not one of the teams.")
            return

        winners_list = betting.get_bets_list(winning_team)
        losers_list  = betting.get_bets_list(winning_team, invert=True)

        # cancel as early as possible to make race conditions less likely (still possible, ofc)
        betting.cancel()

        winners_pot = sum([amount for (u_, t_, amount, e_) in winners_list])
        losers_pot = sum([amount for (u_, t_, amount, e_) in losers_list])
        total_pot = int((winners_pot + losers_pot)*1.1)

        log.info(f"!winner: user {ctx.author.name} reported the winner as {winning_team}")
        log.info(f"!winner: winners_pot {winners_pot}, losers_pot {losers_pot}, total_pot {total_pot}")

        yc.backup_coins()

        # pay out winnings and record wins for stats purposes
        win_amounts = {}
        for bet in winners_list: 
            (user_id, t_, bet_amount, e_) = bet
            user_name = get_username(user_id)

            # enforce maximum payout of 10x
            win_float = float(bet_amount * total_pot) / float(winners_pot)
            win_amount = min(10*bet_amount, int(win_float))

            # guarantee a profit of at least 1 coin as long as you bet at least 10 (no rounding fuckery)
            if bet_amount >= 10: 
                win_amount = max(bet_amount + 1, win_amount)

            log.info(f"!winner: paying out {win_float:.3f} rounded to {win_amount} winnings to {user_name}")
            win_amounts[user_id] = win_amount
            yc.set_coins(user_id, yc.get_coins(user_id) + win_amount, user_name)
            yc.record_win(user_id, win_amount)

        # record losses for stats purposes 
        # no need to take money away - they already lost their money when they made their bet
        for bet in losers_list:
            (user_id, t_, bet_amount, e_) = bet
            user_name = get_username(user_id)
            log.info(f"!winner: recording loss for {user_name}")
            yc.record_loss(user_id, bet_amount)

        await ctx.send(
            f"💰💰💰 Betting is over! **{winning_team}** wins! 💰💰💰\n" + 
            "\n".join([f"<:sorisring:770642052782358530> **{get_username(user_id)}** won {win_amounts[user_id]} YomoCoins!" for (user_id, t_, a_, e_) in winners_list]) + 
            "\n" + 
            "\n".join([f"<:soulless:681461973761654790> **{get_username(user_id)}** lost {amount} YomoCoins..." for (user_id, t_, amount, e_) in losers_list])
        )
        yc.save_coins("yomocoins.csv")


# make a new bet 
@bot.command(name='bet', help="Place a bet")
@commands.guild_only()
async def bet(ctx, team: str, amount: int, emote: str="moneybag"):
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening. Use `!start team1 team2` to start one.")
    elif betting.is_locked(): 
        await ctx.send(f"🔒 Betting is locked for the remainder of this round.")
    elif ctx.channel.id != BETTING_CHANNEL and not ctx.author.guild_permissions.administrator:
        await ctx.send(f"""❌ That command is only allowed in {bot.get_channel(BETTING_CHANNEL).mention}.""")
    else:
        teamlist = betting.get_teamlist()
        user_id = ctx.author.id
        user_coins = yc.get_coins(user_id)

        # users are allowed to up existing bets for the same team if they want
        if betting.bet_exists(user_id):
            existing_bet = betting.get_bet(user_id)
            existing_team = existing_bet["team"]
            existing_amount = existing_bet["amount"]
        else:
            existing_amount = 0

        if emote == "moneybag": 
            display_emote = "💰"
        elif emote == "BoxingChimp":
            display_emote = "<a:BoxingChimp:795509491637682186>"
        elif emote == "vic": 
            display_emote = "<:vic:792318295709581333>"
        else:
            await ctx.send('<:squint:749549668954013696> Invalid command arguments. Maybe try `!help <command>`.') 
            return

        # coin amounts-related error checking
        if user_coins is None:
            await ctx.send(f"<:squint:749549668954013696> You don't appear to be in the YomoCoins system yet. Use `!optin`")
        elif amount <= 0: 
            await ctx.send(f"<:squint:749549668954013696> Invalid amount of YomoCoins.")

        # in the case a user is increasing an existing bet, 
        # we have to temporarily consider those coins as part of a user's effective coins
        elif (user_coins + existing_amount) < amount: 
            if user_coins == 0: 
                await ctx.send(f"<:squint:749549668954013696> You don't have any YomoCoins to bet. Maybe try `!centrelink`?")
            elif user_coins == 1:
                await ctx.send(f"<:squint:749549668954013696> You only have 1 YomoCoin to bet. Maybe try `!centrelink`?")
            else:
                await ctx.send(f"<:squint:749549668954013696> You only have {user_coins} YomoCoins left to bet with.")

        else:
            # team name-related error checking
            if team in teamlist:
                betting_team = team
            elif team.isdigit() and int(team) > 0 and int(team) <= len(teamlist):
                betting_team = teamlist[int(team)-1]
            else:
                await ctx.send(f"<:squint:749549668954013696> I don't recognise that team.\n"
                    f"Use the full name (in double quotes if there are spaces), or just its number.")
                return

            if betting.bet_exists(user_id):
                if betting_team != existing_team or amount < existing_amount:
                    await ctx.send(f"❌ You can't change team or reduce your betting amount.")
                elif amount == existing_amount:
                    await ctx.send(f"<:squint:749549668954013696> You've already placed this exact bet.")
                else:
                    log.info(f"!bet: user {ctx.author.name} increased their bet from {existing_amount} to {amount} on {betting_team}")
                    await ctx.send(f"💰 Bet increased from {existing_amount} to {amount}.")
                    betting.place_bet(user_id, betting_team, amount, display_emote)
                    yc.set_coins(user_id, user_coins - (amount - existing_amount), ctx.author.name)
            else: 
                log.info(f"!bet: user {ctx.author.name} bet {amount} on {betting_team}")
                betting.place_bet(user_id, betting_team, amount, display_emote)
                yc.set_coins(user_id, user_coins - amount, ctx.author.name)
                await ctx.send(f"💰 Bet placed on **{betting_team}** for {amount} YomoCoins! Good luck.")


# bet all of your coins at once
@bot.command(name='betall', aliases=["allin"], help="Same as !bet but bets all of your coins")
@commands.guild_only()
async def betall(ctx, team: str):
    user_id = ctx.author.id
    amount = yc.get_coins(user_id)
    if not betting.is_active(): 
        await ctx.send(f"There is no active betting round happening. Use `!start team1 team2` to start one.")
    elif betting.is_locked(): 
        await ctx.send(f"🔒 Betting is locked for the remainder of this round.")
    elif amount is None:
        await ctx.send(f"<:squint:749549668954013696> You don't appear to be in the YomoCoins system yet. Use `!optin`")
    elif amount == 0: 
        await ctx.send(f"<:squint:749549668954013696> You don't have any YomoCoins to bet. Maybe try `!centrelink`?")
    else:        
        # users are allowed to up existing bets for the same team if they want
        if betting.bet_exists(user_id):
            existing_bet = betting.get_bet(user_id)
            existing_amount = existing_bet["amount"]
        else:
            existing_amount = 0
        await ctx.send(f"https://cdn.discordapp.com/emojis/769258836803452948.gif")
        await bet(ctx, team, amount + existing_amount, "BoxingChimp")


# bet a random amount of coins
@bot.command(name='betnana', help="!bets a random amount for a random team")
@commands.guild_only()
async def betnana(ctx):
    user_id = ctx.author.id
    user_coins = yc.get_coins(user_id)

    if not betting.is_active(): 
        await ctx.send(f"There is no active betting round happening. Use `!start team1 team2` to start one.")
    elif betting.is_locked(): 
        await ctx.send(f"🔒 Betting is locked for the remainder of this round.")
    elif user_coins is None:
        await ctx.send(f"<:squint:749549668954013696> You don't appear to be in the YomoCoins system yet. Use `!optin`")
    elif user_coins == 0: 
        await ctx.send(f"<:squint:749549668954013696> You don't have any YomoCoins to bet. Maybe try `!centrelink`?")
    elif betting.bet_exists(user_id):
        await ctx.send(f"❌ Can't use `!betnana` if you've already bet.")
    else:
        teamlist = betting.get_teamlist()
        team = str(random.randint(1, len(teamlist)))
        amount = random.randint(1, user_coins)
        await ctx.send("<:vic:792318295709581333>")
        await bet(ctx, team, amount, "vic")


# bet all of your coins at once, on a random team
@bot.command(name='betnanaall', aliases=["betallnana", "betnanall"], help="!bets all of your coins on a random team")
@commands.guild_only()
async def betnanaall(ctx):
    user_id = ctx.author.id
    user_coins = yc.get_coins(user_id)

    if not betting.is_active(): 
        await ctx.send(f"There is no active betting round happening. Use `!start team1 team2` to start one.")
    elif betting.is_locked(): 
        await ctx.send(f"🔒 Betting is locked for the remainder of this round.")
    elif user_coins is None:
        await ctx.send(f"<:squint:749549668954013696> You don't appear to be in the YomoCoins system yet. Use `!optin`")
    elif user_coins == 0: 
        await ctx.send(f"<:squint:749549668954013696> You don't have any YomoCoins to bet. Maybe try `!centrelink`?")
    elif betting.bet_exists(user_id):
        await ctx.send(f"❌ Can't do that if you've already bet.")
    else:   
        teamlist = betting.get_teamlist()
        team = str(random.randint(1, len(teamlist)))
        await ctx.send("<:vic:792318295709581333>")
        await bet(ctx, team, user_coins, "vic")


# list current bets
@bot.command(name='bets', aliases=['listbets', 'list_bets', 'allbets', 'all_bets', 'betlist', 'bet_list', 'bets_list', 'betslist'], help="List all current bets")
@commands.guild_only()
async def listbets(ctx):
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening. Use `!start team1 team2` to start one.")
    elif betting.is_empty():
        await ctx.send(f"The current round is between **{betting.get_team1()}** (1) and **{betting.get_team2()}** (2).\nNobody has made a bet yet.")
    else:
        # Team names
        teamlist = betting.get_teamlist()

        # List of bets for each team (ie. a list of lists)
        bets_list_list = [betting.get_bets_list(t) for t in teamlist]

        # Calculate pot sizes
        pot_list = [sum([amount for (u_, t_, amount, e_) in bets_list]) for bets_list in bets_list_list]
        total_pot = int(sum(pot_list)*1.1)

        # Display a nice padlock emoji if the betting is locked
        if betting.is_locked():
            lock_indicator = "🔒"
        else:
            lock_indicator = ""

        # If nobody is betting on a particular team yet, we don't need to put a header 
        def bets_display_text(team, pot_size, bets_list):
            if not bets_list:
                return ""
            else:
                return f"YomoFans betting on **{team}** ({pot_size} YomoCoins):\n" + \
                    '\n'.join([   
                        f"""{emote} **{get_username(user_id)}** bet {amount} YomoCoins ({float(100.0 * amount / pot_size):.1f}%)."""
                        for (user_id, team, amount, emote)
                        in bets_list
                    ]) + "\n\n"

        # Short enumerated list of teams and their numbers
        # Basically produces "Team1 (1), Team2 (2), and Team3 (3)"
        enumerated_team_list = ", ".join(f"**{t}** ({n})" for (n,t) in enumerate(teamlist[:-1], 1)) + " and " + f"**{teamlist[-1]}** ({len(teamlist)})"

        # Finally, piece together the message
        await ctx.send(
            f"💰 The current round is between " + enumerated_team_list + ". " + lock_indicator + 
            f"\nTotal pot size: **{total_pot} YomoCoins**\n\n" + 
            "".join([bets_display_text(t, p, bl) for (t, p, bl) in zip(teamlist, pot_list, bets_list_list)])
        )


# post or request the latest lineup
@bot.command(name='draft', aliases=['lineup'], help="Post or request an image of the draft/lineup")
@commands.guild_only()
async def draft(ctx, link: str=None):
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening. Use `!start team1 team2` to start one.")
    elif link is not None: 
        betting.set_draft(link)
        await ctx.send(f"Lineup image set.")
    elif len(ctx.message.attachments) == 1:
        first_attachment = ctx.message.attachments[0]
        betting.set_draft(first_attachment.url)
        await ctx.send(f"Lineup image set.")
    else: 
        await ctx.send(betting.get_draft())


# list current bets
@bot.command(name='rig', help="Does nothing, stop reading this (admin only)")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def rigbet(ctx):
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening to rig.")
    else:
        rig_messages = [
            "Mods will now receive 445% more winnings than they're entitled to.",
            "Mod bets will now magically change over to whichever team wins.",
            "Mods will no longer actually lose any money if they lose.",
            "A trained sniper has been deployed to kill the team the mods didn't bet on.",
            "Launching Monster Hunter: World on the enemy team's machines to raise CPU temps to critical levels.",
            "DMing rare Booba pictures to distract the enemy team.",
            "Decreasing player skill. Raising complexity levels.",
            "The Bogdanoffs have been contacted. They've made the call. <:BOGGED:707943218192449547>",
            "Replacing a random member of the other team with a bot."
        ]
        await ctx.send("✅ The round is now rigged. " + random.choice(rig_messages) + "\nMake sure not to use this command outside of the secret mod channel.")

################################################################################
#
### Dueling 
### Duels are just 1v1 coinflip bets with no pot bonus

# start dueling round
@bot.command(name='duel', aliases=['challenge', 'startduel'], help="Challenge a user to a duel")
@commands.guild_only()
async def startduel(ctx, accepter: User, amount: int):
    yc.backup_coins()
    challenger = ctx.author
    challenger_coins = yc.get_coins(challenger.id)
    accepter_coins = yc.get_coins(accepter.id)    

    if dueling.is_active(): 
        await ctx.send(
            f"<:squint:749549668954013696> There is already an active duel between " +
            f"{get_username(dueling.get_challenger())} and {get_username(dueling.get_accepter())}.\n" +
            f"Finish this duel (`!accept`, `reject`) before starting another."
        )
    elif challenger_coins is None:
        await ctx.send(f"<:squint:749549668954013696> You don't appear to be in the YomoCoins system yet. Use `!optin`")
    elif accepter_coins is None: 
        await ctx.send(f"<:squint:749549668954013696> {accepter.name} doesn't appear to be in the YomoCoins system yet. Use `!optin`")
    elif challenger.id == accepter.id: 
        await ctx.send(f"<:squint:749549668954013696> You can't challenge yourself to a duel.")
    elif amount <= 0: 
        await ctx.send(f"<:squint:749549668954013696> Invalid duel stakes amount.")
    elif challenger_coins < amount: 
        if challenger_coins == 0: 
            await ctx.send(f"<:squint:749549668954013696> You don't have any YomoCoins to duel with. Maybe try `!centrelink`?")
        elif challenger_coins == 1:
            await ctx.send(f"<:squint:749549668954013696> You only have 1 YomoCoin to duel with. Maybe try `!centrelink`?")
        else:
            await ctx.send(f"<:squint:749549668954013696> You only have {challenger_coins} YomoCoins to duel with.")
    elif accepter_coins < amount: 
        if accepter_coins == 0: 
            await ctx.send(f"<:squint:749549668954013696> {accepter.name} doesn't have any YomoCoins to duel for.")
        elif accepter_coins == 1:
            await ctx.send(f"<:squint:749549668954013696> {accepter.name} only has 1 YomoCoin to duel for.")
        else:
            await ctx.send(f"<:squint:749549668954013696> {accepter.name} only has {accepter_coins} YomoCoins to duel for.")
    else:
        log.info(f"!startduel: {challenger.name} challenged {get_username(accepter.name)} to a duel for {amount}")
        dueling.start(challenger.id, accepter.id, amount)
        yc.set_coins(challenger.id, challenger_coins - amount, challenger.name)
        await ctx.send(
            f"⚔️ {challenger.name} has challenged {accepter.name} to a duel for **{amount} YomoCoins!** Will they accept?\n" +
            f"Type `!accept` to accept the duel, or `!reject` to decline. Mods can use `!cancelduel`."
        )
    yc.save_coins_if_necessary("yomocoins.csv")


# random duel
@bot.command(name='duelnana', help="Duel someone for a random amount")
@commands.guild_only()
async def duelnana(ctx, accepter: User):
    challenger = ctx.author
    challenger_coins = yc.get_coins(challenger.id)
    accepter_coins = yc.get_coins(accepter.id)    

    if dueling.is_active(): 
        await ctx.send(
            f"<:squint:749549668954013696> There is already an active duel between " +
            f"{get_username(dueling.get_challenger())} and {get_username(dueling.get_accepter())}.\n" +
            f"Finish this duel (`!accept`, `reject`) before starting another."
        )
    elif challenger_coins is None:
        await ctx.send(f"<:squint:749549668954013696> You don't appear to be in the YomoCoins system yet. Use `!optin`")
    elif challenger_coins == 0: 
        await ctx.send(f"<:squint:749549668954013696> You don't have any YomoCoins to duel with. Maybe try `!centrelink`?")
    elif accepter_coins is None: 
        await ctx.send(f"<:squint:749549668954013696> {accepter.name} doesn't appear to be in the YomoCoins system yet. Use `!optin`")
    elif accepter_coins == 0: 
        await ctx.send(f"<:squint:749549668954013696> {accepter.name} doesn't have any YomoCoins to duel for.")
    else:   
        amount = random.randint(1, min(challenger_coins, accepter_coins))
        await ctx.send("<:vic:792318295709581333>")
        await startduel(ctx, accepter, amount)
    yc.save_coins_if_necessary("yomocoins.csv")


# duel version of betall
@bot.command(name='duelall', help="Duel someone for the maximum amount")
@commands.guild_only()
async def duelall(ctx, accepter: User):
    challenger = ctx.author
    challenger_coins = yc.get_coins(challenger.id)
    accepter_coins = yc.get_coins(accepter.id)    

    if dueling.is_active(): 
        await ctx.send(
            f"<:squint:749549668954013696> There is already an active duel between " +
            f"{get_username(dueling.get_challenger())} and {get_username(dueling.get_accepter())}.\n" +
            f"Finish this duel (`!accept`, `reject`) before starting another."
        )
    elif challenger_coins is None:
        await ctx.send(f"<:squint:749549668954013696> You don't appear to be in the YomoCoins system yet. Use `!optin`")
    elif challenger_coins == 0: 
        await ctx.send(f"<:squint:749549668954013696> You don't have any YomoCoins to duel with. Maybe try `!centrelink`?")
    elif accepter_coins is None: 
        await ctx.send(f"<:squint:749549668954013696> {accepter.name} doesn't appear to be in the YomoCoins system yet. Use `!optin`")
    elif accepter_coins == 0: 
        await ctx.send(f"<:squint:749549668954013696> {accepter.name} doesn't have any YomoCoins to duel for.")
    else:   
        amount = min(challenger_coins, accepter_coins)
        await ctx.send(f"https://cdn.discordapp.com/emojis/769258836803452948.gif")
        await startduel(ctx, accepter, amount)
    yc.save_coins_if_necessary("yomocoins.csv")


@bot.command(name='accept', aliases=['acceptduel'], help="Accept a challenge to duel")
@commands.guild_only()
async def acceptduel(ctx):
    yc.backup_coins()
    accepter = ctx.author
    accepter_coins = yc.get_coins(accepter.id) 

    if not dueling.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active duel to accept.")      
    elif dueling.get_accepter() != accepter.id: 
        await ctx.send(f"<:squint:749549668954013696> Only {get_username(dueling.get_accepter())} can accept this duel.")
    elif accepter_coins < dueling.get_amount():
        if accepter_coins == 0: 
            await ctx.send(
                f"<:squint:749549668954013696> You can no longer afford to accept - you have have no YomoCoins to duel with.\n" +
                f"<a:morshu:814687320166629396> Come back when you're a little err... richer! (Or use `!reject`)."
            )
        elif accepter_coins == 1:
            await ctx.send(
                f"<:squint:749549668954013696> You can no longer afford to accept - you only have 1 YomoCoin to duel with.\n" +
                f"<a:morshu:814687320166629396> Come back when you're a little err... richer! (Or use `!reject`)."
            )
        else:
            await ctx.send(
                f"<:squint:749549668954013696> You can no longer afford to accept - you only have {accepter_coins} YomoCoins to duel with.\n" +
                f"<a:morshu:814687320166629396> Come back when you're a little err... richer! (Or use `!reject`)."
            )    
    else:
        amount = dueling.get_amount()
        yc.set_coins(accepter.id, accepter_coins - amount, accepter.name)

        challenger_id = dueling.get_challenger()
        challenger_name = get_username(challenger_id)

        await ctx.send(f"⚔️ Duel accepted! Fighting...");
        await asyncio.sleep(3)

        flip_result = random.randint(1,2)

        if flip_result == 1: 
            await ctx.send(f"⚔️ {challenger_name} is victorious! They won {amount} YomoCoins from {accepter.name}.");
            challenger_coins = yc.get_coins(challenger_id) 
            yc.set_coins(challenger_id, challenger_coins + amount*2, challenger_name)
        else: 
            await ctx.send(f"⚔️ {accepter.name} is victorious! They took {amount} YomoCoins from {challenger_name}.");
            accepter_coins = yc.get_coins(accepter.id) 
            yc.set_coins(accepter.id, accepter_coins + amount*2, accepter.name)
        dueling.cancel()
        yc.backup_coins()


@bot.command(name='reject', aliases=['rejectduel'], help="Reject a challenge to duel")
@commands.guild_only()
async def rejectduel(ctx):
    yc.backup_coins()
    accepter = ctx.author
    accepter_coins = yc.get_coins(accepter.id) 

    if not dueling.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active duel to reject.")      
    elif dueling.get_accepter() != accepter.id: 
        await ctx.send(f"<:squint:749549668954013696> Only {get_username(dueling.get_accepter())} can reject this duel.")   
    else:
        amount = dueling.get_amount()
        challenger_id = dueling.get_challenger()
        challenger_name = get_username(challenger_id)
        challenger_coins = yc.get_coins(challenger_id) 
        yc.set_coins(challenger_id, challenger_coins + amount, challenger_name)
        dueling.cancel()
        await ctx.send(f"⚔️ The challenge has been rejected. {amount} YomoCoins have been returned to {challenger_name}.");
        yc.backup_coins()


@bot.command(name='cancelduel', help="Cancel a challenge to duel (mods only)")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def cancelduel(ctx):
    if not dueling.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active duel to cancel.")      
    else:
        amount = dueling.get_amount()
        challenger_id = dueling.get_challenger()
        challenger_name = get_username(challenger_id)
        challenger_coins = yc.get_coins(challenger_id) 
        yc.set_coins(challenger_id, challenger_coins + amount, challenger_name)
        dueling.cancel()
        await ctx.send(f"⚔️ The duel has been cancelled. {amount} YomoCoins have been returned to {challenger_name}.");
        yc.backup_coins()


################################################################################
#
### main function
if __name__ == "__main__":
    yc.load_coins("yomocoins.csv")
    yc.backup_coins()
    bot.run(TOKEN)
