import logging
log = logging.getLogger("yomo")

import random

class RandomSelecting:

    # pick and format completely random team
    def random_team(self):
        team = random.sample(list(self.movesets.keys()), 3)
        return '\n'.join([
            f"Point: {self.character_string(team[0])}",
            f"Mid: {self.character_string(team[1])}",
            f"Anchor: {self.character_string(team[2])}"
        ])

    # pick and format completely random team with duplicate characters
    def random_team3(self):
        char = random.choice(list(self.movesets.keys()))
        return '\n'.join([
            f"Point: {self.character_string(char)}",
            f"Mid: {self.character_string(char)}",
            f"Anchor: {self.character_string(char)}"
        ])

    # pick and format random not-too-terrible team
    def random_tasteful_team(self):
        team = random.sample(list(self.tasteful_movesets.keys()), 3)
        return '\n'.join([
            f"Point: {self.tasteful_character_string(team[0])}",
            f"Mid: {self.tasteful_character_string(team[1])}",
            f"Anchor: {self.tasteful_character_string(team[2])}"
        ])

    # pick and format random not-too-terrible team with duplicate characters
    def random_tasteful_team3(self):
        char = random.choice(list(self.tasteful_movesets.keys()))
        return '\n'.join([
            f"Point: {self.tasteful_character_string(char)}",
            f"Mid: {self.tasteful_character_string(char)}",
            f"Anchor: {self.tasteful_character_string(char)}"
        ])

    # pick and format random team with meta assists
    def random_meta_team(self):
        team = random.sample(list(self.meta_movesets.keys()), 3)
        return '\n'.join([
            f"Point: {self.meta_character_string(team[0])}",
            f"Mid: {self.meta_character_string(team[1])}",
            f"Anchor: {self.meta_character_string(team[2])}"
        ])

    # pick and format random team with meta assists + duplicate characters
    def random_meta_team3(self):
        char = random.choice(list(self.meta_movesets.keys()))
        return '\n'.join([
            f"Point: {self.meta_character_string(char)}",
            f"Mid: {self.meta_character_string(char)}",
            f"Anchor: {self.meta_character_string(char)}"
        ])

    # pick and format a completely random assist
    def character_string(self, character):
        assist = random.choice(self.movesets[character])
        return f"**{character}** ({assist} assist)"

    # pick and format a random not-terrible assist
    def tasteful_character_string(self, character):
        assist = random.choice(self.tasteful_movesets[character])
        return f"**{character}** ({assist} assist)"

    # pick and format a random meta assist
    def meta_character_string(self, character):
        assist = random.choice(self.meta_movesets[character])
        return f"**{character}** ({assist} assist)"

    def __init__(self):

        self.meta_movesets = {
            "ANNIE": 
            [
                "6HP",
                "H CRESCENT CUT",
                "H NORTH KNUCKLE",
                "H DESTRUCTION PILLAR"
            ],
            "BEOWULF": 
            [
                "2HP",
                "L HURTING HURL",
                "H HURTING HURL"
            ],
            "BIG BAND": 
            [
                "L BEAT EXTEND",
                "M BEAT EXTEND",
                "H BEAT EXTEND",
                "H BRASS KNUCKLES",
                "H A TRAIN"
            ],
            "BLACK DAHLIA": 
            [
                "2MK",
                "M ORDER UP!"
            ],
            "CEREBELLA": 
            [
                "H LOCK N LOAD",
                "CERECOPTER",
                "EXCELLABELLA"
            ],
            "DOUBLE": 
            [
                "L BOMBER",
                "M BOMBER",
                "H BOMBER",
                "CILIA SLIDE"
            ],
            "ELIZA": 
            [
                "H OSIRIS SPIRAL",
                "BUTCHERS BLADE",
                "AXE"
            ],
            "FILIA": 
            [
                "H UPDO",
                "H HAIRBALL"
            ],
            "FUKUA": 
            [
                "L DART",
                "M CLONE",
                "H DRILL"
            ],
            "MARIE": 
            [
                "HOP TO IT",
                "MARIE GO ROUND H",
                "HILGARD'S HAYMAKER H"
            ],
            "MS. FORTUNE": 
            [
                "5HK",
                "H FIBER",
                "DASH"
            ],
            "PAINWHEEL": 
            [
                "2MP",
                "L PINION",
                "H PINION"
            ],
            "PARASOUL": 
            [
                "L NAPALM SHOT",
                "NAPALM PILLAR"
            ],
            "PEACOCK": 
            [
                "5HP",
                "L GEORGE",
                "M ITEM DROP",
                "CHARGED M ITEM DROP"
            ],
            "ROBO-FORTUNE": 
            [
                "5HP",
                "H BEAM"
            ],
            "SQUIGLY": 
            [
                "2HP",
                "DRAG N BITE"
            ],
            "UMBRELLA": 
            [
                "6HP",
                "SALT GRINDER",
                "HUNGERN RUSH",
                "WISH MAKER"
            ],
            "VALENTINE": 
            [
                "H BYPASS"
            ],
        }

        self.tasteful_movesets = {
            "ANNIE": 
            [
                "2HK",
                "6MP",
                "6HP",
                "THROW",
                "H CRESCENT CUT",
                "H NORTH KNUCKLE",
                "H DESTRUCTION PILLAR",
                "TAUNT",
                "DASH"
            ],
            "BEOWULF": 
            [
                "2HP",
                "THROW",
                "L HURTING HURL",
                "M HURTING HURL",
                "H HURTING HURL",
                "L WULF BLITZER",
                "WULF SHOOT",
                "TAUNT",
                "DASH"
            ],
            "BIG BAND": 
            [
                "WEED BLASTER",
                "2HK",
                "THROW",
                "L BEAT EXTEND",
                "M BEAT EXTEND",
                "H BEAT EXTEND",
                "M BRASS KNUCKLES",
                "H BRASS KNUCKLES",
                "L A TRAIN",
                "M A TRAIN",
                "H A TRAIN",
                "L GIANT STEP",
                "M GIANT STEP",
                "H GIANT STEP",
                "TAUNT",
                "DASH"
            ],
            "BLACK DAHLIA": 
            [
                "5HP",
                "2MK",
                "THROW",
                "L ORDER UP!",
                "M ORDER UP!",
                "H ORDER UP!",
                "EMPOWER",
                "L COUNTER, STRIKE!",
                "M COUNTER, STRIKE!",
                "H COUNTER, STRIKE!",
                "TAUNT",
                "DASH"
            ],
            "CEREBELLA": 
            [
                "2HK",
                "6HP",
                "H LOCK N LOAD",
                "DEVIL HORNS",
                "CERECOPTER",
                "DIAMOND DROP",
                "MERRY GO RILLA",
                "EXCELLABELLA",
                "KANCHOU",
                "BATTLE BUTT",
                "DASH"
            ],
            "DOUBLE": 
            [
                "5HP",
                "THROW",
                "L LUGER",
                "H LUGER",
                "L BOMBER",
                "M BOMBER",
                "H BOMBER",
                "CILIA SLIDE",
                "DASH"
            ],
            "ELIZA": 
            [
                "5HP",
                "2HK",
                "THROW",
                "M UPPER KHAT",
                "H UPPER KHAT",
                "H OSIRIS SPIRAL",
                "THRONE OF ISIS",
                "DIVE OF HORUS",
                "WEIGHT OF ANUBIS",
                "BUTCHERS BLADE",
                "AXE",
                "DASH"
            ],
            "FILIA": 
            [
                "2MK",
                "THROW",
                "L RINGLET SPIKE",
                "M RINGLET SPIKE",
                "H RINGLET SPIKE",
                "H UPDO",
                "H HAIRBALL",
                "DASH"
            ],
            "FUKUA": 
            [
                "2MK",
                "L DART",
                "M DART",
                "H DART",
                "L CLONE",
                "M CLONE",
                "H CLONE",
                "H DRILL",
                "TENDER EMBRACE",
                "INEVITABLE SNUGGLE",
                "DASH"
            ],
            "MARIE": 
            [
                "5HP",
                "2HP",
                "THROW",
                "HOP TO IT",
                "MARIE GO ROUND H",
                "SUCTION OBSTRUCTION",
                "HILGARD'S HAYMAKER L",
                "HILGARD'S HAYMAKER M",
                "HILGARD'S HAYMAKER H",
                "HILGARD'S HOWL L",
                "HILGARD'S HOWL M",
                "HILGARD'S HOWL H",
                "DASH"
            ],
            "MS. FORTUNE": 
            [
                "5HK",
                "THROW",
                "CAT STRIKE",
                "H FIBER",
                "DASH"
            ],
            "PAINWHEEL": 
            [
                "2MP",
                "THROW",
                "L STINGER",
                "M STINGER",
                "H STINGER",
                "M BUER",
                "L PINION",
                "M PINION",
                "H PINION",
                "DASH"
            ],
            "PARASOUL": 
            [
                "THROW",
                "6LP",
                "6MP",
                "6HP",
                "4HK",
                "L NAPALM SHOT",
                "M NAPALM SHOT",
                "H NAPALM SHOT",
                "L NAPALM TOSS",
                "NAPALM QUAKE",
                "NAPALM PILLAR",
                "EGRET DIVE",
                "EGRET CHARGE",
                "DASH"
            ],
            "PEACOCK": 
            [
                "5HP",
                "2HK",
                "THROW",
                "M BANG",
                "L GEORGE",
                "M GEORGE",
                "H GEORGE",
                "L ITEM DROP",
                "M ITEM DROP",
                "H ITEM DROP",
                "CHARGED L ITEM DROP",
                "CHARGED M ITEM DROP",
                "CHARGED H ITEM DROP",
                "DASH"
            ],
            "ROBO-FORTUNE": 
            [
                "5HP",
                "5HK",
                "2MK",
                "2HK",
                "THROW",
                "L BEAM",
                "M BEAM",
                "H BEAM",
                "RAM",
                "MINE",
                "SALVO",
                "H DANGER",
                "DASH"
            ],
            "SQUIGLY": 
            [
                "2HP",
                "6HP",
                "THROW",
                "LIVER MORTIS",
                "CENTER STAGE",
                "DRAG N BITE",
                "DRAUGEN PUNCH",
                "ARPEGGIO",
                "THE SILVER CHORD",
                "TREMOLO",
                "DASH"
            ],
            "UMBRELLA": 
            [
                "THROW",
                "6HP",
                "TONGUE TWISTER",
                "SALT GRINDER",
                "SLURP 'N' SLIDE",
                "HUNGERN RUSH",
                "CUTIE PTOOIE",
                "BOBBLIN' BUBBLE",
                "WISH MAKER",
                "DASH"
            ],
            "VALENTINE": 
            [
                "5HP",
                "2MK",
                "THROW",
                "H DEAD CROSS",
                "H BYPASS",
                "L VIAL HAZARD",
                "M VIAL HAZARD",
                "H VIAL HAZARD",
                "MORTUARY DROP",
                "DASH"
            ],
        }

        self.movesets = {
            "ANNIE": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "6MP",
                "6HP",
                "THROW",
                "L CRESCENT CUT",
                "M CRESCENT CUT",
                "H CRESCENT CUT",
                "L NORTH KNUCKLE",
                "M NORTH KNUCKLE",
                "H NORTH KNUCKLE",
                "L DESTRUCTION PILLAR",
                "M DESTRUCTION PILLAR",
                "H DESTRUCTION PILLAR",
                "TAUNT",
                "DASH"
            ],
            "BEOWULF": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "THROW",
                "L HURTING HURL",
                "M HURTING HURL",
                "H HURTING HURL",
                "L WULF BLITZER",
                "M WULF BLITZER",
                "H WULF BLITZER",
                "WULF SHOOT",
                "TAUNT",
                "DASH"
            ],
            "BIG BAND": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "WEED BLASTER",
                "2LK",
                "2MK",
                "2HK",
                "THROW",
                "L BEAT EXTEND",
                "M BEAT EXTEND",
                "H BEAT EXTEND",
                "L BRASS KNUCKLES",
                "M BRASS KNUCKLES",
                "H BRASS KNUCKLES",
                "L A TRAIN",
                "M A TRAIN",
                "H A TRAIN",
                "L GIANT STEP",
                "M GIANT STEP",
                "H GIANT STEP",
                "TAUNT",
                "DASH"
            ],
            "BLACK DAHLIA": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "THROW",
                "ONSLAUGHT",
                "L ORDER UP!",
                "M ORDER UP!",
                "H ORDER UP!",
                "L ANOTHER ROUND",
                "M ANOTHER ROUND",
                "H ANOTHER ROUND",
                "L TEA TIME",
                "M TEA TIME",
                "H TEA TIME",
                "EMPOWER",
                "L COUNTER, STRIKE!",
                "M COUNTER, STRIKE!",
                "H COUNTER, STRIKE!",
                "TAUNT",
                "DASH"
            ],
            "CEREBELLA": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "6HP",
                "THROW",
                "L LOCK N LOAD",
                "M LOCK N LOAD",
                "H LOCK N LOAD",
                "DEFLECTOR",
                "DEVIL HORNS",
                "CERECOPTER",
                "DIAMOND DROP",
                "MERRY GO RILLA",
                "EXCELLABELLA",
                "TUMBLING RUN",
                "RUN STOP",
                "KANCHOU",
                "BATTLE BUTT",
                "TAUNT",
                "DASH"
            ],
            "DOUBLE": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "THROW",
                "FLESH STEP",
                "L LUGER",
                "M LUGER",
                "H LUGER",
                "L BOMBER",
                "M BOMBER",
                "H BOMBER",
                "CILIA SLIDE",
                "TAUNT",
                "DASH"
            ],
            "ELIZA": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "THROW",
                "L UPPER KHAT",
                "M UPPER KHAT",
                "H UPPER KHAT",
                "L OSIRIS SPIRAL",
                "M OSIRIS SPIRAL",
                "H OSIRIS SPIRAL",
                "THRONE OF ISIS",
                "DIVE OF HORUS",
                "WEIGHT OF ANUBIS",
                "KHOPESH",
                "BUTCHERS BLADE",
                "AXE",
                "TAUNT",
                "DASH"
            ],
            "FILIA": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "THROW",
                "L RINGLET SPIKE",
                "M RINGLET SPIKE",
                "H RINGLET SPIKE",
                "RINGLET PSYCHE",
                "L UPDO",
                "M UPDO",
                "H UPDO",
                "L HAIRBALL",
                "M HAIRBALL",
                "H HAIRBALL",
                "TAUNT",
                "DASH"
            ],
            "FUKUA": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "L DART",
                "M DART",
                "H DART",
                "L CLONE",
                "M CLONE",
                "H CLONE",
                "L DRILL",
                "M DRILL",
                "H DRILL",
                "TENDER EMBRACE",
                "INEVITABLE SNUGGLE",
                "TAUNT",
                "DASH"
            ],
            "MARIE": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "THROW",
                "HOP TO IT",
                "MARIE GO ROUND L",
                "MARIE GO ROUND M",
                "MARIE GO ROUND H",
                "SUCTION OBSTRUCTION",
                "HILGARD'S HAYMAKER L",
                "HILGARD'S HAYMAKER M",
                "HILGARD'S HAYMAKER H",
                "HILGARD'S HOWL L",
                "HILGARD'S HOWL M",
                "HILGARD'S HOWL H",
                "TAUNT",
                "DASH"
            ],
            "MS. FORTUNE": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "THROW",
                "L CAT SCRATCH",
                "M CAT SCRATCH",
                "H CAT SCRATCH",
                "CAT STRIKE",
                "L FIBER",
                "M FIBER",
                "H FIBER",
                "TAUNT",
                "DASH"
            ],
            "PAINWHEEL": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "THROW",
                "6HK",
                "FLIGHT",
                "L STINGER",
                "M STINGER",
                "H STINGER",
                "L BUER",
                "M BUER",
                "H BUER",
                "L PINION",
                "M PINION",
                "H PINION",
                "TAUNT",
                "DASH"
            ],
            "PARASOUL": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "THROW",
                "6LP",
                "6MP",
                "6HP",
                "4HK",
                "L NAPALM TOSS",
                "M NAPALM TOSS",
                "H NAPALM TOSS",
                "L NAPALM SHOT",
                "M NAPALM SHOT",
                "H NAPALM SHOT",
                "NAPALM TRIGGER",
                "NAPALM QUAKE",
                "NAPALM PILLAR",
                "EGRET CALL",
                "EGRET DIVE",
                "EGRET CHARGE",
                "TAUNT",
                "DASH"
            ],
            "PEACOCK": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "THROW",
                "L BANG",
                "M BANG",
                "H BANG",
                "L GEORGE",
                "M GEORGE",
                "H GEORGE",
                "L ITEM DROP",
                "M ITEM DROP",
                "H ITEM DROP",
                "CHARGED L ITEM DROP",
                "CHARGED M ITEM DROP",
                "CHARGED H ITEM DROP",
                "L TELEPORT",
                "M TELEPORT",
                "H TELEPORT",
                "TAUNT",
                "DASH"
            ],
            "ROBO-FORTUNE": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "THROW",
                "L BEAM",
                "M BEAM",
                "H BEAM",
                "RAM",
                "MINE",
                "SALVO",
                "L DANGER",
                "M DANGER",
                "H DANGER",
                "TAUNT",
                "DASH"
            ],
            "SQUIGLY": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "6HP",
                "THROW",
                "LIVER MORTIS",
                "CENTER STAGE",
                "DRAG N BITE",
                "DRAUGEN PUNCH",
                "ARPEGGIO",
                "THE SILVER CHORD",
                "TREMOLO",
                "TAUNT",
                "DASH"
            ],
            "UMBRELLA": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "THROW",
                "6LP",
                "6HP",
                "TONGUE TWISTER",
                "SALT GRINDER",
                "SLURP 'N' SLIDE",
                "HUNGERN RUSH",
                "CUTIE PTOOIE",
                "BOBBLIN' BUBBLE",
                "WISH MAKER",
                "TAUNT",
                "DASH"
            ],
            "VALENTINE": 
            [
                "5LP",
                "5MP",
                "5HP",
                "5LK",
                "5MK",
                "5HK",
                "2LP",
                "2MP",
                "2HP",
                "2LK",
                "2MK",
                "2HK",
                "THROW",
                "L DEAD CROSS",
                "M DEAD CROSS",
                "H DEAD CROSS",
                "L BYPASS",
                "M BYPASS",
                "H BYPASS",
                "L VIAL HAZARD",
                "M VIAL HAZARD",
                "H VIAL HAZARD",
                "MORTUARY DROP",
                "TAUNT",
                "DASH"
            ],
        }
