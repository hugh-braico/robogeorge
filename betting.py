

class Betting:

    # constructor
    def __init__(self):
        # is there a betting round currently active? 
        self.active = False
        # Are users allowed to bet right now? 
        self.locked = False 
        # The things to bet on
        self.team1 = None
        self.team2 = None
        # dict of user ids to bet amounts
        self.bets = {}


    # check if betting is active
    def is_active(self): 
        return self.active


    # check if betting is locked
    def is_locked(self): 
        return self.locked


    # lock betting
    def lock(self): 
        self.locked = True


    # check if there are any bets yet
    def is_empty(self): 
        if not self.active:
            return True
        else:
            return len(self.bets) == 0


    # start betting round
    def start(self, team1: str, team2: str):
        if self.is_active():
            raise Exception("Tried to use start while betting active")
        else:
            self.active = True
            self.locked = False 
            self.team1 = team1
            self.team2 = team2
            self.bets = {}


    # get team1
    def get_team1(self):
        if not self.is_active():
            raise Exception("Tried to use get_team1 while betting not active")
        else: 
            return self.team1


    # get team2
    def get_team2(self):
        if not self.is_active():
            raise Exception("Tried to use get_team2 while betting not active")
        else: 
            return self.team2


    # cancel betting round - make sure you give everyone's money back first!
    def cancel(self): 
        if not self.is_active():
            raise Exception("Tried to use cancel while betting not active")
        else:
            self.active = False
            self.locked = False
            self.team1 = None
            self.team2 = None
            self.bets = {}


    # check if a user has already placed a bet in the current round
    def bet_exists(self, user_id: int): 
        if not self.is_active():
            raise Exception("Tried to use bet_exists while betting not active")
        else: 
            return user_id in self.bets


    # place a new bet
    def place_bet(self, user_id: int, team: int, amount: int): 
        if not self.is_active():
            raise Exception("Tried to use place_bet while betting not active")
        elif self.bet_exists(user_id):
            raise Exception("Tried to overwrite an existing bet")
        else: 
            if team == 1:
                betting_team = self.team1
            elif team == 2:
                betting_team = self.team2
            self.bets[user_id] = {"team": betting_team, "amount" : amount}


    # ordered list of bets, descending order
    def get_bets_list(self):
        if not self.is_active():
            raise Exception("Tried to use get_bets_list while betting not active")
        else: 
            return [
                (u, self.bets[u]["team"], self.bets[u]["amount"]) 
                for u 
                in sorted(self.bets, key=lambda u: self.bets[u]["amount"], reverse=True)
            ]


    # ordered list of winning bets, descending order
    def get_winners_list(self, winning_team):
        if not self.is_active():
            raise Exception("Tried to use get_winners_list while betting not active")
        else: 
            return [
                (u, self.bets[u]["team"], self.bets[u]["amount"]) 
                for u 
                in sorted(self.bets, key=lambda u: self.bets[u]["amount"], reverse=True)
                if self.bets[u]["team"] == winning_team
            ]


    # ordered list of winning bets, descending order
    def get_losers_list(self, winning_team):
        if not self.is_active():
            raise Exception("Tried to use get_losers_list while betting not active")
        else: 
            return [
                (u, self.bets[u]["team"], self.bets[u]["amount"])
                for u 
                in sorted(self.bets, key=lambda u: self.bets[u]["amount"], reverse=True)
                if self.bets[u]["team"] != winning_team
            ]