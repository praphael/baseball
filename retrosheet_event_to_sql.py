#!/usr/bin/python3

import csv
import sys
import os
import traceback

baseDir = "alldata/events"
baseDirPost = "alldata/postseason"
baseDirBox = "alldata/boxes"
baseDirAS = "alldata/allstar"

clickhouse = False
click_vals_gameinfo = []
click_vals_event_play = []
click_vals_event_start = []
click_vals_event_sub = []
click_vals_event_com = []
click_vals_event_plyr_adj = []
click_vals_event_lineup_adj = []
click_vals_batline = []
click_vals_fldline = []
click_vals_pitline = []


# fields present in EVX 
INFO_FIELDS = ( "date", "number", "gametype",
                "visteam", "hometeam", "daynight",
                "usedh", "howscored", "pitches", 
                "temp", "fieldcond", "winddir", 
                "windspeed", "precip", "sky",
                "site", "attendance", "starttime", 
                "innings", "timeofgame", "oscorer",
                "umphome", "ump1b", "ump2b", "ump3b", "umplf", 
                "umprf", "wp", "lp", "save", "gwrbi")


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

def getFromIDMap(v, idMap):
    if v in idMap:
        return idMap[v]
    return "NULL"

class GameID:
    def __init__(self, v=None) -> None:
        if(v is not None):
            id = v
            self.team = id[0:3]
            self.year = id[3:7]
            self.month = id[7:9]
            self.day = id[9:11]
            self.num = int(id[11])
            self.date = self.year+self.month+self.day

            #print(self.team, self.year, self.month, self.day, self.num)

# enumerations for GameInfo
FIELDCOND = dict()
FIELDCOND["dry"] = 1
FIELDCOND["damp"] = 2
FIELDCOND["wet"] = 3
FIELDCOND["soaked"] = 4
FIELDCOND_A = ["", "dry", "damp", "wet", "soaked"]

PRECIP = dict()
PRECIP["none"] = 1
PRECIP["drizzle"] = 2
PRECIP["rain"] = 3
PRECIP["showers"] = 4
PRECIP["snow"] = 5
PRECIP_A = ["", "none", "drizzle", "rain", "showers", "snow"]

SKYCOND = dict()
SKYCOND["sunny"] = 1
SKYCOND["cloudy"] = 2
SKYCOND["overcast"] = 3
SKYCOND["dome"] = 4
SKYCOND["night"] = 5
SKYCOND_A = ["", "sunny", "cloudy", "overcast", "dome", "night"]

WINDDIR = dict()
WINDDIR["fromcf"] = 1
WINDDIR["fromlf"] = 2
WINDDIR["fromrf"] = 3
WINDDIR["ltor"] = 4
WINDDIR["rtol"] = 5
WINDDIR["tolf"] = 6
WINDDIR["tocf"] = 7
WINDDIR["torf"] = 8
WINDDIR_A = ["", "fromcf", "fromlf", "fromlf", "ltor", "rtol", "tolf", "tocf", "torf"]

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
    nextScorerID = 1

    def __init__(self, gameID=None, gameNumID=None) -> None:
        if gameID is not None and gameNumID is not None:
            self.gameID = gameID
            self.game_date = (gameID.year, gameID.month, gameID.day)
            
            # game num in day 0 for nomrla games, 1 or 2 for double headers
            self.game_num = gameID.num
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
        self.site = "unkwn"

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
                if f == "windspeed" and val > 126:
                    print("windspeed", val, "> 126, truncating to 126")
                    val = 126
                if f == "temp" and val > 126:
                    print("temperature", val, "> 126, truncating to 126")
                    val = 126
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

    
    def insertIntoDB(self, cur, playerCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap, isUpdate=False):
        stmt = "INSERT INTO game_info VALUES("
        if isUpdate:
            stmt = "UPDATE game_info SET"

        away = self.visteam
        home = self.hometeam
        if self.innings not in (7, 9):
            print("Innings scheduled=" , self.innings, " ?!")
        if self.windspeed > 50:
            print("Excessive wind= ", self.windspeed, " ?!")
        if self.temp > 105:
            print("Excessive temp= ", self.temp, " ?!")

        #print("home=", home, "away=", away)
        game_num_type = (self.game_num << 6) | (self.innings << 8)
        # tiebreaker playoff games considered part of the regular season
        if self.gametype=="playoff":
            game_num_type = game_num_type | (5 << 3)
        elif self.gametype in ("wildcard", "divisionseries", "lcs", "worldseries"):
            game_num_type = game_num_type | 1
            if self.gametype == "wildcard":
                game_num_type = game_num_type | (1 << 3)
            elif self.gametype == "divisionseries":
                game_num_type = game_num_type | (2 << 3)
            elif self.gametype == "lcs":
                game_num_type = game_num_type | (3 << 3)
            elif self.gametype == "worldseries":
                game_num_type = game_num_type | (4 << 3)
        elif self.gametype not in ('regular', None):
            print(f"unknown game type '{self.gametype}'")

        dt = self.game_date
        game_date = f"'{dt[0]}-{dt[1]}-{dt[2]}'"
        year = int(dt[0])
        month = int(dt[1])
        
        # set flags
        flags = self.has_pitch_cnt | (self.has_pitch_cnt << 1) | (self.htbf << 2)
        flags = flags | (self.use_dh << 3) | (self.tiebreak_base << 4)

        # set condition
        # if self.winddir != 0:
        #     print("winddir=", self.winddir)
        # if self.sky in (2, 3):
        #     print("sky=", self.sky)
        cond = self.daynight | (self.fieldcond << 1) | (self.precip << 4)
        cond = cond | (self.sky << 7) | (self.winddir << 10) | ((self.windspeed+1)<<14)
        cond = cond | (self.temp << 21)

        park = self.site
        #print(flags, park, cond)

        if clickhouse:
            game_date = f"{dt[0]}-{dt[1]}-{dt[2]}"

            click_vals_gameinfo.append((self.gameNumID, game_date, year, month, 0, self.starttime, away, "NULL", "NULL", 0, home, "NULL", "NULL", 0))
            return None

        if isUpdate:
            stmt += f" start_time={self.starttime}, game_type_num={game_num_type}"
        else:
            # NULL values are for league/division which are not supplied 
            # leagues present in gamelogs, division TBD
            stmt += f"{self.gameNumID}, {game_date}, {year}, {month}, 0, {self.starttime}, {game_num_type}"
            stmt += f", '{away}', NULL, NULL, 0, '{home}', NULL, NULL, 0"

        if isUpdate:
            print("precip=", PRECIP_A[self.precip], "sky=", SKYCOND_A[self.sky])
            print("temp=", self.temp, "windspeed=", self.windspeed, "winddir=", WINDDIR_A[self.winddir])
            print(f"flags={flags}, cond={cond}")
            stmt += f", flags={flags}, cond={cond}"
            stmt += f", attendance={valOrNULL(self.attendance)}"
            stmt += f", game_duration_min={valOrNULL(self.timeofgame)}"
            stmt += f" WHERE game_id={self.gameNumID}"
        else:
            stmt += f", {flags}, '{park}', {valOrNULL(self.attendance)}, {cond}, {valOrNULL(self.timeofgame)}"

            umphome = getFromIDMap(self.umphome, umpCodeToIDMap)
            ump1b = getFromIDMap(self.ump1b, umpCodeToIDMap)
            ump2b = getFromIDMap(self.ump2b, umpCodeToIDMap)
            ump3b = getFromIDMap(self.ump3b, umpCodeToIDMap)
            umplf = getFromIDMap(self.umplf, umpCodeToIDMap)
            umprf = getFromIDMap(self.umprf , umpCodeToIDMap)
            scorer = getFromIDMap(self.oscorer, scorerCodeToIDMap)
            if scorer == "NULL":
                scorer = GameInfo.nextScorerID
                cur.execute(f"INSERT INTO scorer VALUES({scorer}, '{self.oscorer}', '{self.oscorer}')")
                GameInfo.nextScorerID += 1
            
            stmt += f", {scorer}, {umphome}, {ump1b}, {ump2b}, {ump3b}"
            stmt += f", {umplf}, {umprf}"
            win_pitcher = getFromIDMap(self.wp, playerCodeToIDMap)
            loss_pitcher = getFromIDMap(self.lp, playerCodeToIDMap)
            save_pitcher = getFromIDMap(self.save, playerCodeToIDMap)
            gwrbi = getFromIDMap(self.gwrbi, playerCodeToIDMap)
            stmt += f", {win_pitcher}, {loss_pitcher}, {save_pitcher}, {gwrbi})"
        cur.execute(stmt)
    
class Event:
    pass

class EventCom(Event):
    def __init__(self, vals=None) -> None:
        self.com = vals[0]

    def toSQLIns(self, game_id, event_id, gameInfo, playerCodeToIDMap):
        if clickhouse:
            click_vals_event_com.append((game_id, event_id, self.com))
            return None
        stmt = f"INSERT INTO event_com VALUES({game_id}, {event_id}, "
        stmt += "'" + self.com.replace("'", "''") + "')"
        return stmt

class EventStart(Event):
    def __init__(self, vals=None) -> None:
        if vals is not None:
            self.player_id = vals[0]
            self.player_name = vals[1]
            self.side = int(vals[2])
            self.bat_pos = int(vals[3])
            if self.bat_pos > 9:
                print("bat_pos > 10", self.bat_pos)
            self.field_pos = int(vals[4])
            if self.field_pos == 10:  # DH
                self.field_pos = 0
            if self.field_pos > 10:
                print("field_pos > 10", self.field_pos)

    def toSQLIns(self, game_id, event_id, gameInfo, playerCodeToIDMap):
        playerID = self.player_id
        stmt = f"INSERT INTO event_start VALUES({game_id}, {event_id}, "
        team = gameInfo.hometeam
        if self.side == 0:
            team = gameInfo.visteam
        if clickhouse:
            click_vals_event_start.append((game_id, event_id, team, self.bat_pos, self.field_pos))
            return None

        stmt += f"'{playerCodeToIDMap[playerID]}', '{team}', {self.bat_pos}, {self.field_pos})"

        return stmt

class EventSub(Event):
    def __init__(self, vals=None) -> None:
        self.player_id = vals[0]
        # ignore player name for how (should be in player table)
        self.side = int(vals[2])
        self.bat_pos = int(vals[3])
        if self.bat_pos > 9:
            print("bat_pos > 9", self.bat_pos)
        self.field_pos = int(vals[4]) 
        # 11 = pinch hitter, 12 = pinch runner
        if self.field_pos == 10:  # DH
            self.field_pos = 0
        if self.field_pos > 12:
            print("field_pos > 12", self.field_pos)

        
    def toSQLIns(self, game_id, event_id, gameInfo, playerCodeToIDMap):
        stmt = f"INSERT INTO event_sub VALUES({game_id}, {event_id}, "
        playerID = self.player_id
        team = gameInfo.hometeam
        if self.side == 0:
            team = gameInfo.visteam
        if clickhouse:
            click_vals_event_sub.append((game_id, event_id, team, self.bat_pos, self.field_pos))
            return None

        stmt += f"{playerCodeToIDMap[playerID]}, '{team}', {self.bat_pos}, {self.field_pos})"

        return stmt

class EventPlay(Event):
    def __init__(self, vals=None) -> None:
        self.inning = int(vals[0])
        self.side = int(vals[1])
        self.player_id = vals[2]
        self.batter_count = vals[3]
        #print("inning", self.inning)
        self.pitch_seq = vals[4]
        self.play = vals[5]

    def toSQLIns(self, game_id, event_id, gameInfo, playerCodeToIDMap):
        playerID = self.player_id
        
        team = gameInfo.hometeam
        if self.side == 0:
            team = gameInfo.visteam
        if clickhouse:
            click_vals_event_play.append((game_id, event_id, team, playerCodeToIDMap[playerID], self.inning, valOrNULL(self.batter_count), valOrNULL(self.pitch_seq), self.play))
            return None

        stmt = f"INSERT INTO event_play VALUES({game_id}, {event_id}, "
        stmt += f"'{team}', {playerCodeToIDMap[playerID]}, {self.inning}, {valOrNULL(self.batter_count)},"
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

    def toSQLIns(self, game_id, event_id, gameInfo, playerCodeToIDMap):
        tbl = "event_player_adj"
        if self.adjType == "ladj":
            tbl = "event_lineup_adj"
        stmt = f"INSERT INTO {tbl} VALUES({game_id}, {event_id}, "        
        if self.adjType == "ladj":
            team = gameInfo.hometeam
            if self.side == 0:
                team = gameInfo.visteam
            stmt += f"'{team}', "
        else:
            playerID = self.player_id
            adjTypes = {"badj": 0, "radj":1, "padj":2, "presadj":3}
            stmt += f"{playerCodeToIDMap[playerID]}, {adjTypes[self.adjType]}, "
        stmt += f"'{self.adj}')"
        if clickhouse:
            if tbl == "event_player_adj":
                click_vals_event_plyr_adj.append(())
            elif tbl == "event_lineup_adj":
                click_vals_event_lineup_adj.append(())
            return None
        return stmt

class EventData(Event):
    def __init__(self, vals=None) -> None:
        if vals is not None:
            self.dataType = vals[0] 
            self.player_id = vals[1]
            self.amt = int(vals[2])

    def toSQLIns(self, game_id, event_id, gameInfo, playerCodeToIDMap):
        playerID = self.player_id
        if clickhouse:
            click_vals_event_data.append((game_id, event_id, playerCodeToIDMap[playerID], self.amt))
            return None
        stmt = f"INSERT INTO event_data_er VALUES({game_id}, {event_id}, "
        stmt += f"{playerCodeToIDMap[playerID]}, {self.amt})"
        return stmt

class StatLine(Event):
    def __init__(self, vals=None) -> None:
        if vals is not None:
            def fn(x):
                if x == "" or x is None:
                    return 0
                return int(x)
        
            self.lineType = vals[0] 
            if self.lineType in ("btline", "ptline", "dtline", "tline"):
                self.data = list(map(fn, vals[1:]))
            elif self.lineType in ("dpline", "tpline", "hpline", "hrline", "sbline","csline"):
                self.data = list(map(fn, vals[1:]))
            else:
                self.player_id = vals[1]
                self.side = int(vals[2])
                if self.lineType == "bline":
                    self.pos = int(vals[3])
                    self.seq = fn(vals[4])
                    self.data = list(map(fn, vals[5:]))
                elif self.lineType == "pline":
                    self.seq = fn(vals[3])
                    self.data = list(map(fn, vals[4:]))
                elif self.lineType == "phline":
                    self.inning = fn(vals[3])
                    self.pos = 0
                    self.seq = 0
                    self.data = list(map(fn, vals[4:]))
                elif self.lineType == "prline":
                    self.inning = fn(vals[3])
                    self.pos = 0
                    self.seq = 0
                    self.data = list(map(fn, vals[4:]))
                elif self.lineType == "dline":
                    self.seq = fn(vals[3])
                    self.pos = fn(vals[4])
                    self.data = list(map(fn, vals[5:]))

    def toSQLIns(self, game_id, event_id, gameInfo, playerCodeToIDMap):
        # don't use team lines for now
        # because we get this data from gamelogs
        if self.lineType in ("btline", "ptline", "dtline", "tline"):
            return None
        # don't use event lines
        elif self.lineType in ("dpline", "tpline", "hpline", "hrline", "sbline","csline"):
            return None
        mp = {"phline":"player_game_batting",
              "bline":"player_game_batting",
              "dline":"player_game_fielding",
              "pline":"player_game_pitching",
              "prline":"player_game_batting"}
        stmt = f"INSERT INTO {mp[self.lineType]} VALUES({game_id}"
        team = gameInfo.hometeam
        if self.side == 0:
            team = gameInfo.visteam
        stmt += f", {playerCodeToIDMap[self.player_id]}, '{team}'"
        if self.lineType == "pline":
            stmt += f", {self.seq}, "
        else:
            stmt += f", {self.pos}, {self.seq}, "

        def fn(x):
            if x == -1 or x is None:
                return "NULL"
            return str(x)
        # pinch run lines only have r, sb, cs
        data = self.data
        if self.lineType == "prline": 
            data = [None]*17
            data[1] = self.data[0]  # r
            data[13] = self.data[1]  # sb
            data[14] = self.data[2]  # cs
        stmt += ", ".join(map(fn, data))
        stmt += ")"
        if clickhouse:
            if tbl == "player_game_batting":
                click_vals_batline.append(())
            elif tbl == "player_game_fielding":
                click_vals_fldline.append(())
            elif tbl == "player_game_pitching":
                click_vals_pitline.append(())
            return None
        
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

def insertAllIntoClickhouse(conn):
    cur = conn.cursor()

    if len(click_vals_gameinfo) > 0:
        stmt = """INSERT INTO game_info (game_id, game_date, year, month, dow,"
        start_time, game_type_num,  away_team, away_league, away_division, away_game_num,
        home_team, home_league, home_division, home_game_num, flags, park, attendance,
        cond, game_duration_min, scorer_num_id, ump_home_num_id, ump_1b_num_id,
        ump_2b_num_id, ump_3b_num_id, ump_lf_num_id, ump_rf_num_id, win_pitcher_num_id,
        loss_pitcher_num_id,save_pitcher_num_id, gw_rbi_num_id) VALUES"""
        print(click_vals_gameinfo[0])
        cur.execute(stmt, click_vals_gameinfo)

    stmt = """INSERT INTO event_play (game_id, event_id, team, player_num_id ,
    inning, batter_count, pitch_seq, play) VALUES"""
    cur.execute(stmt, click_vals_event_play)

    stmt = """ INSERT INTO event_start (game_id, event_id, player_num_id,
    team, bat_pos, field_pos) VALUES"""
    cur.execute(stmt, click_vals_event_start)

    stmt = """ INSERT INTO event_sub (game_id, event_id, player_num_id,
    team, bat_pos, field_pos) VALUES"""
    cur.execute(stmt, click_vals_event_sub)

    stmt = """ INSERT INTO event_com (game_id, event_id, com) VALUES"""
    cur.execute(stmt, click_vals_event_com)

    click_vals_gameinfo.clear()
    click_vals_event_play.clear()
    click_vals_event_start.clear()
    click_vals_event_sub.clear()
    click_vals_event_com.clear()
    click_vals_event_plyr_adj.clear()
    click_vals_event_lineup_adj.clear()
    click_vals_batline.clear()
    click_vals_fldline.clear()
    click_vals_pitline.clear()
    

def insertEventsIntoDB(gameInfo, gameIDMap, playerCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap, events, conn, isUpdate=False):
    curs = conn.cursor()
    dt = gameInfo.gameID.date
    team = gameInfo.gameID.team
    num = gameInfo.gameID.num
    doIns = True
    if dt in gameIDMap:
        if team in gameIDMap[dt]:
            if num in gameIDMap[dt][team]:
                doIns = False
    if doIns:
        gameInfo.insertIntoDB(curs, playerCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap, isUpdate)
        if dt not in gameIDMap:
            gameIDMap[dt] = dict()
        if team not in gameIDMap[dt]:
            gameIDMap[dt][team] = dict()
        gameIDMap[dt][team][num] = gameInfo.gameNumID
    # else:
    #     print("skipping gameInfo in, game already in DB")
    if isUpdate:
        # only update gameinfo for now
        return
    #print(stmt)
    event_id = 1
    for evt in events:
        #print("gameID=", gameInfo.gameNumID, "event_id=", event_id)
        game_id, event_id = (gameInfo.gameNumID, event_id)
        #print("game_id, event_id=", game_id, event_id)
        stmt = evt.toSQLIns(game_id, event_id, gameInfo, playerCodeToIDMap)
        #print("insertEventsIntoDB: stmt= ", stmt)
        if stmt is not None:
            try:
                curs.execute(stmt)
            except Exception as e:
                print("exception executing", e)
                print(e)
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
    
def parseEventsFromEVX(fPath, gameIDMap, playerCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap, nextGameNum, conn, isUpdate):
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
                if gameID is not None and not clickhouse:
                    insertEventsIntoDB(gameInfo, gameIDMap, playerCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap,
                                       evts, conn, isUpdate)
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
        if gameID is not None and not clickhouse:
            insertEventsIntoDB(gameInfo, gameIDMap, playerCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap,
                               evts, conn, isUpdate)
    return nextGameNum

def parseBox(v, gameInfo, gameID):
    #print(f"parseEvent: v={v}")
    evtType = v[0]
    if evtType == "info":
        if gameInfo == None:
            #print(f"parseEvent: new info")
            gameInfo = GameInfo(gameID, 0)
        gameInfo.add(v[1:])
        return gameInfo
    elif evtType == "id":
        #print(f"parseEvent: new game")
        return GameID(v[1])
    elif evtType == "stat":
        return StatLine(v[1:])
    elif evtType in ("start", "event", "line", "version", "com"):
        return None
    print("unknown event", evtType)
    return None

def parseBoxFromEBX(fPath, gameIDMap, playerCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap, nextGameNum, conn, isUpdate):
    print(f"parseBoxFromEBX: processing file {fPath}")
    with open(fPath, "r") as fIn:
        rdr = csv.reader(fIn, delimiter=',', quotechar='"')
        gameInfo = None
        gameID = None
        evts = []
        
        for row in rdr:
            evt = parseBox(row, gameInfo, gameID)
            if type(evt) == type(GameID()):
                # insert all events from previous game
                if gameID is not None and not clickhouse:
                    insertEventsIntoDB(gameInfo, gameIDMap, playerCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap,
                                       evts, conn, isUpdate)
                gameID = evt
                gameInfo = None
                #print("nextGameNum=", nextGameNum)
                evts.clear()
            elif type(evt) == type(GameInfo()):
                gameNumID = 0
                if gameID.date in gameIDMap:
                    if gameID.team in gameIDMap[gameID.date]:
                        if gameID.num in gameIDMap[gameID.date][gameID.team]:
                            gameNumID = gameIDMap[gameID.date][gameID.team][gameID.num]
                if gameNumID == 0:
                    gameNumID = nextGameNum
                    nextGameNum += 1
                gameInfo = evt
                gameInfo.gameNumID = gameNumID                
            elif evt is not None:
                evts.append(evt)
        
        # insert last record
        if gameID is not None and not clickhouse:
            insertEventsIntoDB(gameInfo, gameIDMap, playerCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap,
                               evts, conn, isUpdate)
    return nextGameNum    
    
def processEventFiles(startYear, endYear, conn, includePayoffs=True, isUpdate=False, clickhouseDB=False):
    clickhouse = clickhouseDB
    #playoffs = ("wc", "dv", "lc", "ws")
    rng = list(range(startYear, endYear+1))
    #rng.extend(playoffs)
    #playoffGTMap = {"wc": "C", "dv":"D", "lc":"L", "ws":"S"}
    # map of date/hometeam/number the integer game id
    fList = os.listdir(baseDir)
    fList.sort()
    gameIDMap = dict()
    umpCodeToIDMap = dict()
    scorerCodeToIDMap = dict()
    playerCodeToIDMap = dict()
    cur = conn.cursor()
    cur.execute("SELECT player_id, player_num_id FROM player")
    tups = cur.fetchall()
    for t in tups:
        playerCodeToIDMap[t[0]] = t[1]

    cur.execute("SELECT ump_id, ump_num_id FROM umpire")
    tups = cur.fetchall()
    for t in tups:
        umpCodeToIDMap[t[0]] = t[1]

    nextGameNum = 1
    for fPath in fList:
        [fDir, fName] = os.path.split(fPath)
        [fBase, fExt] = fName.split(".")
        if fExt in ("EVA", "EVN", "EVF", "EDA", "EDN", "EDF"):
            try:
                if int(fName[0:4]) in rng:
                    #print(f"getPlayerStats: processing file {fPath}")
                    fPath2 = os.path.join(baseDir, fName)
                    
                    nextGameNum = parseEventsFromEVX(fPath2, gameIDMap, playerCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap, nextGameNum, conn, isUpdate)
            except FileNotFoundError as e:
                print(fName)
                print(e)
        if clickhouse:
            insertAllIntoClickhouse(conn)
    # postseason
    fList = os.listdir(baseDirPost)
    fList.sort()
    for fPath in fList:
        [fDir, fName] = os.path.split(fPath)
        [fBase, fExt] = fName.split(".")
        if fExt in ("EVE"):
            try:
                if int(fName[0:4]) in rng:
                    #print(f"getPlayerStats: processing file {fPath}")
                    fPath2 = os.path.join(baseDirPost, fName)
                    
                    nextGameNum = parseEventsFromEVX(fPath2, gameIDMap, playerCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap, nextGameNum, conn, isUpdate)
            except FileNotFoundError as e:
                print(fName)
                print(e)
            #except ValueError:
            #    pass
            if clickhouse:
                insertAllIntoClickhouse(conn)
    
    # from box scores
    fList = os.listdir(baseDirBox)
    fList.sort()
    for fPath in fList:
        [fDir, fName] = os.path.split(fPath)
        [fBase, fExt] = fName.split(".")
        if fExt in ("EBA", "EBN"):
            try:
                if int(fName[0:4]) in rng:
                    #print(f"getPlayerStats: processing file {fPath}")
                    fPath2 = os.path.join(baseDirBox, fName)
                    
                    nextGameNum = parseBoxFromEBX(fPath2, gameIDMap, playerCodeToIDMap, umpCodeToIDMap, scorerCodeToIDMap, nextGameNum, conn, isUpdate)
            except FileNotFoundError as e:
                print(fName)
                print(e)
            #except ValueError:
            #    pass            
            if clickhouse:
                insertAllIntoClickhouse(conn)

    return gameIDMap

if __name__=="__main__":
    import sqlite3
    conn = sqlite3.connect("baseball.db")
    processEventFiles(1871, 2023, conn, True, True)