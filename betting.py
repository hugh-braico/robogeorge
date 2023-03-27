import logging
log = logging.getLogger("yomo")

# betting.py
# Fairly simple class that stores the state of a betting round
# Actual transactions and stuff are handled in yomocoins.py

class Betting:

    # constructor
    def __init__(self):
        # is there a betting round currently active? 
        self.active = False
        # Are users allowed to bet right now? 
        self.locked = False 
        # Is there an auto lock scheduled? 
        self.autolock = None
        # The things to bet on
        self.teamlist = None
        # dict of user ids to bet amounts
        self.bets = {}
        self.canceller_id = None
        self.draft = "A draft image hasn't been linked yet, use `!draft <link>` to link one."


    # check if betting is active
    def is_active(self): 
        return self.active


    # check if betting is locked
    def is_locked(self): 
        return self.locked


    # unlock betting
    def lock(self): 
        self.locked = True


    # lock betting
    def unlock(self): 
        self.locked = False


    # check if a lock is scheduled
    def get_autolock(self): 
        return self.autolock


    # mark if a lock is scheduled or not with a timestamp
    def set_autolock(self, t): 
        self.autolock = t


    # get status of canceller proposal (None if nobody proposing and an id otherwise) 
    def get_canceller(self):
        return self.canceller_id


    # set canceller's id
    def set_canceller(self, user_id: int):
        self.canceller_id = user_id


    # check if there are any bets yet
    def is_empty(self): 
        if not self.active:
            return True
        else:
            return len(self.bets) == 0


    # start betting round
    def start(self, teamlist):
        if self.is_active():
            raise Exception("Tried to use start while betting active")
        else:
            self.active = True
            self.locked = False 
            self.autolock = None 
            self.canceller_id = None
            self.teamlist = teamlist
            self.bets = {}
            self.draft = "A draft image hasn't been linked yet, use `!draft <link>` to link one."


    # cancel betting round
    # does not give each user their money back, so that has to be handled separately
    def cancel(self): 
        if not self.is_active():
            raise Exception("Tried to use cancel while betting not active")
        else:
            self.active = False
            self.locked = False
            self.autolock = None
            self.canceller_id = None
            self.teamlist = None
            self.bets = {}
            self.draft = "A draft image hasn't been linked yet, use `!draft <link>` to link one."


    # how many teams are being bet on? 
    def get_num_teams(self):
        if not self.is_active():
            raise Exception("Tried to use get_num_teams while betting not active")
        else: 
            return len(self.teamlist)


    # get team by index (starting at 0)
    def get_team(self, team_indexber):
        if not self.is_active():
            raise Exception("Tried to use get_team while betting not active")
        else: 
            return self.teamlist[team_indexber]


    # get team by index (starting at 0)
    def get_teamlist(self):
        if not self.is_active():
            raise Exception("Tried to use get_teamlist while betting not active")
        else: 
            return self.teamlist


    # check if a user has already placed a bet in the current round
    def bet_exists(self, user_id: int): 
        if not self.is_active():
            return False
        else: 
            return user_id in self.bets


    # get a user's existing bet
    def get_bet(self, user_id: int): 
        if not self.bet_exists(user_id):
            return None
        else:
            return self.bets[user_id]


    # get the link to the current draft image
    def get_draft(self):
        return self.draft


    # set the link to the current draft image
    def set_draft(self, link: str):
        self.draft = link


    # place a new bet 
    def place_bet(self, user_id: int, team: str, amount: int, display_emote: str): 
        if not self.is_active():
            raise Exception("Tried to use place_bet while betting not active")
        elif team not in self.teamlist:
            raise Exception(f"place_bet: invalid team {team}")
        else: 

            self.bets[user_id] = {
                "team"          : team, 
                "amount"        : amount,
                "team_index"    : self.teamlist.index(team),
                "display_emote" : display_emote
            }


    # ordered list of bets in descending order
    # optional "team" parameter to only get bets for a specific team
    def get_bets_list(self, team: str = None, invert = False):
        if not self.is_active():
            raise Exception("Tried to use get_bets_list while betting not active")
        else: 
            if team:
                if invert:
                    # return only the bets for all teams BUT this team
                    return [
                        (u, self.bets[u]["team"], self.bets[u]["amount"], self.bets[u]["display_emote"]) 
                        for u 
                        in sorted(self.bets, key=lambda u: self.bets[u]["amount"], reverse=True)
                        if self.bets[u]["team"] != team
                    ]
                else:
                    # return only the bets for this team
                    return [
                        (u, self.bets[u]["team"], self.bets[u]["amount"], self.bets[u]["display_emote"]) 
                        for u 
                        in sorted(self.bets, key=lambda u: self.bets[u]["amount"], reverse=True)
                        if self.bets[u]["team"] == team
                    ]
            else:
                # return all bets
                return [
                    (u, self.bets[u]["team"], self.bets[u]["amount"], self.bets[u]["display_emote"]) 
                    for u 
                    in sorted(self.bets, key=lambda u: self.bets[u]["amount"], reverse=True)
                ]