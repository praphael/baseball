#!/usr/bin/python3

import sys
import re

# global
playerIDMap = dict()

class Event:
    def __init__(self):
        pass

class PitchSeqData:
    def __init__(self):
        self.pitchesThrown = 0
        self.strikes = 0
        self.balls = 0
        self.intBalls = 0
        self.pitchOuts = 0
        self.pickoffAttempts = 0
        self.catcherPickoffAttempts = 0
        self.catcherBlocks = 0
        self.runnerGoing = 0
        self.inPlay = False
        self.hitBatter = False

# adopted from Chadwick baseball data
locations = {"1", "13", "15", "1S", "2", "2F", "23", "23F", "25", "25F",
  "3SF", "3F", "3DF", "3S", "3", "3D", "34S", "34", "34D",
  "4S", "4", "4D", "4MS", "4M", "4MD",
  "6MS", "6M", "6MD", "6S", "6", "6D",
  "56S", "56", "56D", "5S", "5", "5D", "5SF", "5F", "5DF",
  "7LSF", "7LS", "7S", "78S", "8S", "89S", "9S", "9LS", "9LSF",
  "7LF", "7L", "7", "78", "8", "89", "9", "9L", "9LF",
  "7LDF", "7LD", "7D", "78D", "8D", "89D", "9D", "9LD", "9LDF",
  "78XD", "8XD", "89XD"}

#* the following locations are nonstandard or archaic, but 
# * appear in existing Retrosheet data 

odd_locations= ("13S", "15S", "2LF", "2RF", "2L", "2R", "3L", "46", "5L", 
  "7LDW", "7DW", "78XDW", "8XDW", "89XDW", "9DW", "9LDW",
  "7LMF", "7LM", "7M", "78M", "8LM", "8M", "8RM", "89M", "9M", "9LM", "9LMF",
  "8LS", "8RS", "8LD", "8RD", "8LXD", "8RXD", "8LXDW", "8RXDW")

# result
# hits: 1=single, 2=double, 3=triple, 4=home run
# PB= passed ball 
# BB= walk
# C= catcher interference
# E= error
# F= flyout
# FLE= foul ball error
# FC= fieders choice
# G= groundout
# HBP= hit by pitch,
# I= intentional walk,
# K= strikeout
# L= line out
# PO= pick off
# P= popout
# _= no result (possibly due to another play on the field
#        at bat may continue if play did not end inning
playCodeMap = {"S": "1", "D":"2", "C":"C", "DGR":"2", "T":"3", "HR":"4", "WP":"WP", "W":"BB", "FC":"FC", 
               "PB":"PB", "E":"E", "F":"F", "G":"G", "HP":"HBP", "IW":"IBB", "K":"K",
               "L":"L", "SB":"SB", "CS":"CS", "PO":"PO", "P":"P", "K23":"K", "NP":"NP" }

for m in list(playCodeMap.keys()):
    playCodeMap[m + "!"] = playCodeMap[m]
    playCodeMap[m + "#"] = playCodeMap[m]
    playCodeMap[m + "?"] = playCodeMap[m]

modCodeMap = {"AP": "appeal play",
"BP": "pop up bunt",
"BG": "ground ball bunt",
"BGDP": "bunt grounded into double play",
"BINT": "batter interference",
"BL": "line drive bunt",
"BOOT": "batting out of turn",
"BP": "bunt pop up",
"BPDP": "bunt popped into double play",
"BR": "runner hit by batted ball",
"C": "called third strike",
"COUB": "courtesy batter",
"COUF": "courtesy fielder",
"COUR": "courtesy runner",
"DP": "unspecified double play",
"E$": "error on $",
"F": "fly",
"FDP": "fly ball double play",
"FINT": "fan interference",
"FL": "foul",
"FO": "force out",
"G": "ground ball",
"GDP": "ground ball double play",
"GTP": "ground ball triple play",
"IF": "infield fly rule",
"INT": "interference",
"IPHR": "inside the park home run",
"L": "line drive",
"LDP": "lined into double play",
"LTP": "lined into triple play",
"MREV": "manager challenge of call on the field",
"NDP": "no double play credited for this play",
"OBS": "obstruction (fielder obstructing a runner)",
"P": "pop fly",
"PASS": "a runner passed another runner and was called out",
"R$": "relay throw from the initial fielder to $ with no out made",
"RINT": "runner interference",
"SF": "sacrifice fly",
"SH": "sacrifice hit (bunt)",
"TH": "throw",
"TH%": "throw to base %",
"TP": "unspecified triple play",
"UINT": "umpire interference",
"UREV": "umpire review of call on the field" }

for m in list(modCodeMap.keys()):
    modCodeMap[m + "!"] = modCodeMap[m]
    modCodeMap[m + "#"] = modCodeMap[m]
    modCodeMap[m + "?"] = modCodeMap[m]
    

batPlaysNoParse = []
runPlaysNoParse = []

class PlayEvent(Event):
    def parsePitchSeq(self):
        if self.pitch_seq != None and self.pitch_seq != "":
            s = PitchSeqData()
            for p in self.pitch_seq:
                if p == "+": #  following pickoff throw by the catcher
                    s.catcherPickoffAttempts += 1
                elif p == "*": #  indicates the following pitch was blocked by the catcher
                    s.catcherBlocks += 1
                elif p == ".": #  marker for play not involving the batter
                    pass
                #  pickoff throw to first
                elif p in ("1", "2", "3"):
                    s.pickoffAttempts += 1
                elif p == ">": #  Indicates a runner going on the pitch
                    s.runnerGoing += 1
                elif p == "A": #  automatic strike, usually for pitch timer violation
                    s.strikes += 1
                elif p == "B": # ball
                    s.balls += 1
                    s.pitchesThrown += 1
                elif p == "C": #  called strike
                    s.strikes += 1
                    s.pitchesThrown += 1
                elif p == "F": #  foul
                    s.strikes += 1
                    s.pitchesThrown += 1
                elif p == "H": #  hit batter
                    s.balls += 1
                    s.hitBatter = True
                    s.pitchesThrown += 1
                elif p == "I": #  intentional ball
                    s.pitchesThrown += 1
                    s.intBalls += 1
                elif p == "K": #  strike (unknown type)
                    s.strikes += 1
                    s.pitchesThrown += 1
                elif p == "L": #  foul bunt
                    s.strikes += 1
                    s.pitchesThrown += 1
                elif p == "M": #  missed bunt attempt
                    s.strikes += 1
                    s.pitchesThrown += 1
                elif p == "N": #  no pitch (on balks and interference calls)
                    pass
                elif p == "O": #  foul tip on bunt
                    s.strikes += 1
                    s.pitchesThrown += 1
                elif p == "P": #  pitchout
                    s.pitchOuts += 1
                elif p == "Q": #  swinging on pitchout
                    s.strikes += 1
                    s.pitchOuts += 1
                elif p == "R": #  foul ball on pitchout
                    s.strikes += 1
                    s.pitchOuts += 1
                elif p == "S": #  swinging strike
                    s.strikes += 1
                    s.pitchesThrown += 1
                elif p == "T": #  foul tip
                    s.strikes += 1
                    s.pitchesThrown += 1
                elif p == "U": #  unknown or missed pitch
                    pass
                elif p == "V": #  called ball because pitcher went to his mouth or automatic ball on intentional walk orpitch timer violation
                    s.balls += 1                    
                elif p == "X": # ball put into play by batter
                    s.strikes += 1
                    s.pitchesThrown += 1
                    s.inPlay = True
                elif p == "Y": # ball put into play on pitchout
                    s.inPlay = True
            self.pitchSeq = s

    def parseRunnerMods(self, modsParens):
        runMods = []
        print(modsParens)
        if modsParens in ("", "#", "!", "?"): # no modifiers
            self.run_adv_mods.append(())
            return
        # break up parenthesis
        m = re.match("\((.*)\)*", modsParens)
        for mods in m.groups():
            for mod in mods.split("/"):
                if mod in modCodeMap:
                    runMods.add(mod)
                    continue
                m = re.fullmatch(r"\((\d)\)", mod)
                if m is not None:
                    self.fielding.putouts.append(m.group(1))
                    return
                m = re.fullmatch(r"\((\d)(\d)\)", mod)
                if m is not None:
                    self.fielding.assists.append(m.group(1))
                    self.fielding.putouts.append(m.group(2))                    
                    return
                m = re.fullmatch(r"TH([123H])", mod)
                if m is not None:
                    runMods.add("TH")
                    print("throw to base", m.group(1))
                    continue
                m = re.fullmatch(r"R([123H])", mod)
                if m is not None:
                    print("relay throw to base", m.group(1))
                    continue
                # error (single fielder)
                m = re.fullmatch(r"E(\d)", mod)
                if m is not None:
                    self.fielding.errors.append(m.group(1))
                    continue
                # error (likely due to catch error)
                m = re.fullmatch(r"(\d)E(\d)", mod)
                if m is not None:
                    self.fielding.errors.append(m.group(2))
                    continue
            
        self.run_adv_mods.append(runMods)
        

    def parseRunnerAdv(self):
        self.run_adv = []
        self.run_adv_mods = []
        if len(self.run_all) == 0:
            return
        run_adv = self.run_all.split(";")
        print(" run_adv=", run_adv)
        for adv in run_adv:
            if "-" in adv: # safe
                isSafe = True
                a = adv.split("-")
            elif "X" in adv:  # out
                isSafe = False
                a = adv.split("X")
            else:
                runPlaysNoParse.append((self.play, self.run_all))
                return            
            if len(a) != 2:
                runPlaysNoParse.append((self.play, self.run_all))
                return
            srcBase = a[0]
            dstBase = a[1][0]
            mods = a[1][1:]
            self.parseRunnerMods(mods)
            if srcBase not in ("B","1","2","3"):
                runPlaysNoParse.append(self.run_all)
                return
            if dstBase not in ("H","1","2","3"):
                runPlaysNoParse.append(self.run_all)
                return
            self.run_adv.append((srcBase, dstBase, isSafe))
            if not isSafe:
                self.run_out.append(srcBase)

    def parseResult(self):
        def parseFirst(bat0):
            if bat0 in playCodeMap.keys():
                self.bat.result = playCodeMap[bat0]
                return
            # single digit likely fly ball, or ground ball fieled by first basement
            m = re.fullmatch(r"(\d)[!#?+-]?", bat0)
            if m is not None:
                self.fielding.putouts.append(m.group(1))
                # assume flyout unless first baseman (on which we assume groundout)
                if m.group(1) != "3":
                    self.bat.result = "F"
                else:  
                    self.bat.result = "G"
                return
            # two digits, likely grond ball followed by throw to first
            m = re.fullmatch(r"(\d)(\d)", bat0)
            if m is not None:
                self.fielding.assists.append(m.group(1))
                self.fielding.putouts.append(m.group(2))
                self.bat.result = "G"
                return            
           
            # base hit, single digit followed by S,D,or T
            #m = re.fullmatch(r"(\d)([SDT])", bat0)
            #if m is not None:  
            #    self.fielding.fielded.append(m.group(1))
            #    self.bat.result = playCodeMap[m.group(2)]
            #    return
            # base hit, S,D,or T followed by single digit 
            m = re.fullmatch(r"([SDT])(\d)[#!?]?", bat0)
            if m is not None:  
                self.fielding.fielded.append(m.group(2))
                self.bat.result = playCodeMap[m.group(1)]
                return
            # error (single fielder)
            m = re.fullmatch(r"E(\d)[#!?]?", bat0)
            if m is not None:
                self.fielding.errors.append(m.group(1))
                self.bat.result = playCodeMap["E"]
                return            
            # error (likely due to catch error)
            m = re.fullmatch(r"(\d)E(\d)[#!?]?", bat0)
            if m is not None:
                self.fielding.errors.append(m.group(2))
                self.bat.result = playCodeMap["E"]
                return
            # three digits - groundout off deflection
            m = re.fullmatch(r"(\d)(\d)(\d)[#!?]?", bat0)
            if m is not None:
                self.fielding.deflected.append(m.group(1))
                self.fielding.assists.append(m.group(2))
                self.fielding.putouts.append(m.group(3))
                self.bat.result = "G"
                return           
            # one digit followed by another digit in parens - force out (unassisted)
            m = re.fullmatch(r"(\d)\((\d)\)[#!?]?", bat0)
            if m is not None:
                self.fielding.putouts.append(m.group(1))
                self.run_out.append(m.group(2))
                self.bat.result = "FO"
                return   
            # single force out (to bag other than first)
            m = re.fullmatch(r"(\d)(\d)\(([123B])\)[#!?]?", bat0)
            if m is not None:
                self.fielding.assists.append(m.group(1))
                self.fielding.putouts.append(m.group(2))
                b = m.group(3)
                if b in ("1", "2", "3"):
                    b = int(b)                
                self.run_out.append(b)
                self.bat.result = "FO"
                return
            # force out, likely double play
            m = re.fullmatch(r"(\d)(\d)\(([123B])\)(\d)[#!?]?", bat0)
            if m is not None:
                self.fielding.assists.append(m.group(1))
                self.fielding.assists.append(m.group(2))
                self.fielding.putouts.append(m.group(2))
                b = m.group(3)
                if b in ("1", "2", "3"):
                    b = int(b)                
                self.run_out.append(b)
                self.fielding.putouts.append(m.group(4))
                self.bat.result = "FO"
                return
            # force out, likely double play (no relay throw)
            m = re.fullmatch(r"(\d)\(([123B])\)(\d)[#!?]?", bat0)
            if m is not None:
                self.fielding.assists.append(m.group(1))
                self.fielding.putouts.append(m.group(1))
                b = m.group(3)
                if b in ("1", "2", "3"):
                    b = int(b)                
                self.run_out.append(b)
                self.fielding.putouts.append(m.group(3))
                self.bat.result = "G"
                return
            # two force outs (double play), likely to bag other than first
            m = re.fullmatch(r"(\d)\(([123B])\)(\d)\(([123B])\)[#!?]?", bat0)
            if m is not None:
                self.fielding.putouts.append(m.group(1))
                b = m.group(2)
                if b in ("1", "2", "3"):
                    b = int(b)
                self.run_out.append(b)
                self.fielding.putouts.append(m.group(3))
                b = m.group(4)
                if b in ("1", "2", "3"):
                    b = int(b)
                self.run_out.append(b)                
                self.bat.result = "G"
                return
            # home run (maybe inside the park)
            m = re.fullmatch(r"HR(\d)[#!?]?", bat0)
            if m is not None:
                self.bat.result = playCodeMap["HR"]
                return
            # fielders choice
            m = re.fullmatch(r"FC(\d)[#!?]?", bat0)  
            if m is not None:
                self.bat.result = playCodeMap["FC"]
                self.bat.base = m.group(1)
                return
            # pickoff
            m = re.fullmatch(r"PO(\d)[#!?]?", bat0)  
            if m is not None:
                self.bat.result = playCodeMap["PO"]
                b = m.group(1)

                self.bat.base = m.group(1)
                if b in ("1", "2", "3"):
                    b = int(b)                
                self.run_out.append(b)
                return
            # pickoff with throw info
            m = re.fullmatch(r"PO(\d)\(.*(\d)(\d)\)[#!?]?", bat0)
            if m is not None:
                self.bat.result = playCodeMap["PO"]
                self.bat.base = m.group(1)
                self.fielding.assists.append(m.group(2))
                self.fielding.putouts.append(m.group(3))
                b = m.group(1)
                if b in ("1", "2", "3"):
                    b = int(b)
                self.run_out.append(b)
                return
            # pickoff with error
            m = re.fullmatch(r"PO(\d)\(E(\d)\)[#!?]?", bat0)
            if m is not None:
                self.bat.result = playCodeMap["PO"]
                self.bat.base = m.group(1)
                self.fielding.errors.append(m.group(2))                
                return
            # stolen base
            m = re.fullmatch(r"SB(.)[#!?]?", bat0)
            if m is not None:
                self.bat.result = playCodeMap["SB"]
                self.bat.base = m.group(1)
                return
            # caught stealing
            m = re.fullmatch(r"CS(.)[#!?]?", bat0)
            if m is not None:
                self.bat.result = playCodeMap["CS"]
                self.bat.base = m.group(1)
                b = m.group(1)
                if b in ("2", "3"):
                    b = int(b)-1
                else: # assume home
                    b = 3
                self.run_out.append(b)
                return  
            # caught stealing with base designation and throw info
            m = re.fullmatch(r"CS(.)\((\d)(\d)*\)[#!?]?", bat0)
            if m is not None:
                self.bat.result = playCodeMap["CS"]
                self.bat.base = m.group(1)
                self.fielding.assists.append(m.groups()[-2])
                self.fielding.putouts.append(m.groups()[-1])
                b = m.group(1)
                if b in ("2", "3"):
                    b = int(b)-1
                else: # assume home
                    b = 3
                self.run_out.append(b)
                return  
            # fielding error on foul ball
            m = re.fullmatch(r"FLE(\d)[#!?]?", bat0)
            if m is not None:
                self.bat.result = playCodeMap["FLE"]
                #self.bat.base = m.group(1)
                self.fielding.errors.append(m.group(1))
                return
            # strikeout (dropped third strike)
            m = re.fullmatch(r"K23[!#?+-]?", bat0)
            if m is not None:
                self.bat.result = "K"
                return
            print("cannot parse ", bat0)
            batPlaysNoParse.append((self.play, bat0))

        def parseMod(mod):
            if mod in locations:
                self.bat.hit_loc = mod
                return
            if mod in modCodeMap:
                print("mod", modCodeMap[mod])
                self.mods.add(mod)
                if mod in ("SH", "SF"):
                    self.bat.result = mod
                return
            m = re.fullmatch(r"(\d)", mod)
            if m is not None:
                self.bat.hit_loc = m.group(1)
                return
            m = re.fullmatch(r"([GLFP])(\d)", mod)
            if m is not None:
                self.bat.hit_type = m.group(1)
                self.bat.hit_loc = m.group(2)
                return
            m = re.fullmatch(r"([GLFP])(\d\d)", mod)
            if m is not None:
                self.bat.hit_type = m.group(1)
                self.bat.hit_loc = m.group(2)
                return
            m = re.fullmatch(r"TH([123H])", mod)
            if m is not None:
                print("throw to base", m.group(1))
                return
            m = re.fullmatch(r"R([123H])", mod)
            if m is not None:
                print("relay throw to base", m.group(1))
                return
            # error (single fielder)
            m = re.fullmatch(r"E(\d)", mod)
            if m is not None:
                self.fielding.errors.append(m.group(1))
                self.bat.result = playCodeMap["E"]
                return            
            # error (likely due to catch error)
            m = re.fullmatch(r"(\d)E(\d)", mod)
            if m is not None:
                self.fielding.errors.append(m.group(2))
                self.bat.result = playCodeMap["E"]
                return
            
            batPlaysNoParse.append((self.play, mod))
        
    
        
        pID = playerIDMap[self.player_id][0]
        print("parseResult ", self.inning, self.team, pID, " bat_all=", self.bat_all)
        # can be multiple plays within single line (e.g. double steals)
        rslt = []
        bases = []
        for bat in self.bat_all.split(";"):
            mods = bat.split("/")
            parseFirst(mods[0])
            rslt.append(self.bat.result)
            bases.append(self.bat.base)
            # modifiers
            for m in mods[1:]:
                parseMod(m)
        self.bat.result = rslt
        self.bat.base = bases
        
        

    def parsePlay(self):
        self.bat = Event() # dummy value
        # result (see playCodeMap)
        self.bat.result = None
        # base parameter for plays such as stolen bases, pick offs, etc.
        self.bat.base = None
        # G=ground ball, F=fly ball L=line drive, P=pop up
        self.bat.hit_type = None
        # toughly where in the field ball was hit, fielder pos
        self.bat.hit_field = None

        self.fielding = Event() # dummy value
        # fielder 
        self.fielding.errors = []
        self.fielding.putouts = []
        self.fielding.assists = []
        self.fielding.deflected = []
        # situations where fielder touched ball not involved above, e.g. a base hit
        self.fielding.fielded = []  
        # additional plays (wild pitches, balks, pitchouts, stolen bases, caught stealing etc.)
        self.run_out = []
        self.run_adv = []
        self.run_all = ""
        s = self.play.split(".")
        self.bat_all = s[0]
        if len(s) > 1:
            self.run_all = s[1]
        if len(s) > 2:
            print("parsePlay: unexpected input (more than one '.') play=", self.play)
            return False
        self.parseResult()
        self.parseRunnerAdv()       
        
                
    def __init__(self, p=None):
        if p is not None:
            # destructure
            self.game_id, self.event_id, self.inning, self.team = p[0:4]
            self.player_id, self.batter_count, self.pitch_seq, self.play = p[4:]
            self.pitchSeq = None
            self.mods = set()
            self.parsePitchSeq()
            self.parsePlay()

class SubEvent(Event):
    def __init__(self, s=None):
        if s is not None:
            self.game_id, self.event_id, self.player_id = s[0:3]
            self.team, self.bat_pos, self.field_pos = s[3:]

class Lineup:
    def __init__(self, team):
        self.team = team
        # map between order in batting (1..9)
        # order 0 has no meaning, or could be interpted as the P when using a DH
        self.battingOrder = [None]*10
        # map between field position, with 1=pitcher 2=catcher, 3=1B etc.
        #zposition has no meaning, or could be interpted as the DH
        self.fieldPos = [None]*10
        self.battingOrderStart = [None]*10
        self.battingOrderSubs = [[] for i in range(10)]
        self.pitchersUsed = []

    def print(self):
        print(self.team, "lineup")
        for b in range(1, 10):
            p = self.battingOrder[b]
            pID = playerIDMap[p]
            fldPos = None
            for f in range(1, 10):
                if p == self.fieldPos[f]:
                    fldPos = f
                    break
            print(b, pID, "playing", fldPos)
        print("Pitching", playerIDMap[self.fieldPos[1]])

    
    def applySub(self, sub):
        rep_batter = None
        rep_fielder = None
        newPos = None
        print("applySub: bat_pos=", sub.bat_pos, " field_pos=", sub.field_pos)
        if sub.field_pos == "1":
            self.pitchersUsed.append(sub.player_id)
        if sub.bat_pos != "P":
            idx = int(sub.bat_pos)
            rep_batter = self.battingOrder[idx]
            self.battingOrder[idx] = sub.player_id            
            self.battingOrderSubs[idx].append(sub.player_id)
        if sub.field_pos not in ("D", "H", "R"):
            idx = int(sub.field_pos)
            rep_fielder = self.fieldPos[idx]
            if rep_batter is not None and self.fieldPos[idx] != rep_batter:
                print("WARNING: player is replacing different fielder.")
                # find position in the field the batter was playing
                for f in range(1, 10):
                    if self.fieldPos[f] == rep_batter:
                        # move fielder to this osition
                        self.fieldPos[f] = rep_fielder
                        newPos = f
                        break
            self.fieldPos[idx] = sub.player_id
        return rep_batter, (rep_fielder, newPos)

class FielderStats:
    def __init__(self):
        self.GP = 1
        self.IF3 = 0
        self.PO = 0
        self.A = 0
        self.E = 0
        self.DP = 0
        self.TP = 0
        self.PB = 0

    def add(self, st):
        self.GP += st.GP
        self.IF3 += st.IF3
        self.PO += st.PO
        self.A += st.A
        self.E += st.E
        self.DP += st.DP
        self.TP += st.TP
        self.PB += st.PB

    def printHeader(self):
        print(" "*8, "IF3 PO A  E  DP TP PB")

    def print(self):
        print(f"{self.IF3:4}{self.PO:3}{self.A:3}{self.E:3}{self.E:3}{self.DP:3}{self.TP:3}{self.PB:3}")

class PitcherStats:
    def __init__(self):
        self.GP = 1
        self.IP3 = 0
        self.NOOUT = 0
        self.BF = 0
        self.H = 0
        self.n2B = 0
        self.n3B = 0
        self.HR = 0
        self.R = 0
        self.ER = 0
        self.BB = 0
        self.IBB = 0
        self.K = 0
        self.HBP = 0
        self.WP = 0
        self.BK = 0
        self.SH = 0
        self.SF = 0

    def add(self, st):
        self.IP3 += st.IP3
        self.NOOUT += st.NOOUT
        self.BF += st.BF
        self.H += st.H
        self.n2B += st.n2B
        self.n3B += st.n3B
        self.HR += st.HR
        self.R += st.R
        self.ER += st.ER
        self.BB += st.BB
        self.IBB += st.IBB
        self.K += st.K
        self.HBP += st.HBP
        self.WP += st.WP
        self.BK += st.BK
        self.SH += st.SH
        self.SF += st.SF

    def printHeader(self):
        print(" "*8, "IP3 BF H  K  R BB 2B 3B HR")

    def print(self):
        print(f"{self.IP3:4}{self.BF:3}{self.H:3}{self.K:3}{self.R:3}{self.BB+self.IBB:3}{self.n2B:3}{self.n3B:3}{self.HR:3}")

class BatterStats:
    def __init__(self):
        self.GP = 1
        self.AB = 0
        self.R = 0
        self.H = 0
        self.n2B = 0
        self.n3B = 0
        self.HR = 0
        self.RBI = 0
        self.SH = 0
        self.SF = 0
        self.HBP = 0
        self.BB = 0
        self.IBB = 0
        self.K = 0
        self.HBP = 0
        self.SB = 0
        self.CS = 0
        self.GIDP = 0
        self.INTF = 0

    def add(self, st):
        self.AB += st.AB
        self.R += st.R
        self.H += st.H
        self.n2B += st.n2B
        self.n3B += st.n3B
        self.HR += st.HR
        self.RBI += st.RBI
        self.SH += st.SH
        self.SF += st.SF
        self.HBP += st.HBP
        self.BB += st.BB
        self.IBB += st.IBB
        self.K += st.K
        self.HBP += st.HBP
        self.SB += st.SB
        self.CS += st.CS
        self.GIDP += st.GIDP
        self.INTF += st.INTF

    def printHeader(self):
        print(" "*10, "AB  H  K  R BB 2B 3B HR")

    def print(self):
        print(f"{self.AB:3}{self.H:3}{self.K:3}{self.R:3}{self.BB+self.IBB:3}{self.n2B:3}{self.n3B:3}{self.HR:3}")


class GameState:
    # batsTop = lineup of team batting at the top of the inning
    # batsBot = lineup of team batting at the bottom of the inning
    def __init__(self, batsTop, batsBot):
        # score for each team
        self.score = dict()
        self.score[batsTop.team] = 0
        self.score[batsBot.team] = 0

        self.batsTop = batsTop
        self.batsBot = batsBot

        # map to stats by team, with last player being the current player
        self.statsBat = dict()
        self.statsBat[batsTop.team] = [[] for i in range(10)]
        self.statsBat[batsBot.team] = [[] for i in range(10)]
        print(self.statsBat[batsTop.team])
        print(self.statsBat[batsBot.team])
        self.statsField = dict()
        self.statsField[batsTop.team] = [[] for i in range(10)]
        self.statsField[batsBot.team] = [[] for i in range(10)]
        print(self.statsField[batsTop.team])
        print(self.statsField[batsBot.team])
        self.statsPitch = dict()
        self.statsPitch[batsTop.team] = []
        self.statsPitch[batsBot.team] = []
        i = 0
        for (p1, p2) in zip(batsTop.battingOrder, batsBot.battingOrder):
            #print("i=", i, " p1=", p1, " p2=", p2)
            if p1 is not None and p2 is not None:
                self.statsBat[batsTop.team][i].append((p1, BatterStats()))
                self.statsBat[batsBot.team][i].append((p2, BatterStats()))
            i += 1
        i = 0
        for (p1, p2) in zip(batsTop.fieldPos, batsBot.fieldPos):
            #print("i=", i, " p1=", p1, " p2=", p2)
            if p1 is not None and p2 is not None:
                self.statsField[batsTop.team][i].append((p1, FielderStats()))
                self.statsField[batsBot.team][i].append((p2, FielderStats()))
            i += 1
        
        startPitTop = batsTop.fieldPos[1]
        self.statsPitch[batsTop.team].append((startPitTop, PitcherStats()))
        startPitBot = batsBot.fieldPos[1]
        self.statsPitch[batsBot.team].append((startPitBot, PitcherStats()))
        print("startPitBot= ", startPitBot, " startPitTop=", startPitTop)
        self.inning = 0
        self.inningHalf = "B"
        self.cur_batter = dict()
        self.cur_batter[batsTop.team] = 1
        self.cur_batter[batsBot.team] = 1
        self.expectGameEnd = False
        self.nextHalfInning()

    def nextHalfInning(self):
        # teap batting in the top (usually vistor) took lead, and other team did not
        # tie or retake lead
        if self.inning >= 9 and self.inningHalf == "B":
            isTrailing = self.score[self.curBat.team] < self.score[self.curField.team]
            if isTrailing:
                print("end of game expected")
                self.expectGameEnd = True
        if self.inningHalf == "B":
            self.inning += 1
            self.inningHalf = "T"
        else:
            self.inningHalf = "B"
        
        self.curBat = self.batsTop
        self.curField = self.batsBot
        if self.inningHalf == "B":
            self.curBat = self.batsBot
            self.curField = self.batsTop
        self.outs = 0
        # 0=home (batter)
        self.baseRunners = [None]*4        
        isLeading = self.score[self.curBat.team] > self.score[self.curField.team]
        if self.inning == 9 and self.inningHalf == "B" and isLeading:
            self.expectGameEnd = True

    def nextBatter(self):
        batTeam = self.curBat.team
        b = (self.cur_batter[batTeam] + 1) 
        if b > 9:
            b = 1
        self.cur_batter[batTeam] = b
        #print("nextBatter: batTeam= ", batTeam, " b=", b)

    def compileGameStatsTeam(self, tm):
        batStats = BatterStats()
        fieldStats = FielderStats()
        pitchStats = PitcherStats()

        print(tm, "batting")
        batStats.printHeader()
        for o in range(1, 10):
            print(o, end=" ")
            stats = self.statsBat[tm][o]
            i = 0
            for (pID, st) in stats:
                lst = "  "
                if i > 0: # sub
                    print(lst, end="  ")
                    lst = ""
                print(playerIDMap[pID][0], end=lst)
                st.print()
                i += 1
                batStats.add(st)

        # fielding stats
        print(tm, "fielding")
        fieldStats.printHeader()
        for o in range(1, 10):
            print(o, end=" ")
            stats = self.statsField[tm][o]
            i = 0
            for (pID, st) in stats:
                lst = "  "
                if i > 0: # sub
                    print(lst, end="")
                    lst = " "
                print(playerIDMap[pID][0], end=lst)
                st.print()
                i += 1
                fieldStats.add(st)
                
        pitchStats = PitcherStats()
        print(tm, " pitching")
        pitchStats.printHeader()
        for (pID, st) in self.statsPitch[tm]:
            print(playerIDMap[pID][0], end="")
            st.print()
            pitchStats.add(st)

        return batStats, fieldStats, pitchStats

    def compileGameStats(self):
        #print(self.batsTop.battingOrderStart)
        self.teamTopBat, self.teamTopField, self.teamTopPitch = self.compileGameStatsTeam(self.batsTop.team)
        self.teamBotBat, self.teamBotField, self.teamBotPitch = self.compileGameStatsTeam(self.batsBot.team)

    def printGameStats(self):
        sBT = self.teamTopBat
        sBB = self.teamBotBat
        print("     AB  H  R  BB RBI 2B 3B HR")        
        print(f"{self.batsTop.team} {sBT.AB:3}{sBT.H:3}{sBT.R:3}{sBT.BB+sBT.IBB:3}{sBT.RBI:3}{sBT.n2B:3}{sBT.n3B:3}{sBT.HR:3}")
        print(f"{self.batsBot.team} {sBB.AB:3}{sBB.H:3}{sBB.R:3}{sBB.BB+sBB.IBB:3}{sBB.RBI:3}{sBB.n2B:3}{sBB.n3B:3}{sBB.HR:3}")

    def applyPlay(self, p):
        #print("applyPlay cur_batter=", self.cur_batter, " curBat", self.curBat.team)
        curBatterIdx = self.cur_batter[self.curBat.team]
        batterID = self.curBat.battingOrder[curBatterIdx]
        pitcherID = self.curField.fieldPos[1]  # position 1 (pitcher)
        err = False
        if self.expectGameEnd:
            print("applyPlay: ERROR end of game expected")
            err = True
        if p.team != self.curBat.team:
            print("applyPlay: ERROR unexpected team", p.team, " expected", self.curBat.team)
            err = True
        if p.inning != self.inning:
            print("applyPlay: ERROR unexpected inning", p.inning, " expected", self.inning)
            err = True
        
        #print("applyPlay batterID=", batterID, "pitcherID=", pitcherID)
        expBat = playerIDMap[batterID][0]
        pit = playerIDMap[pitcherID][0]
        curFieldTeam = self.curField.team
        curBatTeam = self.curBat.team
        batsTopTeam = self.batsTop.team
        batsBotTeam = self.batsBot.team
        scTop = self.score[batsTopTeam]
        scBot = self.score[batsBotTeam]
        print(f"applyPlay {self.inningHalf}{self.inning} {batsTopTeam} {scTop} {batsBotTeam} {scBot} {self.outs} outs ")
        print(curBatTeam, expBat, "at bat", curFieldTeam, pit, " pitching ",)
        print("onBase: ", end="")
        for b in range(1, 4):
            rn = self.baseRunners[b]
            
            print(f"{b}: ", end="")
            if rn == None:
                print(" "*8, end=" ")
            else:
                (runIdx, runID) = rn
                runner = playerIDMap[runID][0]
                print(runner, end=" ")
        print()
        print("play= ", p.play)
        if batterID != p.player_id and p.bat.result[0] != "NP":
            act = playerIDMap[p.player_id][0]
            print("applyPlay: ERROR unexpected batter", act, " expected", expBat)
            err = True
        if err: 
            exit(1)
        batterID = p.player_id
        
        # -1 = last index (current player)
        (bID, stBat) = self.statsBat[curBatTeam][curBatterIdx][-1]
        # print(self.statsPitch[curFieldTeam])
        (pID, stPit) = self.statsPitch[curFieldTeam][-1] 
        if batterID != bID:
            stBatter = playerIDMap[batterID][0]
            print("applyPlay: ERROR batter", stBatter, " does not match lineup", playerIDMap[bID])
        if pitcherID != pID:
            stPitcher = playerIDMap[pitcherID][0]
            print("applyPlay: ERROR batter", stPitcher, " does not match lineup", playerIDMap[bID])

        outs = 0
        runs = 0
        baseRunNxt = [None]*4  # 0 = home (batter), 1 = first, etc.
        
        # most plays advance to the next batter
        # if set false in the following logic, we expect batter to remain at the plate
        # or inning to end
        expectNextBat = True   
        for r, base in zip(p.bat.result, p.bat.base):
            if r in ("1", "2", "3", "4"):
                stBat.AB += 1
                stBat.H += 1
                stPit.H += 1
                if r == "1":
                    print("single")
                    baseRunNxt[1] = (curBatterIdx, batterID)
                elif r == "2":
                    print("double")
                    stBat.n2B += 1
                    stPit.n2B += 1
                    baseRunNxt[2] = (curBatterIdx, batterID)
                elif r == "3":
                    print("triple")
                    stBat.n3B += 1
                    stPit.n3B += 1
                    baseRunNxt[3] = (curBatterIdx, batterID)
                elif r == "4":
                    print("home run")
                    runs += 1
                    stBat.HR += 1
                    stBat.R += 1
                    stBat.RBI += 1
                    stPit.HR += 1
            elif r == "E":
                stBat.AB += 1
                baseRunNxt[1] = (curBatterIdx, batterID)
            elif r in ("F","G", "L", "P"): # flyout/groundout/lineout/popout
                if r == "F":
                    print(f"flyout", end="")
                elif r == "G":
                    print(f"groundout", end="")
                elif r == "L":
                    print(f"lineout", end="")
                elif r == "P":
                    print(f"popout", end="")
                try:
                    print(f" {p.hit_type}", end="")
                except:
                    pass
                try:
                    print(f" to {p.hit_loc}", end="")
                except:
                    pass
                print()
                outs += 1
                stBat.AB += 1
            elif r == "BB":
                print("walk")
                stBat.BB += 1
                stPit.BB += 1
                baseRunNxt[1] = (curBatterIdx, batterID)
            elif r == "IBB":
                print("intentional walk")
                stBat.IBB += 1
                stPit.IBB += 1
                baseRunNxt[1] = (curBatterIdx, batterID)
            elif r == "K": # strike out
                print("strikeout")
                outs += 1
                stBat.AB += 1
                stBat.K += 1
                stPit.K += 1
            elif r == "WP": # wild pitch
                print("wild pitch")
                stPit.WP += 1
                expectNextBat = False
            elif r == "FO": # force out
                print("force out")
                stBat.AB += 1
                baseRunNxt[1] = (curBatterIdx, batterID)
            elif r == "FC": # fielders choice
                print("fielders choice")
                stBat.AB += 1
                baseRunNxt[1] = (curBatterIdx, batterID)
            elif r == "PB": # passed ball
                print("passed ball")
                # position 2 = catcher
                # =1 = last index(current player), 1 = index of stats obj in tuple
                self.statsField[curFieldTeam][2][-1][1].PB += 1
                expectNextBat = False
            elif r == "HBP": # hit by pitch
                print("hit by pitch")
                baseRunNxt[1] = (curBatterIdx, batterID)
                stBat.HBP += 1
            elif r in ("SB", "CS", "PO"): # stolen base / caught stealing / pick off
                b = base
                if b == "H":
                    idx = 4
                else:
                    idx = int(b)
                rn = self.baseRunners[idx-1]
                self.baseRunners[idx-1] = None
                if r == "SB":
                    print("stolen base", b)
                    if b == "H":
                        runs += 1
                    (runIdx, runnerID) = rn
                    self.statsBat[curBatTeam][runIdx][-1][1].SB += 1
                    #self.baseRunners[idx] = (runIdx, runnerID)
                    if idx != 4:
                        baseRunNxt[idx] = (runIdx, runnerID)
                if r in ("CS", "PO"):
                    # outs should be handled by "run_out"
                    if r == "CS":
                        print("caught stealing", b)
                    else:
                        print("pickoff", b)
                    # count pickoff as caught stealing
                    self.statsBat[curBatTeam][runIdx][-1][1].CS += 1
                expectNextBat = False
            elif r == "FLE": # error on foul ball
                print("error on foul ball")
                expectNextBat = False
            elif r == "SF":
                stBat.SF += 1
                outs += 1
            elif r == "SH":
                stBat.SH += 1
                outs += 1
            elif r == "NP": # no play
                print("no play")
                expectNextBat = False
            else:
                expectNextBat = False
                print("Unkonwn play ", r)

        #p.bat.hit_type
        #p.bat.hit_field
        # =1 = last index(current player), 1 = index of stats obj in tuple
        for f in p.fielding.errors:
            self.statsField[curFieldTeam][int(f)][-1][1].E += 1
        for f in p.fielding.putouts:
            self.statsField[curFieldTeam][int(f)][-1][1].PO += 1
        for f in p.fielding.assists:
            self.statsField[curFieldTeam][int(f)][-1][1].A += 1
        #p.fielding.deflected
        # p.fielding.fielded 
        for b in p.run_out:
            print("runner on", b, "is out")
            if b not in ("B", "H"):
                baseRunNxt[int(b)] = None  # clear base runner
            outs += 1
        for mod in p.mods:
            if mod in ("BGDP", "BPDP", "DP", "FDP", "GDP", "LDP"):
                print("double play")
                outs = 2
            if mod in ("GTP", "LTP", "TP"):
                print("triple play")
                outs = 3            
        basesAdv = set()
        for adv in p.run_adv:
            src = adv[0]
            if src == "B":
                runnerID = batterID
                runIdx = curBatterIdx
            else:
                src = int(src)
                #print(src)
                # base could already have been vacated due to stolen base
                if self.baseRunners[src] == None:
                    if r == "SB":
                        (runIdx, runnerID) = baseRunNxt[int(base)]
                    else:
                        print("ERROR: Could not find runner on base", src)
                        exit(1)
                else:
                    (runIdx, runnerID) = self.baseRunners[src]
                basesAdv.add(src)
                
            dst = adv[1]
            if src == "B" and dst != "1":
                # often set before we reach this point, so we clear to avoid 
                # duplicate runners
                baseRunNxt[1] = None
            if dst == "H":
                if adv[2]:
                    runs += 1
                    print("runner on", src, " (", playerIDMap[runnerID][0], ") scored")
                    self.statsBat[curBatTeam][runIdx][-1][1].R += 1
                    stBat.RBI += 1
                else:
                    print("runner on", src, " (", playerIDMap[runnerID][0], ") out at home")
            else:
                dst = int(dst)
                if adv[2]:
                    print("runner on", src, "advanced to", dst)
                    baseRunNxt[dst] = (runIdx, runnerID)
                else: # out
                    print("runner on", src, "out at", dst)
        if len(basesAdv) > 0:
            print("basesAdv=", basesAdv)
        for b in range(1, 4):
            rn = self.baseRunners[b]
            if rn is not None and b not in basesAdv:
                baseRunNxt[b] = self.baseRunners[b]
                print("runner on", b, " does not advance")
        
        print("play runs=", runs, "outs= ", outs)
        self.baseRunners = baseRunNxt
        self.outs += outs
        self.score[self.curBat.team] += runs
        stPit.R += runs
        # credit outs to the pitcher and fielders
        if outs > 0:
            stPit.IP3 += outs
            # all fielders
            for f in range(1, 10):
                self.statsField[curFieldTeam][f][-1][1].IF3 += outs
        if expectNextBat:
            stPit.BF += 1
            self.nextBatter()
        # scored runs on this play in sudden death situation, we expect game to be over
        isLeading = self.score[self.curBat.team] > self.score[self.curField.team]
        if self.inning >= 9 and self.inningHalf == "B" and isLeading:
            self.expectGameEnd = True
        
        if self.outs >= 3:
            if self.outs > 3:
                print(f"ERROR: too many outs ({self.outs})")
                exit(1)
            print(" end of inning")
            self.nextHalfInning()

    def applySub(self, evt):
        if evt.team == self.batsTop.team:
            tm = self.batsTop
        elif evt.team == self.batsBot.team:
            tm = self.batsBot

        rep_batter, (rep_fielder, newPos) = tm.applySub(evt)
        if rep_fielder is not None:
            # destructure
            repFielderID = playerIDMap[rep_fielder]

        subID = playerIDMap[evt.player_id]
        repBatterID = playerIDMap[rep_batter]
        
        print("applySub: ", subID, " replaces ", repBatterID, " playing ", evt.field_pos, " batting", evt.bat_pos)
        if rep_fielder is not None:
            print("    ", repFielderID, " moves to ", newPos)
        if evt.bat_pos != "P":
            stBat = self.statsBat[tm.team][int(evt.bat_pos)]
            stBat.append((evt.player_id, BatterStats()))
        if evt.field_pos not in ("D", "H", "R"):
            stField = self.statsField[tm.team][int(evt.field_pos)]
            stField.append((evt.player_id, FielderStats()))
        if evt.field_pos == "1":  # pitcher
            stPitch = self.statsPitch[tm.team]
            stPitch.append((evt.player_id, PitcherStats()))
        

def parseGame(gameID, plays, conn, cur):
    stmt = "SELECT tiebreak_base, use_dh, has_pitch_cnt, has_pitch_seq, home_team_bat_first,"
    stmt += " win_pitcher, loss_pitcher, save_pitcher, gw_rbi"
    stmt += f" FROM game_info WHERE game_id={gameID}"
    cur.execute(stmt)
    tb_base, use_dh, is_cnt, is_seq, htbf, win_p, lose_p, save_p, gw_rbi = cur.fetchall()[0]
    stmt = f"SELECT home_team, visiting_team, game_date FROM boxscore WHERE game_id={gameID}"
    cur.execute(stmt)
    home_team, visiting_team, game_date = cur.fetchall()[0]
    stmt = f"SELECT * FROM event_start WHERE game_id={gameID} ORDER BY event_id"
    cur.execute(stmt)
    starts = cur.fetchall()
    stmt = f"SELECT * FROM event_sub WHERE game_id={gameID} ORDER BY event_id"
    cur.execute(stmt)
    subs = cur.fetchall()
    print("home= ", home_team, " away=", visiting_team, " date=", game_date)
    home = Lineup(home_team)
    away = Lineup(visiting_team)
    for st in starts:
        #print("st=", st)
        # destructure
        game_id, event_id, player_id, team, bat_pos, field_pos = st
        
        if team == home_team:
            lineup = home
        elif team == visiting_team:
            lineup = away
        else:
            print(f"parseGame ERROR: team=", team, " is neither home=", home_team, " or away=", visiting_team)
            return -1
        pID = playerIDMap[player_id][0] 

        #print(pID, team, " starting at ", field_pos, " batting order ", bat_pos)
        if bat_pos != "P":
            bat_pos = int(bat_pos)
            lineup.battingOrder[bat_pos] = player_id
            lineup.battingOrderStart[bat_pos] = player_id
        if field_pos != "D":
            field_pos = int(field_pos)
            lineup.fieldPos[field_pos] = player_id
        if field_pos == 1:
            lineup.pitchersUsed.append(player_id)
    # print lineups for home/away
    away.print()
    home.print()
    
    print(f"htbf={htbf}")
    batsTop = away
    batsBot = home
    if htbf:
        batsTop = home
        batsBot = away
    game = GameState(batsTop, batsBot)
    events = []
    for p in plays:
        events.append(PlayEvent(p))
    for s in subs:
        events.append(SubEvent(s))

    # sort based on event ID
    events = sorted(events, key=lambda x: x.event_id)

    for evt in events:
        if type(evt) == type(PlayEvent()):
            game.applyPlay(evt)
        elif type(evt) == type(SubEvent()):
            game.applySub(evt)
    game.compileGameStats()
    game.printGameStats()

def parseEventOutcomesGatherStats(conn, cur, gameRange=None):
    whereClause = ""
    if gameRange is not None:
        print("gameRange= ", gameRange)
        whereClause = f"WHERE game_id >= {gameRange[0]} AND game_id <= {gameRange[1]}"
    stmt = f"SELECT * FROM event_play {whereClause} ORDER BY game_id, event_id"
    cur.execute(stmt)
    tups = cur.fetchall()
    print("len(tups)= ", len(tups))
    plays = []
    gameID = None
    for tup in tups:
        if tup[0] != gameID:  # new game
            if gameID != None:
                parseGame(gameID, plays, conn, cur)
            gameID = tup[0]
            plays = []
        plays.append(tup)

    print("Could not parse the following play segments:")
    for p in batPlaysNoParse:
        print(p)

if __name__ == "__main__":
    connectPG = False
    connectSqlite = True
    useDB = connectPG or connectSqlite
    
    gameRange = None
    if len(sys.argv) > 2:
        gameRange = (int(sys.argv[1]), int(sys.argv[2]))

    if connectSqlite:
        import sqlite3
        conn = sqlite3.connect("baseball.db")
        cur = conn.cursor()

    if connectPG:
        import psycopg
        # Connect to an existing database
        conn = psycopg.connect("dbname=postgres user=postgres")
        cur = conn.cursor()
    
    stmt = f"SELECT player_num_id, player_id, name_last, name_other FROM player"
    cur.execute(stmt)
    tups = cur.fetchall()
    for tup in tups:
        playerIDMap[tup[0]] = (tup[1], tup[2], tup[3])

    parseEventOutcomesGatherStats(conn, cur, gameRange)
    conn.commit()
    conn.close()