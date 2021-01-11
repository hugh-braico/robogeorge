import csv
import datetime as dt


class YomoCoins:

    # constructor
    def __init__(self):  
        self.coins_dict = {}
        self.time_last_saved = dt.datetime.now()
        self.daily_coins_day = dt.date.today()
        self.daily_coins_dict = {}


    # load YomoCoins file 
    def load_coins(self, filename: str):
        with open(filename, newline='') as csvfile: 
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.coins_dict[int(row["user_id"])] = {} 
                self.coins_dict[int(row["user_id"])]["coins"] = int(row["coins"])
        print(f"YomoCoins loaded from {filename}.")


    # save YomoCoins file 
    def save_coins(self, filename: str):
        with open(filename, "w", newline='') as csvfile: 
            fieldnames = ["user_id", "coins"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for user_id in self.coins_dict:
                writer.writerow({"user_id" : user_id, "coins" : self.coins_dict[user_id]["coins"]})
        print(f"YomoCoins saved to {filename}.")


    # save YomoCoins file if more than an hour has passed since it was last saved
    def save_coins_if_necessary(self, filename: str):
        now = dt.datetime.now()
        if (self.time_last_saved - now > dt.timedelta(minutes=60)):
            self.save_coins(filename)
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
        self.coins_dict[user_id]["coins"] = coins


    # return descending sorted list of database 
    def sorted_coins_list(self): 
        return sorted(self.coins_dict, key=lambda x: self.get_coins(x), reverse=True)


    # check if a user is eligible to receive daily coins
    def check_daily_eligibility(self, user_id: int):
        today = dt.date.today()
        if today != self.daily_coins_day:
            self.daily_coins_dict = {}
            self.daily_coins_day = today
        if user_id not in self.daily_coins_dict: 
            self.daily_coins_dict[user_id] = True
            return True
        else:
            return False

