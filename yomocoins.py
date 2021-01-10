import csv
import datetime as dt

coins_dict = {}
time_last_saved = dt.datetime.now()


# load YomoCoins file 
def load_coins(filename: str):
    with open(filename, newline='') as csvfile: 
        reader = csv.DictReader(csvfile)
        for row in reader:
            coins_dict[int(row["user_id"])] = {} 
            coins_dict[int(row["user_id"])]["coins"] = int(row["coins"])
    print(f"YomoCoins loaded from {filename}.")


# save YomoCoins file 
def save_coins(filename: str):
    with open(filename, "w", newline='') as csvfile: 
        fieldnames = ["user_id", "coins"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user_id in coins_dict:
            writer.writerow({"user_id" : user_id, "coins" : coins_dict[user_id]["coins"]})
    print(f"YomoCoins saved to {filename}.")


# save YomoCoins file if more than an hour has passed since it was last saved
def save_coins_if_necessary(filename: str):
    now = dt.datetime.now()
    global time_last_saved
    if (time_last_saved - now > dt.timedelta(minutes=60)):
        save_coins(filename)
    time_last_saved = now


# get a user's coins, return None for non-existent entry
def get_coins(user_id: int):
    if user_id not in coins_dict: 
        return None
    else:
        return coins_dict[user_id]["coins"]


# set a user's coins (and add them to the database if they didn't exist before)
def set_coins(user_id: int, coins: int):
    if user_id not in coins_dict: 
        coins_dict[user_id] = {}
    coins_dict[user_id]["coins"] = coins


# return descending sorted list of database 
def sorted_coins_list(): 
    return sorted(coins_dict, key=lambda x: get_coins(x), reverse=True)