#!/usr/bin/python3

import csv
import os
import sys
from retrosheet_boxscores_to_sql import getBoxScoreData
from retrosheet_event_to_sql import processEventFiles

# parse park names, teams names from Retrosheet data
# game info and events from EVX files
baseDir = "alldata"

# convert CSV to dataase
def fromCSV(fPath, tableName, conn, rowIDFirst=False, rowIDMapField=None):    
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
        for row in rdr:
            # skip header
            if first:
                first = False
                #for v in row:
                #    header.append(v)
                #print("header=", header)
                continue
            ln = f"INSERT INTO {tableName} VALUES("
            vals = ""
            if rowIDFirst:
                vals += f"{rowNum}, "
            col = 0
            for v in row:
                vr = v
                if len(v) == 0:
                    #vals += "NULL, "
                    vals += "'', "
                else:
                    # replace single ' with two '' so we don't escape string
                    vr = v.replace("'", "''")
                    #if header[col] == "BAT.CHG":
                    #    print("BAT.CHG=", vr)
                    vals += f"'{vr}', "
                col += 1

            # build lookup table for each field
            if rowIDMapField is not None:
                v = row[rowIDMapField]
                if v in rowIDMap:
                    print(f"ERROR: fromCSV Duplicate ID v={v}")
                rowIDMap[v] = rowNum
                rowNum += 1

            vals = vals[:-2] # drop last comma
            ln += vals + ")"
            cur.execute(ln)
        conn.commit()
    return rowIDMap

def parks(conn):
    fName = "ballparks.csv"
    fPath = os.path.join(baseDir, fName)
    return fromCSV(fPath, "park", conn)

def teams(conn):
    fName = "teams.csv"
    fPath = os.path.join(baseDir, fName)

    fromCSV(fPath, "team", conn)

    # insert all-star for each league as a team
    cur = conn.cursor()

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
    return fromCSV(fPath, "player", conn)

def player_num_ids(conn):
    cur = conn.cursor()
    cur.execute("SELECT player_id FROM player")
    tups = cur.fetchall()
    player_num = 1
    for t in tups:
        player_id = t[0]
        cur.execute(f"INSERT INTO player_num_id VALUES({player_num}, '{player_id}')")
        player_num += 1

if __name__ == "__main__":
    connectPG = False
    connectSqlite = True
    useDB = connectPG or connectSqlite
    writeFiles = False
    startYear = 1871
    endYear = 2023
    if len(sys.argv) > 1:
        startYear = int(sys.argv[1])
    if len(sys.argv) > 2:
        endYear = int(sys.argv[2])

    if connectSqlite:
        import sqlite3
        conn = sqlite3.connect("baseball.db")

    if connectPG:
        import psycopg
        # Connect to an existing database
        conn = psycopg.connect("dbname=postgres user=postgres")

    cur = conn.cursor()
    idxs = (("event_play_idx", "event_play(game_id)"),
            ("event_start_idx", "event_start(game_id)"),
            ("event_sub_idx", "event_sub(game_id)"),
            ("game_info_idx", "game_info(game_id)"),
            ("game_info_home_idx", "game_info(home_team)"),
            ("game_info_away_idx", "game_info(away_team)"),
            ("player_num_id_idx", "player_num_id(player_num_id)"))
    for idx in idxs:
        try:
            cur.execute(f"DROP INDEX {idx[0]}")    
        except:
            pass
    teams(conn)
    parks(conn)
    players(conn)
    player_num_ids(conn)
    processEventFiles(startYear, endYear, conn, True)
    print("creating indices")
    # these indices significantly speeds up parsing event outcomes
    # also helps in later view joins when querying on specific params (e.g. team name)
    for idx in idxs:
        cur.execute(f"CREATE INDEX {idx[0]} ON {idx[1]}")
    #getBoxScoreData(startYear, endYear, conn, True)
    #if endYear > 1968:
    #    endYear = 1968
    #getPlayerStats(startYear, endYear, gameIDMap, playerIDMap, conn, cur, True)
    
    conn.commit()
    conn.close()
