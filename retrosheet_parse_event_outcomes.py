#!/usr/bin/python3

import sys
import re
import traceback
import time
from random import randint
from copy import deepcopy

# global
playerCodeToIDMap = dict()
playerIDToCodeMap = dict()
#playerIDMap = dict()

SKIP_GAMES = ("1938-05-14SLNCIN0", # this game was protested and replayed later
)

class BatResult:
    def __init__(self, results=[], bases=[], hit_type=None, hit_loc=None, mods=[]):
        self.results = list(results)
        # base paramters for each result
        self.bases = list(bases)
        # G=ground ball, F=fly ball L=line drive, P=pop up
        self.hit_type = hit_type
        # roughly where in the field ball was hit, 
        self.hit_loc = hit_loc
        self.mods = list(mods)

class FieldingResult:
    def __init__(self, errors=[], putouts=[], assists=[], fielded=[]):
        self.errors = list(errors)
        self.putouts = list(putouts)
        self.assists = list(assists)
        self.fielded = list(fielded)

class RunResult:
    def __init__(self, out=[], adv=[], mods=[]):            
        self.out = list(out)
        self.adv = list(adv)
        self.mods = list(mods)

# the interpretation of results of these plays is ambiguous 
# amd would be difficul to resolve with general rules
# therefore the results are entered in manually
AMBIGUOUS_PLAYS = dict() 
# game date, home team, away team, double header num (0, 1, 2)
# innning, inning half, batter code, play count with batter
br = BatResult(("O",), bases=(None,), hit_type="G", hit_loc="4")
fr = FieldingResult(errors=[6], assists=(4,), putouts=(3,))
rr = RunResult(adv=[(1, 2, True)], out=((0, False, 1),))

#S9.2-H(UR);BXH(E9)(932)
br2 = BatResult(("S",), bases=(None,), hit_loc="9")
fr2 = FieldingResult(errors=(9,), assists=(9, 3), putouts=[2,])
rr2 = RunResult(adv=((2, 4, True), (0, 4, False)))
AMBIGUOUS_PLAYS["1922-05-10NYACHA0"] = { (11, "T", "strua102", 0) : (br, fr, rr),  
                                         (11, "T", "hooph101", 0) : (br2, fr2, rr2)}

# setting to True will print debugging output for all games
# if false, only games which fail to parse
DEBUG = False
DEBUG_OUT = []

def DEBUG_PRINT(*args,end="\n"):
    if DEBUG:        
        print(*args, end=end)
    else:
        DEBUG_OUT.append((args, end))

def PRINT_DEBUG_OUT():
    for l in DEBUG_OUT:
        for s in l[0]:
            print(s, end=" ")
        print(end=l[1])

def valOrNULL(v):
    if v == None:
        return "NULL"
    # wrap in single quotes
    if type(v) == type(""):
        return "'" + v + "'"
    elif type(v) == type(True):
        if v:
            return "0"
        return "1"
    return v

def baseToNum(b):
    if b == 'B':
        return 0
    elif b == 'H':
        return 4
    return int(b)

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

FIELD_POS_NUM = range(1, 10)

# adopted from Chadwick baseball data
locations = {"1":0, "13":1, "15":2, "1S":3, "2":4, "2F":5, "23":6, 
             "23F":7, "25":8, "25F":9, "3SF":10, "3F":11, "3DF":12,
             "3S":13, "3":14, "3D":15, "34S":16, "34":17, "34D":18,
             "4S":19, "4":20, "4D":21, "4MS":22, "4M":22, "4MD":23,
             "6MS":24, "6M":25, "6MD":26, "6S":27, "6":28, "6D":29,
             "56S":30, "56":31, "56D":32, "5S":33, "5":34, "5D":35,
             "5SF":36, "5F":37, "5DF":38, "7LSF":39, "7LS":40, "7S":41,
             "78S":42, "8S":43, "89S":44, "9S":45, "9LS":46, "9LSF":47,
             "7LF":48, "7L":49, "7":50, "78":51, "8":52, "89":53, "9":54,
             "9L":55, "9LF":56, "7LDF":57, "7LD":58, "7D":59, "78D":60,
             "8D":61, "89D":62, "9D":63, "9LD":64, "9LDF":65, "78XD":66,
             "8XD":67, "89XD":68 }

# "the following locations are nonstandard or archaic,
# but appear in existing Retrosheet data  ""
# adopted from Chadwick baseball data
# remap to canonical locations
# TODO mapping locations need to be improved
odd_locations= { # pitchers mound area
                "13S":"13", "15S":"15", 
                # catcher
                "2LF":"LF", "2RF":"RF", 
                "2L":"2", "2R":"2", 
                # first base
                "3L":"3", 
                # second base
                "46":"4",
                # third base
                "5L":"5", 
                # left field
                "7LDW":"7", "7DW":"7", "78XDW":"7", 
                "7LMF":"7", "7LM":"7", "7M":"7", "78M":"7",
                # center field
                "8XDW":"8", "89XDW":"8", 
                "8LS":"8", "8RS":"8", "8LD":"8", "8RD":"8",
                "8LXD":"8", "8RXD":"8", "8LXDW":"8", "8RXDW":"8",
                "8LM":"8", "8M":"8", "8RM":"8", "89M":"8",
                # right field
                "9DW":"9", "9LDW":"9",
                "9M":"9", "9LM":"9", "9LMF":"9" }

# playCodeNumMap = {"S":0, "D":1, "CI":2, "DGR":3, "T":4, "HR":5, 
#                   "WP":6, "BB":7, "FC":8, "PB":9, "E":10, "O":11,
#                   "HBP":12, "IBB":13, "K":14, "SB":15, "CS":16, "BK":17,
#                   "PO":18, "POCS":19, "POE":20, "OA":21, "DI":22, "NP":23,
#                    "FLE":24, "FO":25}

playCodeMap = {"S": "single", "D":"double", "CI":"catcher interference", 
               "DGR":"ground rule double", "T":"triple", "HR":"home run", 
               "WP":"wild pitch", "BB":"walk", "FC":"fielders choice", "PB":"pass ball",
               "E":"error", "O":"out", "HBP":"hit by pitch", "IBB":"intentional walk",
               "K":"strikeout", "SB":"stolen base", "CS":"caught stealing", "BK":"balk",
               "PO":"pick off", "POCS":"pickoff caught stealing", "POE":"pick off error", "OA":"other advance",
               "DI":"defensive indifference", "NP":"(no play)", }

# retro sheet to play code for certain lays
RStoPlayCodeMap = {"W": "BB", "I":"IBB", "IW":"IBB", "HP":"HBP", "WP":"WP", 
                   "PB":"PB", "K":"K", "DI":"DI", "OA":"OA", "NP":"NP", "BK":"BK",
                   "C":"CI", "DGR":"DGR"}

HIT_TYPES = {None:0, "G":1,"L":2, "F":3, "P":4}
for p in list(RStoPlayCodeMap.keys()):
    RStoPlayCodeMap[p + "!"] = RStoPlayCodeMap[p]
    RStoPlayCodeMap[p + "#"] = RStoPlayCodeMap[p]
    RStoPlayCodeMap[p + "?"] = RStoPlayCodeMap[p]
    RStoPlayCodeMap[p + "+"] = RStoPlayCodeMap[p]
    RStoPlayCodeMap[p + "-"] = RStoPlayCodeMap[p]
                   
for m in list(playCodeMap.keys()):
    playCodeMap[m + "!"] = playCodeMap[m]
    playCodeMap[m + "#"] = playCodeMap[m]
    playCodeMap[m + "?"] = playCodeMap[m]
    playCodeMap[m + "+"] = playCodeMap[m]
    playCodeMap[m + "-"] = playCodeMap[m]

modCodeMap = {"AP": "appeal play",
"BP": "pop up bunt",
"BF": "bunt foul",
"BG": "ground ball bunt",
"BGDP": "bunt grounded into double play",
"BINT": "batter interference",
"BL": "line drive bunt",
"BOOT": "batting out of turn",
"BPDP": "bunt popped into double play",
"BR": "runner hit by batted ball",
"C": "called third strike",
"COUB": "courtesy batter",
"COUF": "courtesy fielder",
"COUR": "courtesy runner",
"DP": "unspecified double play",
"DGR": "ground rule double",
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

# modCodeNumMap = {"H":0, "B":0, "1":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7,
#                  "8":8, "9":9, "AP": 10, "BP": 11, "BF": 12, 
#                  "BG": 13, "BGDP": 14,
#     "BINT": 15, "BL": 16, "BOOT": 17, "BPDP": 18, "BR": 19, "C": 20, 
#     "COUB": 21, "COUF": 22, "COUR": 23, "DP": 24, "DGR": 25, 
#     "E": 26, "F": 27, "FDP": 28, "FINT": 29, "FL": 30, "FO": 31, 
#     "G": 32, "GDP": 33, "GTP": 34, "IF": 35, "INT": 36, "IPHR": 37,
#     "L": 38, "LDP": 39, "LTP": 40, "MREV": 41, "NDP": 42, "OBS": 43,
#     "P": 44, "PASS": 45, "R$": 46, "RINT": 47, "SF": 48, "SH": 49,
#     "TH": 50, "TP": 51, "UINT": 52, "UREV": 53, "T":54 }

# for m in list(modCodeNumMap.keys()):
#     modCodeNumMap[m + "!"] = modCodeNumMap[m]
#     modCodeNumMap[m + "#"] = modCodeNumMap[m]
#     modCodeNumMap[m + "?"] = modCodeNumMap[m]
#     modCodeNumMap[m + "+"] = modCodeNumMap[m]
#     modCodeNumMap[m + "-"] = modCodeNumMap[m]

for m in list(modCodeMap.keys()):
    modCodeMap[m + "!"] = modCodeMap[m]
    modCodeMap[m + "#"] = modCodeMap[m]
    modCodeMap[m + "?"] = modCodeMap[m]
    modCodeMap[m + "+"] = modCodeMap[m]
    modCodeMap[m + "-"] = modCodeMap[m]

batPlaysNoParse = []
runPlaysNoParse = []

sqlStmts = []

def baseNumForPOCS(b, play):
    if b is None:
        return None
    if b in ("1", "2", "3"):
        b = int(b)                
    else:
        b = 4
    if play in ("CS", "POCS"):
        b = b-1
    return b

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

    def getFielderPOA(self, play):
        r_m = re.fullmatch(r"(\d*)(\d).*", play)
        if r_m is not None:
            fldrs = set(r_m.group(1))
            for f in fldrs:
                self.fielding.assists.append(int(f))
            self.fielding.putouts.append(int(r_m.group(2)))
    
    def parseRunnerMods(self, modsParens):
        runMods = []
        if modsParens == "": 
            #self.run.mods.append(())
            return []
        # break up parentheses
        idx = 0
        mods_m = re.match(r"(\([^()]*\))", modsParens)
        # all modifications for this advance 
        
        while mods_m is not None and modsParens != "":
            mods = mods_m.group(1)
            # remove enclosing parentheses
            mods=mods[1:-1]
            DEBUG_PRINT(f"parseRunnerMods: mods={mods}")
            runSubMod = []
            for mod in mods.split("/"):
                DEBUG_PRINT(mod)
                if mod in modCodeMap:
                    runSubMod.append(mod)
                    continue
                # runner thrown out, possibly due to rundown
                m = re.fullmatch(r"\((\d+)\)", mod)
                if m is not None:
                    grps = m.groups()
                    self.getFielderPOA(grps[2])
                    DEBUG_PRINT("runner out")
                    runSubMod.append("O")
                    continue
                m = re.fullmatch(r"TH([123H])", mod)
                if m is not None:
                    runSubMod.append(("TH", m.group(1)))
                    DEBUG_PRINT("throw to base", m.group(1))
                    continue
                m = re.fullmatch(r"R([123H])", mod)
                if m is not None:
                    runSubMod.append(("R", m.group(1)))
                    DEBUG_PRINT("relay throw to base", m.group(1))
                    continue
                # error (fielding or catch)
                m = re.fullmatch(r"(\d*)E(\d)", mod)
                if m is not None:
                    grps = m.groups()
                    if grps[0] is not None:
                        DEBUG_PRINT("error - catch")
                        fldrs = set(grps[0])
                        for f in fldrs:
                            self.fielding.fielded.append(int(f))
                    else:
                        DEBUG_PRINT("fielding error")
                    self.fielding.errors.append(int(grps[1]))
                    runSubMod.append(("E", int(grps[1])))
                    continue
            DEBUG_PRINT(runSubMod)
            runMods.append(runSubMod)
            
            idx = mods_m.end()
            modsParens = modsParens[idx:]
            mods_m = re.match(r"(\([^()]*\))", modsParens)
        self.run.mods.append(runMods)
        return runMods        

    def parseRunnerAdv(self, run_all):
        self.run.adv = []
        self.run.mods = []
        if len(run_all) == 0:
            return False
        run_adv = run_all.split(";")
        DEBUG_PRINT("parseRunnerAdv: run_adv=", run_adv)
        
        for adv in run_adv:      
            idx = adv.find("(")
            a0 = adv
            mods = ""
            if idx != -1:
                a0 = adv[:idx]
                mods = adv[idx:]            
            if "-" in a0: # safe
                a = a0.split("-")
                isSafe = True
            elif "X" in a0:  # out
                a = a0.split("X")
                isSafe = False
            else:
                DEBUG_PRINT("no valid separator found")
                return True
            if len(a) != 2:
                DEBUG_PRINT("len(a) != 2")
                return True
            srcBase = a[0]
            dstBase = a[1][0]
            
            if len(mods) > 0 and mods[0] in ("#", "?", "!"):
                mods = a[1][2:]
            runMods = self.parseRunnerMods(mods)
            if srcBase not in ("B","1","2","3"):
                DEBUG_PRINT("bad srcBase=", srcBase)
                return True
            if dstBase not in ("H","1","2","3"):
                DEBUG_PRINT("bad dstBase=", dstBase)
                return True
            
            possiblySafeDueToError = False
            if not isSafe:
                # if there was error on this play, runner might be safe
                # despite being marked out on the score sheet
                # for example see game id = PIT191205310, top of the 3rd inning
                # or  PIT/NY1  date= 191208232 top of the 2nd inning
                # OTOH, they could also be out - see CHA @ BOS19120827 Top of the 6th
                # handle speculation in parseGame/applyPlay, if inning ends before or after
                # expected, use the other interpretation
                DEBUG_PRINT("parseRunAdv: runMods=", runMods)
                possiblySafeDueToError = False
                for mods in runMods:
                    for subMod in mods:
                        if type(subMod) == type(tuple()):
                            if subMod[0] == "E":
                                DEBUG_PRINT("runner marked as out may be safe due to error")
                                possiblySafeDueToError = True
                                break
                    if possiblySafeDueToError:
                        break                
            # use E designation as opposed to True/False
            if possiblySafeDueToError:
                isSafe = "E"
            t = (srcBase, dstBase, isSafe)
            DEBUG_PRINT("parseRunAdv: appending ", t)
            self.run.adv.append(t)
        return False
            

    def parseBat(self, bat_all):
        # parse a single play
        def parseFirst(bat0):
            # 99 generic out, unknown fielder
            if bat0 == "99":
                DEBUG_PRINT("generic fielding out (99)")
                return False, "O", None, len(bat0)
            # walks, etc. 
            if bat0 in RStoPlayCodeMap.keys():
                result = RStoPlayCodeMap[bat0]
                DEBUG_PRINT("mapped to code", playCodeMap[result])
                return False, result, None, len(bat0)
            # stolen base
            m = re.match(r"^SB([123H])[#!?]?", bat0)  
            if m is not None:
                DEBUG_PRINT("stolen base")
                return False, "SB", m.group(1), m.end()
            # caught stealing / pickoff 
            m = re.match(r"^(CS|POCS|PO)([123H])\((.*)\)?[#!?]?", bat0)  
            if m is not None:
                DEBUG_PRINT("caught stealing/pickoff")
                grps = m.groups()
                DEBUG_PRINT(m.group(1), grps)
                result = grps[0]
                base = grps[1]
                
                m_end = m.end()
                isError = False
                if grps[2] is not None:
                    DEBUG_PRINT("CS/POCS/PO grps[2]=", grps[2])
                    # error on play
                    e_m = re.fullmatch(r"(.*)E(\d).*", grps[2])
                    if e_m is not None:
                        self.fielding.errors.append(int(e_m.group(2)))
                        isError = True

                    self.getFielderPOA(grps[2])
                b = baseNumForPOCS(base, result)
                self.run.out.append((b, isError, base))
                return False, result, base, m_end
            # base hit/single/double/triple S,D,or T followed by single digit (optional)
            m = re.match(r"^([SDT])(.*)?[#!?+-]?", bat0)
            if m is not None:
                DEBUG_PRINT("hit")  
                if m.group(2) is not None:
                    self.bat.hit_loc = m.group(2)
                return False, m.group(1), None, m.end()
            # home run (possibly inside the park)
            m = re.match(r"^HR?(.*)?[#!?+-]?", bat0)
            if m is not None:
                DEBUG_PRINT("home run")
                if m.group(1) is not None:
                    self.bat.hit_loc = m.group(1)
                return False, "HR", None, m.end()
            # error (fielding or catch)
            m = re.match(r"^(\d*)[#!?]?E(\d)[#!?+-]?", bat0)
            if m is not None:
                grps = m.groups()
                if grps[0] is not None:
                    DEBUG_PRINT("error - catch")
                    for f in grps[0]:
                        if f.isnumeric():
                            self.fielding.fielded.append(int(f))
                else:
                    DEBUG_PRINT("fielding error")
                self.fielding.errors.append(int(grps[1]))
                return False, "E", None, m.end()
            
            # more complciated play need to come first
            # since we are not doing fullmatch and less complicated plays woule
            # match this pattern

            # triple play, batter out first  may be due to caught ball
            m = re.match(r"^(\d).?\(B\)(.*)\(([123])\)(.*)\(([123])\)(\d.)?", bat0)
            if m is not None:
                DEBUG_PRINT("triple play")
                grps = m.groups()
                self.run.out.append((int(grps[2]), False, int(grps[2])+1))
                self.run.out.append((int(grps[4]), False, int(grps[4])+1))
                for f in grps[0]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.putouts.append(flast)
                for f in grps[1]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.putouts.append(flast)
                flast = int(grps[4][0])
                self.fielding.putouts.append(flast) 
                return False, "O", None, m.end()
            
            # triple play - ground ball, forceout, explicity or implied runner out at first
            m = re.match(r"^(\d.*)\(([123])\)(\d.*)\(([123])\)(\d.?)(\(B\))?", bat0)
            if m is not None:
                DEBUG_PRINT("triple play")
                grps = m.groups()
                self.run.out.append((int(grps[1]), False, int(grps[1])+1))
                self.run.out.append((int(grps[3]), False, int(grps[3])+1))
                for f in grps[0]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.putouts.append(flast)
                for f in grps[2]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.putouts.append(flast)
                flast = int(grps[4][0])
                self.fielding.putouts.append(flast)                    
                
                return False, "O", None, m.end()
            
            # triple play - ground ball 
            m = re.match(r"^(\d.*)\(([123B])\)(\d.*)\(([123B])\)(\d.*)\(([123B])\)", bat0)
            if m is not None:
                DEBUG_PRINT("triple play")
                grps = m.groups()
                b1 = baseToNum(grps[1])
                b2 = baseToNum(grps[3])
                b3 = baseToNum(grps[5])
                if b1 != 0:
                    self.run.out.append((b1, False, b1+1))
                if b2 != 0:
                    self.run.out.append((b2, False, b2+1))
                if b3 != 0:
                    self.run.out.append((b3, False, b3+1))
                for f in grps[0]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.putouts.append(flast)
                for f in grps[2]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.putouts.append(flast)
                for f in grps[4]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.putouts.append(flast)                    
                
                return False, "O", None, m.end()
            
            # double play, either ball caught, runner tagged out
            # or force at first followed by tag of other runner 
            m = re.match(r"^(\d.*)\(B\)(\d.*)\(([123])\)", bat0)
            if m is not None:
                DEBUG_PRINT("double play")
                grps = m.groups()
                self.run.out.append((int(grps[2]), False, int(grps[2])+1))
                for f in grps[0]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.putouts.append(flast)
                for f in grps[1]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.assists.pop()
                self.fielding.putouts.append(flast)
                return False, "O", None, m.end()
            
            # double play to bags other than first 
            m = re.match(r"^(\d.*)\(([123])\)[!]?(\d.*)\(([123])\)", bat0)
            if m is not None:
                DEBUG_PRINT("double play (bags other than first)")
                grps = m.groups()
                self.run.out.append((int(grps[1]), False, int(grps[1])+1))
                self.run.out.append((int(grps[3]), False, int(grps[3])+1))
                for f in grps[0]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.putouts.append(flast)
                for f in grps[2]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.putouts.append(flast)
                return False, "FO", None, m.end()
            
            # double play - implied or explicit runner out at first
            m = re.match(r"^(\d.*)\(([123])\)[!]?(\d.*)(\(B\))?", bat0)
            if m is not None:
                DEBUG_PRINT("double play - runner out at first")
                grps = m.groups()
                self.run.out.append((int(grps[1]), False, int(grps[1])+1))
                for f in grps[0]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.putouts.append(flast)
                for f in grps[2]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.assists.pop()
                self.fielding.putouts.append(flast)

                return False, "O", None, m.end()
            
            
            
            # force out (single out) to bag other than first 
            m = re.match(r"^(\d.*)\(([123])\)", bat0)
            if m is not None:
                DEBUG_PRINT("force out")
                grps = m.groups()
                self.run.out.append((int(grps[1]), False, int(grps[1])+1))
                for f in grps[0]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.putouts.append(flast)
                return False, "FO", None, m.end()
            
            # generic fielding out (batter)
            m = re.match(r"^(\d.*)", bat0)
            if m is not None:
                DEBUG_PRINT("generic out")
                grps = m.groups()
                for f in grps[0]:
                    if f.isnumeric():
                        flast = int(f)
                        self.fielding.assists.append(flast)
                self.fielding.assists.pop()
                self.fielding.putouts.append(flast)
                return False, "O", None, m.end()
            
            # fielders choice / defensive indifference / other advance
            m = re.match(r"^(FC|DI|OA)(\d)?[#!?+-]?", bat0)  
            if m is not None:
                DEBUG_PRINT("fielders choice/DI/OA")
                return False, m.group(1), m.group(2), m.end()
  
            # fielding error on foul ball
            m = re.fullmatch(r"^FLE(\d)[#!?+-]?", bat0)
            if m is not None:
                DEBUG_PRINT("fielding error on foul ball")
                self.fielding.errors.append(int(m.group(1)))
                return False, "FLE", None, m.end()
            # strikeout, potentially with dropped third strike 
            # and plays by other fielders
            m = re.match(r"^K(\d.*)[!#?]?", bat0)
            if m is not None:
                DEBUG_PRINT("strikeout")
                return False, "K", None, m.end()
            DEBUG_PRINT("cannot parse ", bat0)
            return True, None, None, None
        # end parseFirst()

        def parseBatMod(mod, mods):
            if mod in locations:
                self.bat.hit_loc = mod
                return False
            elif mod in odd_locations:
                # map to canonical
                self.bat.hit_loc = odd_locations[mod]
                return False
            elif mod in modCodeMap:
                mods.append(mod)
                return False
            m = re.match(r"([GLFP])(.*)?[#!?+-]?", mod)
            if m is not None:
                self.bat.hit_type = m.group(1)
                self.bat.hit_loc = m.group(2)
                DEBUG_PRINT("hit_type", self.bat.hit_type, "hit_loc", self.bat.hit_loc)
                return False
            m = re.match(r"TH([123H])[#!?]?", mod)
            if m is not None:
                b = m.group(1)
                DEBUG_PRINT("throw to base", b)
                mods.append(("TH", b))
                return False
            m = re.match(r"R([123H])", mod)
            if m is not None:
                b = m.group(1)
                DEBUG_PRINT("relay throw to base", b)
                mods.append(("R", b))
                return False
            # error (catch or field)
            m = re.match(r"(\d)?E(\d)", mod)
            if m is not None:
                grps = m.groups()
                if grps[0] is not None:
                    self.fielding.fielded.append(int(m.group(1)))
                self.fielding.errors.append(int(m.group(2)))
                mods.append(("E", int(m.group(2))))
                return False
            DEBUG_PRINT("cannot parse batter mod", mod)
            return True
        # end parseBatMod

        #pID = playerIDMap[self.player_id][0]
        pID = self.player_id
        DEBUG_PRINT("parseBat ", self.inning, self.team, pID, " bat_all=", bat_all)
        # can be multiple plays within single line (e.g. double steals)
        # so we split them up 
        # NOTE we cannot further split into "combo plays" such as K+SB 
        # because '+' can also be used to denote "hard hit ball"
        plays = bat_all.split(";")
        for p in plays:
            p1 = p.split("/")
            p1_0 = p1[0]
            DEBUG_PRINT("parseBat: p1_0=", p1_0)
            p1_1 = p1[1:]
            DEBUG_PRINT("parseBat: p1_1=", p1_1)
            
            # detect combo play
            m = re.match(r"^(K|K\d*|W|IW|I)\+", p1_0)
            if m is not None:
                err, result, base, lastIdx = parseFirst(m.group(1))
                if err:
                    return True
                self.bat.results.append(result)
                self.bat.bases.append(base)
                self.bat.mods.append([])
                p1_0 = p1_0[m.end():]
            err, result, base, lastIdx = parseFirst(p1_0)
            rest = p1_0[lastIdx:]
            if len(rest) > 0:
                print("parseFirst: unparsed=", rest, "p1_0=", p1_0)
            if err:
                return True
            self.bat.results.append(result)
            self.bat.bases.append(base)
           
            # modifiers
            mods = []
            # there may be fragment(s) left after the "/" split
            # e.g., 'PO1(E2/TH)' will have fragment 'TH)'
            if rest != "":
                if rest[0] == "(":
                    rest = rest[1:]
                if rest[-1] == ")":
                    rest = rest[::-1]
                parseBatMod(rest, mods)
            for m in p1_1:
                parseBatMod(m, mods)
            self.bat.mods.append(mods)
        return False

    def parsePlay(self):
        # split up bat and base run
        run_all = ""
        s = self.play.split(".")
        bat_all = s[0]
        if len(s) > 1:
            run_all = s[1]
        if len(s) > 2:
            DEBUG_PRINT("parsePlay: unexpected input (more than one '.') play=", self.play)
            return True
        err = self.parseBat(bat_all)
        if err:
            return True
        err = self.parseRunnerAdv(run_all)       
        if err:
            return True
        return False
        
                
    def __init__(self, p=None):
        if p is not None:
            # destructure
            self.game_id, self.event_id, self.team_id, self.player_id = p[0:4]
            self.inning, self.batter_count, self.pitch_seq, self.play = p[4:]
            self.team = self.team_id
            self.player_id = playerIDToCodeMap[self.player_id]
            #print("team=", self.team)
            self.pitchSeq = None
            self.bat = BatResult() 
            self.fielding = FieldingResult()
            self.run = RunResult()
            
            
class SubEvent(Event):
    def __init__(self, s=None):
        if s is not None:
            self.game_id, self.event_id, self.player_id = s[0:3]
            self.team_id, self.bat_pos, self.field_pos = s[3:]
            self.player_id = playerIDToCodeMap[self.player_id]
            self.bat_pos = int(self.bat_pos)
            self.field_pos = int(self.field_pos)
            self.team = self.team_id

class PlayerAdjEvent(Event):
    def __init__(self, p=None):
        if p is not None:
            # destructure
            self.game_id, self.event_id, self.player_id = p[0:3]
            self.adjType, self.adj = p[3:]
            self.player_id = playerIDToCodeMap[self.player_id]

    def print(self):
        DEBUG_PRINT(f"**** Player adjustment: {self.player_id}  {self.adjType} {self.adj}")

class LineupAdjEvent(Event):
    def __init__(self, l=None):
        if l is not None:
            # destructure            
            self.game_id, self.event_id, self.team = l[0:3]
            self.adj = int(l[3])
    def print(self):
        DEBUG_PRINT(f"***** Lineup adjustment: {self.team} {self.adj}")

class DataEREvent(Event):
    def __init__(self, d=None):
        if d is not None:
            # destructure
            self.game_id, self.event_id, self.player_id = d[0:3]
            self.er = int(d[3])
            self.player_id = playerIDToCodeMap[self.player_id]
    
    def print(self):
        DEBUG_PRINT(f"ER: {self.player_id} {self.er}")

class ComEvent(Event):
    def __init__(self, d=None):
        if d is not None:
            self.game_id, self.event_id, self.com = d[0:3]
            self.event_id = int(self.event_id)

class Lineup:
    def __init__(self, team_id):
        self.team_id = team_id
        self.team = team_id
        # map between order in batting (1..9)
        # order 0 has no meaning, or could be interpted as the P when using a DH
        self.battingOrder = [None]*10
        # map between field position, with 1=pitcher 2=catcher, 3=1B etc.
        # 0 position has no meaning, or could be the DH
        self.fieldPos = [None]*10
        self.battingOrderStart = [None]*10
        self.battingOrderSubs = [[] for i in range(10)]
        self.pitchersUsed = []
    
    def print(self):
        DEBUG_PRINT(self.team, "lineup")
        for b in range(1, 10):
            p = self.battingOrder[b]
            #pID = playerIDMap[p]
            pID = p
            fldPos = None
            for f in range(1, 10):
                if p == self.fieldPos[f]:
                    fldPos = f
                    break
            DEBUG_PRINT(b, pID, "playing", fldPos)
        DEBUG_PRINT("Pitching", self.fieldPos[1])

    
    def applySub(self, sub):
        rep_batter = None
        rep_fielder = None
        newPos = None
        DEBUG_PRINT("applySub: sub=", sub.player_id,  "bat_pos=", sub.bat_pos, " field_pos=", sub.field_pos )
        if sub.field_pos == 1:
            self.pitchersUsed.append(sub.player_id)
        if sub.bat_pos != 0:
            idx = sub.bat_pos
            rep_batter = self.battingOrder[idx]
            if rep_batter != sub.player_id:         
                DEBUG_PRINT("applySub: appending to batting order at ", idx)
                self.battingOrder[idx] = sub.player_id
                self.battingOrderSubs[idx].append(sub.player_id)
            else:
                DEBUG_PRINT("applySub: rep_batter=", rep_batter, " replacing self in order (field position change")
        if sub.field_pos in FIELD_POS_NUM:
            idx = int(sub.field_pos)
            rep_fielder = self.fieldPos[idx]
            if rep_batter is not None and self.fieldPos[idx] != rep_batter:
                DEBUG_PRINT("WARNING: player is replacing different fielder.")
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

    def insertIntoDB(self, cur, game_id, player_id, team_id, pos, seq):
        pid = playerCodeToIDMap[player_id]
        stmt = f"INSERT INTO player_game_fielding VALUES ({game_id}, {pid}"
        stmt += f", '{team_id}', {pos}, {seq}, {self.IF3}, {self.PO}, {self.A}, {self.E}"
        stmt += f", {self.DP}, {self.TP}, {self.PB})"
        DEBUG_PRINT(stmt)
        cur.execute(stmt)

    def printHeader(self):
        DEBUG_PRINT(" "*14, "IF3 PO A  E  DP TP PB")

    def print(self):
        DEBUG_PRINT(f"{self.IF3:4}{self.PO:3}{self.A:3}{self.E:3}{self.E:3}{self.DP:3}{self.TP:3}{self.PB:3}")

class PitcherStats:
    def __init__(self):
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
        DEBUG_PRINT(" "*10, "IP3 BF H  K  R ER BB 2B 3B HR")

    def print(self):
        DEBUG_PRINT(f"{self.IP3:4}{self.BF:3}{self.H:3}{self.K:3}{self.R:3}{self.ER:3}{self.BB+self.IBB:3}{self.n2B:3}{self.n3B:3}{self.HR:3}")

    def insertIntoDB(self, cur, game_id, player_id, team_id, seq):
        pid = playerCodeToIDMap[player_id]
        stmt = f"INSERT INTO player_game_pitching VALUES ({game_id}, {pid}"
        stmt += f", '{team_id}', {seq}, {self.IP3}, {self.NOOUT}, {self.BF}, {self.H}"
        stmt += f", {self.n2B}, {self.n3B}, {self.HR}, {self.R}, {self.ER}, {self.BB}"
        stmt += f", {self.IBB}, {self.K}, {self.HBP}, {self.WP}, {self.BK}, {self.SH}"
        stmt += f", {self.SF})"
        DEBUG_PRINT(stmt)
        cur.execute(stmt)

class BatterStats:
    def __init__(self):
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
        DEBUG_PRINT(" "*14, "AB  H  K  R BB 2B 3B HR SB CS")

    def print(self):
        DEBUG_PRINT(f"{self.AB:3}{self.H:3}{self.K:3}{self.R:3}{self.BB+self.IBB:3}{self.n2B:3}{self.n3B:3}{self.HR:3}{self.SB:3}{self.CS:3}")

    def insertIntoDB(self, cur, game_id, player_id, team_id, pos, seq):
        pid = playerCodeToIDMap[player_id]
        stmt = f"INSERT INTO player_game_batting VALUES ({game_id}, {pid}"
        stmt += f", '{team_id}', {pos}, {seq}, {self.AB}, {self.R}, {self.H}"
        stmt += f", {self.n2B}, {self.n3B}, {self.HR}, {self.RBI}, {self.SH}, {self.SF}"
        stmt += f", {self.HBP}, {self.BB}, {self.IBB}, {self.K}, {self.SB}, {self.CS}"
        stmt += f", {self.GIDP}, {self.INTF})"
        DEBUG_PRINT(stmt)
        cur.execute(stmt)

TEAM_STAT_LIST = ("AB", "H", "n2B", "n3B", "HR", "RBI", "SH", "SF", "HBP")
TEAM_STAT_LIST += ("BB", "IBB", "K", "SB", "CS", "GIDP", "CI", "LOB", "PI")
TEAM_STAT_LIST += ("ERI", "ERT", "WP", "BK", "PO", "A", "E", "PB", "DP", "TP")

class TeamStats:
    def __init__(self):
        for st in TEAM_STAT_LIST:
            setattr(self, st, 0)
        self.runs = 0
        self.runs_inning = [None]*10

    def loadfromDB(self, hOrV, gameID, cur):
        stmt = f"SELECT {hOrV}_score"
        for inn in range(1,10):
            stmt += f", {hOrV}_score_inning_{inn}"
        stmt += f", {hOrV}_at_bats, {hOrV}_hits, {hOrV}_doubles, {hOrV}_triples"
        stmt += f", {hOrV}_home_runs, {hOrV}_rbi, {hOrV}_sac_hit, {hOrV}_sac_fly"
        stmt += f", {hOrV}_hit_by_pitch, {hOrV}_walks, {hOrV}_int_walks"
        stmt += f", {hOrV}_strikeouts, {hOrV}_stolen_bases, {hOrV}_caught_stealing"
        stmt += f", {hOrV}_gidp, {hOrV}_catcher_interference, {hOrV}_left_on_base"
        stmt += f", {hOrV}_pitchers_used, {hOrV}_indiv_earned_runs, {hOrV}_team_earned_runs"
        stmt += f", {hOrV}_wild_pitches, {hOrV}_balks, {hOrV}_putouts, {hOrV}_assists"
        stmt += f", {hOrV}_errors, {hOrV}_passed_balls, {hOrV}_double_plays, {hOrV}_triple_plays"
        stmt += f" FROM gamelog_view WHERE game_id={gameID}"
        #print(stmt)
        cur.execute(stmt)
        tups = cur.fetchall()
        tups = tups[0]
        self.runs = tups[0]
        self.runs_inning[1:] = tups[1:10]
        i = 10
        for st in TEAM_STAT_LIST:
            setattr(self, st, tups[i])
            i += 1

    def print(self):
        print("     runs", self.runs)
        print("by inning", end=" ")
        for r in self.runs_inning:
            print(r, end=" ")
        print()
        for st in TEAM_STAT_LIST[1:15]:
            print(f"{st:4}", end="")
        print()
        for st in TEAM_STAT_LIST[1:15]:
            print(f"{getattr(self, st):4}", end="")
        print()
        for st in TEAM_STAT_LIST[15:]:
            print(f"{st:4}", end="")
        print()
        for st in TEAM_STAT_LIST[15:]:
            print(f"{getattr(self, st):4}", end="")
        print()

    def compare(self, other):
        v1 = self.runs
        v2 = other.runs
        if v1 != v2:
            DEBUG_PRINT(f"runs {v1} != {v2}")
        for i in range(1, 10):
            v1 = self.runs_inning[i]
            v2 = other.runs_inning[i]
            if v1 != v2:
                DEBUG_PRINT(f"inn {i} {v1} != {v2}")

        for i in range(len(TEAM_STAT_LIST)):
            st = TEAM_STAT_LIST[i]
            v1 = getattr(self, st)
            v2 = getattr(other, st)
            if v1 != v2:
                DEBUG_PRINT(f"{st} {v1} != {v2}")


class GameState:
    # batsTop = lineup of team batting at the top of the inning
    # batsBot = lineup of team batting at the bottom of the inning
    def __init__(self, batsTop, batsBot, gameID, gameKey, tiebreakbase, inningsSched):
        self.gameID = gameID
        self.gameKey = gameKey
        # score for each team
        self.score = dict()
        self.score[batsTop.team_id] = 0
        self.score[batsBot.team_id] = 0

        self.teamStats = dict()
        self.teamStats[batsTop.team_id] = TeamStats()
        self.teamStats[batsBot.team_id] = TeamStats()
        self.tiebreakbase = tiebreakbase
        self.inningsSched = inningsSched
        if(inningsSched < 7):
            print("inningsSched= ", inningsSched, " ?!")
            exit(1)
        self.batsTop = batsTop
        self.batsBot = batsBot

        # map to stats by team, with last player being the current player
        self.statsBat = dict()
        self.statsBat[batsTop.team_id] = [[] for i in range(10)]
        self.statsBat[batsBot.team_id] = [[] for i in range(10)]
        self.statsField = dict()
        self.statsField[batsTop.team_id] = [[] for i in range(10)]
        self.statsField[batsBot.team_id] = [[] for i in range(10)]        
        self.statsPitch = dict()
        self.statsPitch[batsTop.team_id] = []
        self.statsPitch[batsBot.team_id] = []
        i = 0
        for (p1, p2) in zip(batsTop.battingOrder, batsBot.battingOrder):
            #DEBUG_PRINT("i=", i, " p1=", p1, " p2=", p2)
            if p1 is not None and p2 is not None:
                self.statsBat[batsTop.team][i].append((p1, BatterStats()))
                self.statsBat[batsBot.team][i].append((p2, BatterStats()))
            i += 1
        i = 0
        for (p1, p2) in zip(batsTop.fieldPos, batsBot.fieldPos):
            #DEBUG_PRINT("i=", i, " p1=", p1, " p2=", p2)
            if p1 is not None and p2 is not None:
                self.statsField[batsTop.team][i].append((p1, FielderStats()))
                self.statsField[batsBot.team][i].append((p2, FielderStats()))
            i += 1
        
        startPitTop = batsTop.fieldPos[1]
        self.statsPitch[batsTop.team].append((startPitTop, PitcherStats()))
        startPitBot = batsBot.fieldPos[1]
        self.statsPitch[batsBot.team].append((startPitBot, PitcherStats()))
        DEBUG_PRINT("startPitBot= ", startPitBot, " startPitTop=", startPitTop)
        self.inning = 0
        self.inningHalf = "B"
        self.cur_batter = dict()
        self.cur_batter[batsTop.team] = 1
        self.cur_batter[batsBot.team] = 1
        self.expectGameEnd = False
        self.SQLstmts = []
        self.nextHalfInning()

    def finalize(self, cur):
        for s in self.SQLstmts:
            DEBUG_PRINT(s)
            cur.execute(s)

    def nextHalfInning(self):
        # calcualte LOB (if we have started game)
        if self.inning > 0:
            lob = sum(map(lambda x: x is not None, self.baseRunners[1:]))
            self.teamStats[self.curBat.team].LOB += lob
            t1 = time.time()
            dt = t1 - self.timeHalfInn
            #print(f"execution took {dt*1000} ms")
            
            
        self.timeHalfInn = time.time()
        self.batterPlayCnt = 0
        self.lastBatter = None
        
        # teap batting in the top (usually vistor) took lead, and other team did not
        # tie or retake lead
        if self.inning >= self.inningsSched and self.inningHalf == "B":
            isTrailing = self.score[self.curBat.team] < self.score[self.curField.team]
            if isTrailing:
                DEBUG_PRINT("end of game expected")
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
        # place baserunner on tiebreakbase
        if self.inning > self.inningsSched and self.tiebreakbase > 0:
            # place batter to get last out on base
            prevBatterIdx = self.cur_batter[self.curBat.team] - 1 
            if prevBatterIdx == 0:
                prevBatterIdx = 9
            prevBatter = self.curBat.battingOrder[prevBatterIdx]
            DEBUG_PRINT(self.inningHalf, self.inning, " placing ", prevBatter, " on ", self.tiebreakbase)
            self.baseRunners[self.tiebreakbase] = (prevBatterIdx, prevBatter)

    def nextBatter(self):
        batTeam = self.curBat.team
        b = (self.cur_batter[batTeam] + 1) 
        if b > 9:
            b = 1
        self.cur_batter[batTeam] = b
        #DEBUG_PRINT("nextBatter: batTeam= ", batTeam, " b=", b)

    def compileGameStatsTeam(self, tm, cur):
        batStats = BatterStats()
        fieldStats = FielderStats()
        pitchStats = PitcherStats()

        if tm == self.batsBot.team:
            self.teamStats[tm].PI = len(self.batsBot.pitchersUsed)
            tm_id = self.batsBot.team_id
        else:
            self.teamStats[tm].PI = len(self.batsTop.pitchersUsed)
            tm_id = self.batsTop.team_id
        DEBUG_PRINT(tm, "batting")
        batStats.printHeader()
        for o in range(1, 10):
            DEBUG_PRINT(o, end=" ")
            stats = self.statsBat[tm][o]
            i = 0
            for (pID, st) in stats:
                lst = "  "
                if i > 0: # sub
                    DEBUG_PRINT(lst, end="  ")
                    lst = ""
                #DEBUG_PRINT(playerIDMap[pID][0], end=lst)
                DEBUG_PRINT(pID, end=lst)
                st.print()
                batStats.add(st)
                #insertIntoDB(self, cur, game_id, player_num_id, team, seq, pos):
                try:
                    st.insertIntoDB(cur, self.gameID, pID, tm_id, o, i+1)
                except Exception as e:
                    pass
                i += 1

        # fielding stats
        DEBUG_PRINT(tm, "fielding")
        fieldStats.printHeader()
        for o in range(1, 10):
            DEBUG_PRINT(o, end=" ")
            stats = self.statsField[tm][o]
            i = 0
            for (pID, st) in stats:
                lst = "  "
                if i > 0: # sub
                    DEBUG_PRINT(lst, end="")
                    lst = " "
                DEBUG_PRINT(pID, end=lst)
                #DEBUG_PRINT(playerIDMap[pID][0], end=lst)
                st.print()
                fieldStats.add(st)
                try:
                    st.insertIntoDB(cur, self.gameID, pID, tm_id, o, i+1)
                except Exception as e:
                    pass
                i += 1
        
                
        pitchStats = PitcherStats()
        DEBUG_PRINT(tm, " pitching")
        pitchStats.printHeader()
        i = 1
        for (pID, st) in self.statsPitch[tm]:
            #DEBUG_PRINT(playerIDMap[pID][0], end="")
            DEBUG_PRINT(pID, end="")
            st.print()
            pitchStats.add(st)
            try:
                st.insertIntoDB(cur, self.gameID, pID, tm_id, i)
            except Exception as e:
                pass
            i += 1

        return batStats, fieldStats, pitchStats

    def compileGameStats(self, cur):
        #DEBUG_PRINT(self.batsTop.battingOrderStart)
        self.teamTopBat, self.teamTopField, self.teamTopPitch = self.compileGameStatsTeam(self.batsTop.team, cur)
        self.teamBotBat, self.teamBotField, self.teamBotPitch = self.compileGameStatsTeam(self.batsBot.team, cur)

    def printGameStats(self):
        sBT = self.teamTopBat
        sBB = self.teamBotBat
        DEBUG_PRINT("     AB  H  R  BB RBI 2B 3B HR")        
        DEBUG_PRINT(f"{self.batsTop.team} {sBT.AB:3}{sBT.H:3}{sBT.R:3}{sBT.BB+sBT.IBB:3}{sBT.RBI:3}{sBT.n2B:3}{sBT.n3B:3}{sBT.HR:3}")
        DEBUG_PRINT(f"{self.batsBot.team} {sBB.AB:3}{sBB.H:3}{sBB.R:3}{sBB.BB+sBB.IBB:3}{sBB.RBI:3}{sBB.n2B:3}{sBB.n3B:3}{sBB.HR:3}")

    def applyLineupAdj(self, lAdj):
        DEBUG_PRINT("***** LINEUP ADJUSTMENT ***** ")
        lAdj.print()
        self.cur_batter[self.curBat.team] = int(lAdj.adj)

    def applyPlayerAdj(self, pAdj):
        pAdj.print()

    def applyDataER(self, dER):
        # find pitcher and add to ER count
        for pID, pitStats in self.statsPitch[self.batsTop.team]:
            if pID == dER.player_id: 
                pitStats.ER += dER.er
                self.teamStats[self.batsTop.team].ERI += dER.er
                self.teamStats[self.batsTop.team].ERT += dER.er
                return
        for pID, pitStats in self.statsPitch[self.batsBot.team]:
            if pID == dER.player_id: 
                pitStats.ER += dER.er
                self.teamStats[self.batsBot.team].ERI += dER.er
                self.teamStats[self.batsBot.team].ERT += dER.er
                return

    # treatBaserunModErrorAsOut, whether to treat an error listed in 
    # baserunner mods where is marked out as run (True) or out (False)
    def applyPlay(self, p, treatBaserunErrorAsOut=False):
        if p.bat.results[0] == "NP": # no play
            DEBUG_PRINT("applyPlay(): no play")
            return None
        
        #DEBUG_PRINT("applyPlay batterID=", batterID, "pitcherID=", pitcherID)
        
        curFieldTeam = self.curField.team
        curBatTeam = self.curBat.team
        batsTopTeam = self.batsTop.team
        batsBotTeam = self.batsBot.team
        scTop = self.score[batsTopTeam]
        scBot = self.score[batsBotTeam]
        scBat = scTop
        scField = scBot
        if curBatTeam == batsTopTeam:
            scBat = scBot
            scField = scTop

        DEBUG_PRINT(f">>>> applyPlay {self.inningHalf}{self.inning} {batsTopTeam} {scTop} {batsBotTeam} {scBot} {self.outs} outs ")
        DEBUG_PRINT(f"treatBaserunErrorAsOut={treatBaserunErrorAsOut}")
        #DEBUG_PRINT("applyPlay cur_batter=", self.cur_batter, " curBat", self.curBat.team)
        curBatterIdx = self.cur_batter[self.curBat.team]
        batterID = self.curBat.battingOrder[curBatterIdx]
        pitcherID = self.curField.fieldPos[1]  # position 1 (pitcher)

        #expBat = playerIDMap[batterID][0]
        expBat = batterID
        #pit = playerIDMap[pitcherID][0]
        pit = pitcherID
        err = False
        
        if self.expectGameEnd:
            DEBUG_PRINT("applyPlay: ERROR end of game expected")
            err = True
        if p.team != self.curBat.team:
            DEBUG_PRINT("applyPlay: ERROR unexpected team", p.team, " expected", self.curBat.team)
            err = True
        if p.inning != self.inning:
            DEBUG_PRINT("applyPlay: ERROR unexpected inning", p.inning, " expected", self.inning)
            err = True
        
        DEBUG_PRINT(curBatTeam, curBatterIdx, expBat, "at bat", curFieldTeam, pit, " pitching ",)
        
        if self.lastBatter == batterID:
            self.batterPlayCnt += 1
        else:
            self.batterPlayCnt = 0
        self.lastBatter = batterID
        if self.gameKey in AMBIGUOUS_PLAYS:
            ambPlays = AMBIGUOUS_PLAYS[self.gameKey]
            sit = (self.inning, self.inningHalf, batterID, self.batterPlayCnt)
            if sit in ambPlays:
                DEBUG_PRINT("?????  Ambigious play - replacing parsed result with manual")
                p.bat, p.fielding, p.run  = ambPlays[sit]

        batterID = p.player_id
        
        # -1 = last index (current player)
        (bID, stBat) = self.statsBat[curBatTeam][curBatterIdx][-1]
        # DEBUG_PRINT(self.statsPitch[curFieldTeam])
        (pID, stPit) = self.statsPitch[curFieldTeam][-1] 
        # pitchers get credited with putouts for strikeouts
        (pID, stPitField) = self.statsField[curFieldTeam][1][-1] 
        if batterID != bID:
            stBatter = batterID
            DEBUG_PRINT("applyPlay: ERROR batter", stBatter, " does not match lineup", bID)
            err = True
        if pitcherID != pID:
            stPitcher = pitcherID
            DEBUG_PRINT("applyPlay: ERROR pitcher", stPitcher, " does not match lineup", pID)
            err = True
        gameID = p.game_id
        eventID = p.event_id
        if err: 
            return err, False, False
        DEBUG_PRINT("onBase: ", end="")
        for b in range(1, 4):
            rn = self.baseRunners[b]
            
            DEBUG_PRINT(f"{b}: ", end="")
            if rn == None:
                DEBUG_PRINT(" "*8, end=" ")
            else:
                (runIdx, runID) = rn
                #runner = playerIDMap[runID][0]
                DEBUG_PRINT(runID, end=" ")
        DEBUG_PRINT()
        DEBUG_PRINT("play= ", p.play, end=" ")
        DEBUG_PRINT("hit_type= ", p.bat.hit_type, end=" ")
        DEBUG_PRINT("hit_loc= ", p.bat.hit_loc)
        
        # inn_out_bat_cnt = (self.inning << 8) 
        # if self.inningHalf == "B":
        #     inn_out_bat_cnt += (1 << 7)
        # inn_out_bat_cnt += (self.outs << 5)
        # inn_out_bat_cnt += p.batter_count
        pitch_cnt = p.batter_count
        if pitch_cnt == "??":
            pitch_cnt = None
        bid = playerCodeToIDMap[batterID]            
        pid = playerCodeToIDMap[pitcherID]
        gs_stmt = f"INSERT INTO game_situation VALUES({gameID}, {eventID}, {bid}"
        gs_stmt += f", {pid}, {self.inning}, '{self.inningHalf}', {self.outs}"
        gs_stmt += f", {valOrNULL(pitch_cnt)}, {scBat}, {scField}"
        
        DEBUG_PRINT("results=", p.bat.results)
        DEBUG_PRINT("bases=", p.bat.bases)
        DEBUG_PRINT("mods=", p.bat.mods)
        
        # baserunners in separate table to save space (over half of plays do not have baserunners)
        bases_stmt = f"INSERT INTO game_situation_bases VALUES({gameID}, {eventID}"
        numOcc = 0
        for b in self.baseRunners[1:4]:
            if b is None:
                bases_stmt +=f", NULL"
            else:
                numOcc += 1
                bases_stmt += f", {playerCodeToIDMap[b[1]]}"
        bases_stmt += ")"
        if numOcc > 0:
            self.SQLstmts.append(bases_stmt)

        # split multiple result plays into different relation
        if len(p.bat.results) > 1:
            gs2_stmt = f"INSERT INTO game_situation_result2 VALUES({gameID}, {eventID}"
            r2 = p.bat.results[1]
            b2 = "NULL"
            if p.bat.bases[1] is not None:
               b2 = baseToNum(p.bat.bases[1])
            gs2_stmt += f", '{r2}', {b2})"
            DEBUG_PRINT(gs2_stmt)
            self.SQLstmts.append(gs2_stmt)
        if len(p.bat.results) > 2:
            gs3_stmt = f"INSERT INTO game_situation_result3 VALUES({gameID}, {eventID}"
            r3 = p.bat.results[2]
            b3 = "NULL"
            if p.bat.bases[2] is not None:
               b2 = baseToNum(p.bat.bases[2])
            gs3_stmt += f", '{r3}', {b3})"
            self.SQLstmts.append(gs3_stmt)
        
        # place current batter as a "baserunner" from home
        self.baseRunners[0] = (curBatterIdx, batterID)
        baseRunNxt = [None]*4  # 0 = home (batter), 1 = first, etc.
        
        # runners present at beginning of play, including batter 
        # (base 0 = home)
        # -1 mean runner is now out
        # e.g., for 'SB2' movedRunners[1] = 2
        # for 'CS2'  movedRunners[1] = -1
        self.movedRunners = [None]*4 
        # default is for runners to stay at base
        for b in range(0, 4):
            if self.baseRunners[b] is not None:
                self.movedRunners[b] = b
        
        
        def applyBaseRunResult(r2, base2):
            DEBUG_PRINT("applyBaseRunResult: r2=", r2, " base2=", base2)
            
            if base2 == "H":
                dst = 4
            else:
                dst = int(base2)
            src = dst
            
            if r2 in ("SB", "CS", "POCS"):
                src = dst - 1
                runIdx, runnerID = self.baseRunners[src]
                if r2 == "SB":
                    DEBUG_PRINT("stolen base", dst)
                    self.movedRunners[src] = dst
                    self.statsBat[curBatTeam][runIdx][-1][1].SB += 1
                    self.teamStats[curBatTeam].SB += 1
                if r2 in ("CS", "POCS"):
                    self.statsBat[curBatTeam][runIdx][-1][1].CS += 1
                    self.teamStats[curBatTeam].CS += 1
                    DEBUG_PRINT("caught stealing", dst)                    
                else:
                    DEBUG_PRINT("pickoff", src)
            # end applyBaseRunResult

        # most plays advance to the next batter
        # if set false in the following logic, we expect batter to remain at the plate
        # or inning to end.  Only check on first play if mulitple plays (sucha s K+SB)
        expectNextBat = True
        isDoublePlay = False
        isTriplePlay = False
        rNum = 1
        for r, base, mods in zip(p.bat.results, p.bat.bases, p.bat.mods):
            if r == "O":  # generic out
                if "G" in mods:
                    DEBUG_PRINT("groundout")
                elif "F" in mods:
                    DEBUG_PRINT("flyout")
                elif "L" in mods:
                    DEBUG_PRINT("lineout")
                elif "P" in mods:
                    DEBUG_PRINT("popout")
                elif "FL" in mods:
                    DEBUG_PRINT("fouled out")
                elif "BG" in mods:
                    DEBUG_PRINT("bunt groundout")
                elif "BL" in mods:
                    DEBUG_PRINT("bunt line drive out")
                else:
                    DEBUG_PRINT("out - other")
                stBat.AB += 1
                self.teamStats[curBatTeam].AB += 1
                self.movedRunners[0] = -1
            elif r in ("S", "D", "DGR", "T", "HR"):
                stBat.AB += 1
                stBat.H += 1
                self.teamStats[curBatTeam].AB += 1
                self.teamStats[curBatTeam].H += 1
                stPit.H += 1
                if r == "S":
                    DEBUG_PRINT("single")
                    self.movedRunners[0] = 1
                elif r in ("D", "DGR"):
                    DEBUG_PRINT("double")
                    stBat.n2B += 1
                    self.teamStats[curBatTeam].n2B += 1
                    stPit.n2B += 1
                    self.movedRunners[0] = 2
                elif r == "T":
                    DEBUG_PRINT("triple")
                    stBat.n3B += 1
                    self.teamStats[curBatTeam].n3B += 1
                    stPit.n3B += 1
                    self.movedRunners[0] = 3
                elif r == "HR":
                    DEBUG_PRINT("home run")
                    stBat.HR += 1
                    self.teamStats[curBatTeam].HR += 1
                    stPit.HR += 1
                    self.movedRunners[0] = 4
            elif r == "BB":
                DEBUG_PRINT("walk")
                stBat.BB += 1
                self.teamStats[curBatTeam].BB += 1
                stPit.BB += 1
                self.movedRunners[0] = 1   
            elif r == "IBB":
                DEBUG_PRINT("intentional walk")
                stBat.IBB += 1
                self.teamStats[curBatTeam].IBB += 1
                stPit.IBB += 1
                self.movedRunners[0] = 1   
            elif r == "K": # strike out
                DEBUG_PRINT("strikeout")
                stBat.AB += 1
                stBat.K += 1
                self.teamStats[curBatTeam].AB += 1
                self.teamStats[curBatTeam].K += 1
                stPit.K += 1
                stPitField.PO += 1
                self.movedRunners[0] = -1
            elif r == "FO": # force out (runner(s) other than batter)
                DEBUG_PRINT("force out")
                stBat.AB += 1
                self.teamStats[curBatTeam].AB += 1
                self.movedRunners[0] = 1
            elif r == "FC": # fielders choice
                DEBUG_PRINT("fielders choice")
                stBat.AB += 1
                self.teamStats[curBatTeam].AB += 1
                self.movedRunners[0] = 1   
            elif r == "BK": # balk
                DEBUG_PRINT("balk")
                stPit.BK += 1
                self.teamStats[curFieldTeam].BK += 1
                expectNextBat = False
            elif r == "HBP": # hit by pitch
                DEBUG_PRINT("hit by pitch")
                self.teamStats[curBatTeam].HBP += 1
                stBat.HBP += 1
                self.movedRunners[0] = 1   
            elif r == "FLE": # error on foul ball
                DEBUG_PRINT("error on foul ball")
                expectNextBat = False           
            elif r == "POE": # pick off error
                DEBUG_PRINT("pick off error")
                expectNextBat = False
            elif r == "CI": # catcher interference
                DEBUG_PRINT("catcher interference")
                self.teamStats[curFieldTeam].CI += 1
                self.movedRunners[0] = 1   
            elif r == "E":
                stBat.AB += 1
                self.teamStats[curBatTeam].AB += 1
                if rNum == 1:
                    self.movedRunners[0] = 1   
            elif r == "WP": # wildpitch
                DEBUG_PRINT("wild pitch")
                if rNum == 1: # handle combo plays
                    expectNextBat = False
                stPit.WP += 1
                self.teamStats[curFieldTeam].WP += 1
            elif r == "PB": # passed ball
                DEBUG_PRINT("passed ball")
                if rNum == 1: # handle combo plays
                    expectNextBat = False
                # position 2 = catcher
                # =1 = last index(current player), 1 = index of stats obj in tuple
                self.statsField[curFieldTeam][2][-1][1].PB += 1    
                self.teamStats[curFieldTeam].PB += 1
            elif r in ("DI", "OA"):
                DEBUG_PRINT("defensive indifference/other advance")
                if rNum == 1: # handle combo plays
                    expectNextBat = False
                # should noted in runAdv
            elif r in ("SB", "CS", "PO", "POCS"):
                if rNum == 1:  # handle combo plays
                    expectNextBat = False
                applyBaseRunResult(r, base)
            else:
                expectNextBat = False
                DEBUG_PRINT("Unknown play ", r)
                return True, False, False
            seq = 1
            for mod in mods:
                prm = 0
                if type(mod) == type(tuple()):
                    prm = mod[1]
                    if prm in ("H", "B"):
                        prm = 0
                    mod = mod[0]                    
                stmt = f"INSERT INTO game_situation_result{rNum}_mod"
                stmt += f" VALUES({gameID}, {eventID}"
                stmt += f", {seq}, '{mod}', '{prm}')"
                if mod in modCodeMap:
                    DEBUG_PRINT(modCodeMap[mod])
                if mod == "SH":
                    self.teamStats[curBatTeam].SH += 1
                    stBat.SH += 1
                elif mod == "SF":
                    self.teamStats[curBatTeam].SF += 1
                    stBat.SF += 1
                elif mod in ("GDP", "BGDP", "GTP"):
                    self.teamStats[curBatTeam].GIDP += 1
                    stBat.GIDP += 1
                elif mod in ("DP", "FDP", "LDP"):
                    isDoublePlay = True
                elif mod in ("LTP", "TP"):
                    isTriplePlay = True
                self.SQLstmts.append(stmt)
                seq += 1
            rNum += 1
        # END for loop

        stmt_fldr_ass = f"INSERT INTO game_situation_fielder_assist VALUES({gameID}, {eventID}"
        stmt_fldr_po = f"INSERT INTO game_situation_fielder_putout VALUES({gameID}, {eventID}"
        stmt_fldr_err = f"INSERT INTO game_situation_fielder_error VALUES({gameID}, {eventID}"
        stmt_fldr_fld = f"INSERT INTO game_situation_fielder_fielded VALUES({gameID}, {eventID}"
        seq = 1
        for f in p.fielding.errors:
            DEBUG_PRINT("fielding error on ", f, end=" ")
            fcode = self.curField.fieldPos[f]
            DEBUG_PRINT(fcode)
            fldr_id = playerCodeToIDMap[fcode]
            self.statsField[curFieldTeam][f][-1][1].E += 1
            self.teamStats[curFieldTeam].E += 1
            stmt_err = stmt_fldr_err + f", {fldr_id}, {seq})"
            self.SQLstmts.append(stmt_err)
            seq += 1
        seq = 1
        for f in p.fielding.putouts:
            DEBUG_PRINT("putout for ", f, end=" ")
            f = int(f)
            fcode = self.curField.fieldPos[f]
            DEBUG_PRINT(fcode)
            fldr_id = playerCodeToIDMap[fcode]            
            self.statsField[curFieldTeam][f][-1][1].PO += 1
            self.teamStats[curFieldTeam].PO += 1
            stmt_po = stmt_fldr_po + f", {fldr_id}, {seq})"
            self.SQLstmts.append(stmt_po)
            seq += 1
        seq = 1
        for f in p.fielding.assists:
            DEBUG_PRINT("assist for ", f, end=" ")
            f = int(f)
            fcode = self.curField.fieldPos[f]
            DEBUG_PRINT(fcode)
            fldr_id = playerCodeToIDMap[fcode]
            self.statsField[curFieldTeam][f][-1][1].A += 1
            self.teamStats[curFieldTeam].A += 1
            stmt_ass = stmt_fldr_ass + f", {fldr_id}, {seq})"
            self.SQLstmts.append(stmt_ass)
            seq += 1
        seq = 1
        for f in p.fielding.fielded:
            DEBUG_PRINT("fielded by ", f, end=" ")
            f = int(f)
            fcode = self.curField.fieldPos[f]
            DEBUG_PRINT(fcode)
            fldr_id = playerCodeToIDMap[fcode]
            stmt_fld = stmt_fldr_fld + f", {fldr_id}, {seq})"
            self.SQLstmts.append(stmt_fld)
            seq += 1
        
        self.possiblySafeDueToError = False
        
        def handleBaseRunners():
            # explicit outs not having to do with runner advances
            DEBUG_PRINT("runners out", p.run.out)
            for b in p.run.out:
                src = b
                src = baseToNum(b[0])
                isError = b[1]
                dst = b[2]

                # clear base runner
                if isError:
                    self.possiblySafeDueToError = True
                    DEBUG_PRINT("error in play with base runner at ", b, end= " ")
                    if treatBaserunErrorAsOut:
                        DEBUG_PRINT("treating as out")
                        self.movedRunners[src] = -1
                    else:
                        DEBUG_PRINT("treating as safe")
                        self.movedRunners[src] = dst
                else:
                    self.movedRunners[src] = -1
            stmt_base_run = f"INSERT INTO game_situation_base_run VALUES({gameID}, {eventID}"
            for adv in p.run.adv:
                src = baseToNum(adv[0])
                dst = baseToNum(adv[1])
                isSafe = adv[2]
                DEBUG_PRINT("src=", src, "dst=", dst, "isSafe=", isSafe)
                #DEBUG_PRINT(self.baseRunners)
                #DEBUG_PRINT(self.movedRunners)
                # we expect base runner to be there but they are
                # not, probalby due to misinterpretation of error
                if self.baseRunners[src] is None:
                    DEBUG_PRINT("ERROR: expected base runner at ", src)
                    return None
                runIdx, runnerID = self.baseRunners[src]
                
                if isSafe == "E": # error
                    self.possiblySafeDueToError = True                
                    if treatBaserunErrorAsOut:
                        DEBUG_PRINT(f"runner on src ({runnerID}) treating as out at {dst}, ignoring error")
                        self.movedRunners[src] = -1
                    else:
                        DEBUG_PRINT(f"runner on {src} {runnerID} treating as safe at {dst} due to error")
                        self.movedRunners[src] = dst
                elif isSafe: # safe
                    self.movedRunners[src] = dst
                else:  # out
                    self.movedRunners[src] = -1 
                    
                a2 = isSafe
                if isSafe == "E":
                     a2 = treatBaserunErrorAsOut
                stmt = stmt_base_run + f", {src}, {dst}, {a2})"
                self.SQLstmts.append(stmt)
            
            baseRunNxt = [None]*4
            runs = 0
            outs = 0
            for b in range(0, 4):
                rn = self.baseRunners[b]
                nxtBase = self.movedRunners[b]
                if nxtBase is not None:
                    nxtBase = baseToNum(nxtBase)

                if rn is not None:    
                    runIdx, runnerID = self.baseRunners[b]
                    if nxtBase == b:
                        DEBUG_PRINT("runner on", b, " does not advance")
                    else:
                        if nxtBase == 4:
                            DEBUG_PRINT("runner on", b, " scores")
                        elif nxtBase == -1:
                            DEBUG_PRINT("runner on", b, " is out")
                            outs += 1
                        else:
                            DEBUG_PRINT("runner on", b, " advances to ", nxtBase)
                    
                    if nxtBase == 4:
                        runs += 1
                        self.statsBat[curBatTeam][runIdx][-1][1].R += 1
                        if p.bat.results[0] not in ("WP", "PB", "BK", "SB", "E") and not isDoublePlay:
                            stBat.RBI += 1
                            self.teamStats[curBatTeam].RBI += 1
                    elif nxtBase is not None and nxtBase > 0:
                        baseRunNxt[nxtBase] = (runIdx, runnerID)
            return runs, outs, baseRunNxt
        
        ret = handleBaseRunners()
        self.possiblySafeDueToError = self.possiblySafeDueToError
        if ret is None:
            return True, self.possiblySafeDueToError, False
        runs, outs, baseRunNxt = ret
        DEBUG_PRINT("handleBaseRunners returned runs=", runs, "outs= ", outs)
        DEBUG_PRINT("basedRunners=", self.baseRunners)
        DEBUG_PRINT("movedRunners=", self.movedRunners)
        DEBUG_PRINT("baseRunNxt=", baseRunNxt)
        if isDoublePlay and outs != 2:
            DEBUG_PRINT("double play but calculated outs != 2")
            return True, self.possiblySafeDueToError, False
        if isTriplePlay and outs != 3:
            DEBUG_PRINT("triple play but calculated outs != 3")
            return True, self.possiblySafeDueToError, False

        stmt_base_run_mod = f"INSERT INTO game_situation_base_run_mod VALUES({gameID}, {eventID}"
        for base_mod, adv in zip(p.run.mods, p.run.adv):
            src = baseToNum(adv[0])
            dst = baseToNum(adv[1])
            isOut = adv[2]
            if isOut == "E":
                isOut = treatBaserunErrorAsOut
            seq = 1
            for mods in base_mod:
                #DEBUG_PRINT(mods)
                if len(mods) == 0:
                    continue
                sub_mod0 = mods[0]                
                #DEBUG_PRINT("mod[0]=", sub_mod0)
                #src_dst_out = (src << 6) + (dst << 3) + isOut
                #seq_mod_prm = (seq << 10) + (modCodeNumMap[sub_mod0[0]] << 5)
                mod_prm = None
                if type(sub_mod0) == type(tuple()):
                    sub_mod0_0 = sub_mod0[0]
                    mod_prm = sub_mod0[1]
                    # if type(mod_prm) == type(""):
                    #     mod_prm = modCodeNumMap[mod_prm]
                   
                    #seq_mod_prm += mod_prm
                else:
                    sub_mod0_0 = sub_mod0
                    
                stmt = stmt_base_run_mod + f", {src}"
                stmt += f", {seq}, '{sub_mod0_0}', '{mod_prm}')"
                self.SQLstmts.append(stmt)
                #stmt_br_smod = f"INSERT INTO game_situation_base_run_sub_mod"
                #stmt_br_smod += f" VALUES({(gameID << 10) + eventID}, {src_dst_out}"
                #stmt_br_smod += f", {seq_mod_prm}"
                for sub_mod in mods[1:]:
                    DEBUG_PRINT("sub_mod=", sub_mod)
                    
                    #if type(sub_mod) == type(tuple()):
                        #sub_mod_packed = (modCodeNumMap[sub_mod[0]] << 10)
                        #sub_mod_packed += (modCodeNumMap[sub_mod[1]] << 5)
                    #else:
                        #sub_mod_packed = (modCodeNumMap[sub_mod] << 10)
                    #stmt_br_smod += f", {sub_mod_packed})"
                    #DEBUG_PRINT(stmt_br_smod)
                    #self.SQLstmts.append(stmt_br_smod)
                seq += 1

        gs_stmt += f", '{p.bat.results[0]}', {valOrNULL(p.bat.bases[0])}"
        gs_stmt += f", {valOrNULL(p.bat.hit_loc)}, {valOrNULL(p.bat.hit_type)}, {outs}, {runs})" 
        
        # finish game situation statement
        #gs_stmt += f", {outs}, {runs})"
        self.SQLstmts.append(gs_stmt)        

        self.baseRunners = baseRunNxt
        self.outs += outs
        self.score[curBatTeam] += runs
        self.teamStats[curBatTeam].runs += runs
        if self.inning < 10:
            if self.teamStats[curBatTeam].runs_inning[self.inning] is None:
                self.teamStats[curBatTeam].runs_inning[self.inning] = 0
            self.teamStats[curBatTeam].runs_inning[self.inning] += runs
        stPit.R += runs
        
        # credit outs to the pitcher and fielders
        if outs > 0:
            stPit.IP3 += outs
            # all fielders
            for f in range(1, 10):
                # -1 = last fielder in list (currently on field)
                self.statsField[curFieldTeam][f][-1][1].IF3 += outs
        if expectNextBat:
            stPit.BF += 1
            self.nextBatter()
        # scored runs on this play in sudden death situation, we expect game to be over
        isLeading = self.score[self.curBat.team] > self.score[self.curField.team]
        if self.inning >= 9 and self.inningHalf == "B" and isLeading:
            self.expectGameEnd = True
        
        isNextHalfInning = False
        if self.outs >= 3:
            if self.outs > 3:
                DEBUG_PRINT(f"ERROR: too many outs ({self.outs})")
                return True, self.possiblySafeDueToError, isNextHalfInning
            DEBUG_PRINT("----- end of inning ------")
            self.nextHalfInning()
            isNextHalfInning = True

        return False, self.possiblySafeDueToError, isNextHalfInning

    def applySub(self, evt):
        if evt.team_id == self.batsTop.team_id:
            tm = self.batsTop
        elif evt.team_id == self.batsBot.team_id:
            tm = self.batsBot
        else:
            print("applySub: bad team", evt.team_id)
            return None

        rep_batter, (rep_fielder, newPos) = tm.applySub(evt)
        DEBUG_PRINT("applySub: rep_batter=", rep_batter, " rep_fielder= ", rep_fielder, " newPos=", newPos)
        repFielderID = None
        if rep_fielder is not None:
            # destructure
            repFielderID = rep_fielder

        subID = evt.player_id
        repBatterID = None
        if rep_batter is not None:
            repBatterID = rep_batter
        
        DEBUG_PRINT("applySub: ", tm.team, subID, " replaces ", repBatterID, " playing ", evt.field_pos, " batting", evt.bat_pos)
        if rep_fielder is not None:
            DEBUG_PRINT("    ", repFielderID, " moves to ", newPos)
        if evt.bat_pos != 0:
            stBat = self.statsBat[tm.team][evt.bat_pos]
            if subID != repBatterID:
                stBat.append((evt.player_id, BatterStats()))
            else:
                DEBUG_PRINT("applySub: not appending to batting stats, replacing self (field pos change)")
        if evt.field_pos in FIELD_POS_NUM:
            stField = self.statsField[tm.team][evt.field_pos]
            stField.append((evt.player_id, FielderStats()))
        if evt.field_pos == 1:  # pitcher
            stPitch = self.statsPitch[tm.team]
            stPitch.append((evt.player_id, PitcherStats()))
        if evt.field_pos == "R":
            DEBUG_PRINT("applySub: replacing runner on base")
            runnerFound = False
            for b in range(len(self.baseRunners)):
                rn = self.baseRunners[b]
                if rn is not None and rn[1] == rep_batter:
                    self.baseRunners[b] = (evt.bat_pos, evt.player_id)
                    runnerFound = True
                    break
            if not runnerFound:
                DEBUG_PRINT("applySub: could not find replacement on base")
                return True
        return False
        
def compareStatsToBoxScore(game, htbf, conn, cur):
    for hOrV in ("home", "away"):
        #print(f"compareStatsToBoxScore: hOrV={hOrV}")
        stats = TeamStats()
        stats.loadfromDB(hOrV, game.gameID, cur)
        tm = game.batsBot.team
        if htbf:
            tm = game.batsTop.team
        if hOrV == "visiting":
            tm = game.batsTop.team
            if htbf:
                tm = game.batsBot.team
        DEBUG_PRINT(tm, " stats discrepancies to boxscore:")
        game.teamStats[tm].compare(stats)

def deleteDBAfterEvent(gameID, eventID):
    allTables = ("game_situation", "game_situation_fielder_assist",
                "game_situation_fielder_putout", "game_situation_fielder_error",
                "game_situation_fielder_fielded", "game_situation_result1_mod", 
                "game_situation_base_run", "game_situation_base_run_mod",
                "game_situation_result2",
                "game_situation_result3", "game_situation_result1_mod",
                "game_situation_result2_mod", "game_situation_result3_mod", 
                "game_situation_bases", "game_situation_coms")
    
    gameTables = ("player_game_batting", "player_game_pitching", "player_game_fielding")
    for tbl in allTables:
        stmt =  f"DELETE FROM {tbl} WHERE game_id={gameID}"
        stmt += f" AND event_id > {eventID}"
        DEBUG_PRINT(stmt)
        try: 
            cur.execute(stmt)
        except KeyboardInterrupt as e:
            exit(1)
        except Exception as e:
            print(e)

    for tbl in gameTables:
        stmt =  f"DELETE FROM {tbl} WHERE game_id={gameID}"
        DEBUG_PRINT(stmt)
        try:
            cur.execute(stmt)
        except KeyboardInterrupt as e:
            exit(1)
        except Exception as e:
            print(e)

def parseGame(game_info_tup, plays, starts, subs, lineupAdjs, playerAdjs, dataER, coms, conn):
    # detect if already parsed game
    cur = conn.cursor()
    tStart = time.time() 

    gameID, home_team, away_team, game_date, dh_num, tiebreakbase, innSched, htbf = game_info_tup
    htbf = bool(htbf)

    gameKey = game_date + home_team + away_team + str(dh_num)
    if gameKey in SKIP_GAMES:
        print("explicitly skipping ", gameKey)
        return False
    print(f"parsing game {gameID} {gameKey}")

    DEBUG_PRINT("home= ", home_team, " away=", away_team, " date=", game_date, " dh_num", dh_num)


    home = Lineup(home_team)
    away = Lineup(away_team)
    for st in starts:
        #DEBUG_PRINT("st=", st)
        # destructure
        #print(st)
        game_id, event_id, player_id = st[0:3]
        team_id, bat_pos, field_pos = st[3:]
        
        if team_id == home_team:
            lineup = home
        elif team_id == away_team:
            lineup = away
        else:
            DEBUG_PRINT(f"parseGame ERROR: team=", team_id, " is neither home=", home_team, " or away=", away_team)
            return True
        #pID = playerIDMap[player_id][0] 
        pID = playerIDToCodeMap[player_id]

        DEBUG_PRINT(pID, team_id, " starting at ", field_pos, " batting order ", bat_pos)
        if bat_pos != 0:
            lineup.battingOrder[bat_pos] = pID
            lineup.battingOrderStart[bat_pos] = pID
        if field_pos != 0: # not DH
            lineup.fieldPos[field_pos] = pID
        if field_pos == 1:  # pitcher
            lineup.pitchersUsed.append(pID)
    t1 = time.time()
    dt = t1 - tStart
    #print(f"fetch took {dt*1000} ms")

    # DEBUG_PRINT lineups for home/away
    away.print()
    home.print()
    
    DEBUG_PRINT(f"htbf={htbf}")
    batsTop = away
    batsBot = home
    if htbf:
        batsTop = home
        batsBot = away

    game = GameState(batsTop, batsBot, gameID, gameKey, tiebreakbase, innSched)
    events = []
    tStart = time.time()
    for p in plays:
        pEvt = PlayEvent(p)
        err = pEvt.parsePlay()
        if err:
            return True            
        events.append(pEvt)
    for s in subs:
        events.append(SubEvent(s))
    for lAdj in lineupAdjs:
        events.append(LineupAdjEvent(lAdj))
    for pAdj in playerAdjs:
        events.append(PlayerAdjEvent(pAdj))
    for dER in dataER:
        events.append(DataEREvent(dER))
    for c in coms:
        events.append(ComEvent(c))

    t1 = time.time()
    dt = t1 - tStart
    # print(f"parse plays took {dt*1000} ms")
    # sort based on event ID
    events = sorted(events, key=lambda x: x.event_id)
    
    # replay attempt within half inning
    # if we 
    replayAttempt = 0  
    maxReplayAttempts = 10
    gameCpyBeginInning = [None]*50
    IBeginInning = [-1]*50
    posssiblySafeDueToErrorInInning = 0
    defaultTreatBaserunErrorAsOut = False
    treatBaserunErrorAsOut = defaultTreatBaserunErrorAsOut    
    isNextHalfInning = False
    inningEndedPriorPlay = False
    i = 0
    # treat each inning as a transaction
    #cur.execute("BEGIN")
    tStart = time.time()
    coms_play = []
    prevPlayID = 0
    gameCpyBeginInning[0] = deepcopy(game)
    IBeginInning[0] = 0
    while i < len(events):
        evt = events[i]
        DEBUG_PRINT("parseGame: i=", i, "event_id", evt.event_id)
        if type(evt) == type(PlayEvent()):
            treatBaserunErrorAsOut = defaultTreatBaserunErrorAsOut
            if replayAttempt == 1:
                treatBaserunErrorAsOut = not defaultTreatBaserunErrorAsOut
            elif replayAttempt > 1:
                # there can be different interpretations of runners marked as out
                # even within the same inning
                # see e.g NYA/CHA 1922-05-10
                treatBaserunErrorAsOut = bool(randint(0, 1))
            ret = game.applyPlay(evt, treatBaserunErrorAsOut)
            if ret is None:  # for no play
                i += 1
                continue
            elif replayAttempt == 0:
                prevPlayID = evt.event_id
            err, posssiblySafeDueToError, isNextHalfInning = ret
            DEBUG_PRINT(f"parseGame: posssiblySafeDueToError={posssiblySafeDueToError}, isNextHalfInning={isNextHalfInning}")
            if err:
                DEBUG_PRINT(f"parseGame: replayAttempt={replayAttempt}, posssiblySafeDueToErrorInInning={posssiblySafeDueToErrorInInning}")
                if replayAttempt < maxReplayAttempts and posssiblySafeDueToErrorInInning > 0 or posssiblySafeDueToError:
                    DEBUG_PRINT(f"###### REPLAYING HALF INNING ######")
                    DEBUG_PRINT(f"treatBaserunErrorAsOut={treatBaserunErrorAsOut}")
                    DEBUG_PRINT(f"isNextHalfInning={isNextHalfInning}")
                    # restore and replay
                    replayAttempt += 1
                    posssiblySafeDueToErrorInInning = 0
                    idx = 2*(game.inning-1) + (game.inningHalf == "B")
                    if isNextHalfInning:
                        idx -= 1
                    game = deepcopy(gameCpyBeginInning[idx])  
                    i = IBeginInning[idx] + 1
                    # treatBaserunModErrorAsOut = not treatBaserunModErrorAsOut
                    #cur.execute("ROLLBACK")
                    #cur.execute("BEGIN")
                    # deleteDBAfterEvent(gameID, savePtEventID)
                    continue
                else: 
                    DEBUG_PRINT("Cannot handle error, skipping rest of game")
                    return True
            
            if posssiblySafeDueToError:
                posssiblySafeDueToErrorInInning += 1
            # we expect new inning to start during the next play
            # but we don't know if we encounter errors until we 
            # apply the play, so keep these vars as a cache
            if isNextHalfInning:
                DEBUG_PRINT("parseGame: isNextHalfInning")
                inningEndedPriorPlay = True
                gameCpyNext = deepcopy(game)
                nextSavePtI = i

            # since we are sure that starting a fresh inning does not '
            # misalign roster, we can reset vars 
            elif inningEndedPriorPlay:
                #cur.execute("COMMIT")
                #cur.execute("BEGIN")
                DEBUG_PRINT("parseGame: inningEndedPriorPlay")
                replayAttempt = 0
                inningEndedPriorPlay = False
                idx = 2*(game.inning-1) + (game.inningHalf == "B")
                gameCpyBeginInning[idx] = gameCpyNext
                IBeginInning[idx] = nextSavePtI                
                posssiblySafeDueToErrorInInning = 0
                if posssiblySafeDueToError:
                    posssiblySafeDueToErrorInInning = 1
            
        elif type(evt) == type(SubEvent()):
            if game.applySub(evt):
                return True
        elif type(evt) == type(PlayerAdjEvent()):
            game.applyPlayerAdj(evt)
        elif type(evt) == type(LineupAdjEvent()):
            game.applyLineupAdj(evt)
        elif type(evt) == type(DataEREvent()):
            game.applyDataER(evt)
        elif type(evt) == type(ComEvent()):
            coms_play.append((prevPlayID, evt.event_id))

        i += 1
    
    t1 = time.time()
    dt = t1 - tStart
    #print(f"apply plays took {dt*1000} ms")
    try:
        game.compileGameStats(cur)
    except KeyboardInterrupt as e:
        exit(1)
    except Exception as e:
        print(e)

    for c in coms_play:
        stmt = "INSERT INTO game_situation_coms VALUES("
        stmt += str(gameID) + ", " + str(c[0]) + ", " + str(c[1]) + ")"
        # cur.execute(stmt)
        sqlStmts.append(stmt)


    #game.finalize(cur)
    sqlStmts.extend(game.SQLstmts)

    #compareStatsToBoxScore(game, htbf, conn, cur)
    
    #try:
    
    #except Exception as e:
    #    DEBUG_PRINT(e)
    #    return True
    
    return False

def parseEventOutcomesGatherStats(conn, cur, gameRange=[0, 200000], quit_on_err=True, reparse=False):
    whereClause = ""
    lastGameID = gameRange[0]-1
    gamesPerBatch = 1000
    failed = 0
    total = 0
    failedGames = []
    stmt = f"SELECT player_num_id, player_id FROM player"
    cur.execute(stmt)
    tups2 = cur.fetchall()
    delAll = False

    for t in tups2:
        playerCodeToIDMap[t[1]] = int(t[0])
        playerIDToCodeMap[t[0]] = t[1]

    while lastGameID < gameRange[1]:
        whereClause = f"WHERE game_id BETWEEN {lastGameID} AND {lastGameID+gamesPerBatch-1}"

        stmt = f"SELECT game_id, home_team, away_team, game_date, dh_num, tiebreakbase, inn_sched, home_team_bat_first FROM game_info_view " + whereClause
        DEBUG_PRINT(stmt)
        cur.execute(stmt)
        game_info_tups = cur.fetchall()

        orderBy = " ORDER BY game_id, event_id"
        stmt = f"SELECT * FROM event_play " + whereClause + orderBy
        cur.execute(stmt)
        plays = cur.fetchall()
        stmt = f"SELECT * FROM event_start " + whereClause + orderBy
        cur.execute(stmt)
        starts = cur.fetchall()
        stmt = f"SELECT * FROM event_sub " + whereClause + orderBy
        cur.execute(stmt)
        subs = cur.fetchall()
        stmt = f"SELECT * FROM event_lineup_adj " + whereClause + orderBy
        cur.execute(stmt)
        lineupAdjs = cur.fetchall()
        stmt = f"SELECT * FROM event_player_adj " + whereClause + orderBy
        cur.execute(stmt)
        playerAdjs = cur.fetchall()
        stmt = f"SELECT * FROM event_data_er " + whereClause + orderBy
        cur.execute(stmt)
        dataER = cur.fetchall()
        stmt = f"SELECT * FROM event_com " + whereClause + orderBy
        cur.execute(stmt)
        coms = cur.fetchall()

        gameSits = set()
        if not delAll:
            stmt = f"SELECT game_id FROM game_situation " + whereClause + " ORDER BY game_id"
            cur.execute(stmt)
            for g in cur.fetchall():
                gameSits.add(g[0])

        lastGameID += gamesPerBatch
        
        plays_i = 0
        starts_i = 0
        subs_i = 0
        lineupAdjs_i = 0
        playerAdjs_i = 0
        dataER_i = 0
        coms_i = 0
        plays_i_nxt = 0
        starts_i_nxt = 0
        subs_i_nxt = 0
        lineupAdjs_i_nxt = 0
        playerAdjs_i_nxt = 0
        dataER_i_nxt = 0
        coms_i_nxt = 0

        try:
            for tup in game_info_tups:
                total += 1
                gameID = tup[0]
                if delAll:
                    deleteDBAfterEvent(gameID, -1)
                elif gameID in gameSits:
                    print(f"skipping {gameID}, already parsed")
                    continue
                while plays_i_nxt < len(plays) and plays[plays_i_nxt][0] == gameID:
                    plays_i_nxt += 1
                while starts_i_nxt < len(starts) and starts[starts_i_nxt][0] == gameID:
                    starts_i_nxt += 1
                while subs_i_nxt < len(subs) and subs[subs_i_nxt][0] == gameID:
                    subs_i_nxt += 1
                while lineupAdjs_i_nxt < len(lineupAdjs) and lineupAdjs[lineupAdjs_i_nxt][0] == gameID:
                    lineupAdjs_i_nxt += 1
                while playerAdjs_i_nxt < len(playerAdjs) and playerAdjs[playerAdjs_i_nxt][0] == gameID:
                    playerAdjs_i_nxt += 1
                while dataER_i_nxt < len(dataER) and dataER[dataER_i_nxt][0] == gameID:
                    dataER_i_nxt += 1
                while coms_i_nxt < len(coms) and coms[coms_i_nxt][0] == gameID:
                    coms_i_nxt += 1

                try:
                    err = parseGame(tup, plays[plays_i:plays_i_nxt], starts[starts_i:starts_i_nxt],
                                    subs[subs_i:subs_i_nxt], lineupAdjs[lineupAdjs_i:lineupAdjs_i_nxt],
                                    playerAdjs[playerAdjs_i:playerAdjs_i_nxt], dataER[dataER_i:dataER_i_nxt], 
                                    coms[coms_i:coms_i_nxt], conn)
                except KeyboardInterrupt as e:
                    print("broken by keyboard interrupt")
                    kbInt = True
                    break
                except Exception as e:
                    traceback.print_exc()
                    err = True
                if err:
                    print(f"failed to parse {gameID}")
                    failed += 1
                    failedGames.append((gameID, plays))
                    delFailed = True
                    while delFailed:
                        try:
                            deleteDBAfterEvent(gameID, -1)
                            delFailed = False
                        except KeyboardInterrupt as e:
                            print("broken by keyboard interrupt")
                            exit(1)
                        except Exception as e:
                            time.sleep(0.1)
                            pass

                    if quit_on_err:
                        PRINT_DEBUG_OUT()
                        exit(1)
                    #PRINT_DEBUG_OUT()
                    #print(f"parsed ", total, "before failure")
                    #exit(1)                        
                else:
                    # try to commit to DB
                    # we could get "database locked" error,
                    # so keep trying
                    uncommited = True
                    while uncommited:
                        try:
                            conn.commit()
                            uncommited = False
                        except KeyboardInterrupt as e:
                            print("broken by keyboard interrupt")
                            exit(1)
                        except Exception as e:
                            print(e)
                plays_i = plays_i_nxt
                starts_i = starts_i_nxt
                subs_i = subs_i_nxt
                lineupAdjs_i = lineupAdjs_i_nxt
                playerAdjs_i = playerAdjs_i_nxt
                dataER_i = dataER_i_nxt
                coms_i = coms_i_nxt

                # clear debugging output to save mem/CPU
                DEBUG_OUT = []  
                
            for stmt in sqlStmts:
                try:
                    cur.execute(stmt)
                except KeyboardInterrupt as e:
                    print("broken by keyboard interrupt")
                    exit(1)
                except Exception as e:
                    DEBUG_PRINT(stmt)
                    print(e)
            sqlStmts.clear()
        except KeyboardInterrupt as e:
            print("broken by keyboard interrupt")
            exit(1)
        #DEBUG_PRINT("Could not parse the following play segments:")
        #for p in batPlaysNoParse:
        #    DEBUG_PRINT(p)

        #DEBUG_PRINT("Could not parse the following games:")
        #for g in failedGames:
            #DEBUG_PRINT(g)
    
    if not reparse:
        print(f"total=", total, " failed=", failed, end=" ")
        print(f" % {100.0-failed*100.0/total:0.3}")
        return
    # attempt to reparse failed games
    reparsed = set()
    reparseSuccess = 0
    while len(failedGames) > 0 and not quit_on_err:
        reparseSuccess = 0
        for g in failedGames:
            if gameID in reparsed:
                continue
            gameID = g[0]
            plays = g[1]
            print(f"reparse game {gameID}")
            try:
                err = parseGame(gameID, plays, conn)
            except KeyboardInterrupt as e:
                print("broken by keyboard interrupt")
                exit(1)
            except Exception as e:
                traceback.print_exc()
                err = True
            if err:
                print(f"failed to reparse {gameID}")
                deleteDBAfterEvent(gameID, -1)
            else:
                reparseSuccess += 1
                reparsed.add(gameID)
        # we could not successfully repase any games, so break
        if reparseSuccess == 0:
            break
        # clear debugging output to save mem/CPU
        DEBUG_OUT = []

    print("total=", total, " initial failed=", failed, f" % {100.0-failed*100.0/total:0.3}")
    print("total=", total, " final failed=", failed-reparseSuccess, f" % {100.0-(failed-reparseSuccess)*100.0/total:0.3}")

if __name__ == "__main__":
    connectPG = False
    connectSqlite = True
    useDB = connectPG or connectSqlite
    
    gameRange = (0, 200000)
    quit_on_err = False
    if len(sys.argv) > 2:
        gameRange = (int(sys.argv[1]), int(sys.argv[2]))
    if len(sys.argv) > 3:
        if sys.argv[3] in ("1", "T"):
            quit_on_err = True
    if len(sys.argv) > 4:
        if sys.argv[4] in ("1", "T"):
            DEBUG = True
    reparse = False
    if len(sys.argv) > 5:
        if sys.argv[5] in ("1", "T"):
            reparse = True
    print("gameRange", gameRange)
    print("quit_on_err", quit_on_err)
    print("debug", DEBUG)
    if connectSqlite:
        import sqlite3
        conn = sqlite3.connect("baseball.db")
        cur = conn.cursor()

    if connectPG:
        import psycopg
        # Connect to an existing database
        conn = psycopg.connect("dbname=postgres user=postgres")
        cur = conn.cursor()
    
    # stmt = f"SELECT player_id, name_last, name_other FROM player"
    # cur.execute(stmt)
    # tups = cur.fetchall()
    # for tup in tups:
    #     playerIDMap[tup[0]] = (tup[1], tup[2])

    parseEventOutcomesGatherStats(conn, cur, gameRange, quit_on_err, reparse)
    conn.close()
    print("done")