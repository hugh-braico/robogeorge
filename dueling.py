import logging
log = logging.getLogger("yomo")

# dueling.py
# A duel is just a 1 on 1 bet that is decided by coinflip
# Actual transactions and stuff are handled in yomocoins.py

class Dueling:

    # constructor
    def __init__(self):
        # Simple list of (challenger_id, accepter_id, amount) tuples
        # There aren't going to be enough concurrent duels that this even approaches being a problem
        self.duels = []


    # Find bet by challenger id and accepter id, return amount if found and None if not found
    def duel_exists(self, cid: int, aid: int):
        found = next((duel for duel in self.duels if duel[0] == cid and duel[1] == aid), None)
        if found: 
            return found[2]
        else:
            return None


    # get amount for a specific duel - just syntactic sugar for duel_exists
    def get_amount(self, cid: int, aid: int):
        return self.duel_exists(cid, aid)


    # start a new dueling round
    def start(self, challenger: int, accepter: int, amount: int):
        if self.duel_exists(challenger, accepter):
            raise Exception(f"dueling: start(): Tried to add duplicate duel ({challenger}, {accepter}, {amount})")
        else:
            self.duels.append((challenger, accepter, amount))


    # remove dueling round
    # does not give each user their money back, so that has to be handled separately (!)
    def remove(self, challenger: int, accepter: int):
        amount = self.duel_exists(challenger, accepter)
        if not amount:
            raise Exception(f"dueling: remove(): Tried to remove a duel that does not exist ({challenger}, {accepter}, x)") 
        else:
            self.duels.remove((challenger, accepter, amount))


    # get all duels sorted in descending amount order
    # optionally filter by challenger and/or accepter
    def get_duels(self, challenger: int=None, accepter: int=None):
        result = self.duels
        if challenger:
            result = [duel for duel in result if duel[0] == challenger]
        if accepter: 
            result = [duel for duel in result if duel[1] == accepter]
        return sorted(result, key=lambda d: d[2], reverse=True)


    # get all duels that involve a certain user (on either side)
    def get_duels_involving(self, user_id: int):
        result = [duel for duel in self.duels if duel[0] == user_id or duel[1] == user_id]
        return sorted(result, key=lambda d: d[2], reverse=True)