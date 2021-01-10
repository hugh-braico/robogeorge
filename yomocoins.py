import csv
import datetime as dt

coins_dict = {}
time_last_saved = dt.datetime.now()

# load YomoCoins file 
def load_coins(filename):
    with open(filename, newline='') as csvfile: 
        reader = csv.DictReader(csvfile)
        for row in reader:
            coins_dict[int(row["user_id"])] = {} 
            coins_dict[int(row["user_id"])]["coins"] = int(row["coins"])
    print(f"YomoCoins loaded from {filename}.")


# save YomoCoins file 
def save_coins(filename):
    with open(filename, "w", newline='') as csvfile: 
        fieldnames = ["user_id", "coins"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user_id in coins_dict:
            writer.writerow({"user_id" : user_id, "coins" : coins_dict[user_id]["coins"]})
    print(f"YomoCoins saved to {filename}.")


# save YomoCoins file if more than an hour has passed since it was last saved
def save_coins_if_necessary(filename):
    now = dt.datetime.now()
    global time_last_saved
    if (time_last_saved - now > dt.timedelta(minutes=60)):
        save_coins(filename)
    time_last_saved = now