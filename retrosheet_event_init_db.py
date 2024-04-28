#!/usr/bin/python3

import sys

allTables = dict()
allViews = dict()

allTables["player_game_batting"] = """CREATE TABLE player_game_batting (
    game_id integer,
    batter_id char(8),
    team char(3),
    pos smallint, 
    seq smallint,
    AB smallint,
    R smallint,
    H smallint,
    n2B smallint,
    n3B smallint,
    HR smallint,
    RBI smallint,
    SH smallint,
    SF smallint,
    HBP smallint,
    BB smallint,
    IBB smallint,
    K smallint,
    SB smallint,
    CS smallint,
    GIDP smallint,
    INTF smallint
    PRIMARY KEY(game_id, batter_id)
)"""

allTables["player_game_fielding"] = """CREATE TABLE player_game_fielding (
    game_id integer,
    fielder_id smallint,
    team char(3),
    pos smallint,
    seq smallint,
    IF3 smallint,
    PO
    A
    E smallint,
    DP
    TP
    PB smallint
    PRIMARY KEY(game_id, fielder_id, pos_seq)
)"""

allTables["player_game_pitching"] = """CREATE TABLE player_game_pitching (
    game_id integer,
    pitcher_id char(8),
    team char(3),
    seq smallint,
    IP3 smallint,
    NOOUT smallint,
    BF smallint,
    H smallint,
    n2B smallint,
    n3B smallint,
    HR smallint,
    R smallint,
    ER smallint,
    BB smallint,
    IBB smallint,
    K smallint,
    HBP smallint,
    WP smallint,
    BK smallint,
    SH smallint,
    SF smallint,
    PRIMARY KEY(game_id, pitcher_id)
)"""

# inning = inning + (inning_half << 6)
allTables["game_situation"] = """CREATE TABLE game_situation (
    game_id integer,
    event_id smallint,
    batter_id char(8) NOT NULL,
    pitcher_id char(8) NOT NULL,
    inning smallint NOT NULL,
    outs smallint NOT NULL,
    pitch_cnt char(2),
    bat_team_score smallint NOT NULL,
    pitch_team_score smallint NOT NULL,
    bat_result char(3),
    bat_base smallint,
    hit_loc char(3),
    hit_type char(1),
    outs_made smallint,
    runs_scored smallint
    PRIMARY KEY(game_id, event_id)
)"""

allTables["game_situation_bases"] = """CREATE TABLE game_situation_bases (
    game_id integer,   
    event_id smallint,   
    bases_first char(8),
    bases_second char(8),
    bases_third char(8)
    PRIMARY KEY(game_id, event_id)
)"""

allTables["game_situation_result2"] = """CREATE TABLE game_situation_result2 (
    game_id integer,
    event_id smallint,
    bat_result char(3),
    bat_base smallint
    PRIMARY KEY(game_id, event_id)
)"""

allTables["game_situation_result3"] = """CREATE TABLE game_situation_result3 (
    game_id integer,
    event_id smallint,
    bat_result char(3),
    bat_base smallint
    PRIMARY KEY(game_id, event_id)
)"""

allTables["game_situation_fielder_assist"] = """CREATE TABLE game_situation_fielder_assist (
    game_id integer,
    event_id smallint,
    fielder_id char(8),
    seq smallint
    PRIMARY KEY(game_id, event_id, fielder_id, seq)
)"""

allTables["game_situation_fielder_putout"] = """CREATE TABLE game_situation_fielder_putout (
    game_id integer,
    event_id smallint,
    fielder_id char(8),
    seq smallint
    PRIMARY KEY(game_id, event_id, fielder_id, seq)
)"""

allTables["game_situation_fielder_error"] = """CREATE TABLE game_situation_fielder_error (
    game_id integer,
    event_id smallint,
    fielder_id char(8),
    seq smallint
    PRIMARY KEY(game_id, event_id, fielder_id, seq)
)"""

allTables["game_situation_fielder_fielded"] = """CREATE TABLE game_situation_fielder_fielded (
    game_id integer,
    event_id smallint,
    fielder_id char(8),
    seq smallint
    PRIMARY KEY(game_id, event_id, fielder_id, seq)
)"""

allTables["game_situation_result1_mod"] = """CREATE TABLE game_situation_result1_mod (
    game_id integer,
    event_id smallint,
    seq smallint,
    mod char(4),
    prm varchar(8)
    PRIMARY KEY(game_id, event_id, seq)
)"""

allTables["game_situation_result2_mod"] = """CREATE TABLE game_situation_result2_mod (
    game_id integer,
    event_id smallint,
    seq smallint,
    mod char(4),
    prm varchar(8)
    PRIMARY KEY(game_id, event_id, seq)
)"""

allTables["game_situation_result3_mod"] = """CREATE TABLE game_situation_result3_mod (
    game_id integer,
    event_id smallint,
    seq smallint,
    mod char(4),
    prm varchar(8)
    PRIMARY KEY(game_id, event_id, seq)
)"""

allTables["game_situation_base_run"] = """CREATE TABLE game_situation_base_run (
    game_id integer,
    event_id smallint,
    src smallint, 
    dst smallint,
    out boolean
    PRIMARY KEY(game_id_event_id, src)
)"""

allTables["game_situation_base_run_mod"] = """CREATE TABLE game_situation_base_run_mod (
    game_id integer,
    event_id smallint,
    src smallint,
    seq smallint,
    mod char(4),
    prm varchar(8)
    PRIMARY KEY(game_id_event_id, src, seq)
)"""

if __name__ == "__main__":
    db = "sqlite"    

    if len(sys.argv) > 1:
        db = sys.argv[1]
    if db == "sqlite":
        import sqlite3
        conn = sqlite3.connect("baseball.db")
        cur = conn.cursor()
    elif db == "postgres":
        import psycopg
        # Connect to an existing database
        conn = psycopg.connect("dbname=postgres user=postgres")
        cur = conn.cursor()
    else:
        print("unrecognized db", db)
        exit()

    for table, createStmt in allTables.items():
        try:
            if db == "postgres":
                cur.execute(f"DROP TABLE IF EXISTS {table}")
            else:                
                cur.execute(f"DROP TABLE {table}")
        except Exception as e:
            pass
        #print(createStmt)
        print("creating table ", table)
        cur.execute(createStmt)

    for view, createStmt in allViews.items():
        try:
            if db == "postgres":
                cur.execute(f"DROP VIEW IF EXISTS {table}")
            else:
                cur.execute(f"DROP VIEW {view}")
        except Exception as e:
            pass
        #print(createStmt)
        print("creating view ", view)
        cur.execute(createStmt)
    conn.commit()
    conn.close()