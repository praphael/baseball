#!/usr/bin/python3

import csv
import os
import re
import sys
from retrosheet_boxscores_to_sql import getBoxScoreData
from retrosheet_player_stats_to_sql import getPlayerStats
from retrosheet_event_to_sql import getEvents

# parse park names, teams names from Retrosheet data
baseDir = "alldata"

# convert CSV to dataase
def fromCSV(fPath, tableName, writeFiles, conn, cur, rowIDFirst=False, rowIDMapField=None):
    useDB = conn is not None
    s = ""
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
            if first:
                first = False
                #for v in row:
                #    header.append(v)
                #print("header=", header)
                continue
            ln = f"INSERT INTO {tableName} VALUES("
            vals = ""
            if rowIDFirst:
                vals += str(rowNum) + ", "
            col = 0
            for v in row:
                vr = v
                if len(v) == 0:
                    vals += "NULL, "
                else:
                    vr = v.replace("'", "''")
                    #if header[col] == "BAT.CHG":
                    #    print("BAT.CHG=", vr)
                    vals += "'" + vr + "', "
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
            s += ln + ";\n"
            #print(ln)
            if useDB:
                cur.execute(ln)
        if useDB:
            conn.commit()

    if writeFiles:
        fPath = f"{tableName}.sql"
        fout = open(fPath, "w")
        if fout is None:
            print(f"ERROR: cannot open '{fPath}' for writing")
            exit(1)
        fout.write("BEGIN;\n")
        fout.write(s)
        fout.write("COMMIT;\n")
        fout.close()

    return rowIDMap

def parks(writeFiles, conn, cur):
    fName = "ballparks.csv"
    fPath = os.path.join(baseDir, fName)
    fromCSV(fPath, "parks", writeFiles, conn, cur)

def teams(writeFiles, conn, cur):
    fName = "teams.csv"
    fPath = os.path.join(baseDir, fName)
    fromCSV(fPath, "teams", writeFiles, conn, cur)

def players(writeFiles, conn, cur):
    fName = "biofile.csv"
    fPath = os.path.join(baseDir, fName)
    return fromCSV(fPath, "player", writeFiles, conn, cur, True, 0)


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
        cur = conn.cursor()

    if connectPG:
        import psycopg
        # Connect to an existing database
        conn = psycopg.connect("dbname=postgres user=postgres")
        cur = conn.cursor()
    teams(writeFiles, conn, cur)
    parks(writeFiles, conn, cur)
    playerIDMap = players(writeFiles, conn, cur)
    gameIDMap = getBoxScoreData(startYear, endYear, writeFiles, conn, cur, True)
    #if endYear > 1968:
    #    endYear = 1968
    #getPlayerStats(startYear, endYear, gameIDMap, playerIDMap, conn, cur, True)
    getEvents(startYear, endYear, gameIDMap, playerIDMap, conn, cur, True)
    conn.commit()
    conn.close()
