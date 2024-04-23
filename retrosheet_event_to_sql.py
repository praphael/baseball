#!/usr/bin/python3

import csv
import sys
import os

baseDir = "alldata/events"

INFO_FIELDS = ("date", "number", "type", "hometeam", "visteam", "site",
               "starttime", "innings", "flags", "cond", "timeofgame",
                "attendance",  "oscorer", "umphome", "ump1b", "ump2b", "ump3b",
                "umplf", "umprf", "wp", "lp", "save", "gwrbi")

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
FIELDCOND["damp"] = "A"

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
        self.daynight = "U"
        self.sky = "U"
        self.winddir = "U"
        self.precip = "U"
        self.fieldcond =  "U"
        self.innings = "9"
        self.use_dh = False
        self.htbf = False
        self.windspeed = -1
        self.temp = 0
        self.has_pitch_cnt = False
        self.has_pitch_seq = False
        self.tiebreak_base = 0

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
                    self.tiebreak_base = int(v)
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
        # game_number_id
        for f in INFO_FIELDS[6:]:
            v = getattr(self, f)
            if f == "flags":
                flags = self.has_pitch_cnt & (self.has_pitch_seq << 1)
                flags = flags & (self.htbf << 2) & (self.use_dh << 3)
                flags = flags &  (self.tiebreak_base << 5)
                flags += 32 # ensure printable char
                vals.append(f"{flags}")
            elif f == "cond":
                v = self.daynight + self.fieldcond + self.precip 
                ws = str(self.windspeed)
                if len(ws) < 2:
                    ws = "0" + ws
                tmp = str(self.temp)
                if len(tmp) < 2:
                    tmp = "0" + tmp
                v += self.sky + self.winddir + ws + tmp
                vals.append(f"'{v}'")
            elif v is None:
                vals.append("NULL")
            elif type(v) == type(True):
                vals.append(str(int(v)))
            elif type(v) == type(""):
                # wrap string values in quotes
                vals.append(f"'{v}'")
            else:  # default (numeric type)
                vals.append(str(v))
        stmt += ", ".join(vals) + ")"
        return stmt

class Event:
    pass

class EventCom(Event):
    def __init__(self, vals=None) -> None:
        self.com = vals[0]

    def toSQLIns(self, event_id, gameIDstr, gameInfo, playerIDMap):
        stmt = "INSERT INTO event_com VALUES("
        stmt += gameIDstr + ","
        stmt += str(event_id) + ", "
        stmt += "'" + self.com.replace("'", "''") + "')"
        return stmt

class EventStart(Event):
    def __init__(self, vals=None) -> None:
        if vals is not None:
            self.player_id = vals[0]
            self.player_name = vals[1]
            self.side = int(vals[2])
            self.bat_pos = vals[3]
            if self.bat_pos == "0":
                self.bat_pos = "P"
            self.field_pos = vals[4]
            if self.field_pos == "10":
                self.field_pos = "D"

    def toSQLIns(self, event_id, gameIDstr, gameInfo, playerIDMap):
        playerID = playerIDMap[self.player_id]
        stmt = "INSERT INTO event_start VALUES("
        stmt += gameIDstr + ","
        stmt += str(event_id) + ", "
        team = gameInfo.hometeam
        if self.side == 0:
            team = gameInfo.visteam
        stmt += str(playerID) + ", "
        stmt += "'" + team + "', "
        stmt += "'" + "', '".join((self.bat_pos, self.field_pos)) 
        stmt += "')"
        return stmt

class EventSub(Event):
    def __init__(self, vals=None) -> None:
        self.player_id = vals[0]
        # ignore player name for how (should be in player table)
        self.side = int(vals[2])
        self.bat_pos = vals[3]
        if self.bat_pos == "0":
            self.bat_pos = "P"
        self.field_pos = vals[4]
        if self.field_pos == "10":
            self.field_pos = "D"
        if self.field_pos == "11":
            self.field_pos = "H"
        if self.field_pos == "12":
            self.field_pos = "R"
        
    def toSQLIns(self, event_id, gameIDstr, gameInfo, playerIDMap):
        stmt = "INSERT INTO event_sub VALUES("
        playerID = playerIDMap[self.player_id]
        stmt += gameIDstr + ","
        stmt += str(event_id) + ", "
        team = gameInfo.hometeam
        if self.side == 0:
            team = gameInfo.visteam
        stmt += str(playerID) + ", "
        stmt += "'" + team + "', "
        stmt += "'" + "', '".join((self.bat_pos, self.field_pos)) 
        stmt += "')"
        return stmt

class EventPlay(Event):
    def __init__(self, vals=None) -> None:
        self.inning = int(vals[0])
        self.side = int(vals[1])
        self.player_id = vals[2]
        self.batter_count = vals[3]
        self.pitch_seq = vals[4]
        self.play = vals[5]

    def toSQLIns(self, event_id, gameIDstr, gameInfo, playerIDMap):
        stmt = "INSERT INTO event_play VALUES("
        playerID = playerIDMap[self.player_id]
        stmt += gameIDstr + ","
        stmt += str(event_id) + ", "
        stmt += str(self.inning) + ", "
        team = gameInfo.hometeam
        if self.side == 0:
            team = gameInfo.visteam
        stmt += "'" + team + "', "
        stmt += str(playerID) + ", "
        stmt += "'" + "', '".join((self.batter_count, self.pitch_seq, self.play)) 
        stmt += "')"
        return stmt 

class EventAdjustment(Event):
    def __init__(self, adjType=None, vals=None) -> None:
        self.adjType = adjType
        #print(f"EventAdjustment adjType={adjType} vals={vals}")
        if vals is not None:
            if adjType == "ladj":
                self.side = int(vals[0])
            else:
                self.player_id = vals[0]
            self.adj = vals[1]

    def toSQLIns(self, event_id, gameIDstr, gameInfo, playerIDMap):
        tbl = "event_player_adj"
        if self.adjType == "ladj":
            tbl = "event_lineup_adj"
        stmt = f"INSERT INTO {tbl} VALUES("        
        stmt += gameIDstr + ","
        stmt += str(event_id) + ", "
        if self.adjType == "ladj":
            team = gameInfo.hometeam
            if self.side == 0:
                team = gameInfo.visteam
            stmt += "'" + team + "', "
        else:
            playerID = playerIDMap[self.player_id]
            stmt += str(playerID) + ", "
            stmt += "'" + self.adjType + "', "
        stmt += "'" + self.adj + "')"
        
        return stmt

class EventData(Event):
    def __init__(self, vals=None) -> None:
        if vals is not None:
            self.dataType = vals[0] 
            self.player_id = vals[1]
            self.amt = int(vals[2])

    def toSQLIns(self, event_id, gameIDstr, gameInfo, playerIDMap):
        stmt = "INSERT INTO event_data_er VALUES("
        playerID = playerIDMap[self.player_id]
        stmt += gameIDstr + ","
        stmt += str(event_id) + ", "
        stmt += str(playerID) + ", "
        stmt += str(self.amt) + ")"
        return stmt

EVENT_TYPE_DICT = dict()
EVENT_TYPE_DICT["id"] = GameID
EVENT_TYPE_DICT["info"] = GameInfo
EVENT_TYPE_DICT["com"] = EventCom
EVENT_TYPE_DICT["play"] = EventPlay
EVENT_TYPE_DICT["start"] = EventStart
EVENT_TYPE_DICT["sub"] = EventSub
EVENT_TYPE_DICT["data"] = EventData
EVENT_TYPE_DICT["badj"] = EventAdjustment
EVENT_TYPE_DICT["radj"] = EventAdjustment
EVENT_TYPE_DICT["ladj"] = EventAdjustment
EVENT_TYPE_DICT["padj"] = EventAdjustment
EVENT_TYPE_DICT["presadj"] = EventAdjustment

def insertEventsIntoDB(gameInfo, gameIDMap, playerIDMap, events, conn, curs):
    gameIDstr = str(gameInfo.getGameID(gameIDMap))
    stmt = gameInfo.toSQLIns(gameIDMap)
    #print("insertStatsIntoDB: gameInfo stmt= ", stmt)
    curs.execute(stmt)
    event_id = 1
    for evt in events:
        stmt = evt.toSQLIns(event_id, gameIDstr, gameInfo, playerIDMap)
        try:
            curs.execute(stmt)
        except Exception as e:
            print(e)
            print("insertEventsIntoDB: stmt= ", stmt)
        event_id += 1
    conn.commit()

def parseEvent(v, gameInfo):
    #print(f"parseEvent: v={v}")
    evtType = v[0]
    if evtType not in EVENT_TYPE_DICT:
        #print(f"parseEvent: Unknown event type {evtType}")
        return None
    elif evtType == "info":
        if gameInfo == None:
            #print(f"parseEvent: new info")
            gameInfo = GameInfo()
        gameInfo.add(v[1:])
        return gameInfo
    elif evtType == "id":
        #print(f"parseEvent: new game")
        return GameID(v[1])
    else:
        if v[0] in ("ladj", "padj", "badj", "radj", "presadj"):
            evt = EVENT_TYPE_DICT[evtType](v[0], v[1:])
        else:
            evt = EVENT_TYPE_DICT[evtType](v[1:])
        return evt

def parseEventsFromEVX(fPath, gameIDMap, playerIDMap, conn, curs):
    print(f"parseEventsFromEVX: processing file {fPath}")
    with open(fPath, "r") as fIn:
        rdr = csv.reader(fIn, delimiter=',', quotechar='"')
        gameInfo = None
        gameID = None
        evts = []
        for row in rdr:
            evt = parseEvent(row, gameInfo)
            if type(evt) == type(GameID()):
                # insert all events from previous game
                if gameID is not None:
                    insertEventsIntoDB(gameInfo, gameIDMap, playerIDMap, evts, conn, curs)
                gameID = evt
                gameInfo = None
                evts.clear()
            elif type(evt) == type(GameInfo()):
                gameInfo = evt
            elif evt is not None:
                evts.append(evt)
        
        # insert last record
        if gameID is not None:
            insertEventsIntoDB(gameInfo, gameIDMap, playerIDMap, evts, conn, curs)

def getEvents(startYear, endYear, gameIDMap, playerIDMap, conn, curs, includePayoffs=True):
    #playoffs = ("wc", "dv", "lc", "ws")
    rng = list(range(startYear, endYear+1))
    #rng.extend(playoffs)
    #playoffGTMap = {"wc": "C", "dv":"D", "lc":"L", "ws":"S"}
    # map of date/hometeam/number the integer game id
    fList = os.listdir(baseDir)
    for fPath in fList:
        [fDir, fName] = os.path.split(fPath)
        [fBase, fExt] = fName.split(".")
        if fExt in ("EVA", "EVN", "EVF", "EDA", "EDN", "EDF"):
            try:
                if int(fName[0:4]) in rng:
                    #print(f"getPlayerStats: processing file {fPath}")
                    fPath = os.path.join(baseDir, fName)
                    parseEventsFromEVX(fPath, gameIDMap, playerIDMap, conn, curs)
            except FileNotFoundError:
                pass
            except ValueError:
                pass