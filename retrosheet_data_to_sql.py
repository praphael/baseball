#!/usr/bin/python3

import csv
import os
import sys
from retrosheet_boxscores_to_sql import getBoxScoreData
from retrosheet_event_to_sql import processEventFiles

# parse park names, teams names from Retrosheet data
# game info and events from EVX files
baseDir = "alldata"
clickhouse = False

PLAYER_FIELDS= """player_num_id, player_id, name_last, name_first,
    name_other, birth, birth_city, birth_state, birth_country, debut,
    last_game, manager_debut, manager_last_game, coach_debut, coach_last_game,
    ump_debut, ump_last_game, death, death_city, death_state, death_country,
    bats, throws, height, weight,cemetary, cemetary_city, cemetary_state,
    cemetary_country, cemetary_note, birth_name, name_change, bat_change,
    hall_of_fame
""" 

PARK_FIELDS= """park_id, park_name, park_aka, park_city, park_state,
    park_open, park_close, park_league, notes"""

TEAM_FIELDS="""team_id, team_league, team_city, team_nickname,
    team_first, team_last"""

UMPIRE_FIELDS="""ump_num_id, ump_id, ump_name_last, ump_name_first"""

click_vals = []

# convert CSV to dataase
def fromCSV(fPath, tableName, conn, rowIDFirst=False, rowIDMapField=None, rowIDOffset=0, numericCols=set()):    
    cur = conn.cursor()
    print(f"processing file {fPath}")
    rowIDMap = None
    if rowIDMapField is not None:
        rowIDMap = dict()
    with open(fPath, "r") as fIn:
        rdr = csv.reader(fIn, delimiter=',', quotechar='"')
        first = True
        rowNum = 1
        #header = []
        ins_stmts = []
        for row in rdr:
            # skip header
            if first:
                first = False
                #for v in row:
                #    header.append(v)
                #print("header=", header)
                continue
            ln = f"INSERT INTO {tableName} VALUES("
            vals = ()
            if rowIDFirst:
                vals += (rowNum+rowIDOffset,)
            col = 0
            for v in row:
                vr = v
                if col in numericCols:
                    if vr == "":
                        vals += (0,)
                    else:
                        vals += (int(vr), )
                elif len(v) == 0:
                    vals += ('',)
                    #vals += "'', "
                else:
                    # replace single ' with two '' so we don't escape string
                    vr = v.replace("'", "''")
                    #if header[col] == "BAT.CHG":
                    #    print("BAT.CHG=", vr)
                    vals += (vr,)
                col += 1

            # build lookup table for each field
            if rowIDMapField is not None:
                v = row[rowIDMapField]
                if v in rowIDMap:
                    print(f"ERROR: fromCSV Duplicate ID v={v}")
                rowIDMap[v] = rowNum
                rowNum += 1

            #print(ln)
            if clickhouse:
                click_vals.append(vals)
            else:
                def fn(x):
                    if type(x) == type(""):
                        return "'" + x + "'"
                    elif type(x) == type(0):
                        return str(x)
                    elif x is None:
                        return "NULL"
                ins_stmts.append(ln + ", ".join(map(fn, vals)) + ")")

        for ln in ins_stmts:
            #print(ln)
            cur.execute(ln)
        conn.commit()
    return rowIDMap

def parks(conn):
    fName = "ballparks.csv"
    fPath = os.path.join(baseDir, fName)
    fromCSV(fPath, "park", conn)
    if clickhouse:
        stmt = "INSERT INTO park (" + PARK_FIELDS + ") VALUES"
        cur = conn.cursor()
        cur.execute(stmt, click_vals)
        click_vals.clear()

def teams(conn):
    fName = "teams.csv"
    fPath = os.path.join(baseDir, fName)

    fromCSV(fPath, "team", conn, numericCols={4, 5})
    cur = conn.cursor()

    if clickhouse:
        stmt = "INSERT INTO team (" + TEAM_FIELDS + ") VALUES"
        cur.execute(stmt, click_vals)
        click_vals.clear()

    # insert all-star for each league as a team

    # this team appears in boxscores but there is no info about them 
    # probably team from Baltimore
    stmt = f"INSERT INTO team VALUES('BL5', '', 'Baltimore', 'BL5', 1882, 1882)"
    cur.execute(stmt)
    # leagues = ("AL", "NL", "NA", "AA", "UA", "FL", "PL")
    # for l in leagues:
    #     team_num_id += 1
    #     team_name = l
    #     teamIDMap[team_num_id] = l
    #     stmt = f"INSERT INTO team VALUES({team_num_id}, '{l}', '', '{team_name}', '', '', '')"
    #     cur.execute(stmt)

def players(conn):
    fName = "biofile.csv"
    fPath = os.path.join(baseDir, fName)
    fromCSV(fPath, "player", conn, rowIDFirst=True, rowIDMapField=0, numericCols={23})
    if clickhouse:
        stmt = "INSERT INTO player (" + PLAYER_FIELDS + ") VALUES"
        cur = conn.cursor()
        cur.execute(stmt, click_vals)
        click_vals.clear()


def umpires(conn):
    offset = 0
    for year in range(1871, 2024):
        fName = f"UMPIRES{year}.txt"
        fPath = os.path.join(baseDir, "umpires", fName)
        umpMap = fromCSV(fPath, "umpire", conn, rowIDFirst=True, rowIDMapField=0, rowIDOffset=offset)    
        offset += len(umpMap)
    if clickhouse:
        stmt = "INSERT INTO umpire (" + UMPIRE_FIELDS + ") VALUES"
        cur = conn.cursor()
        cur.execute(stmt, click_vals)
        click_vals.clear()

if __name__ == "__main__":
    db = "sqlite"
    startYear = 1871
    endYear = 2023
    if len(sys.argv) > 1:
        db = sys.argv[1]
    if len(sys.argv) > 2:
        startYear = int(sys.argv[2])
    if len(sys.argv) > 3:
        endYear = int(sys.argv[3])

    if db == "sqlite":
        import sqlite3
        conn = sqlite3.connect("baseball.db")
    elif db == "postgres":
        import psycopg
        # Connect to an existing database
        conn = psycopg.connect("dbname=postgres user=postgres")
    elif db == "clickhouse":
        clickhouse = True
        from clickhouse_driver import Client
        client = Client(host='localhost')
        class ClickCurs:
            def __init__(self, client):
                self.client = client

            def execute(self, q, prm=None):
                #print(q)
                if prm == None:
                    self.data = self.client.execute(q)
                else:
                    self.data = self.client.execute(q, prm)

            def fetchall(self):
                return self.data
            
        class ClickConn: 
            def __init__(self, client):
                self.client = client

            def cursor(self):
                return ClickCurs(self.client)
            
            def commit(self):
                pass

        conn = ClickConn(client)

    cur = conn.cursor()

    idxs = (("event_play_idx", "event_play(game_id)"),
            ("event_start_idx", "event_start(game_id)"),
            ("event_sub_idx", "event_sub(game_id)"),
            ("event_com_idx", "event_com(game_id)"),
            ("game_info_idx", "game_info(game_id)"),            
            ("player_num_id_idx", "player(player_num_id)"),
            ("player_id_idx", "player(player_id)"))
    for idx in idxs:
        try:
            cur.execute(f"DROP INDEX {idx[0]}")    
        except:
            pass
    teams(conn)
    parks(conn)
    players(conn)
    umpires(conn)
    processEventFiles(startYear, endYear, conn, True, clickhouseDB=clickhouse)
    print("creating indices")
    # these indices significantly speeds up parsing event outcomes
    # also helps in later view joins when querying on specific params (e.g. team name)
    for idx in idxs:
        cur.execute(f"CREATE INDEX {idx[0]} ON {idx[1]}")
    #getBoxScoreData(startYear, endYear, conn, True)
    #if endYear > 1968:
    #    endYear = 1968
    #getPlayerStats(startYear, endYear, gameIDMap, playerIDMap, conn, cur, True)
    
    if db != "clickhouse":
        conn.commit()
        conn.close()
