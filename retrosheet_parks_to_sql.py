#!/usr/bin/python3

import csv
import os
import re
import sys

# parse park names from Retrosheet

connectPG = False
connectSqlite = False
useDB = connectPG or connectSqlite
writeFiles = True

if connectSqlite:
    import sqlite3
    conn = sqlite3.connect("baseball.db")
    cur = conn.cursor()

if connectPG:
    import psycopg
    # Connect to an existing database
    conn = psycopg.connect("dbname=postgres user=postgres")
    cur = conn.cursor()

s = ""
baseDir = "alldata"
fName = "ballparks.csv"
fPath = os.path.join(baseDir, fName)
print(f"processing file {fPath}")
with open(fPath, "r") as fIn:
    rdr = csv.reader(fIn, delimiter=',', quotechar='"')
    first = True
    for row in rdr:   
        if first:
            first = False
            continue # skip header
        ln = "INSERT INTO parks VALUES("
        vals = ""
        for v in row:
             if len(v) == 0:
                 vals += "NULL, "
             else:
                 v = v.replace("'", "''")
                 vals += "'" + v + "', "
        vals = vals[:-2] # drop last common
        ln += vals + ")"
        s += ln + ";\n"
        if useDB:
            cur.execute(ln)
    if useDB:
        conn.commit()

if writeFiles:
    fPath = f"parks.sql"
    fout = open(fPath, "w")
    if fout is None:
        print(f"ERROR: cannot open '{fPath}' for writing")
        exit(1)     
    fout.write("BEGIN;\n")           
    fout.write(s)
    fout.write("COMMIT;\n")
    fout.close()



