import csv
import datetime as dt

import logging
log = logging.getLogger("yomo")

# yomocoins.py
# Class for storing information and statistics about each user's YomoCoins.
# Bit of scope creep: also stores info about each user's betting stats,
# because it's convenient to be all in one place.

class YomoCoins:

    # constructor
    def __init__(self):  
        self.coins_dict = {}
        self.time_last_saved = dt.datetime.now()


    # load YomoCoins file from disk 
    def load_coins(self, filename: str):
        log.info(f"Loading data from {filename} ...")
        with open(filename, newline='') as csvfile: 
            reader = csv.DictReader(csvfile)
            for row in reader:
                # convert each row in the csv to an entry in a simple Python dictionary
                user_id = int(row["user_id"])
                self.coins_dict[user_id] = {} 
                self.coins_dict[user_id]["coins"]        = int(row["coins"])
                self.coins_dict[user_id]["daily"]        = (dt.datetime.strptime(row["daily"], "%Y-%m-%d")).date()
                self.coins_dict[user_id]["wins"]         = int(row["wins"])
                self.coins_dict[user_id]["losses"]       = int(row["losses"])
                self.coins_dict[user_id]["streak"]       = int(row["streak"])
                self.coins_dict[user_id]["best_streak"]  = int(row["best_streak"])
                self.coins_dict[user_id]["biggest_win"]  = int(row["biggest_win"])
                self.coins_dict[user_id]["biggest_loss"] = int(row["biggest_loss"])
                self.coins_dict[user_id]["duel_profits"] = int(row["duel_profits"])
                # yeah im piggybacking off this table to store steam ids as well
                self.coins_dict[user_id]["steam_id"]     = row["steam_id"]


    # save YomoCoins file to disk
    def save_coins(self, filename: str):
        log.info(f"Saving to CSV file: {filename} ...")
        with open(filename, "w", newline='') as csvfile: 
            fieldnames = [
                "user_id", 
                "coins", 
                "daily", 
                "wins", 
                "losses", 
                "streak", 
                "best_streak", 
                "biggest_win", 
                "biggest_loss",
                "duel_profits",
                "steam_id"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for user_id in self.coins_dict:
                writer.writerow({
                    "user_id"      : user_id, 
                    "coins"        : self.coins_dict[user_id]["coins"],
                    "daily"        : self.coins_dict[user_id]["daily"].strftime("%Y-%m-%d"),
                    "wins"         : self.coins_dict[user_id]["wins"],
                    "losses"       : self.coins_dict[user_id]["losses"],
                    "streak"       : self.coins_dict[user_id]["streak"],
                    "best_streak"  : self.coins_dict[user_id]["best_streak"],
                    "biggest_win"  : self.coins_dict[user_id]["biggest_win"],
                    "biggest_loss" : self.coins_dict[user_id]["biggest_loss"],
                    "duel_profits" : self.coins_dict[user_id]["duel_profits"],
                    "steam_id"     : self.coins_dict[user_id]["steam_id"]
                })


    # backup coins to a timestamped file inside the backups folder
    def backup_coins(self):
        now = dt.datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H%M")
        log.info(f"Backing up CSV file: yomocoin_backups/yomocoins_{timestamp}.csv ...")
        self.save_coins(f"yomocoin_backups/yomocoins_{timestamp}.csv")


    # caching - save YomoCoins file if a certain amount of time has passed since it was last saved
    def save_coins_if_necessary(self, filename: str):
        now = dt.datetime.now()
        if (self.time_last_saved - now > dt.timedelta(minutes=30)):
            log.info("Automatically saving CSV file...")
            self.save_coins(filename)
            self.backup_coins()
            self.time_last_saved = now


    # get a user's coins, return None for non-existent entry
    def get_coins(self, user_id: int):
        if user_id not in self.coins_dict: 
            return None
        else:
            return self.coins_dict[user_id]["coins"]


    # set a user's coins (and add them to the database if they didn't exist before)
    def set_coins(self, user_id: int, coins: int, name: str):
        if user_id not in self.coins_dict: 
            self.coins_dict[user_id] = {}
            self.coins_dict[user_id]["daily"] = dt.date.today() - dt.timedelta(days=1)
            self.coins_dict[user_id]["coins"]        = 0
            self.coins_dict[user_id]["wins"]         = 0
            self.coins_dict[user_id]["losses"]       = 0
            self.coins_dict[user_id]["streak"]       = 0
            self.coins_dict[user_id]["best_streak"]  = 0
            self.coins_dict[user_id]["biggest_win"]  = 0
            self.coins_dict[user_id]["biggest_loss"] = 0
            self.coins_dict[user_id]["duel_profits"] = 0
            self.coins_dict[user_id]["steam_id"]     = ""
        log.info(f"""set_coins: {name}: {self.coins_dict[user_id]["coins"]} -> {coins}""")
        self.coins_dict[user_id]["coins"] = coins


    # list of all user ids, sorted from richest to poorest
    def sorted_coins_list(self): 
        return sorted(self.coins_dict, key=lambda x: self.get_coins(x), reverse=True)


    # check if a user has already claimed their daily coins
    def get_daily_claimed(self, user_id: int):
        return dt.date.today() == self.coins_dict[user_id]["daily"]


    # record that a user claimed their daily today
    def set_daily_claimed(self, user_id: int):
        self.coins_dict[user_id]["daily"] = dt.date.today()


    # get a user's total wins
    def get_wins(self, user_id: int): 
        return self.coins_dict[user_id]["wins"]


    # record a successful bet (and indirectly also set streak and best_streak)
    def record_win(self, user_id: int, amount: int): 
        # increment win counter
        new_wins = self.coins_dict[user_id]["wins"] + 1
        self.coins_dict[user_id]["wins"] = new_wins

        # increment streak counter
        new_streak = self.coins_dict[user_id]["streak"] + 1
        self.coins_dict[user_id]["streak"] = new_streak

        # record new best streak if applicable
        if new_streak > self.coins_dict[user_id]["best_streak"]:
            self.coins_dict[user_id]["best_streak"] = new_streak

        # record new biggest win if applicable
        if amount > self.coins_dict[user_id]["biggest_win"]:
            self.coins_dict[user_id]["biggest_win"] = amount


    # get a user's total losses
    def get_losses(self, user_id: int): 
        return self.coins_dict[user_id]["losses"]


    # record a failed bet (and reset streak)
    def record_loss(self, user_id: int, amount: int): 
        # increment loss counter
        new_losses = self.coins_dict[user_id]["losses"] + 1
        self.coins_dict[user_id]["losses"] = new_losses

        # reset streak counter
        self.coins_dict[user_id]["streak"] = 0

        # record new biggest loss if applicable
        if amount > self.coins_dict[user_id]["biggest_loss"]:
            self.coins_dict[user_id]["biggest_loss"] = amount


    # get a user's current winning streak
    def get_streak(self, user_id: int): 
        return self.coins_dict[user_id]["streak"]


    # get a user's current winning streak
    def get_best_streak(self, user_id: int): 
        return self.coins_dict[user_id]["best_streak"]


    # get a user's biggest win amount
    def get_biggest_win(self, user_id: int): 
        return self.coins_dict[user_id]["biggest_win"]


    # get a user's biggest loss amount
    def get_biggest_loss(self, user_id: int): 
        return self.coins_dict[user_id]["biggest_loss"]


    def is_richest_yomofan(self, user_id: int): 
        # If everyone has the exact same amount of coins we don't want to deadlock centrelink
        return (
            user_id == max(self.coins_dict, key=lambda k: self.coins_dict[k]["coins"])
            and user_id != min(self.coins_dict, key=lambda k: self.coins_dict[k]["coins"])
        )


    def get_winrate(self, user_id: int): 
        wins   = self.get_wins(user_id)
        losses = self.get_losses(user_id)
        total  = wins + losses
        if total > 0: 
            return float(100 * wins / total)
        else:
            return 0


    def sorted_winrate_list(self):
        winrate_list = [
            (user_id, self.get_winrate(user_id)) 
            for user_id 
            in self.coins_dict.keys() 
            if self.get_wins(user_id) >= 25
        ]
        return sorted(winrate_list, key=lambda t: t[1], reverse=True) 


    def get_duel_profit(self, user_id: int): 
        return self.coins_dict[user_id]["duel_profits"]


    def record_duel_profit(self, user_id: int, amount: int): 
        new_profit = self.coins_dict[user_id]["duel_profits"] + amount
        self.coins_dict[user_id]["duel_profits"] = new_profit


    # get a user's steamid
    def get_steam_id(self, user_id: int):
        if user_id not in self.coins_dict: 
            return None
        else:
            return self.coins_dict[user_id]["steam_id"]


    # set a user's coins (and add them to the database if they didn't exist before)
    def set_steam_id(self, user_id: int, id_str: str, name: str):
        if user_id not in self.coins_dict: 
            self.coins_dict[user_id] = {}
            self.coins_dict[user_id]["daily"] = dt.date.today() - dt.timedelta(days=1)
            self.coins_dict[user_id]["coins"]        = 310
            self.coins_dict[user_id]["wins"]         = 0
            self.coins_dict[user_id]["losses"]       = 0
            self.coins_dict[user_id]["streak"]       = 0
            self.coins_dict[user_id]["best_streak"]  = 0
            self.coins_dict[user_id]["biggest_win"]  = 0
            self.coins_dict[user_id]["biggest_loss"] = 0
            self.coins_dict[user_id]["duel_profits"] = 0
            self.coins_dict[user_id]["steam_id"]     = ""
        log.info(f"""set_steam_id: {name}: {self.coins_dict[user_id]["steam_id"]} -> {id_str}""")
        self.coins_dict[user_id]["steam_id"] = id_str