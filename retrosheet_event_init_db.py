#!/usr/bin/python3

allTables = dict()

allTables["player_game_batting"] = """CREATE TABLE player_game_batting (
    game_id integer,
    player_num_id smallint,
    team varchar(4),
    lineup char(1),
    seq char(1),
    pos char(1),
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
    INTF smallint,
    PRIMARY KEY(game_id, player_num_id)
)"""

allTables["player_game_fielding"] = """CREATE TABLE player_game_fielding (
    game_id integer,
    player_num_id smallint,
    team varchar(4),
    pos char(1),
    seq char(1),
    IF3 smallint,
    PO smallint,
    A smallint,
    E smallint,
    DP smallint,
    TP smallint,
    PB smallint,
    PRIMARY KEY(game_id, player_num_id, pos, seq)
)"""

allTables["player_game_pitching"] = """CREATE TABLE player_game_pitching (
    game_id integer,
    player_num_id smallint,
    team varchar(4),
    seq char(1),
    IP3 smallint,
    NOOUT smallint,
    BFP smallint,
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
    PRIMARY KEY(game_id, player_num_id, seq)
)"""

allTables["game_situation"] = """CREATE TABLE game_situation (
    game_id integer,
    event_id smallint,
    batter_id smallint,
    pitcher_id smallint,
    inning char(1),
    inning_half char(1),
    outs char(1),
    bat_team_score smallint,
    pitch_team_score smallint,
    bases_first smallint,
    bases_second smallint,
    bases_third smallint,
    pitch_cnt char(2),
    bat_result varchar(4),
    bat_base char(1),
    hit_loc char(4),
    hit_type char(4),
    bat_result2 char(4),
    bat_base2 char(1),
    outs_made char(1),
    runs_scored char(1),
    PRIMARY KEY(game_id, event_id)
)"""

allTables["game_situation_fielder_assist"] = """CREATE TABLE game_situation_fielder_assist (
    game_id integer,
    event_id smallint,
    fielder_id smallint,
    seq char(1),
    PRIMARY KEY(game_id, event_id, fielder_id, seq)
)"""

allTables["game_situation_fielder_putout"] = """CREATE TABLE game_situation_fielder_putout (
    game_id integer,
    event_id smallint,
    fielder_id smallint,
    seq char(1),
    PRIMARY KEY(game_id, event_id, fielder_id, seq)
)"""

allTables["game_situation_fielder_error"] = """CREATE TABLE game_situation_fielder_error (
    game_id integer,
    event_id smallint,
    fielder_id smallint,
    seq char(1),
    PRIMARY KEY(game_id, event_id, fielder_id, seq)
)"""

allTables["game_situation_fielder_fielded"] = """CREATE TABLE game_situation_fielder_fielded (
    game_id integer,
    event_id smallint,
    fielder_id smallint,    
    seq char(1),
    PRIMARY KEY(game_id, event_id, fielder_id, seq)
)"""

allTables["game_situation_bat_mod"] = """CREATE TABLE game_situation_bat_mod (
    game_id integer,
    event_id smallint,
    seq char(1),
    mod char(4),
    prm char(2),
    PRIMARY KEY(game_id, event_id, seq)
)"""

allTables["game_situation_base_run"] = """CREATE TABLE game_situation_base_run (
    game_id integer,
    event_id smallint,
    base_src char(1),
    base_dst char(1),
    out char(1),
    PRIMARY KEY(game_id, event_id, base_src)
)"""

allTables["game_situation_base_run_mod"] = """CREATE TABLE game_situation_base_run_mod (
    game_id integer,
    event_id smallint,
    base_src char(1),
    base_dst char(1),
    seq char(1),
    mod char(4),
    prm char(4),
    PRIMARY KEY(game_id, event_id, base_src, seq)
)"""

allTables["game_situation_base_run_sub_mod"] = """CREATE TABLE game_situation_base_run_sub_mod (
    game_id integer,
    event_id smallint,
    base_src char(1),
    base_dst char(1),
    seq char(1),
    mod char(4),
    submod char(4),
    prm char(4),
    PRIMARY KEY(game_id, event_id, base_src, seq, mod)
)"""

if __name__ == "__main__":
    connectPG = False
    connectSqlite = True
    useDB = connectPG or connectSqlite

    if connectSqlite:
        import sqlite3
        conn = sqlite3.connect("baseball.db")
        cur = conn.cursor()

    if connectPG:
        import psycopg
        # Connect to an existing database
        conn = psycopg.connect("dbname=postgres user=postgres")
        cur = conn.cursor()

    for table, createStmt in allTables.items():
        try:
            cur.execute(f"DROP TABLE {table}")
        except Exception as e:
            pass
        #print(createStmt)
        print("creating table ", table)
        cur.execute(createStmt)
    conn.commit()
    conn.close()