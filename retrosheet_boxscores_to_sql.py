#!/usr/bin/python3

import csv
import os
import re
import sys

# parse boxscores from Retrosheet data

# Field(s)  Meaning
#     1     Date in the form "yyyymmdd"
#     2     Number of game:
#              "0" -- a single game
#              "1" -- the first game of a double (or triple) header
#                     including seperate admission doubleheaders
#              "2" -- the second game of a double (or triple) header
#                     including seperate admission doubleheaders
#              "3" -- the third game of a triple-header
#              "A" -- the first game of a double-header involving 3 teams
#              "B" -- the second game of a double-header involving 3 teams
#     3     Day of week  ("Sun","Mon","Tue","Wed","Thu","Fri","Sat")
#   4-5     Visiting team and league
#     6     Visiting team game number
#           For this and the home team game number, ties are counted as
#           games and suspended games are counted from the starting
#           rather than the ending date.
#   7-8     Home team and league
#     9     Home team game number
# 10-11     Visiting and home team score (unquoted)
#    12     Length of game in outs (unquoted).  A full 9-inning game would
#           have a 54 in this field.  If the home team won without batting
#           in the bottom of the ninth, this field would contain a 51.
#    13     Day/night indicator ("D" or "N")
#    14     Completion information.  If the game was completed at a
#           later date (either due to a suspension or an upheld protest)
#           this field will include:
#              "yyyymmdd,park,vs,hs,len" Where
#           yyyymmdd -- the date the game was completed
#           park -- the park ID where the game was completed
#           vs -- the visitor score at the time of interruption
#           hs -- the home score at the time of interruption
#           len -- the length of the game in outs at time of interruption
#           All the rest of the information in the record refers to the
#           entire game.
#    15     Forfeit information:
#              "V" -- the game was forfeited to the visiting team
#              "H" -- the game was forfeited to the home team
#              "T" -- the game was ruled a no-decision
#    16     Protest information:
#              "P" -- the game was protested by an unidentified team
#              "V" -- a disallowed protest was made by the visiting team
#              "H" -- a disallowed protest was made by the home team
#              "X" -- an upheld protest was made by the visiting team
#              "Y" -- an upheld protest was made by the home team
#           Note: two of these last four codes can appear in the field
#           (if both teams protested the game).
#    17     Park ID
#    18     Attendance (unquoted)
#    19     Time of game in minutes (unquoted)
# 20-21     Visiting and home line scores.  For example:
#              "010000(10)0x"
#           Would indicate a game where the home team scored a run in
#           the second inning, ten in the seventh and didn't bat in the
#           bottom of the ninth.
# 22-38     Visiting team offensive statistics (unquoted) (in order):
#              at-bats
#              hits
#              doubles
#              triples
#              homeruns
#              RBI
#              sacrifice hits.  This may include sacrifice flies for years
#                 prior to 1954 when sacrifice flies were allowed.
#              sacrifice flies (since 1954)
#              hit-by-pitch
#              walks
#              intentional walks
#              strikeouts
#              stolen bases
#              caught stealing
#              grounded into double plays
#              awarded first on catcher's interference
#              left on base
# 39-43     Visiting team pitching statistics (unquoted)(in order):
#              pitchers used ( 1 means it was a complete game )
#              individual earned runs
#              team earned runs
#              wild pitches
#              balks
# 44-49     Visiting team defensive statistics (unquoted) (in order):
#              putouts.  Note: prior to 1931, this may not equal 3 times
#                 the number of innings pitched.  Prior to that, no
#                 putout was awarded when a runner was declared out for
#                 being hit by a batted ball.
#              assists
#              errors
#              passed balls
#              double plays
#              triple plays
# 50-66     Home team offensive statistics
# 67-71     Home team pitching statistics
# 72-77     Home team defensive statistics
# 78-79     Home plate umpire ID and name
# 80-81     1B umpire ID and name
# 82-83     2B umpire ID and name
# 84-85     3B umpire ID and name
# 86-87     LF umpire ID and name
# 88-89     RF umpire ID and name
#           If any umpire positions were not filled for a particular game
#           the fields will be "","(none)".
# 90-91     Visiting team manager ID and name
# 92-93     Home team manager ID and name
# 94-95     Winning pitcher ID and name
# 96-97     Losing pitcher ID and name
# 98-99     Saving pitcher ID and name--"","(none)" if none awarded
# 100-101   Game Winning RBI batter ID and name--"","(none)" if none
#           awarded
# 102-103   Visiting starting pitcher ID and name
# 104-105   Home starting pitcher ID and name
# 106-132   Visiting starting players ID, name and defensive position,
#           listed in the order (1-9) they appeared in the batting order.
# 133-159   Home starting players ID, name and defensive position
#           listed in the order (1-9) they appeared in the batting order.
#   160     Additional information.  This is a grab-bag of informational
#           items that might not warrant a field on their own.  The field 
#           is alpha-numeric. Some items are represented by tokens such as:
#              "HTBF" -- home team batted first.
#              Note: if "HTBF" is specified it would be possible to see
#              something like "01002000x" in the visitor's line score.
#           Changes in umpire positions during a game will also appear in 
#           this field.  These will be in the form:
#              umpchange,inning,umpPosition,umpid with the latter three
#              repeated for each umpire.
#           These changes occur with umpire injuries, late arrival of 
#           umpires or changes from completion of suspended games. Details
#           of suspended games are in field 14.
#   161     Acquisition information:
#              "Y" -- we have the complete game
#              "N" -- we don't have any portion of the game
#              "D" -- the game was derived from box score and game story
#              "P" -- we have some portion of the game.  We may be missing
#                     innings at the beginning, middle and end of the game.
 
# Missing fields will be NULL.
# 


dateIdx = [0]
strIdx = [1, 2, 3, 4, 6, 7, 12, 14, 15, 16]
strIdx.extend(list(range(77, 161)))
posStrIdx = list(range(107, 159, 3))
baseDir = os.path.join("alldata", "gamelogs")

def getYear(s, isEnd=False):
    typ = 'start'
    if isEnd:
        typ = 'end'
    try:
        year = int(s)
        return year
    except:
        print(f"could not parse {typ} year '{s}'")
    return None    

def parseCompletionInfo(r): 
    s = "NULL"
    return s 

def parseLineScore(r):
    i = 0
    inn = 1
    extras = ""
    s = ""
    # keep iteratingg for at least nine innings
    # and use all chars
    isExtra = False
    while inn < 10 or i < len(r):
        if inn == 10:
            isExtra = True
            firstNine = s
            print('extra inning game ', end="")
            s = ""
        if inn > 1 and inn != 10:
            s += ", "
        if inn > 9:
            print(f"{inn} ", end="")
        # run out of innings, so keep appending NULL    
        if i >= len(r):
            s += "NULL"
            inn += 1
            continue

        runStr = "NULL"
        if r[i] != "x":
            if r[i] == '(':
                i += 1
                runStr = r[i:i+2]
                i += 2
                if r[i] != ")":
                    print(f"ERROR: attempting to parse line score {r}")
                    print(f"       expected ')' got {r[i]}")
                    runStr = "NULL"
            else:
                runStr = r[i:i+1]           
            # ensure runs is an interger
            if runStr != "NULL":
                try:
                    runs = int(runStr)
                except:
                    print(f"ERROR: attempting to parse line score {r}")
                    print(f"       expected intger value got {runStr}")
                    runStr = "NULL"
        if isExtra:
            print(f"runs {runStr} ", end="")
        s += runStr
        i += 1
        inn += 1
    if isExtra:
        extras = s
        print(f"    extras= {extras}")  
        print(f"    firstNine= {firstNine}")                
    else:
        firstNine = s
    return (firstNine, extras)

def getBoxScoreData(yearStart, yearEnd, writeFiles, conn, cur):
    s = ""
    numFields = 0
    # games which went to extra innings
    extras = []
    # completions for games scheduled at a later date
    completions = []
    useDB = conn is not None

    for year in range(yearStart, yearEnd+1):
        fName = f"gl{year}.txt"
        fPath = os.path.join(baseDir, fName)
        print(f"processing file {fPath}")
        with open(fPath, "r") as fIn:
            rdr = csv.reader(fIn, delimiter=',', quotechar='"')
            for row in rdr:
                ext_visit = None   # score for visitor in extra innints
                i = 0
                # clear string to save space if we aren't writing out query
                if not writeFiles:
                    s = ""
                ln = "INSERT INTO boxscore VALUES("
                for v in row:
                    if i > 76:
                        break
                    x = "NULL"
                    if i == 0:
                        x = f"DATE('{v[0:4]}-{v[4:6]}-{v[6:]}')"
                    elif i == 13:
                        x = "TRUE"
                        if len(v) > 0:
                            x = "FALSE"
                            completions.append((game_date, game_num, home_team, v))
                    elif i in (19, 20):
                        (x, ext) = parseLineScore(v)
                        if(len(ext) > 0):
                            if i == 19:
                                ext_visit = ext
                            else:
                                extras.append((game_date, game_num, home_team, ext_visit, ext))
                    elif i in posStrIdx:
                        if v == '':
                            x = "'U'"
                        else:
                            x = int(v)
                            if x == 10:
                                x = "'D'"
                            elif x > 10:
                                print(f"ERROR, listed position {v} > 10")
                                exit(1)
                            else:
                                x= f"'{str(x)}'"
                    else:
                        x = v
                        if i in strIdx:
                            vr = v
                            if "'" in v:
                                vr = v.replace("'", "''")
                            x = f"'{vr}'"
                            
                    if len(x) == 0:
                        x = "NULL"

                    # need to remember these as they consit of the key
                    # used fro completion info an extra innings
                    if i == 0:
                        game_date = x
                    elif i == 1:
                        game_num = x
                    elif i == 6:
                        home_team = x

                    ln += x
                    i += 1
                    ln += ", "
                # remove last comma
                ln = ln[:-2]
                ln += ")"
                if useDB:
                    cur.execute(ln)
                ln += "\n"
                numFields = ln.count(",") + 1
                s += ln
        if useDB:
            conn.commit()

    s += "\n"
    # extra inning infor
    for g in extras:
        # clear string to save space if we aren't writing out query
        if not writeFiles:
            s = ""
        ln = f"INSERT INTO extra VALUES({g[0]}, {g[1]}, {g[2]}"
        ext = g[3]  # visitor 
        for n in range(2):
            r = re.split(",", ext)
            for i in range(10, 26):
                ln += ", "
                if i-10 < len(r):
                    ln += r[i-10]
                else:
                    ln += "NULL"
            ext = g[4]  # home
        ln += ")"
        if useDB:
            cur.execute(ln)
        ln += ";\n"
        s += ln

    if useDB:
        conn.commit()

    s += "\n"
    # completion info
    for g in completions:    
        # clear string to save space if we aren't writing out query
        if not writeFiles:
            s = ""
        ln = f"INSERT INTO completion VALUES({g[0]}, {g[1]}, {g[2]}, "
        r = re.split(",",  g[3])
        dt = r[0]
        print(f"dt= {dt}")
        ln += f"DATE('{dt[0:4]}-{dt[4:6]}-{dt[6:8]}'), "
        ln += f"'{r[1]}', "
        ln += f"{r[2]}, "
        ln += f"{r[3]}, "
        ln += f"{r[4]}"
        ln += ")"
        if useDB:
            cur.execute(ln)
        ln += ";\n"
        s += ln

    if useDB:
        conn.commit()

    #           yyyymmdd -- the date the game was completed
    #           park -- the park ID where the game was completed
    #           vs -- the visitor score at the time of interruption
    #           hs -- the home score at the time of interruption
    #           len -- the length of the game in outs at time of interruption

    print(f'numFields= {numFields}')        

    if writeFiles:
        fPath = f"boxscores_{yearStart}_to_{yearEnd}.sql"
        fout = open(fPath, "w")
        if fout is None:
            print(f"ERROR: cannot open '{fPath}' for writing")
            exit(1)     
        fout.write("BEGIN;\n")           
        fout.write(s)
        fout.write("COMMIT;\n")
        fout.close()

if __name__=="__main__":
    connectPG = False
    connectSqlite = True
    useDB = connectPG or connectSqlite
    writeFiles = False

    conn = None
    cur = None
    if connectSqlite:
        import sqlite3
        conn = sqlite3.connect("baseball.db")
        cur = conn.cursor()

    if connectPG:
        import psycopg
        # Connect to an existing database
        conn = psycopg.connect("dbname=postgres user=postgres")
        cur = conn.cursor()

    narg = len(sys.argv)
    yearStart = 1871
    yearEnd = 2022
    if narg > 3:
        print(f"Too many arguments, encountered {narg}  expected between 0 and 2")
        exit(1)
    if narg > 1:
        yearStart = getYear(sys.argv[1])
    if narg > 2:
        yearEnd = getYear(sys.argv[2], True)    
    if yearStart == None or yearEnd == None:
        print("bad years")
        exit(1)
    getBoxScoreData(yearStart, yearEnd, writeFiles, conn, cur)

