import logging
log = logging.getLogger("yomo")

# mahjong.py
# Fairly simple class that stores the state of a mahjong round
# Actual transactions and stuff are handled in yomocoins.py

class Mahjong:

    # constructor
    def __init__(self):
        # is there a mahjong round currently active? 
        self.active = False
        # The amount of yomocoins that it costs to buy in
        self.buyin = None
        # list of players
        self.players = []


    # check if mahjong is active
    def is_active(self): 
        return self.active


    # start mahjong round
    # does not handle buy ins, so that has to be handled separately
    def start(self, buyin, playerlist):
        if self.is_active():
            raise Exception("Tried to use start while mahjong active")
        else:
            self.active = True
            self.buyin = buyin
            self.players = playerlist


    # cancel mahjong round
    # does not give each user their money back, so that has to be handled separately
    def cancel(self): 
        if not self.is_active():
            raise Exception("Tried to use cancel while mahjong not active")
        else:
            self.active = False
            self.buyin = None
            self.players = []


    # check if a user is playing mahjong
    def buyin_exists(self, user_id: int): 
        if not self.is_active():
            return False
        else: 
            return user_id in self.players


    # get the current buyin
    def get_buyin(self): 
        return self.buyin


    # get players list
    def get_players(self):
        if not self.is_active():
            raise Exception("Tried to use get_players while mahjong not active")
        else: 
            return self.players