import csv
import datetime as dt

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
        with open(filename, newline='') as csvfile: 
            reader = csv.DictReader(csvfile)
            for row in reader:
                # convert each row in the csv to an entry in a simple Python dictionary
                user_id = int(row["user_id"])
                self.coins_dict[user_id] = {} 
                self.coins_dict[user_id]["coins"]       = int(row["coins"])
                self.coins_dict[user_id]["daily"]       = (dt.datetime.strptime(row["daily"], "%Y-%m-%d")).date()
                self.coins_dict[user_id]["wins"]        = int(row["wins"])
                self.coins_dict[user_id]["losses"]      = int(row["losses"])
                self.coins_dict[user_id]["streak"]      = int(row["streak"])
                self.coins_dict[user_id]["best_streak"] = int(row["best_streak"])
        print(self.logging_timestamp() + f"YomoCoins loaded from {filename}.")

    # save YomoCoins file to disk
    def save_coins(self, filename: str):
        with open(filename, "w", newline='') as csvfile: 
            fieldnames = ["user_id", "coins", "daily", "wins", "losses", "streak", "best_streak"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for user_id in self.coins_dict:
                writer.writerow({
                    "user_id"     : user_id, 
                    "coins"       : self.coins_dict[user_id]["coins"],
                    "daily"       : self.coins_dict[user_id]["daily"].strftime("%Y-%m-%d"),
                    "wins"        : self.coins_dict[user_id]["wins"],
                    "losses"      : self.coins_dict[user_id]["losses"],
                    "streak"      : self.coins_dict[user_id]["streak"],
                    "best_streak" : self.coins_dict[user_id]["best_streak"]
                })
        print(self.logging_timestamp() + f"YomoCoins saved to {filename}.")


    # backup coins to a timestamped file inside the backups folder
    def backup_coins(self):
        now = dt.datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H%M")
        self.save_coins(f"yomocoin_backups/yomocoins_{timestamp}.csv")


    # caching - save YomoCoins file if a certain amount of time has passed since it was last saved
    def save_coins_if_necessary(self, filename: str):
        now = dt.datetime.now()
        if (self.time_last_saved - now > dt.timedelta(minutes=30)):
            print(self.logging_timestamp() + "Autosaving CSV file.")
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
    def set_coins(self, user_id: int, coins: int):
        if user_id not in self.coins_dict: 
            self.coins_dict[user_id] = {}
            self.coins_dict[user_id]["daily"] = dt.date.today() - dt.timedelta(days=1)
            self.coins_dict[user_id]["wins"]        = 0
            self.coins_dict[user_id]["losses"]      = 0
            self.coins_dict[user_id]["streak"]      = 0
            self.coins_dict[user_id]["best_streak"] = 0
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
    def record_win(self, user_id: int): 
        # increment win counter
        new_wins = self.coins_dict[user_id]["wins"] + 1
        self.coins_dict[user_id]["wins"] = new_wins

        # increment streak counter
        new_streak = self.coins_dict[user_id]["streak"] + 1
        self.coins_dict[user_id]["streak"] = new_streak

        # record new best streak if applicable
        if new_streak > self.coins_dict[user_id]["best_streak"]:
            self.coins_dict[user_id]["best_streak"] = new_streak


    # get a user's total losses
    def get_losses(self, user_id: int): 
        return self.coins_dict[user_id]["losses"]


    # record a failed bet (and reset streak)
    def record_loss(self, user_id: int): 
        # increment loss counter
        new_losses = self.coins_dict[user_id]["losses"] + 1
        self.coins_dict[user_id]["losses"] = new_losses

        # reset streak counter
        self.coins_dict[user_id]["streak"] = 0


    # get a user's current winning streak
    def get_streak(self, user_id: int): 
        return self.coins_dict[user_id]["streak"]


    # get a user's current winning streak
    def get_best_streak(self, user_id: int): 
        return self.coins_dict[user_id]["best_streak"]


    # string of current date/time for log purposes    
    # Maybe this belongs in another file
    def logging_timestamp(self):
        now = dt.datetime.now()
        return f"""[{now.strftime("%Y-%m-%d %H:%M:%S")}] """
