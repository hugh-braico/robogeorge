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
import betting

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SEAJAY = int(os.getenv('SEAJAY'))
intents = discord.Intents.default()
intents.members = True
daily_amount = 25
bot = commands.Bot(command_prefix='!', intents=intents)
yc = yomocoins.YomoCoins()
betting = betting.Betting()

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
@bot.command(name='ping', help='Ping test')
@commands.guild_only()
async def ping(ctx):
    await ctx.send(f"🏓 approx. latency = {round(bot.latency, 3)}s");


# shoot the bot
@bot.command(name='kill', aliases=['bang'], help='Kills the bot (SeaJay only)')
@commands.guild_only()
async def bang(ctx):
    if ctx.author.id == SEAJAY: 
        await ctx.send("<:sadcat:712998237975478282> Saving YomoCoins database and shutting down...")
        yc.save_coins("yomocoins.csv")
        sys.exit(0)
    else: 
        await ctx.send("<:squint:749549668954013696> You don't have the right permissions to do that.")


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
        await ctx.send(f'<:squint:749549668954013696> {ctx.command} has been disabled.')
    elif isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        except discord.HTTPException:
            pass
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("<:squint:749549668954013696> I don't recognise that command. Try `!help` for a list of all commands.")
    elif isinstance(error, commands.BadArgument):
        if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
            await ctx.send('<:squint:749549668954013696> I could not find that member. Please try again.')
        else:
            await ctx.send('<:squint:749549668954013696> Invalid command arguments. Maybe try `!help <command>`.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("<:squint:749549668954013696> Looks like you didn't supply enough arguments. Maybe try `!help <command>`.")
    elif isinstance(error, commands.ExpectedClosingQuoteError) or isinstance(error, commands.UnexpectedQuoteError):
        await ctx.send("<:squint:749549668954013696> Looks like you didn't close your double quotes properly.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("<:squint:749549668954013696> You don't have the right permissions to do that.")
    else:
        await ctx.send('<:squint:749549668954013696> An unknown error occurred. CJ should probably handle this better.')
        # All other Errors not returned come here. And we can just print the default TraceBack.
        print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


################################################################################
#
### YomoCoins


# opt into the YomoCoins system
@bot.command(name='optin', aliases=['opt_in'], help='Opt into YomoCoins, get 310 starting coins')
@commands.guild_only()
async def optin(ctx):
    if yc.get_coins(ctx.author.id) is None:
        yc.set_coins(ctx.author.id, 310)
        await ctx.send(f"🪙 Welcome to YomoCoins! You have been given 310 starting YomoCoins.")
    else: 
        await ctx.send(f"❌ You have already opted in.")
    yc.save_coins_if_necessary("yomocoins.csv")


# set someone's yomocoins (admin only, obviously)
@bot.command(name='set', aliases=['setcoins', 'set_coins'], help="Set a user's coins (admin only)")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def set(ctx, user: User, coins: int):
    yc.set_coins(user.id, coins)
    await ctx.send(f"🪙 {user}'s YomoCoins set to {coins}.")
    yc.save_coins_if_necessary("yomocoins.csv")


# give someone yomocoins
@bot.command(name='give', aliases=['givecoins', 'give_coins', 'givecoin', 'give_coin'], help="Give some of your coins to another user")
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
        yc.set_coins(giver.id, giver_coins - coins)
        yc.set_coins(recipient.id, recipient_coins + coins)
        await ctx.send(f"🪙 You have given {recipient.name} {coins} YomoCoins.")
    yc.save_coins_if_necessary("yomocoins.csv")


# award someone yomocoins (admin only)
@bot.command(name='treat', aliases=['award', 'awardcoins', 'award_coins', 'awardcoin', 'award_coin'], help="Award coins as a treat (admin only)")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def award(ctx, recipient: User, coins: int):
    recipient_coins = yc.get_coins(recipient.id)
    if recipient_coins is None: 
        await ctx.send(f"<:squint:749549668954013696> {recipient.name} doesn't appear to be in the YomoCoins system yet. Use `!optin`")
    elif coins <= 0: 
        await ctx.send(f"<:squint:749549668954013696> Invalid amount of YomoCoins.")
    else: 
        if ctx.author.id == recipient.id: 
            await ctx.send("https://i.kym-cdn.com/entries/icons/facebook/000/030/329/cover1.jpg")
        yc.set_coins(recipient.id, recipient_coins + coins)
        await ctx.send(f"🪙 {recipient.name} can have {coins} YomoCoins, as a treat.")
    yc.save_coins_if_necessary("yomocoins.csv")


# save yomocoins
@bot.command(name='save', aliases=['savecoins', 'save_coins', 'savecoin', 'save_coin'], help="Manually save the coin database (admin only)")
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def save(ctx):
    yc.save_coins("yomocoins.csv")
    await ctx.send(f"💰 YomoCoins saved!")
    

# list everyone's yomocoins
@bot.command(name='list', aliases=['listcoins', 'list_coins', 'listcoin', 'list_coin'], help="List how many coins everyone has")
@commands.guild_only()
async def list(ctx):
    await ctx.send('\n'.join([   
            f"""🪙 **{bot.get_user(int(user_id)).name}**: {yc.get_coins(user_id)} YomoCoins.""" 
            for user_id in yc.sorted_coins_list()
        ])
    )
    

# print one person's yomocoins
@bot.command(name='coins', aliases=['coin', 'mycoins', 'my_coins', 'checkcoins', 'check_coins'], help="List how many coins you have, or a specific user")
@commands.guild_only()
async def single_coins(ctx, user: User = None):
    if user is None: 
        user = ctx.author
    coins = yc.get_coins(user.id)
    if coins is None:
        await ctx.send(f"""<:squint:749549668954013696> Invalid user, or user is not in the YomoCoins database yet. If the latter, use `!optin`""")
    else: 
        await ctx.send(f"""🪙 {user.name} has {coins} coins.""")
    

# claim daily coins 
@bot.command(name='centrelink', help="Claim a daily 25 coins")
@commands.guild_only()
async def centrelink(ctx):
    recipient_id = ctx.author.id
    recipient_coins = yc.get_coins(recipient_id)
    if recipient_coins == None:
        await ctx.send(f"<:squint:749549668954013696> You don't appear to be in the YomoCoins system yet. Use `!optin`")
    elif yc.get_daily_claimed(recipient_id):
        await ctx.send(f"<:squint:749549668954013696> You have already claimed today's free daily YomoCoins.")
    else: 
        recipient_coins = yc.get_coins(recipient_id)
        global daily_amount
        yc.set_coins(recipient_id, recipient_coins + daily_amount)
        yc.set_daily_claimed(recipient_id)
        await ctx.send(f"🪙 Claimed {daily_amount} daily YomoCoins. Come back tomorrow for more.")
    yc.save_coins_if_necessary("yomocoins.csv")


################################################################################
#
### Betting

# start betting round
@bot.command(name='start', aliases=['startbets', 'startbet', 'start_bet', 'startbetting',  'start_betting', 'startround',  'start_round', 'start_bets'], help="Start a new betting round")
@commands.guild_only()
async def startbets(ctx, team1: str, team2: str):
    if betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is already an active betting round between "
            f"{betting.get_team1()} and {betting.get_team2()}.\n"
            f"Either `!cancel` or `!winner` this round before starting another one.")
    elif team1.lower() == team2.lower():
        await ctx.send(f"<:squint:749549668954013696> Those team names are too similar.")
    elif team1.isspace() or team2.isspace() or not team1.isprintable() or not team2.isprintable(): 
        await ctx.send(f"<:squint:749549668954013696> Those team names don't look very readable.")
    elif team1 == "2" or team2 == "1": 
        await ctx.send(f"<:squint:749549668954013696> Team names can't be the opposite of the shorthands for obvious reasons.")
    elif len(team1) > 30 or len(team2) > 30: 
        await ctx.send(f"<:squint:749549668954013696> Those team names are a bit too long.")
    else:
        betting.start(team1, team2)
        gamblers_role = discord.utils.get(ctx.guild.roles, name='yomocoin-gamblers')
        await ctx.send(
            f"💰 Betting has started! Who will reign supreme? {gamblers_role.mention}\n"
            f"To bet on **{team1}**, type `!bet \"{team1}\" <amount>` or simply `!bet 1 <amount>`.\n"
            f"To bet on **{team2}**, type `!bet \"{team2}\" <amount>` or simply `!bet 2 <amount>`.\n"
            f"To report the outcome, type `!winner \"{team1} OR {team2}\"` or simply `!winner <1 OR 2>`.\n"
            f"To cancel the round, type `!cancel`."
        )
    yc.save_coins_if_necessary("yomocoins.csv")


# cancel betting round
@bot.command(name='cancel', aliases=['cancelbets', 'cancelbetting', 'cancelround'], help="Cancel the current betting round")
@commands.guild_only()
async def cancel(ctx):
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening. Use `!startbets team1 team2` to start one.")
        return
    # Confirmation process
    canceller = betting.get_canceller()
    author_id = ctx.author.id
    # Cancelling is allowed if there are no bets, or it has already been proposed and this person is not the proposer
    if betting.is_empty() or (canceller != None and canceller != author_id):
        bets = betting.get_bets_list()
        for bet in bets:
            user_id, team, amount = bet
            yc.set_coins(user_id, yc.get_coins(user_id) + amount)
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
@bot.command(name='lock', aliases=['close', 'closebets', 'lockbets', 'lock_bets', 'lockbetting', 'lock_betting'], help="Stop any further bets from being made in this round")
@commands.guild_only()
async def lock_bets(ctx):
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening. Use `!startbets team1 team2` to start one.")
    elif betting.is_locked(): 
        await ctx.send(f"<:squint:749549668954013696> Betting is already locked.")
    else:
        betting.lock()
        await ctx.send(f"🔒 Betting is now locked. No more bets can be made until the round is cancelled or reported.")


# unlock betting round
@bot.command(name='unlock', help="Opposite of lock (admin only)")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def unlock_bets(ctx):
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening. Use `!startbets team1 team2` to start one.")
    elif not betting.is_locked(): 
        await ctx.send(f"<:squint:749549668954013696> Betting is not locked.")
    else:
        betting.unlock()
        await ctx.send(f"🔓 Betting has been unlocked.")


# report betting round winning team
@bot.command(name='winner', aliases=['reportwinner', 'reportround', 'report', 'finish', 'finishbets', 'endbets'], help="Report the winner of a round")
@commands.guild_only()
async def winner(ctx, team: str):
    yc.save_coins_if_necessary("yomocoins.csv")
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening. Use `!startbets team1 team2` to start one.")
    else:
        if betting.is_empty():
            await ctx.send(f"Betting is now over, but nobody placed any bets... <:soulless:681461973761654790>")
        else:
            team1 = betting.get_team1()
            team2 = betting.get_team2()
            if team == "1" or team.lower() == team1.lower():
                winning_team = team1
            elif team == "2" or team.lower() == team2.lower():
                winning_team = team2

            winners_list = betting.get_winners_list(winning_team)
            losers_list = betting.get_losers_list(winning_team)

            winners_pot = sum([amount for (u_id, team, amount) in winners_list])
            losers_pot = sum([amount for (u_id, team, amount) in losers_list])
            total_pot = int((winners_pot + losers_pot)*1.1)

            # pay out winnings
            for bet in winners_list: 
                (user_id, t_, bet_amount) = bet
                win_amount = int((float)((bet_amount / winners_pot) * total_pot))
                yc.set_coins(user_id, yc.get_coins(user_id) + win_amount)

            await ctx.send(
                f"💰💰💰 Betting is over! **{winning_team}** wins! 💰💰💰\n" + 
                "\n".join([f"<:sorisring:770642052782358530> **{bot.get_user(int(user_id)).name}** won {int((float)((amount / winners_pot) * total_pot))} YomoCoins!" for (user_id, t_, amount) in winners_list]) + 
                "\n" + 
                "\n".join([f"<:soulless:681461973761654790> **{bot.get_user(int(user_id)).name}** lost {amount} YomoCoins..." for (user_id, t_, amount) in losers_list])
            )
        betting.cancel()
        yc.save_coins_if_necessary("yomocoins.csv")


# make a new bet 
@bot.command(name='bet', aliases=['makebet', 'betcoins', 'bet_coins'], help="Place a bet")
@commands.guild_only()
async def bet(ctx, team: str, amount: int):
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening. Use `!startbets team1 team2` to start one.")
    elif betting.is_locked(): 
        await ctx.send(f"Betting is locked for the remainder of this round.")
    else:
        team1 = betting.get_team1()
        team2 = betting.get_team2()
        user_id = ctx.author.id
        user_coins = yc.get_coins(user_id)

        # coin amounts-related error checking
        if user_coins is None:
            await ctx.send(f"<:squint:749549668954013696> You don't appear to be in the YomoCoins system yet. Use `!optin`")
        elif amount <= 0: 
            await ctx.send(f"<:squint:749549668954013696> Invalid amount of YomoCoins.")
        elif user_coins < amount: 
            if user_coins == 0: 
                await ctx.send(f"<:squint:749549668954013696> You don't have any YomoCoins to bet. Maybe try `!centrelink`?")
            elif user_coins == 1:
                await ctx.send(f"<:squint:749549668954013696> You only have 1 YomoCoin to bet. Maybe try `!centrelink`?")
            else:
                await ctx.send(f"<:squint:749549668954013696> You only have {user_coins} YomoCoins to bet.")
        else:
            # team name-related error checking
            if team == "1" or team.lower() == team1.lower():
                betting_team = 1
            elif team == "2" or team.lower() == team2.lower():
                betting_team = 2
            else:
                betting_team = None
                await ctx.send(f"<:squint:749549668954013696> I don't recognise that team name.\n"
                    "Use the full name in double quotes, or just 1 for team 1 or 2 for team 2.") 
            if betting_team is not None: 
                if betting.bet_exists(user_id):
                    await ctx.send(f"<:squint:749549668954013696> You've already placed a bet. All bets are final.")
                else: 
                    betting.place_bet(user_id, betting_team, amount)
                    yc.set_coins(user_id, user_coins - amount)
                    await ctx.send(f"💰 Bet placed! Good luck.")
    yc.save_coins_if_necessary("yomocoins.csv")


# bet all of your coins at once
@bot.command(name='betall', help="Same as !bet but bets all of your coins")
@commands.guild_only()
async def betall(ctx, team: str):
    user_id = ctx.author.id
    amount = yc.get_coins(user_id)
    if not betting.is_active(): 
        await ctx.send(f"There is no active betting round happening. Use `!startbets team1 team2` to start one.")
    elif betting.is_locked(): 
        await ctx.send(f"Betting is locked for the remainder of this round.")
    elif amount is None:
        await ctx.send(f"<:squint:749549668954013696> You don't appear to be in the YomoCoins system yet. Use `!optin`")
    elif amount == 0: 
        await ctx.send(f"<:squint:749549668954013696> You don't have any YomoCoins to bet. Maybe try `!centrelink`?")
    else:
        await bet(ctx, team, amount)


# list current bets
@bot.command(name='bets', aliases=['listbets', 'list_bets', 'allbets', 'all_bets', 'betlist', 'bet_list', 'bets_list', 'betslist'], help="List all current bets")
@commands.guild_only()
async def listbets(ctx):
    if not betting.is_active(): 
        await ctx.send(f"<:squint:749549668954013696> There is no active betting round happening. Use `!startbets team1 team2` to start one.")
    elif betting.is_empty():
        await ctx.send(f"The current round is between **{betting.get_team1()}** (1) and **{betting.get_team2()}** (2).\nNobody has made a bet yet.")
    else:
        team1 = betting.get_team1()
        team2 = betting.get_team2()
        bets_list = betting.get_bets_list()

        team1_pot = sum([amount for (u_id, team, amount) in bets_list if team == team1])
        team2_pot = sum([amount for (u_id, team, amount) in bets_list if team == team2])
        total_pot = int((team1_pot + team2_pot)*1.1)

        await ctx.send(f"The current round is between **{team1}** (1) and **{team2}** (2).\nTotal pot size: **{total_pot} YomoCoins**\n" + 
            '\n'.join([   
                f"""💰 **{bot.get_user(int(user_id)).name}** bet {amount} YomoCoins on {team} ({float(100.0 * amount / team1_pot):.1f}%)."""
                if team == team1 
                else f"""💰 **{bot.get_user(int(user_id)).name}** bet {amount} YomoCoins on {team} ({float(100.0 * amount / team2_pot):.1f}%)."""
                for (user_id, team, amount)
                in bets_list
            ])
        )


################################################################################
#
### main function
if __name__ == "__main__":
    yc.load_coins("yomocoins.csv")
    now = dt.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H%M")
    yc.save_coins(f"yomocoin_backups/yomocoins_{timestamp}.csv")
    bot.run(TOKEN)
