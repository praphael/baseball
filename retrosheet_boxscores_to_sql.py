#!/usr/bin/python3

import csv
import os
import re
import sys
from datetime import date

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


# game_id integer PRIMARY KEY,
# away_score smallint NOT NULL,
# home_score smallint NOT NULL,
# game_len_outs smallint NOT NULL,
# away_score_inning_12345 integer NOT NULL, 
# away_score_inning_6789 integer NOT NULL, 
# home_score_inning_12345 integer NOT NULL, 
# home_score_inning_6789 integer NOT NULL,     
# away_at_bats_hits smallint NOT NULL,
# away_doubles_triples smallint NOT NULL, 
# away_home_runs_rbi smallint NOT NULL,
# away_sac_hit_sac_fly smallint NOT NULL,
# away_hit_by_pitch_walks smallint NOT NULL,
# away_int_walks_strikeouts smallint NOT NULL,
# away_stolen_bases_caught_stealing smallint NOT NULL,
# away_gidp_catcher_interference smallint NOT NULL,
# away_left_on_base_pitchers_used smallint NOT NULL,
# away_indiv_earned_runs_team_earned_runs smallint NOT NULL,
# away_wild_pitches_balks smallint NOT NULL,
# away_putouts_assists smallint NOT NULL,
# away_errors_passed_balls smallint NOT NULL,
# away_double_plays_triple_plays smallint NOT NULL,
# home_at_bats_hits smallint NOT NULL, 
# home_doubles_triples smallint NOT NULL, 
# home_home_runs_rbi smallint NOT NULL,
# home_sac_hit_sac_fly smallint NOT NULL,
# home_hit_by_pitch_walks smallint NOT NULL,
# home_int_walks_strikeouts smallint NOT NULL,
# home_stolen_bases_caught_stealing smallint NOT NULL,
# home_gidp_catcher_interference smallint NOT NULL,
# home_left_on_base_pitchers_used smallint NOT NULL,
# home_indiv_earned_runs_team_earned_runs smallint NOT NULL,
# home_wild_pitches_balks smallint NOT NULL,
# home_putouts_assists smallint NOT NULL,
# home_error_passed_balls smallint NOT NULL,
# home_double_plays_triple_plays

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

dateIdx = [0]
strIdx = [1, 2, 3, 4, 6, 7, 12, 14, 15, 16]
strIdx.extend(list(range(77, 161)))
posStrIdx = list(range(107, 159, 3))
baseDir = os.path.join("alldata", "gamelogs")

def parseLineScore(r):
    i = 0
    inn = 1
    scoreByInn = [None]*27
    # keep iteratingg for at least nine innings
    # and use all chars
    while i < len(r):
        if r[i] != "x":
            # more than 9 runs in the inning
            if r[i] == '(':
                i += 1
                scoreByInn[inn-1] = int(r[i:i+2])
                i += 2
                if r[i] != ")":
                    print(f"ERROR: attempting to parse line score {r}")
                    print(f"       expected ')' got {r[i]}")
            else:
                scoreByInn[inn-1] = int(r[i:i+1])
        i += 1
        inn += 1
    
    extras = scoreByInn[9:]
    return (scoreByInn[:9], extras)

def getBoxScoreData(yearStart, yearEnd, conn, includePayoffs=True, db="sqlite"):
    tbl = "gamelog"
    extra_tbl = "extra"
    comp_tbl = "completion"
    innings_tbl = "score_by_inning"

    playoffs = ("wc", "dv", "lc", "ws")
    rng = list(range(yearStart, yearEnd+1))
    rng.extend(playoffs)
    playoffGTMap = {"wc": 1, "dv":2, "lc":3, "ws":4}
    # game ids for games which do not have corresponding IDs in game_info
    # make very large number to avoid conflicts with normal games
    game_id_next = (1 << 28)
    cur = conn.cursor()
    MONTHS = dict()
    stmt = "SELECT num, d FROM month"
    cur.execute(stmt)
    tups = cur.fetchall()
    for t in tups:
        MONTHS[t[0]] = t[1]
    DAYS_OF_WEEK = dict()
    stmt = "SELECT num, d FROM day_in_week"
    cur.execute(stmt)
    tups = cur.fetchall()
    for t in tups:
        DAYS_OF_WEEK[t[1]] = t[0]
    print("DAYS_OF_WEEK=", DAYS_OF_WEEK)
    # map of date/hometeam/number the integer game id
    #gameIDMap = dict()
    teamIDMap = dict()
    cur.execute("SELECT team_id, team_nickname FROM team")
    tups = cur.fetchall()
    for t in tups:
        teamIDMap[t[0]] = t[1]

    # clear tables
    del_stmt = f"DELETE FROM {tbl}"
    del_comp_stmt = f"DELETE FROM {comp_tbl}"
    del_innings_stmt = f"DELETE FROM {innings_tbl}"

    cur.execute(del_stmt)
    cur.execute(del_comp_stmt)
    cur.execute(del_innings_stmt)
    
    for f in rng:
        fName = f"gl{f}.txt"
        fPath = os.path.join(baseDir, fName)
        print(f"processing file {fPath}")
        
        game_type = 0
        if f in playoffs:
            game_type = 1
            playoff_type = playoffGTMap[f]

        gameIDMap = dict()
        # flag map from gameID, for setting forfeit/protest/compelted
        flags = dict() 

        forfMap = {"":0, "V":1, "H":2, "T":3}
        protMap = {"":0, "P":1, "V":2, "H":3, "X":4, "Y":5}
        missing_teams = []
        with open(fPath, "r") as fIn:
            rdr = csv.reader(fIn, delimiter=',', quotechar='"')
            for row in rdr:
                i = 0
                    
                for v in row:
                    if i > 76:  # don't read all data
                        break
                    if i == 0:
                        game_year = int(v[0:4])
                        game_month = int(v[4:6])
                        game_day = int(v[6:])
                        game_date = date(game_year, game_month, game_day)
                        # x = f"DATE('{v[0:4]}-{v[4:6]}-{v[6:]}')"
                    elif i == 1:
                        dh_game_num = int(v)
                    elif i == 2:
                        dow = v
                    elif i == 3:
                        away_team = v
                        if away_team not in teamIDMap and away_team not in missing_teams:
                            #print(teamIDMap)                            
                            print("Could not find team ", away_team)
                            missing_teams.append(away_team)
                    elif i == 4:
                        away_league = v
                    elif i == 5:
                        away_game_num = int(v)
                    elif i == 6:  # enough info to get gameID
                        home_team = v

                        # fetch game IDs for this year if we have not already done so
                        if game_year not in gameIDMap:
                            stmt = "SELECT game_id, game_date, home_team, game_type_num, flags"
                            #stmt += f" year={game_year}"
                            stmt += f" FROM game_info WHERE year={game_year}"

                            #print(stmt)
                            cur.execute(stmt)
                            tups = cur.fetchall()
                            #print(len(tups))
                            gameIDMap[game_year] = dict()
                            for t in tups:
                                #print(t)
                                game_id = int(t[0])
                                if db == "sqlite":
                                    #game_dt = date(t[1][0:4], t[1][4:6], t[1][6:])
                                    game_dt = date.fromisoformat(t[1])
                                elif db == "postgres":
                                    game_dt = date.fromisoformat(t[1])
                                    
                                #print("game_dt=", game_dt)
                                #print("game_ddte=", game_date)
                                ht = t[2]
                                dh_num = 3 & (int(t[3]) >> 6)
                                if game_dt not in gameIDMap[game_year]:
                                    gameIDMap[game_year][game_dt] = dict()
                                if ht not in gameIDMap[game_year][game_dt]:
                                    gameIDMap[game_year][game_dt][ht] = dict()
                                gameIDMap[game_year][game_dt][ht][dh_num] = game_id
                                flags[game_id] = t[4]

                        if home_team in teamIDMap:
                            home_team_name = teamIDMap[home_team]
                            #home_team_name = home_team_name.replace("'", "''")
                        else:
                            print(teamIDMap)
                            print("Could not find team ", home_team)
                            home_team_name = home_team
                            missing_teams.append(home_team)
                        game_id = -1
                        try: 
                            game_id = gameIDMap[game_year][game_date][home_team][dh_game_num]
                        except: 
                            pass
                        if game_id == -1:
                            print("could not find gameID in gameIDMap game_year=", game_year)
                            game_id = game_id_next
                            game_id_next += 1
                        
                        #print("game_year=", game_year, "game_id=", game_id)
                        
                        # start statment
                        stmt = f"INSERT INTO {tbl} VALUES({game_id}"                        
                    elif i == 7:
                        home_league = v
                    elif i == 8:
                        home_game_num = int(v)
                    elif i == 9:
                        away_score = int(v)
                        stmt += f", {away_score}"
                    elif i == 10:
                        home_score = int(v)
                        stmt += f", {home_score}"
                    elif i == 11:
                        game_len_outs = 0
                        if v != "":
                            game_len_outs = int(v)
                        stmt += f", {game_len_outs}"
                    elif i == 13:  # completion
                        #stmt += f", '{v}'"
                        # completion info, including date on which game was completed
                        completed = True
                        if len(v) > 0:  
                            completed = False
                            v.split(",")
                            # yyyymmdd,park,vs,hs,len
                            c_stmt = f"INSERT INTO {comp_tbl} VALUES({game_id}"
                            c_stmt += f", '{v[0:4]}-{v[4:6]}-{v[6:8]}'"
                            c_stmt += f", {v[1]}, {v[2]}, {v[3]}, {v[4]})"
                            #print(c_stmt)
                            cur.execute(c_stmt)
                    elif i == 14:
                        forfeit = v
                    elif i == 15:
                        protest = v
                    elif i == 18:
                        game_len_min = 0
                        if v != "":
                            game_len_min = int(v)
                    elif i in (19, 20):  # score by inning
                        (oneTo9, ext) = parseLineScore(v)
                        if (i == 19):
                            awayOneTo9 = list(oneTo9)
                            awayExt = list(ext)
                        else:
                            for inn in range(0, 9):
                                if awayOneTo9[inn] == None:
                                    break
                                inn_stmt = f"INSERT INTO {innings_tbl} VALUES({game_id}, {inn+1}"
                                inn_stmt += f", {valOrNULL(oneTo9[inn])}, {valOrNULL(awayOneTo9[inn])})"
                                cur.execute(inn_stmt)
                            inn = 10
                            while ext[inn] != None:
                                inn_stmt = f"INSERT INTO {innings_tbl}  VALUES({game_id}, {inn+1}"
                                inn_stmt += f", {valOrNULL(ext[inn])}, {valOrNULL(awayExt[inn])})"
                                cur.execute(inn_stmt)
                                inn += 1
                    elif i in range(21, 77):  # stats
                        if v == "":
                            stmt += f", NULL"
                        else:
                            stmt += f", {int(v)}"
                    i += 1
                # end for v in row

                stmt += ")"
                #print(stmt)
                cur.execute(stmt)

                # 6: completed
                # 7-8: forfeit 
                # 9-11: protest 

                #  update game info with protest, forfeit, day of week, game lenetc.
                
                # not new game
                if game_id < (1 << 28):
                    fl = flags[game_id]
                    fl = fl | (completed << 6) 
                    fl = fl | (forfMap[forfeit] << 7)
                    fl = fl | (protMap[protest] << 9)
                    stmt = f"UPDATE game_info SET flags={fl}"
                    stmt += f", dow={DAYS_OF_WEEK[dow]}"
                    stmt += f", game_duration_min={game_len_min}"
                    stmt += f", away_league='{away_league}'"
                    stmt += f", away_game_num={away_game_num}"
                    stmt += f", home_league='{home_league}'"
                    stmt += f", home_game_num={home_game_num}"
                    stmt += f" WHERE game_id={game_id}"
                    cur.execute(stmt)
                else:
                    # TODO make new game-info
                    pass 
                
        conn.commit()

if __name__=="__main__":
    narg = len(sys.argv)
    yearStart = 1871
    yearEnd = 2023
    db = "sqlite"
    if narg > 4:
        print(f"Too many arguments, encountered {narg}  expected between 0 and 2")
        exit(1)
    if narg > 1:
        yearStart = int(sys.argv[1])
    if narg > 2:
        yearEnd = int(sys.argv[2])    
    if narg > 3:
        db = sys.argv[3]
    
    conn = None
    if db == "sqlite":
        import sqlite3
        conn = sqlite3.connect("baseball.db")
    elif db == "postgres":
        import psycopg
        # Connect to an existing database
        conn = psycopg.connect("dbname=postgres user=postgres")
    else:
        print("unsupported DB", db)
        exit(1)

    cur = conn.cursor()
    
    #print(teamIDMap)
    getBoxScoreData(yearStart, yearEnd, conn, True, db)

