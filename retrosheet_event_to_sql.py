#!/usr/bin/python3

import csv
import sys
import os

baseDir = "alldata/events"
baseDir2 = "alldata/postseason"


# fields present in EVX 
INFO_FIELDS = ( "date", "number", "type", 
                "visteam", "hometeam", "daynight",
                "usedh", "howscored", "pitches", 
                "temp", "fieldcond", "winddir", 
                "windspeed", "precip", "sky",
                "site", "attendance", "starttime", 
                "innings", "timeofgame", "oscorer",
                "umphome", "ump1b", "ump2b", "ump3b", "umplf", 
                "umprf", "wp", "lp", "save", "gwrbi")

class GameID:
    def __init__(self, v=None) -> None:
        if(v is not None):
            id = v
            self.team = id[0:3]
            self.year = int(id[3:7])
            self.month = int(id[7:9])
            self.day = int(id[9:11])
            self.num = int(id[11])

            #print(self.team, self.year, self.month, self.day, self.num)

# enumerations for GameInfo
FIELDCOND = dict()
FIELDCOND["dry"] = 1
FIELDCOND["damp"] = 2
FIELDCOND["wet"] = 3
FIELDCOND["soaked"] = 4


PRECIP = dict()
PRECIP["none"] = 1
PRECIP["drizzle"] = 2
PRECIP["rain"] = 3
PRECIP["showers"] = 4
PRECIP["snow"] = 5

SKYCOND = dict()
SKYCOND["sunny"] = 1
SKYCOND["cloudy"] = 2
SKYCOND["overcast"] = 3
SKYCOND["dome"] = 4
SKYCOND["night"] = 5

WINDDIR = dict()
WINDDIR["fromcf"] = 1
WINDDIR["fromlf"] = 2
WINDDIR["fromrf"] = 3
WINDDIR["ltor"] = 4
WINDDIR["rtol"] = 5
WINDDIR["tolf"] = 6
WINDDIR["tocf"] = 7
WINDDIR["torf"] = 8

DAYNIGHT = dict()
DAYNIGHT["day"] = 0
DAYNIGHT["night"] = 1

INFO_ENUM_DICT = dict()
INFO_ENUM_DICT["precip"] = PRECIP
INFO_ENUM_DICT["fieldcond"] = FIELDCOND
INFO_ENUM_DICT["sky"] = SKYCOND
INFO_ENUM_DICT["winddir"] = WINDDIR
INFO_ENUM_DICT["daynight"] = DAYNIGHT

def getFromMap(mp, k):
    # add new value
    if k not in mp:
        mp[k] = len(mp)
    return mp[k]
    
class GameInfo:
    def __init__(self, gameID=None, gameNumID=None) -> None:
        if gameID is not None and gameNumID is not None:
            dt = ((gameID.year-1870) << 24) + (gameID.month << 20)
            dt += (gameID.day << 13)
            self.game_datetime = dt
            
            # game num in day 0 for nomrla games, 1 or 2 for double headers
            self.game_num_type = gameID.num
            # unique numeric game id for DB
            self.gameNumID = gameNumID
            for fld in INFO_FIELDS:
                setattr(self, fld, None)
            self.starttime = 0
            self.timeofgame = 0
            self.season = 0
            self.playoff = 0
            self.daynight = 0
            self.precip = 0
            self.fieldcond = 0
            self.sky = 0
            self.winddir = 0
            self.windspeed = -1
            self.temp = -1

            self.innings = 9
            self.use_dh = False
            self.htbf = False
            self.has_pitch_cnt = False
            self.has_pitch_seq = False
            self.tiebreak_base = 0

    def add(self, vals):
        f = vals[0]
        v = vals[1]
        if f == "date":
            #self.year, self.month, self.day = v.split("/")
            ymd = v.split("/")
            self.date = "".join(ymd)
            return
        if v in ("unknown", "(none)"):
            return
        
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

    def setGameNumID(self, gameIDMap):
        # get the numeric id of the game
        gameIDMap[self.date][self.hometeam][self.number] = self.gameNumID
    
    def toSQLIns(self, playerCodeToIDMap, parkCodeToIDMap, teamCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap):
        stmt = "INSERT INTO game_info VALUES("
        
        away = teamCodeToIDMap[self.visteam]
        home = teamCodeToIDMap[self.hometeam]
        #print("home=", home, "away=", away)
        self.hometeam_id = home
        self.visteam_id = away
        game_num_type = (self.game_num_type << 6) + (self.innings << 8)
        game_dt = self.game_datetime + self.starttime
        stmt += f"{self.gameNumID}, {game_dt}, {game_num_type}"
        stmt += f", {away}, 0, {home}, 0"
        
        # set flags
        flags = self.has_pitch_cnt + (self.has_pitch_cnt << 1) + (self.htbf << 2)
        flags += (self.use_dh << 3) + (self.tiebreak_base << 4)

        # set condition
        cond = self.daynight + (self.fieldcond << 1) + (self.precip << 4)
        cond += (self.sky << 7) + (self.winddir << 10) + (self.windspeed+1)<<14
        cond += (self.temp << 20)

        park = 0
        if self.site in parkCodeToIDMap:
            park = parkCodeToIDMap[self.site]
        #print(flags, park, cond)

        stmt += f", {flags}, {park}, {self.attendance}, {cond}, {self.timeofgame}"
        

        # TODO get these from an ID map
        scorer = 0
        umphome = getFromMap(umpCodeToIDMap, self.umphome)
        ump1b = getFromMap(umpCodeToIDMap, self.ump1b)
        ump2b = getFromMap(umpCodeToIDMap, self.ump2b)
        ump3b = getFromMap(umpCodeToIDMap, self.ump3b)
        umplf = getFromMap(umpCodeToIDMap, self.umplf)
        umprf = getFromMap(umpCodeToIDMap, self.umprf)
        scorer = getFromMap(scorerCodeToIDMap, self.oscorer)
        
        stmt += f", {scorer}, {umphome}, {ump1b}, {ump2b}, {ump3b}"
        stmt += f", {umplf}, {umprf}"
        win_pitcher = 0
        if self.wp in playerCodeToIDMap:
            win_pitcher = playerCodeToIDMap[self.wp]
        
        loss_pitcher = 0
        if self.lp in playerCodeToIDMap:
            loss_pitcher = playerCodeToIDMap[self.lp]

        save_pitcher = 0
        if self.save in playerCodeToIDMap:
            loss_pitcher = playerCodeToIDMap[self.save]

        gwrbi = 0
        if self.gwrbi in playerCodeToIDMap:
            gwrbi = playerCodeToIDMap[self.gwrbi]
        stmt += f", {win_pitcher}, {loss_pitcher}, {save_pitcher}, {gwrbi})"

        return stmt
class Event:
    pass

class EventCom(Event):
    def __init__(self, vals=None) -> None:
        self.com = vals[0]

    def toSQLIns(self, game_id_event_id, gameInfo, playerIDMap):
        stmt = f"INSERT INTO event_com VALUES({game_id_event_id}, "
        stmt += "'" + self.com.replace("'", "''") + "')"
        return stmt

class EventStart(Event):
    def __init__(self, vals=None) -> None:
        if vals is not None:
            self.player_id = vals[0]
            self.player_name = vals[1]
            self.side = int(vals[2])
            self.bat_pos = int(vals[3])

            self.field_pos = int(vals[4])
            if self.field_pos == 10:  # DH
                self.field_pos = 0

    def toSQLIns(self, game_id_event_id, gameInfo, playerIDMap):
        playerID = playerIDMap[self.player_id]
        stmt = f"INSERT INTO event_start VALUES({game_id_event_id}, "
        team = gameInfo.hometeam_id
        if self.side == 0:
            team = gameInfo.visteam_id
        stmt += f"{playerID}, {team},  {self.bat_pos << 4 + self.field_pos})"
        return stmt

class EventSub(Event):
    def __init__(self, vals=None) -> None:
        self.player_id = vals[0]
        # ignore player name for how (should be in player table)
        self.side = int(vals[2])
        self.bat_pos = int(vals[3])
        self.field_pos = int(vals[4]) 
        # 11 = pinch hitter, 12 = pinch runner
        if self.field_pos == 10:  # DH
            self.field_pos = 0

        
    def toSQLIns(self, game_id_event_id, gameInfo, playerIDMap):
        stmt = f"INSERT INTO event_sub VALUES({game_id_event_id}, "
        playerID = playerIDMap[self.player_id]
        team = gameInfo.hometeam_id
        if self.side == 0:
            team = gameInfo.visteam_id
        stmt += f"{playerID}, {team}, {self.bat_pos << 4 + self.field_pos})"
        return stmt

class EventPlay(Event):
    def __init__(self, vals=None) -> None:
        self.inning = int(vals[0])
        self.side = int(vals[1])
        self.player_id = vals[2]
        self.batter_count = 31
        if vals[3] not in ("", "??"):
            try:
                self.batter_count = (int(vals[3][1]) << 2) + int(vals[3][0])
            except Exception as e:
                pass
        self.pitch_seq = vals[4]
        self.play = vals[5]

    def toSQLIns(self, game_id_event_id, gameInfo, playerIDMap):
        stmt = f"INSERT INTO event_play VALUES({game_id_event_id}, "
        playerID = playerIDMap[self.player_id]
        
        team = gameInfo.hometeam_id
        if self.side == 0:
            team = gameInfo.visteam_id
        stmt += f"{team}, {playerID}, {self.inning << 5 + self.batter_count},"
        stmt += f"'{self.pitch_seq}', '{self.play}')"
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

    def toSQLIns(self, game_id_event_id, gameInfo, playerIDMap):
        tbl = "event_player_adj"
        if self.adjType == "ladj":
            tbl = "event_lineup_adj"
        stmt = f"INSERT INTO {tbl} VALUES({game_id_event_id}, "        
        if self.adjType == "ladj":
            team = gameInfo.hometeam_id
            if self.side == 0:
                team = gameInfo.visteam_id
            stmt += f"{team}, "
        else:
            playerID = playerIDMap[self.player_id]
            adjTypes = {"badj": 0, "radj":1, "padj":2, "presadj":3}
            stmt += f"{playerID}, {adjTypes[self.adjType]}, "
        stmt += f"{ord(self.adj)})"
        
        return stmt

class EventData(Event):
    def __init__(self, vals=None) -> None:
        if vals is not None:
            self.dataType = vals[0] 
            self.player_id = vals[1]
            self.amt = int(vals[2])

    def toSQLIns(self, game_id_event_id, gameInfo, playerIDMap):
        stmt = f"INSERT INTO event_data_er VALUES({game_id_event_id}, "
        playerID = playerIDMap[self.player_id]
        stmt += f"{playerID}, {self.amt})"
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

def insertEventsIntoDB(gameInfo, gameIDMap, playerCodeToIDMap, teamCodeToIDMap,
                       parkCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap, events, conn):
    curs = conn.cursor()
    stmt = gameInfo.toSQLIns(playerCodeToIDMap, parkCodeToIDMap, teamCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap)
    curs.execute(stmt)
    event_id = 1
    for evt in events:
        #print("gameID=", gameInfo.gameNumID, "event_id=", event_id)
        game_id_event_id = (gameInfo.gameNumID << 10) + event_id
        #print("game_id_event_id=", game_id_event_id)
        stmt = evt.toSQLIns(game_id_event_id, gameInfo, playerCodeToIDMap)
        #print("insertEventsIntoDB: stmt= ", stmt)
        curs.execute(stmt)
        event_id += 1
    conn.commit()

def parseEvent(v, gameInfo, gameID, nextGameNum):
    #print(f"parseEvent: v={v}")
    evtType = v[0]
    if evtType not in EVENT_TYPE_DICT:
        #print(f"parseEvent: Unknown event type {evtType}")
        return None
    elif evtType == "info":
        if gameInfo == None:
            #print(f"parseEvent: new info")
            gameInfo = GameInfo(gameID, nextGameNum)
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

def parseEventsFromEVX(fPath, gameIDMap, playerCodeToIDMap, teamCodeToIDMap, 
                       parkCodeIDMap, umpCodeToIDMap, scorerCodeToIDMap, nextGameNum, conn):
    print(f"parseEventsFromEVX: processing file {fPath}")
    with open(fPath, "r") as fIn:
        rdr = csv.reader(fIn, delimiter=',', quotechar='"')
        gameInfo = None
        gameID = None
        evts = []
        
        for row in rdr:
            evt = parseEvent(row, gameInfo, gameID, nextGameNum)
            if type(evt) == type(GameID()):
                # insert all events from previous game
                if gameID is not None:
                    insertEventsIntoDB(gameInfo, gameIDMap, playerCodeToIDMap, teamCodeToIDMap,
                                       parkCodeIDMap, umpCodeToIDMap, scorerCodeToIDMap,
                                       evts, conn)
                gameID = evt
                gameInfo = None
                nextGameNum += 1
                #print("nextGameNum=", nextGameNum)
                evts.clear()
            elif type(evt) == type(GameInfo()):
                gameInfo = evt                
            elif evt is not None:
                evts.append(evt)
        
        # insert last record
        if gameID is not None:
            insertEventsIntoDB(gameInfo, gameIDMap, playerCodeToIDMap, teamCodeToIDMap,
                               parkCodeIDMap, umpCodeToIDMap, scorerCodeToIDMap,
                               evts, conn)
    return nextGameNum

def processEventFiles(startYear, endYear, playerCodeToIDMap, teamCodeToIDMap,
                      parkCodeToIDMap, conn, includePayoffs=True):
    #playoffs = ("wc", "dv", "lc", "ws")
    rng = list(range(startYear, endYear+1))
    #rng.extend(playoffs)
    #playoffGTMap = {"wc": "C", "dv":"D", "lc":"L", "ws":"S"}
    # map of date/hometeam/number the integer game id
    fList = os.listdir(baseDir)
    gameIDMap = dict()
    umpCodeToIDMap = dict()
    scorerCodeToIDMap = dict()
    nextGameNum = 1
    for fPath in fList:
        [fDir, fName] = os.path.split(fPath)
        [fBase, fExt] = fName.split(".")
        if fExt in ("EVA", "EVN", "EVF", "EDA", "EDN", "EDF"):
            try:
                if int(fName[0:4]) in rng:
                    #print(f"getPlayerStats: processing file {fPath}")
                    fPath2 = os.path.join(baseDir, fName)
                    
                    nextGameNum = parseEventsFromEVX(fPath2, gameIDMap, playerCodeToIDMap, teamCodeToIDMap,
                                       parkCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap, nextGameNum, conn)
            except FileNotFoundError as e:
                print(fName)
                print(e)
    # postseason
    fList = os.listdir(baseDir2)
    for fPath in fList:
        [fDir, fName] = os.path.split(fPath)
        [fBase, fExt] = fName.split(".")
        if fExt in ("EVE"):
            try:
                if int(fName[0:4]) in rng:
                    #print(f"getPlayerStats: processing file {fPath}")
                    fPath2 = os.path.join(baseDir2, fName)
                    
                    nextGameNum = parseEventsFromEVX(fPath2, gameIDMap, playerCodeToIDMap, teamCodeToIDMap,
                                       parkCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap, nextGameNum, conn)
            except FileNotFoundError as e:
                print(fName)
                print(e)
            #except ValueError:
            #    pass
    return gameIDMap