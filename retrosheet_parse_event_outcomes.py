#!/usr/bin/python3

import sys
import re
import traceback
from random import randint
from copy import deepcopy

# global
playerIDMap = dict()
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

FIELD_POS_NUM = list(map(str, range(1, 10)))

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
                "9M":"9", "9LM":"9", "9LMF":"9"
                }

playCodeMap = {"S": "single", "D":"double", "CI":"catcher interference", 
               "DGR":"ground rule double", "T":"triple", "HR":"home run", 
               "WP":"wild pitch", "BB":"walk", "FC":"fielders choice", "PB":"pass ball",
               "E":"error", "O":"out", "HBP":"hit by pitch", "IBB":"intentional walk",
               "K":"strikeout", "SB":"stolen base", "CS":"caught stealing", "BK":"balk",
               "PO":"pick off", "POE":"pick off error", "OA":"other advance",
               "DI":"defensive indifference", "NP":"(no play)", }

# retro sheet to play code for certainp lays
RStoPlayCodeMap = {"W": "BB", "I":"IBB", "IW":"IBB", "HP":"HBP", "WP":"WP", 
                   "PB":"PB", "K":"K", "DI":"DI", "OA":"OA", "NP":"NP", "BK":"BK",
                   "C":"CI"}

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

for m in list(modCodeMap.keys()):
    modCodeMap[m + "!"] = modCodeMap[m]
    modCodeMap[m + "#"] = modCodeMap[m]
    modCodeMap[m + "?"] = modCodeMap[m]
    modCodeMap[m + "+"] = modCodeMap[m]
    modCodeMap[m + "-"] = modCodeMap[m]

batPlaysNoParse = []
runPlaysNoParse = []

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
            if "-" in adv: # safe
                isSafe = True
                a = adv.split("-")
            elif "X" in adv:  # out
                isSafe = False
                a = adv.split("X")
            else:
                DEBUG_PRINT("no valid separator found")
                return True
            if len(a) != 2:
                DEBUG_PRINT("len(a) != 2")
                return True
            srcBase = a[0]
            dstBase = a[1][0]
            mods = a[1][1:]
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
                if not possiblySafeDueToError:
                    self.run.out.append(srcBase)
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
                if grps[2] is not None:
                    DEBUG_PRINT("CS/POCS/PO grps[2]=", grps[2])
                    # error on play
                    e_m = re.fullmatch(r"(.*)E(\d).*", grps[2])
                    if e_m is not None:
                        self.fielding.errors.append(int(e_m.group(2)))
                        self.possiblySafeDueToError = True
                        return False, result, base, m_end
                    
                    self.getFielderPOA(grps[2])
                b = baseNumForPOCS(base, result)
                self.run.out.append(b)
                return False, result, base, m_end
            # base hit/single/double/triple S,D,or T followed by single digit (optional)
            m = re.match(r"^([SDT])(\d)?[#!?+-]?", bat0)
            if m is not None:
                DEBUG_PRINT("hit")  
                if m.group(2) is not None:
                    self.fielding.fielded.append(int(m.group(2)))
                return False, m.group(1), None, m.end()
            # home run (possibly inside the park)
            m = re.match(r"^HR?(\d)?[#!?+-]?", bat0)
            if m is not None:
                DEBUG_PRINT("home run")
                if m.group(1) is not None:
                    self.bat.hit_loc = m.group(1)
                return False, "HR", None, m.end()
            # error (fielding or catch)
            m = re.match(r"^(\d)?[#!?]?E(\d)[#!?+-]?", bat0)
            if m is not None:
                grps = m.groups()
                if grps[0] is not None:
                    DEBUG_PRINT("error - catch")
                    self.fielding.fielded.append(int(grps[0]))
                else:
                    DEBUG_PRINT("fielding error")
                self.fielding.errors.append(int(grps[1]))
                return False, "E", None, m.end()
            
            # more complciated play need to come first
            # since we are not doing fullmatch and less complicated plays woule
            # match this pattern

            # triple play, ball caught and runners doubled up and/or tagged out
            m = re.match(r"^(\d).?\(B\)(.*)\(([123H])\)(.*)\(([123H])\)(\d.)?", bat0)
            if m is not None:
                DEBUG_PRINT("triple play")
                grps = m.groups()
                self.run.out.append(grps[2])
                self.run.out.append(grps[4])
                return False, "O", None, m.end()
            
            # triple play - ground ball, forceout, implied runner out at first
            m = re.match(r"^(\d.*)\(([123H])\)(\d.+)\(([123H])\)(\d.?)", bat0)
            if m is not None:
                DEBUG_PRINT("triple play")
                grps = m.groups()
                self.run.out.append(grps[1])
                self.run.out.append(grps[3])
                return False, "O", None, m.end()
            
            # double play, either ball caught, runner tagged out
            # or force at first followed by tag of other runner 
            m = re.match(r"^(\d.*)\(B\)(\d.*)\(([123H])\)", bat0)
            if m is not None:
                DEBUG_PRINT("double play")
                grps = m.groups()
                self.run.out.append(grps[2])
                return False, "O", None, m.end()
            
            # double play - implied runner out at first
            m = re.match(r"^(\d.*)\(([123H])\)(\d.?)", bat0)
            if m is not None:
                DEBUG_PRINT("double play - runner out at first")
                grps = m.groups()
                self.run.out.append(grps[1])
                return False, "O", None, m.end()
            
            # force out (single out) to bag other than first 
            m = re.match(r"^(\d.*)\(([123H])\)", bat0)
            if m is not None:
                DEBUG_PRINT("force out")
                grps = m.groups()
                self.run.out.append(int(grps[1]))
                return False, "FO", None, m.end()
            
            # generic fielding out
            m = re.match(r"^(\d.*)", bat0)
            if m is not None:
                DEBUG_PRINT("generic out")
                return False, "O", None, m.end()
            
            # fielders choice / defensive indifference / other advance
            m = re.match(r"^(FC|DI|OA)(\d)?[#!?+-]?", bat0)  
            if m is not None:
                DEBUG_PRINT("fielders choice/DI/OA")
                return False, m.group(1), m.group(2), m.end()
            
            # ground rule double
            if bat0 == "DGR":
                DEBUG_PRINT("ground rule double")
                #self.bat.mods.append("DGR")
                return False, "D", None, len(bat0)
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
            m = re.fullmatch(r"([GLFP])(.*)[#!?+-]", mod)
            if m is not None:
                self.bat.hit_type = m.group(1)
                self.bat.hit_loc = m.group(2)
                return False
            m = re.fullmatch(r"TH([123H])[#!?]?", mod)
            if m is not None:
                b = m.group(1)
                DEBUG_PRINT("throw to base", b)
                mods.append(("TH", b))
                return False
            m = re.fullmatch(r"R([123H])", mod)
            if m is not None:
                b = m.group(1)
                DEBUG_PRINT("relay throw to base", b)
                mods.append(("R", b))
                return False
            # error (catch or field)
            m = re.fullmatch(r"(\d)?E(\d)", mod)
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

        pID = playerIDMap[self.player_id][0]
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
                print("parseFirst: unparsed=", rest)
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
            self.game_id, self.event_id, self.inning, self.team = p[0:4]
            self.player_id, self.pitch_cnt, self.pitch_seq, self.play = p[4:]
            self.pitchSeq = None
            self.bat = Event() # dummy value
            # results (see playCodeMap)
            # more than one result is possible for e.g, double steals
            # or plays at the plate combined with steals
            self.bat.results = []
            # base paramters for each result
            self.bat.bases = []                        
            # G=ground ball, F=fly ball L=line drive, P=pop up
            self.bat.hit_type = None
            # roughly where in the field ball was hit, fielder pos
            self.bat.hit_loc = None
            self.bat.mods = []

            self.fielding = Event() # dummy value
            # fielder 
            self.fielding.errors = []
            self.fielding.putouts = []
            self.fielding.assists = []
            # situations where fielder touched ball not involved above, e.g. a base hit
            self.fielding.fielded = []  
            
            self.run = Event()
            # baserunners which were out on the play
            self.run.out = []
            # baserunner advances
            self.run.adv = []
            # mod for each advance
            self.run.mods = []
            # self.parsePitchSeq()    
            self.possiblySafeDueToError = False

class SubEvent(Event):
    def __init__(self, s=None):
        if s is not None:
            self.game_id, self.event_id, self.player_id = s[0:3]
            self.team, self.bat_pos, self.field_pos = s[3:]

class PlayerAdjEvent(Event):
    def __init__(self, p=None):
        if p is not None:
            # destructure
            self.game_id, self.event_id, self.player_id, self.adjType, self.adj = p

    def print(self):
        DEBUG_PRINT(f"**** Player adjustment: {self.player_id}  {self.adjType} {self.adj}")

class LineupAdjEvent(Event):
    def __init__(self, l=None):
        if l is not None:
            # destructure
            self.game_id, self.event_id, self.team, self.adj = l

    def print(self):
        DEBUG_PRINT(f"***** Lineup adjustment: {self.team} {self.adj}")

class DataEREvent(Event):
    def __init__(self, d=None):
        if d is not None:
            # destructure
            self.game_id, self.event_id, self.player_id, self.er = d
    
    def print(self):
        DEBUG_PRINT(f"ER: {self.player_id} {self.er}")

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
        DEBUG_PRINT(self.team, "lineup")
        for b in range(1, 10):
            p = self.battingOrder[b]
            pID = playerIDMap[p]
            fldPos = None
            for f in range(1, 10):
                if p == self.fieldPos[f]:
                    fldPos = f
                    break
            DEBUG_PRINT(b, pID, "playing", fldPos)
        DEBUG_PRINT("Pitching", playerIDMap[self.fieldPos[1]])

    
    def applySub(self, sub):
        rep_batter = None
        rep_fielder = None
        newPos = None
        DEBUG_PRINT("applySub: sub=", sub.player_id,  "bat_pos=", sub.bat_pos, " field_pos=", sub.field_pos )
        if sub.field_pos == "1":
            self.pitchersUsed.append(sub.player_id)
        if sub.bat_pos != "P":
            idx = int(sub.bat_pos)
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

    def insertIntoDB(self, cur, game_id, player_num_id, team, pos, seq):
        stmt = f"INSERT INTO player_game_fielding VALUES ({game_id}, {player_num_id}"
        stmt += f", '{team}', {pos}, {seq}, {self.IF3}, {self.PO}, {self.A}, {self.E}"
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

    def insertIntoDB(self, cur, game_id, player_num_id, team, seq):
        stmt = f"INSERT INTO player_game_pitching VALUES ({game_id}, {player_num_id}"
        stmt += f", '{team}', {seq}, {self.IP3}, {self.NOOUT}, {self.BF}, {self.H}"
        stmt += f", {self.n2B}, {self.n3B}, {self.HR}, {self.R}, {self.ER}, {self.BB}"
        stmt += f", {self.IBB}, {self.K}, {self.HBP}, {self.WP}, {self.BK}"
        stmt += f", {self.SH}, {self.SF})"
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

    def insertIntoDB(self, cur, game_id, player_num_id, team, pos, seq):
        stmt = f"INSERT INTO player_game_batting VALUES ({game_id}, {player_num_id}"
        stmt += f", '{team}', {pos}, {seq}, {self.AB}, {self.R}, {self.H}, {self.n2B}"
        stmt += f", {self.n3B}, {self.HR}, {self.RBI}, {self.SH}, {self.SF}, {self.HBP}"
        stmt += f", {self.BB}, {self.IBB}, {self.K}, {self.SB}, {self.CS}, {self.GIDP}"
        stmt += f", {self.INTF})"
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
        stmt += f" FROM boxscore WHERE game_id={gameID}"
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
    def __init__(self, batsTop, batsBot, gameID):
        self.gameID = gameID
        # score for each team
        self.score = dict()
        self.score[batsTop.team] = 0
        self.score[batsBot.team] = 0

        self.teamStats = dict()
        self.teamStats[batsTop.team] = TeamStats()
        self.teamStats[batsBot.team] = TeamStats()

        self.batsTop = batsTop
        self.batsBot = batsBot

        # map to stats by team, with last player being the current player
        self.statsBat = dict()
        self.statsBat[batsTop.team] = [[] for i in range(10)]
        self.statsBat[batsBot.team] = [[] for i in range(10)]
        self.statsField = dict()
        self.statsField[batsTop.team] = [[] for i in range(10)]
        self.statsField[batsBot.team] = [[] for i in range(10)]        
        self.statsPitch = dict()
        self.statsPitch[batsTop.team] = []
        self.statsPitch[batsBot.team] = []
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
        self.nextHalfInning()

    def nextHalfInning(self):
        # calcualte LOB (if we have started game)
        if self.inning > 0:
            lob = sum(map(lambda x: x is not None, self.baseRunners))
            self.teamStats[self.curBat.team].LOB += lob

        # teap batting in the top (usually vistor) took lead, and other team did not
        # tie or retake lead
        if self.inning >= 9 and self.inningHalf == "B":
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

        # saved game states due to spec. on errors and runner advancements
        self.savedStates = []

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
        else:
            self.teamStats[tm].PI = len(self.batsTop.pitchersUsed)
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
                DEBUG_PRINT(playerIDMap[pID][0], end=lst)
                st.print()
                i += 1
                batStats.add(st)
                #insertIntoDB(self, cur, game_id, player_num_id, team, seq, pos):
                st.insertIntoDB(cur, self.gameID, pID, tm, o, i+1)

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
                DEBUG_PRINT(playerIDMap[pID][0], end=lst)
                st.print()
                i += 1
                fieldStats.add(st)
                st.insertIntoDB(cur, self.gameID, pID, tm, o, i+1)
                
        pitchStats = PitcherStats()
        DEBUG_PRINT(tm, " pitching")
        pitchStats.printHeader()
        i = 1
        for (pID, st) in self.statsPitch[tm]:
            DEBUG_PRINT(playerIDMap[pID][0], end="")
            st.print()
            pitchStats.add(st)
            st.insertIntoDB(cur, self.gameID, pID, tm, i)
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
        self.cur_batter[self.curBat] = lAdj.adj

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
    def applyPlay(self, p, treatBaserunModErrorAsOut=False):
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
        #DEBUG_PRINT("applyPlay cur_batter=", self.cur_batter, " curBat", self.curBat.team)
        curBatterIdx = self.cur_batter[self.curBat.team]
        batterID = self.curBat.battingOrder[curBatterIdx]
        pitcherID = self.curField.fieldPos[1]  # position 1 (pitcher)
        expBat = playerIDMap[batterID][0]
        pit = playerIDMap[pitcherID][0]
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
        batterID = p.player_id
        
        # -1 = last index (current player)
        (bID, stBat) = self.statsBat[curBatTeam][curBatterIdx][-1]
        # DEBUG_PRINT(self.statsPitch[curFieldTeam])
        (pID, stPit) = self.statsPitch[curFieldTeam][-1] 
        if batterID != bID:
            stBatter = playerIDMap[batterID][0]
            DEBUG_PRINT("applyPlay: ERROR batter", stBatter, " does not match lineup", playerIDMap[bID])
            err = True
        if pitcherID != pID:
            stPitcher = playerIDMap[pitcherID][0]
            DEBUG_PRINT("applyPlay: ERROR pitcher", stPitcher, " does not match lineup", playerIDMap[pID])
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
                runner = playerIDMap[runID][0]
                DEBUG_PRINT(runner, end=" ")
        DEBUG_PRINT()
        DEBUG_PRINT("play= ", p.play)
        gs_stmt = f"INSERT INTO game_situation VALUES({gameID}, {eventID}, {batterID}"
        gs_stmt += f", {pitcherID}, {self.inning}, '{self.inningHalf}', {self.outs}"
        gs_stmt += f", {scBat}, {scField}"
        for b in self.baseRunners[1:4]:
            if b is None:
                gs_stmt +=f", NULL"
            else:
                gs_stmt +=f", {b[0]}"
        pitch_cnt = p.pitch_cnt
        if pitch_cnt == "??":
            pitch_cnt = None
        DEBUG_PRINT("results=", p.bat.results)
        DEBUG_PRINT("bases=", p.bat.bases)
        DEBUG_PRINT("mods=", p.bat.mods)
        gs_stmt += f", {valOrNULL(pitch_cnt)}, '{p.bat.results[0]}', {valOrNULL(p.bat.bases[0])}" 
        gs_stmt += f", {valOrNULL(p.bat.hit_loc)}, {valOrNULL(p.bat.hit_type)}"

        # split multiple result plays into different relation
        if len(p.bat.results) > 1:
            gs2_stmt = f"INSERT INTO game_situation_result2 VALUES({gameID}, {eventID}"
            gs2_stmt += f", {valOrNULL(p.bat.results[1])}, {valOrNULL(p.bat.bases[1])})"
            cur.execute(gs2_stmt)
        if len(p.bat.results) > 2:
            gs3_stmt = f"INSERT INTO game_situation_result3 VALUES({gameID}, {eventID}"
            gs3_stmt += f", {valOrNULL(p.bat.results[2])}, {valOrNULL(p.bat.bases[2])})"
            cur.execute(gs3_stmt)
        
        outs = 0
        runs = 0
        baseRunNxt = [None]*4  # 0 = home (batter), 1 = first, etc.
        # bases which were vacated by steals, pickoffs and caught stealing
        self.vacatedBases = [None]*4
        # base which batter should occupy
        self.batterBase = None

        def applyBaseRunResult(r2, base2):
            DEBUG_PRINT("applyBaseRunResult: r2=", r2, " base2=", base2)
            runs = 0
            if r2 in ("SB", "CS", "PO", "POCS"): # stolen base / caught stealing / pick off
                b = base2
                if b == "H":
                    b = 4
                else:
                    b = int(b)
                if r2 == "PO": # for pickoffs number is the source base
                    rn = self.baseRunners[b]
                    self.vacatedBases[b] = rn
                    self.baseRunners[b] = None
                else:
                    rn = self.baseRunners[b-1]
                    self.vacatedBases[b-1] = rn
                    self.baseRunners[b-1] = None
                if rn is None:
                    return None
                (runIdx, runnerID) = rn
                if r2 == "SB":
                    DEBUG_PRINT("stolen base", b)
                    if b == 4:
                        runs += 1
                    self.statsBat[curBatTeam][runIdx][-1][1].SB += 1
                    self.teamStats[curBatTeam].SB += 1
                    if b != 4:
                        baseRunNxt[b] = (runIdx, runnerID)
                elif r2 in ("CS", "PO", "POCS"):
                    # outs should be handled by "run.out"
                    # unless possiblySafeDueToError
                    if p.possiblySafeDueToError:
                         DEBUG_PRINT("applyBaseRunResult: CS/PO/POCS possibly safe due to error")
                         if treatBaserunModErrorAsOut:
                             DEBUG_PRINT("applyBaseRunResult: treating as out")
                             #outs += 1
                         else:
                             DEBUG_PRINT("applyBaseRunResult: treating as safe")
                             if b == 4:
                                 runs += 1
                             else:
                                 baseRunNxt[b] = (runIdx, runnerID)

                    if r2 in ("CS", "POCS"):
                        self.statsBat[curBatTeam][runIdx][-1][1].CS += 1
                        self.teamStats[curBatTeam].CS += 1
                        DEBUG_PRINT("caught stealing", b)
                    else:
                        DEBUG_PRINT("pickoff", b)
            return runs
            # end applyOtherResult

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
                outs += 1
            elif r in ("S", "D", "T", "HR"):
                stBat.AB += 1
                stBat.H += 1
                self.teamStats[curBatTeam].AB += 1
                self.teamStats[curBatTeam].H += 1
                stPit.H += 1
                if r == "S":
                    DEBUG_PRINT("single")
                    self.batterBase = 1
                elif r == "D":
                    DEBUG_PRINT("double")
                    stBat.n2B += 1
                    self.teamStats[curBatTeam].n2B += 1
                    stPit.n2B += 1
                    self.batterBase = 2                
                elif r == "T":
                    DEBUG_PRINT("triple")
                    stBat.n3B += 1
                    self.teamStats[curBatTeam].n3B += 1
                    stPit.n3B += 1
                    self.batterBase = 3                
                elif r == "HR":
                    DEBUG_PRINT("home run")
                    runs += 1
                    stBat.HR += 1
                    stBat.R += 1
                    stBat.RBI += 1
                    self.teamStats[curBatTeam].HR += 1
                    self.teamStats[curBatTeam].RBI += 1
                    stPit.HR += 1
            elif r == "BB":
                DEBUG_PRINT("walk")
                stBat.BB += 1
                self.teamStats[curBatTeam].BB += 1
                stPit.BB += 1
                self.batterBase = 1            
            elif r == "IBB":
                DEBUG_PRINT("intentional walk")
                stBat.IBB += 1
                self.teamStats[curBatTeam].IBB += 1
                stPit.IBB += 1
                self.batterBase = 1            
            elif r == "K": # strike out
                DEBUG_PRINT("strikeout")
                outs += 1
                stBat.AB += 1
                stBat.K += 1
                self.teamStats[curBatTeam].AB += 1
                self.teamStats[curBatTeam].K += 1
                stPit.K += 1
            elif r == "FO": # force out (runner(s) other than batter)
                DEBUG_PRINT("force out")
                stBat.AB += 1
                self.teamStats[curBatTeam].AB += 1
                self.batterBase = 1
            elif r == "FC": # fielders choice
                DEBUG_PRINT("fielders choice")
                stBat.AB += 1
                self.teamStats[curBatTeam].AB += 1
                self.batterBase = 1
            elif r == "BK": # balk
                DEBUG_PRINT("balk")
                stPit.BK += 1
                self.teamStats[curFieldTeam].BK += 1
                expectNextBat = False
            elif r == "HBP": # hit by pitch
                DEBUG_PRINT("hit by pitch")
                self.batterBase = 1
                self.teamStats[curBatTeam].HBP += 1
                stBat.HBP += 1
            elif r == "FLE": # error on foul ball
                DEBUG_PRINT("error on foul ball")
                expectNextBat = False           
            elif r == "POE": # pick off error
                DEBUG_PRINT("pick off error")
                expectNextBat = False
            elif r == "CI": # catcher interference
                DEBUG_PRINT("catcher interference")
                self.teamStats[curFieldTeam].CI += 1
                self.batterBase = 1
            elif r == "E":
                stBat.AB += 1
                self.teamStats[curBatTeam].AB += 1
                self.batterBase = 1
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
                oth_runs = applyBaseRunResult(r, base)
                if oth_runs is None:
                    return True, False, False
                runs += oth_runs                
            else:
                expectNextBat = False
                DEBUG_PRINT("Unknown play ", r)
                return True, False, False
            seq = 1
            for mod in mods:
                prm = None
                if type(mod) == type(tuple()):
                    prm = mod[1]
                    mod = mod[0]                    
                stmt = f"INSERT INTO game_situation_result{rNum}_mod"
                stmt += f" VALUES({gameID}, {eventID}, {seq}"
                stmt += f", {valOrNULL(mod)}, {valOrNULL(prm)})"
                DEBUG_PRINT(stmt)
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
                DEBUG_PRINT(stmt)
                cur.execute(stmt)
                seq += 1
            rNum += 1
        # END for loop

        # if error on play, not present in run.adv, 
        # may need to increment outs
        if p.possiblySafeDueToError and treatBaserunModErrorAsOut:
            outs += 1
        stmt_fldr_ass = f"INSERT INTO game_situation_fielder_assist VALUES({gameID}, {eventID}"
        stmt_fldr_po = f"INSERT INTO game_situation_fielder_putout VALUES({gameID}, {eventID}"
        stmt_fldr_err = f"INSERT INTO game_situation_fielder_error VALUES({gameID}, {eventID}"
        stmt_fldr_fld = f"INSERT INTO game_situation_fielder_fielded VALUES({gameID}, {eventID}"
        seq = 1
        for f in p.fielding.errors:
            fldr_id = self.curField.fieldPos[f]
            DEBUG_PRINT("fielding error on ", f, playerIDMap[fldr_id])
            self.statsField[curFieldTeam][f][-1][1].E += 1
            self.teamStats[curFieldTeam].E += 1
            stmt_err = stmt_fldr_err + f", {fldr_id}, {seq})"
            cur.execute(stmt_err)
            seq += 1
        seq = 1
        for f in p.fielding.putouts:
            fldr_id = self.curField.fieldPos[f]
            DEBUG_PRINT("putout for ", f, playerIDMap[fldr_id])
            self.statsField[curFieldTeam][f][-1][1].PO += 1
            self.teamStats[curFieldTeam].PO += 1
            stmt_po = stmt_fldr_po + f", {fldr_id}, {seq})"
            cur.execute(stmt_po)
            seq += 1
        seq = 1
        for f in p.fielding.assists:
            fldr_id = self.curField.fieldPos[f]
            DEBUG_PRINT("assist for ", f, playerIDMap[fldr_id])
            self.statsField[curFieldTeam][f][-1][1].A += 1
            self.teamStats[curFieldTeam].A += 1
            stmt_ass = stmt_fldr_ass + f", {fldr_id}, {seq})"
            cur.execute(stmt_ass)
            seq += 1
        seq = 1
        for f in p.fielding.fielded:
            fldr_id = self.curField.fieldPos[f]
            DEBUG_PRINT("fielded by ", f, playerIDMap[fldr_id])
            stmt_fld = stmt_fldr_fld + f", {fldr_id}, {seq})"
            cur.execute(stmt_fld)
            seq += 1
        
        basesAdv = set()
        self.possiblySafeDueToError = False
        
        def handleBaseRunners():
            runs = 0
            outs = 0
            # explicit outs not having to do with runner advances
            DEBUG_PRINT("runners out", p.run.out)
            for b in p.run.out:                
                if b not in ("B", "H"):                
                    baseRunNxt[int(b)] = None  # clear base runner
                outs += 1
            stmt_base_run = f"INSERT INTO game_situation_base_run VALUES({gameID}, {eventID}"
            strikeOutAdv = False
            for adv in p.run.adv:
                DEBUG_PRINT("adv=", adv)
                
                src = adv[0]
                # runner explicitly marked as safe, so override
                if src != "B" and int(src) in p.run.out and adv[2]:
                    DEBUG_PRINT("overriding runner ", src, " being makred as out")
                    outs -= 1
                if src == "B":
                    runnerID = batterID
                    runIdx = curBatterIdx
                    # if result of strikeout, subtract out due to strikeout
                    if p.bat.results[0] == "K":
                        outs -= 1                        
                        strikeOutAdv = True
                else:
                    src = int(src)
                    #DEBUG_PRINT(src)
                    # base could already have been vacated due to stolen base
                    if self.baseRunners[src] == None:
                        if self.vacatedBases[src] is not None:
                            (runIdx, runnerID) = self.vacatedBases[src]
                        #elif self.vacatedBases[src] is not None:
                        #    (runIdx, runnerID) = self.vacatedBases[src]
                        else:
                            DEBUG_PRINT("ERROR: Could not find runner on base", src)
                            return None
                    else:
                        (runIdx, runnerID) = self.baseRunners[src]
                basesAdv.add(src)
                    
                dst = adv[1]
                if adv[2] == "E":
                    self.possiblySafeDueToError = True
                if src == "B":
                    # clear since advance is explicit
                    self.batterBase = None

                # if we treat as out, need to increment outs
                if (adv[2] == "E" and treatBaserunModErrorAsOut):
                    outs += 1
                if dst == "H":
                    if (adv[2] == "E" and not treatBaserunModErrorAsOut) or adv[2] is True: 
                        # there are some plays where explict advance from B-H is given
                        # after a home run, perhaps due to umpire review
                        # see BAL/DET 1963/9/14
                        if src != "B" or r != "HR":
                            runs += 1
                        if adv[2] == "E":
                            DEBUG_PRINT("runner on", src, " (", playerIDMap[runnerID][0], ") treating as safe at home due to error")
                        else:
                            DEBUG_PRINT("runner on", src, " (", playerIDMap[runnerID][0], ") scored ")
                        self.statsBat[curBatTeam][runIdx][-1][1].R += 1
                        stBat.RBI += 1
                        self.teamStats[curBatTeam].RBI += 1
                    else:
                        if adv[2] == "E":
                            DEBUG_PRINT("runner on", src, " (", playerIDMap[runnerID][0], ") treating as out at home, ignoring error")
                        else:
                            DEBUG_PRINT("runner on", src, " (", playerIDMap[runnerID][0], ") out at home")

                else: # base other than home
                    dst = int(dst)                    
                    if (adv[2] == "E" and not treatBaserunModErrorAsOut) or adv[2] is True:
                        if adv[2] == "E":
                            DEBUG_PRINT("runner on", src, "treating as safe at", dst, "due to error")
                        else:
                            DEBUG_PRINT("runner on", src, "advanced to", dst)
                        baseRunNxt[dst] = (runIdx, runnerID)
                    else: # out
                        if adv[2] == "E":
                            DEBUG_PRINT("runner on", src, " (", playerIDMap[runnerID][0], ") treating as out at ", dst, ", ignoring error")
                        else:
                            DEBUG_PRINT("runner on", src, "out at", dst)
                a2 = adv[2]
                if adv[2] == "E":
                     a2 = treatBaserunModErrorAsOut
                stmt = stmt_base_run + f", '{adv[0]}', '{adv[1]}', '{a2}')"
                cur.execute(stmt)
            if self.batterBase is not None:
                baseRunNxt[self.batterBase] = (curBatterIdx, batterID)
            if len(basesAdv) > 0:
                DEBUG_PRINT("basesAdv=", basesAdv)
            for b in range(1, 4):
                rn = self.baseRunners[b]
                if rn is not None and b not in basesAdv:
                    baseRunNxt[b] = self.baseRunners[b]
                    DEBUG_PRINT("runner on", b, " does not advance")
            return runs, outs, strikeOutAdv
        
        ret = handleBaseRunners()
        if ret is None:
            return True, False, False
        rb, ob, strikeOutAdv = ret
        runs += rb
        outs += ob        
        DEBUG_PRINT("handleBaseRunners returned runs=", runs, "outs= ", outs)
        DEBUG_PRINT("possiblySafeDueToError=", self.possiblySafeDueToError)
        if isDoublePlay and outs != 2:
            DEBUG_PRINT("double play but calculated outs != 2")
            return True, self.possiblySafeDueToError, False
        if isTriplePlay and outs != 3:
            DEBUG_PRINT("triple play but calculated outs != 3")
            return True, self.possiblySafeDueToError, False

        # finish game situation statement
        gs_stmt += f", {outs}, {runs})"
        DEBUG_PRINT(gs_stmt)
        cur.execute(gs_stmt)        

        stmt_base_run_mod = f"INSERT INTO game_situation_base_run_mod VALUES({gameID}, {eventID}"
        for base_mod, adv in zip(p.run.mods, p.run.adv):
            src = adv[0]
            dst = adv[1]
            seq = 1
            for mods in base_mod:
                #DEBUG_PRINT(mods)
                if len(mods) == 0:
                    continue
                sub_mod0 = mods[0]                
                #DEBUG_PRINT("mod[0]=", sub_mod0)
                if type(sub_mod0) == type(tuple()):
                    sub_mod0_0 = sub_mod0[0]
                    stmt = stmt_base_run_mod + f", '{src}', '{dst}', '{seq}'"
                    stmt += f", '{sub_mod0[0]}', '{sub_mod0[1]}')"
                else:
                    sub_mod0_0 = sub_mod0
                    stmt = stmt_base_run_mod + f", '{src}', '{dst}', '{seq}'"
                    stmt += f", '{sub_mod0_0}', NULL)"
                cur.execute(stmt)
                stmt_base_run_sub_mod = f"INSERT INTO game_situation_base_run_sub_mod"
                stmt_base_run_sub_mod += f" VALUES({gameID}, {eventID}, '{src}', '{dst}'"
                stmt_base_run_sub_mod += f", '{seq}', '{sub_mod0_0}'"
                for sub_mod in mods[1:]:
                    DEBUG_PRINT("sub_mod=", sub_mod)
                    if type(sub_mod) == type(tuple()):
                        stmt = stmt_base_run_sub_mod + f", '{sub_mod[0]}', '{sub_mod[1]}')"
                    else:
                        stmt = stmt_base_run_sub_mod + f", '{sub_mod}', NULL)"
                    #DEBUG_PRINT(stmt)
                    cur.execute(stmt)
                seq += 1
            
        # base_src char(1),
        # base_dst char(1),
        # mod char(4),
        # prm char(2),

        self.baseRunners = baseRunNxt
        self.outs += outs
        self.score[self.curBat.team] += runs
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
        if evt.team == self.batsTop.team:
            tm = self.batsTop
        elif evt.team == self.batsBot.team:
            tm = self.batsBot

        rep_batter, (rep_fielder, newPos) = tm.applySub(evt)
        DEBUG_PRINT("applySub: rep_batter=", rep_batter, " rep_fielder= ", rep_fielder, " newPos=", newPos)
        repFielderID = None
        if rep_fielder is not None:
            # destructure
            repFielderID = playerIDMap[rep_fielder]

        subID = playerIDMap[evt.player_id]
        repBatterID = None
        if rep_batter is not None:
            repBatterID = playerIDMap[rep_batter]
        
        DEBUG_PRINT("applySub: ", tm.team, subID, " replaces ", repBatterID, " playing ", evt.field_pos, " batting", evt.bat_pos)
        if rep_fielder is not None:
            DEBUG_PRINT("    ", repFielderID, " moves to ", newPos)
        if evt.bat_pos != "P":
            stBat = self.statsBat[tm.team][int(evt.bat_pos)]
            if subID != repBatterID:
                stBat.append((evt.player_id, BatterStats()))
            else:
                DEBUG_PRINT("applySub: not appending to batting stats, replacing self (field pos change)")
        if evt.field_pos in FIELD_POS_NUM:
            stField = self.statsField[tm.team][int(evt.field_pos)]
            stField.append((evt.player_id, FielderStats()))
        if evt.field_pos == "1":  # pitcher
            stPitch = self.statsPitch[tm.team]
            stPitch.append((evt.player_id, PitcherStats()))
        
def compareStatsToBoxScore(game, htbf, conn, cur):
    for hOrV in ("home", "visiting"):
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

def deleteDBAfterEvent(gameID, savePtEventID):
    allTables = ("game_situation", "game_situation_fielder_assist",
                "game_situation_fielder_putout", "game_situation_fielder_error",
                "game_situation_fielder_fielded", "game_situation_bat_mod", 
                "game_situation_base_run", "game_situation_base_run_mod",
                "game_situation_base_run_sub_mod", "game_situation_result2",
                "game_situation_result3", "game_situation_result1_mod",
                "game_situation_result2_mod", "game_situation_result3_mod")
    
    for tbl in allTables:
        stmt =  f"DELETE FROM {tbl} WHERE game_id={gameID}"
        stmt += f" AND event_id>{savePtEventID}"
        DEBUG_PRINT(stmt)
        cur.execute(stmt)

def parseGame(gameID, plays, conn, cur):
    # detect if already parsed game
    stmt = f"SELECT * from game_situation WHERE game_id={gameID}"
    cur.execute(stmt)
    tups = cur.fetchall()    
    if len(tups) > 0:
        print(f"skipping {gameID}")
        return False

    stmt = "SELECT flags, win_pitcher, loss_pitcher, save_pitcher, gw_rbi"
    stmt += f" FROM game_info WHERE game_id={gameID}"
    cur.execute(stmt)
    flags, win_p, lose_p, save_p, gw_rbi = cur.fetchall()[0]
    htbf = bool(flags & (1 << 2))
    stmt = f"SELECT home_team, visiting_team, game_date FROM boxscore WHERE game_id={gameID}"
    cur.execute(stmt)
    home_team, away_team, game_date = cur.fetchall()[0]
    stmt = f"SELECT * FROM event_start WHERE game_id={gameID} ORDER BY event_id"
    cur.execute(stmt)
    starts = cur.fetchall()
    stmt = f"SELECT * FROM event_sub WHERE game_id={gameID} ORDER BY event_id"
    cur.execute(stmt)
    subs = cur.fetchall()

    stmt = f"SELECT * FROM event_lineup_adj WHERE game_id={gameID} ORDER BY event_id"
    cur.execute(stmt)
    lineupAdjs = cur.fetchall()

    stmt = f"SELECT * FROM event_player_adj WHERE game_id={gameID} ORDER BY event_id"
    cur.execute(stmt)
    playerAdjs = cur.fetchall()

    stmt = f"SELECT * FROM event_data_er WHERE game_id={gameID} ORDER BY event_id"
    cur.execute(stmt)
    dataER = cur.fetchall()

    DEBUG_PRINT("home= ", home_team, " away=", away_team, " date=", game_date)
    home = Lineup(home_team)
    away = Lineup(away_team)
    for st in starts:
        #DEBUG_PRINT("st=", st)
        # destructure
        game_id, event_id, player_id, team, bat_pos, field_pos = st
        
        if team == home_team:
            lineup = home
        elif team == away_team:
            lineup = away
        else:
            DEBUG_PRINT(f"parseGame ERROR: team=", team, " is neither home=", home_team, " or away=", away_team)
            return True
        pID = playerIDMap[player_id][0] 

        #DEBUG_PRINT(pID, team, " starting at ", field_pos, " batting order ", bat_pos)
        if bat_pos != "P":
            bat_pos = int(bat_pos)
            lineup.battingOrder[bat_pos] = player_id
            lineup.battingOrderStart[bat_pos] = player_id
        if field_pos != "D":
            field_pos = int(field_pos)
            lineup.fieldPos[field_pos] = player_id
        if field_pos == 1:
            lineup.pitchersUsed.append(player_id)
    # DEBUG_PRINT lineups for home/away
    away.print()
    home.print()
    
    DEBUG_PRINT(f"htbf={htbf}")
    batsTop = away
    batsBot = home
    if htbf:
        batsTop = home
        batsBot = away
    game = GameState(batsTop, batsBot, gameID)
    events = []
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

    # sort based on event ID
    events = sorted(events, key=lambda x: x.event_id)
    
    # replay attempt within half inning
    # if we 
    replayAttempt = 0  
    maxReplayAttempts = 4
    gameCpyNext = None
    gameCpyBeginInning = deepcopy(game)
    savePtI = 0
    savePtEventID = event_id 
    posssiblySafeDueToErrorInInning = 0
    defaultTreatBaserunModErrorAsOut = False
    treatBaserunModErrorAsOut = defaultTreatBaserunModErrorAsOut    
    isNextHalfInning = False
    inningEndedPriorPlay = False
    i = 0
    # treat each inning as a transaction
    #cur.execute("BEGIN")
    while i < len(events):
        evt = events[i]
        if type(evt) == type(PlayEvent()):
            if replayAttempt == 1:
                treatBaserunModErrorAsOut = not defaultTreatBaserunModErrorAsOut
            elif replayAttempt > 1:
                treatBaserunModErrorAsOut = randint(0, 1)
            ret = game.applyPlay(evt, treatBaserunModErrorAsOut)
            if ret is None:  # for no play
                i += 1
                continue
            err, posssiblySafeDueToError, isNextHalfInning = ret
            if err:
                DEBUG_PRINT(f"posssiblySafeDueToError={posssiblySafeDueToError}")
                if replayAttempt < maxReplayAttempts and posssiblySafeDueToErrorInInning > 0 or posssiblySafeDueToError:
                    DEBUG_PRINT(f"###### REPLAYING HALF INNING ######")
                    DEBUG_PRINT(f"treatBaserunModErrorAsOut={treatBaserunModErrorAsOut}")
                    # restore and replay
                    replayAttempt += 1
                    game = gameCpyBeginInning
                    i = savePtI+1
                    # treatBaserunModErrorAsOut = not treatBaserunModErrorAsOut
                    #cur.execute("ROLLBACK")
                    #cur.execute("BEGIN")
                    deleteDBAfterEvent(gameID, savePtEventID)
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
                nextSavePtEventID = evt.event_id                

            # since we are sure that starting a fresh inning does not '
            # misalign roster, we can reset vars 
            elif inningEndedPriorPlay:
                #cur.execute("COMMIT")
                #cur.execute("BEGIN")
                DEBUG_PRINT("parseGame: inningEndedPriorPlay")
                replayAttempt = 0
                treatBaserunModErrorAsOut = defaultTreatBaserunModErrorAsOut
                inningEndedPriorPlay = False
                gameCpyBeginInning = gameCpyNext
                savePtI = nextSavePtI
                savePtEventID = nextSavePtEventID
                posssiblySafeDueToErrorInInning = 0
                if posssiblySafeDueToError:
                    posssiblySafeDueToErrorInInning = 1
            
        elif type(evt) == type(SubEvent()):
            game.applySub(evt)
        elif type(evt) == type(PlayerAdjEvent()):
            game.applyPlayerAdj(evt)
        elif type(evt) == type(LineupAdjEvent()):
            game.applyLineupAdj(evt)
        elif type(evt) == type(DataEREvent()):
            game.applyDataER(evt)
        i += 1
    game.compileGameStats(cur)
    compareStatsToBoxScore(game, htbf, conn, cur)
    
    #try:
    
    #except Exception as e:
    #    DEBUG_PRINT(e)
    #    return True
    
    return False

def parseEventOutcomesGatherStats(conn, cur, gameRange=None, quit_on_err=True):
    whereClause = ""
    if gameRange is not None:
        print("gameRange= ", gameRange)
        whereClause = f"WHERE game_id >= {gameRange[0]} AND game_id <= {gameRange[1]}"
    stmt = f"SELECT * FROM event_play {whereClause} ORDER BY game_id, event_id"
    cur.execute(stmt)
    tups = cur.fetchall()
    DEBUG_PRINT("len(tups)= ", len(tups))
    plays = []
    gameID = None
    failedGames = []
    failed = 0
    total = 0
    try:
        for tup in tups:
            if tup[0] != gameID:  # new game
                if gameID != None:
                    print(f"parsing game {gameID}")
                    total += 1
                    try:
                        err = parseGame(gameID, plays, conn, cur)
                    except KeyboardInterrupt as e:
                        print("broken by keyboard interrupt")
                        break
                    except Exception as e:
                        traceback.print_exc()
                        err = True
                    if err:
                        print(f"failed to parse {gameID}")
                        failed += 1
                        failedGames.append((gameID, plays))
                        deleteDBAfterEvent(gameID, 0)
                        if quit_on_err:
                            PRINT_DEBUG_OUT()
                            break
                        #PRINT_DEBUG_OUT()
                        #print(f"parsed ", total, "before failure")
                        #exit(1)                        
                    else:
                        conn.commit()
                    # clear debugging output to save mem/CPU
                    DEBUG_OUT = []
                gameID = tup[0]
                plays = []
            plays.append(tup)
    except KeyboardInterrupt as e:
        print("broken by keyboard interrupt")
        exit(1)
    #DEBUG_PRINT("Could not parse the following play segments:")
    #for p in batPlaysNoParse:
    #    DEBUG_PRINT(p)

    #DEBUG_PRINT("Could not parse the following games:")
    #for g in failedGames:
        #DEBUG_PRINT(g)
    
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
                err = parseGame(gameID, plays, conn, cur)
            except KeyboardInterrupt as e:
                print("broken by keyboard interrupt")
                break
            except Exception as e:
                traceback.print_exc()
                err = True
            if err:
                print(f"failed to reparse {gameID}")
                deleteDBAfterEvent(gameID, 0)
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
    
    gameRange = None
    quit_on_err = True
    if len(sys.argv) > 2:
        gameRange = (int(sys.argv[1]), int(sys.argv[2]))
    if len(sys.argv) > 3:
        if sys.argv[3] in ("0", "F"):
            quit_on_err = False
    print("gameRange", gameRange)
    print("quit_on_err", quit_on_err)
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

    parseEventOutcomesGatherStats(conn, cur, gameRange, quit_on_err)
    conn.commit()
    conn.close()