import logging
log = logging.getLogger("yomo")

# dueling.py
# A duel is just a 1 on 1 bet that is decided by coinflip
# Actual transactions and stuff are handled in yomocoins.py

class Dueling:

    # constructor
    def __init__(self):
        # is there a dueling round currently active? 
        self.active = False
        # The participants of the duel (user IDs)
        self.challenger = None
        self.accepter = None
        # The stakes of the duel
        self.amount = None
        

    # check if a duel exists
    def is_active(self): 
        return self.active


    # start dueling round
    def start(self, challenger: int, accepter: int, amount: int):
        if self.is_active():
            raise Exception("Tried to use start while dueling active")
        else:
            self.active = True 
            self.challenger = challenger
            self.accepter = accepter
            self.amount = amount


    # cancel dueling round
    # does not give each user their money back, so that has to be handled separately
    def cancel(self): 
        if not self.is_active():
            raise Exception("Tried to use cancel while dueling not active")
        else:
            self.active = False
            self.challenger = None
            self.accepter = None
            self.amount = None


    # get challenger
    def get_challenger(self):
        if not self.is_active():
            raise Exception("Tried to use get_challenger while dueling not active")
        else: 
            return self.challenger


    # get accepter
    def get_accepter(self):
        if not self.is_active():
            raise Exception("Tried to use get_accepter while dueling not active")
        else: 
            return self.accepter


    # get amount
    def get_amount(self):
        if not self.is_active():
            raise Exception("Tried to use get_amount while dueling not active")
        else: 
            return self.amount