#!/usr/bin/python3

allTables = dict()
allViews = dict()

allTables["player_game_batting"] = """CREATE TABLE player_game_batting (
    game_id integer,
    batter_id smallint,
    team smallint,
    pos_seq smallint,
    AB_R_H smallint,
    n2B_3B_HR smallint,
    RBI_SH_SF smallint,
    HBP_BB_IBB smallint,
    K_SB_CS smallint,
    GIDP_INTF smallint,
    PRIMARY KEY(game_id, batter_id)
)"""

allTables["player_game_fielding"] = """CREATE TABLE player_game_fielding (
    game_id integer,
    fielder_id smallint,
    team smallint,
    pos_seq smallint,
    IF3 smallint,
    PO_A_E smallint,
    DP_TP_PB smallint,
    PRIMARY KEY(game_id, fielder_id, pos_seq)
)"""

allTables["player_game_pitching"] = """CREATE TABLE player_game_pitching (
    game_id integer,
    pitcher_id smallint,
    team smallint,
    seq smallint,
    IP3 smallint,
    NOOUT_BF_H smallint,
    n2B_3B_HR smallint,
    R_ER_BB smallint,
    IBB_K_HBP smallint,
    WP_BK_SH smallint,
    SH smallint,
    PRIMARY KEY(game_id, pitcher_id)
)"""

# inning = inning + (inning_half << 6)
allTables["game_situation"] = """CREATE TABLE game_situation (
    game_id_event_id integer,
    batter_id smallint,
    pitcher_id smallint,
    inning_outs_pitch_cnt smallint,    
    team_scores smallint,
    bases_first smallint,
    bases_second smallint,
    bases_third smallint,
    bat_result_base smallint,
    hit_loc_hit_type_outs_made_runs_scored smallint,
    PRIMARY KEY(game_id_event_id)
)"""

allTables["game_situation_result2"] = """CREATE TABLE game_situation_result2 (
    game_id_event_id integer,
    bat_result2_base2,
    PRIMARY KEY(game_id_event_id)
)"""

allTables["game_situation_result3"] = """CREATE TABLE game_situation_result3 (
    game_id_event_id integer,
    bat_result3_base3 smallint,
    PRIMARY KEY(game_id_event_id)
)"""

allTables["game_situation_fielder_assist"] = """CREATE TABLE game_situation_fielder_assist (
    game_id_event_id integer,
    fielder_id smallint,
    seq smallint,
    PRIMARY KEY(game_id_event_id, fielder_id, seq)
)"""

allTables["game_situation_fielder_putout"] = """CREATE TABLE game_situation_fielder_putout (
    game_id_event_id integer,
    fielder_id smallint,
    seq smallint,
    PRIMARY KEY(game_id, event_id, fielder_id, seq)
)"""

allTables["game_situation_fielder_error"] = """CREATE TABLE game_situation_fielder_error (
    game_id_event_id integer,
    fielder_id smallint,
    seq smallint,
    PRIMARY KEY(game_id_event_id, fielder_id, seq)
)"""

allTables["game_situation_fielder_fielded"] = """CREATE TABLE game_situation_fielder_fielded (
    game_id_event_id integer,
    fielder_id smallint,
    seq smallint,
    PRIMARY KEY(game_id_event_id, fielder_id, seq)
)"""

allTables["game_situation_result1_mod"] = """CREATE TABLE game_situation_result1_mod (
    game_id_event_id integer,
    seq_mod_prm smallint,
    PRIMARY KEY(game_id_event_id, seq_mod_prm)
)"""

allTables["game_situation_result2_mod"] = """CREATE TABLE game_situation_result2_mod (
    game_id_event_id integer,
    seq_mod_prm smallint,
    PRIMARY KEY(game_id_event_id, seq_mod_prm)
)"""
allTables["game_situation_result3_mod"] = """CREATE TABLE game_situation_result3_mod (
    game_id_event_id integer,
    seq_mod_prm smallint,
    PRIMARY KEY(game_id_event_id, seq_mod_prm)
)"""

allTables["game_situation_base_run"] = """CREATE TABLE game_situation_base_run (
    game_id_event_id integer,
    base_src_dst_out smallint,
    PRIMARY KEY(game_id_event_id, base_src_dst_out)
)"""

allTables["game_situation_base_run_mod"] = """CREATE TABLE game_situation_base_run_mod (
    game_id_event_id integer,
    base_src_dst_out smallint,
    seq_mod_prm smallint,
    PRIMARY KEY(game_id_event_id, base_src_dst_out, seq_mod_prm)
)"""

allTables["game_situation_base_run_sub_mod"] = """CREATE TABLE game_situation_base_run_sub_mod (
    game_id_event_id integer,
    base_src_dst smallint,
    seq_mod_prm smallint, 
    submod smallint,
    PRIMARY KEY(game_id_event_id, base_src_dst, seq_mod_prm)
)"""

allTables["play_mod"] = """CREATE TABLE play_mod (
    num smallint,
    desc char(8)
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

    for view, createStmt in allViews.items():
        try:
            cur.execute(f"DROP VIEW {view}")
        except Exception as e:
            pass
        #print(createStmt)
        print("creating view ", view)
        cur.execute(createStmt)
    conn.commit()
    conn.close()