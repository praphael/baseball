#!/usr/bin/python3

import csv
import os
import re
import sys
from retrosheet_boxscores_to_sql import getBoxScoreData

# parse park names, teams names from Retrosheet data

baseDir = "alldata"

def fromCSV(fPath, tableName, writeFiles, conn, cur):
    useDB = conn is not None
    s = ""
    print(f"processing file {fPath}")
    with open(fPath, "r") as fIn:
        rdr = csv.reader(fIn, delimiter=',', quotechar='"')
        first = True
        for row in rdr:   
            if first:
                first = False
                continue # skip header
            ln = f"INSERT INTO {tableName} VALUES("
            vals = ""
            for v in row:
                if len(v) == 0:
                    vals += "NULL, "
                else:
                    v = v.replace("'", "''")
                    vals += "'" + v + "', "
            vals = vals[:-2] # drop last comma
            ln += vals + ")"
            s += ln + ";\n"
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

def parks(writeFiles, conn, cur):
    fName = "ballparks.csv"
    fPath = os.path.join(baseDir, fName)
    fromCSV(fPath, "parks", writeFiles, conn, cur)

def teams(writeFiles, conn, cur):
    fName = "teams.csv"
    fPath = os.path.join(baseDir, fName)
    fromCSV(fPath, "teams", writeFiles, conn, cur)

if __name__ == "__main__":
    connectPG = False
    connectSqlite = True
    useDB = connectPG or connectSqlite
    writeFiles = False

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
    getBoxScoreData(1871, 2022, writeFiles, conn, cur)
    conn.commit()
    conn.close()



