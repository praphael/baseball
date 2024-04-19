#!/usr/bin/python3

import csv
import os
baseDir = "alldata/boxes"

INFO_FIELDS = ("date", "number", "type", "hometeam", "visteam", "site", "starttime", "daynight",
               "innings", "tiebreaker", "usedh", "pitches", "htbf",
               "fieldcond", "precip", "sky", "temp", "winddir", "windspeed", "timeofgame",
                "attendance", "oscorer", "umphome", "ump1b", "ump2b", "ump3b", "umplf", "umprf", 
                "wp", "lp", "save", "gwrbi")

class GameID:
    def __init__(self, v=None) -> None:
        if(v is not None):
            id = v
            self.team = id[0:3]
            self.date = id[3:11]
            self.num = id[11]

    def asSQL(self):
        return self.date + ", '" + self.team + "', '" + self.num + "'"

# enumerations for GameInfo
FIELDCOND = dict()
FIELDCOND["dry"] = "D"
FIELDCOND["soaked"] = "S"
FIELDCOND["wet"] = "W"

PRECIP = dict()
PRECIP["drizzle"] = "D"
PRECIP["none"] = "N"
PRECIP["rain"] = "R"
PRECIP["showers"] = "S"
PRECIP["snow"] = "W"

SKYCOND = dict()
SKYCOND["cloudy"] = "C"
SKYCOND["dome"] = "D"
SKYCOND["night"] = "N"
SKYCOND["overcast"] = "O"
SKYCOND["sunny"] = "S"

WINDDIR = dict()
WINDDIR["fromcf"] = "FC"
WINDDIR["fromlf"] = "Fl"
WINDDIR["fromrf"] = "FR"
WINDDIR["ltor"] = "LR"
WINDDIR["rtol"] = "RT"
WINDDIR["tolf"] = "TL"
WINDDIR["tocf"] = "TC"
WINDDIR["torf"] = "TR"

DAYNIGHT = dict()
DAYNIGHT["day"] = "D"
DAYNIGHT["night"] = "N"

INFO_ENUM_DICT = dict()
INFO_ENUM_DICT["precip"] = PRECIP
INFO_ENUM_DICT["fieldcond"] = FIELDCOND
INFO_ENUM_DICT["sky"] = SKYCOND
INFO_ENUM_DICT["winddir"] = WINDDIR
INFO_ENUM_DICT["daynight"] = DAYNIGHT

class GameInfo:
    def __init__(self) -> None:
        for fld in INFO_FIELDS:
            setattr(self, fld, None)
        self.game_type = "R"
        self.htbf = True
        self.sky = "U"
        self.winddir = "U"
        self.precip = "U"
        self.fieldcond = "U"
        self.innings = 9
        self.has_pitch_cnt = False
        self.has_pitch_seq = False

    def add(self, vals):
        f = vals[0]
        v = vals[1]
        if f in INFO_FIELDS:
            if f == "date":
                #self.year, self.month, self.day = v.split("/")
                ymd = v.split("/")
                self.date = "".join(ymd)
            elif v not in ("unknown", "(none)"):
                # boolean values
                if f in ("useddh", "htbf"):
                    if v in ("true"):
                        setattr(self, f, True)
                    elif v in ("false"):
                        setattr(self, f, False)
                    else:
                        print(f"GameInfo: Unknown value for ", f, ": ", v)
                        return
                elif f in ("pitches"):
                    if v == "pitches":
                        setattr(self, "has_pitch_seq", True)
                        setattr(self, "has_pitch_cnt", True)
                    elif v == "count":
                        setattr(self, "has_pitch_seq", False)
                        setattr(self, "has_pitch_cnt", True)
                elif f == "tiebreaker":
                    if v not in ("1", "2", "3"):
                        print(f"GameInfo: Unknown value for ", f, ": ", v)
                        return
                    self.tiebreaker = v
                # integral values
                elif f in ("innings", "windspeed", "temp", "timeofgame", "attendance"):
                    try:
                        val = int(v)
                    except ValueError as e:
                        #print(f"GameInfo: failure to parse integer field ", f, ",  v=", v)
                        return
                    setattr(self, f, val)
                elif f == "starttime":  
                    # parse start time to integer (military time)
                    hr, rst = v.split(":")
                    min = rst[0:2]
                    ampm = rst[2:]
                    try:
                        hr = int(hr)
                        min = int(min)
                    except ValueError as e:
                        #print(f"GameInfo: failure to parse starttime: v=", v)
                        return
                    offset = 0
                    if ampm == "AM":
                        pass
                    elif ampm == "PM":
                        if hr < 12:
                            offset = 1200
                    else:
                        #print("GameInfo: Bad AM/PM for starttime v=", v)
                        return
                    self.starttime = offset + hr*100 + min
                elif f in INFO_ENUM_DICT:
                    en = INFO_ENUM_DICT[f]
                    if v in en:
                        setattr(self, f, en[v])
                    else:
                        print(f"GameInfo: Unknown value for ", f, ": ", v)
                else:  # generic string value
                    setattr(self, f, v)
        else:
            pass
            #print(f"GameInfo: Unknown field ", f, " v=", v)

    def getGameID(self, gameIDMap):
        # get the numeric id of the game
        return gameIDMap[self.date][self.hometeam][self.number]

    def toSQLIns(self, gameIDMap):
        stmt = "INSERT INTO game_info VALUES("
        game_id = self.getGameID(gameIDMap)
        vals = [str(game_id)]
        # start at 6th field because this info is in boxscores with 
        # game_game_number_id
        for f in INFO_FIELDS[6:]:
            v = getattr(self, f)
            if f == "pitches":
                vals.append(str(int(self.has_pitch_cnt)))
                vals.append(str(int(self.has_pitch_seq)))
            elif v is None:
                vals.append("NULL")
            elif type(v) == type(True):
                vals.append(str(int(v)))
            elif type(v) == type(""):
                # wrap string values in quotes
                vals.append("'" + v + "'")
            else:  # default (numeric type)
                vals.append(str(v))
        stmt += ", ".join(vals) + ")"
        return stmt

def makeStatLine(stats):
    s = ""
    #print("stats=", stats)
    for st in stats:
        if st == None or st == "" or st == "-1":
            s += "NULL"
        else:
            s += str(st)
        s += ", "
    s = s[:-2]
    return s

class StatLine:
   pass

class StatBattingLine(StatLine):
    def __init__(self, vals=None) -> None:
        if vals is not None:
            self.player_id = vals[0]
            self.side = vals[1]
            self.lineup = int(vals[2])
            self.seq = int(vals[3])
            self.stats = vals[4:]

    def toSQLIns(self, gameIDstr, playerIDMap, gameInfo):
        playerID = playerIDMap[self.player_id]
        team = gameInfo.hometeam
        if self.side == 1:
            team = gameInfo.visteam
        tbl = "player_game_batting"
        stmt = f"INSERT INTO {tbl} VALUES("
        stmt += gameIDstr + ", "
        stmt += str(playerID) + ", "
        stmt += "'" + team + "', "
        stmt += str(self.lineup) + ", "
        stmt += str(self.seq) + ", "
        stmt += makeStatLine(self.stats) + ")"
        return stmt

class StatPinchRunnerLine(StatLine):
    def __init__(self, vals=None) -> None:
        if vals is not None:
            self.player_id = vals[0]
            self.inning = int(vals[1])
            self.side = vals[2]            
            self.stats = vals[3:]
           
    def toSQLIns(self, gameIDstr, playerIDMap, gameInfo):
        playerID = playerIDMap[self.player_id]
        team = gameInfo.hometeam
        if self.side == 1:
            team = gameInfo.visteam
        tbl = "player_game_pinchrunning"
        stmt = f"INSERT INTO {tbl} VALUES("
        stmt += gameIDstr + ", "
        stmt += str(playerID) + ", "
        stmt += "'" + team + "', "
        stmt += str(self.inning) + ", "
        stmt += makeStatLine(self.stats) + ")"
        return stmt

class StatPinchHitterLine(StatBattingLine):
    def __init__(self, vals=None) -> None:
        if vals is not None:
            self.player_id = vals[0]
            self.inning = int(vals[1])
            self.side = vals[2]            
            self.stats = vals[3:]

    def toSQLIns(self, gameIDstr, playerIDMap, gameInfo):
        playerID = playerIDMap[self.player_id]
        team = gameInfo.hometeam
        if self.side == 1:
            team = gameInfo.visteam
        tbl = "player_game_pinchhitting"
        stmt = f"INSERT INTO {tbl} VALUES("
        stmt += gameIDstr + ", "
        stmt += str(playerID) + ", "
        stmt += "'" + team + "', "
        stmt += str(self.inning) + ", "
        stmt += makeStatLine(self.stats) + ")"
        return stmt

class StatPitchingLine(StatLine):
    def __init__(self, vals=None) -> None:
        if vals is not None:
            self.player_id = vals[0]
            self.side = vals[1]
            self.seq = int(vals[2])
            self.stats = vals[3:]

    def toSQLIns(self, gameIDstr, playerIDMap, gameInfo):
        playerID = playerIDMap[self.player_id]
        team = gameInfo.hometeam
        if self.side == 1:
            team = gameInfo.visteam
        tbl = "player_game_pitching"
        stmt = f"INSERT INTO {tbl} VALUES("
        stmt += gameIDstr + ", "
        stmt += str(playerID) + ", "
        stmt += "'" + team + "', "
        stmt += str(self.seq) + ", "
        stmt += makeStatLine(self.stats) + ")"
        return stmt

class StatFieldingLine(StatLine):
    def __init__(self, vals=None) -> None:
        if vals is not None:
            self.player_id = vals[0]
            self.side = vals[1]
            self.seq = int(vals[2])
            self.pos = int(vals[3])
            self.stats = vals[4:]

    def toSQLIns(self, gameIDstr, playerIDMap, gameInfo):
        playerID = playerIDMap[self.player_id]
        team = gameInfo.hometeam
        if self.side == 1:
            team = gameInfo.visteam
        #print("player_id:", self.player_id, " playerID:", playerID, " team:", team)

        tbl = "player_game_fielding"
        stmt = f"INSERT INTO {tbl} VALUES("
        stmt += gameIDstr + ", "
        stmt += str(playerID) + ", "
        stmt += "'" + team + "', "
        stmt += str(self.pos) + ", "
        stmt += str(self.seq) + ", "
        stmt += makeStatLine(self.stats) + ")"
        return stmt

STAT_TYPE_DICT = dict()
STAT_TYPE_DICT["id"] = GameID
STAT_TYPE_DICT["info"] = GameInfo
STAT_TYPE_DICT["stat"] = {"bline": StatBattingLine, 
                          "dline": StatFieldingLine,
                          "pline": StatPitchingLine,
                          "prline": StatPinchRunnerLine,
                          "phline": StatPinchHitterLine}

EVENT_FIELDS = ("id", "info", "stat")

def insertStatsIntoDB(gameInfo, gameIDMap, playerIDMap, stats, conn, curs):
    gameIDstr = str(gameInfo.getGameID(gameIDMap))
    stmt = gameInfo.toSQLIns(gameIDMap)
    #print("insertStatsIntoDB: gameInfo stmt= ", stmt)
    curs.execute(stmt)
    for st in stats:
        stmt = st.toSQLIns(gameIDstr, playerIDMap, gameInfo)
        try:
            curs.execute(stmt)
        except Exception as e:
            print(e)
            print("insertStatsIntoDB: stmt= ", stmt)
        
    conn.commit()

def parseStat(v, gameInfo):
    #print(f"parseStat: v={v}")
    statType = v[0]
    if statType not in STAT_TYPE_DICT:
        #print(f"parseStat: Unknown type {statType}")
        return None
    elif statType == "info":
        if gameInfo == None:
            #print(f"parseStat: new info")
            gameInfo = GameInfo()
        gameInfo.add(v[1:])
        return gameInfo
    elif statType == "id":
        #print(f"parseStat: new game")
        return GameID(v[1])
    elif statType == "stat":
        line = v[1]
        #print(f"parseStat: line=", line)
        d = STAT_TYPE_DICT[statType]
        if line in d:
            st = d[line](v[2:])
            return st
    return None

def parseStatsFromEBX(fPath, gameIDMap, playerIDMap, conn, curs):
    print(f"parseStatsFromEBX: processing file {fPath}")
    with open(fPath, "r") as fIn:
        rdr = csv.reader(fIn, delimiter=',', quotechar='"')
        gameInfo = None
        gameID = None
        stats = []
        for row in rdr:
            st = parseStat(row, gameInfo)
            if type(st) == type(GameID()):
                # insert all events from previous game
                if gameID is not None:
                    insertStatsIntoDB(gameInfo, gameIDMap, playerIDMap, stats, conn, curs)
                gameID = st
                gameInfo = None
                stats.clear()
            elif type(st) == type(GameInfo()):
                gameInfo = st
            elif st is not None:
                stats.append(st)
        
        # insert last record
        if gameID is not None:
            insertStatsIntoDB(gameInfo, gameIDMap, playerIDMap, stats, conn, curs)

def getPlayerStats(startYear, endYear, gameIDMap, playerIDMap, conn, curs, includePayoffs=True):
    useDB = conn is not None
    
    #playoffs = ("wc", "dv", "lc", "ws")
    rng = list(range(startYear, endYear+1))
    #rng.extend(playoffs)
    #playoffGTMap = {"wc": "C", "dv":"D", "lc":"L", "ws":"S"}
    # map of date/hometeam/number the integer game id
    for f in rng:
        fNames = (f"{f}.EBA", f"{f}.EBN" )
        if f == 1914 or f == 1915:
            fNames = fNames + (f"{f}.EBF",)
        for fName in fNames:
            try:
                fPath = os.path.join(baseDir, fName)
                #print(f"getPlayerStats: processing file {fPath}")
                parseStatsFromEBX(fPath, gameIDMap, playerIDMap, conn, curs)
            except FileNotFoundError as e:
                pass

        

        

    