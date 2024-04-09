#!/usr/bin/python3

boxscoreCreate="""CREATE TABLE boxscore (
    game_date date,
    game_num char(1),
    game_day_of_week char(3),
    visiting_team varchar(4),
    visiting_league varchar(4),
    visiting_game_num smallint, 
    home_team varchar(4),
    home_league varchar(4),
    home_game_num smallint, 
    visiting_score smallint,
    home_score smallint,
    game_len_outs smallint,
    day_night char(1),
    completed boolean, 
    forfeit varchar(1), 
    protest varchar(2),
    park varchar(16),
    attendance integer,
    game_time_minutes smallint,
    visiting_score_inning_1 smallint, 
    visiting_score_inning_2 smallint, 
    visiting_score_inning_3 smallint, 
    visiting_score_inning_4 smallint, 
    visiting_score_inning_5 smallint, 
    visiting_score_inning_6 smallint, 
    visiting_score_inning_7 smallint, 
    visiting_score_inning_8 smallint, 
    visiting_score_inning_9 smallint, 
    home_score_inning_1 smallint, 
    home_score_inning_2 smallint, 
    home_score_inning_3 smallint, 
    home_score_inning_4 smallint, 
    home_score_inning_5 smallint, 
    home_score_inning_6 smallint, 
    home_score_inning_7 smallint, 
    home_score_inning_8 smallint, 
    home_score_inning_9 smallint, 
    visiting_at_bats smallint,
    visiting_hits smallint, 
    visiting_doubles smallint, 
    visiting_triples smallint, 
    visiting_home_runs smallint, 
    visiting_rbi smallint,
    visiting_sac_hit smallint,
    visiting_sac_fly smallint,
    visiting_hit_by_pitch smallint,
    visiting_walks smallint,
    visiting_int_walks smallint,
    visiting_strikeouts smallint,
    visiting_stolen_bases smallint,
    visiting_caught_stealing smallint,
    visiting_gidp smallint,
    visiting_catcher_interference smallint,
    visiting_left_on_base smallint,
    visiting_pitchers_used smallint,
    visiting_indiv_earned_runs smallint,
    visiting_team_earned_runs smallint,
    visiting_wild_pitches smallint,
    visiting_balks smallint,
    visiting_putouts smallint,
    visiting_assists smallint,
    visiting_errors smallint,
    visiting_passed_balls smallint,
    visiting_double_plays smallint,
    visiting_triple_plays smallint,
    home_at_bats smallint,
    home_hits smallint, 
    home_doubles smallint, 
    home_triples smallint, 
    home_home_runs smallint, 
    home_rbi smallint,
    home_sac_hit smallint,
    home_sac_fly smallint,
    home_hit_by_pitch smallint,
    home_walks smallint,
    home_int_walks smallint,
    home_strikeouts smallint,
    home_stolen_bases smallint,
    home_caught_stealing smallint,
    home_gidp smallint,
    home_catcher_interference smallint,
    home_left_on_base smallint,
    home_pitchers_used smallint,
    home_indiv_earned_runs smallint,
    home_team_earned_runs smallint,
    home_wild_pitches smallint,
    home_balks smallint,
    home_putouts smallint,
    home_assists smallint,
    home_errors smallint,
    home_passed_balls smallint,
    home_double_plays smallint,
    home_triple_plays smallint,
    PRIMARY KEY(game_date, game_num, home_team)
)"""

# excluded data from boxscores - add after "home_triple_plays" to add back in
    # umpire_home_plate_id varchar(16), 
    # umpire_home_plate_name varchar(64),
    # umpire_1b_id varchar(16),
    # umpire_1b_name varchar(64),
    # umpire_2b_id varchar(16),
    # umpire_2b_name varchar(64),
    # umpire_3b_id varchar(16),
    # umpire_3b_name varchar(64),
    # umpire_lf_id varchar(16),
    # umpire_lf_name varchar(64),
    # umpire_rf_id varchar(16),
    # umpire_rf_name varchar(64),
    # visiting_manager_id varchar(16),
    # visiting_manager_name varchar(64),
    # home_manager_id varchar(16),
    # home_manager_name varchar(64),
    # winning_pitcher_id varchar(16),
    # winning_pitcher_name varchar(64),
    # losing_pitcher_id varchar(16),
    # losing_pitcher_name varchar(64),
    # saving_pitcher_id varchar(16),
    # saving_pitcher_name varchar(64),
    # game_winning_rbi_batter_id varchar(16),
    # game_winning_rbi_batter_name varchar(64), 
    # visiting_starting_pitcher_id varchar(16),
    # visiting_starting_pitcher_name varchar(64),
    # home_starting_pitcher_id varchar(16),
    # home_starting_pitcher_name varchar(64),
    # visiting_player_1_id varchar(16),
    # visiting_player_1_name varchar(64),
    # visiting_player_1_pos char(1),
    # visiting_player_2_id varchar(16),
    # visiting_player_2_name varchar(64),
    # visiting_player_2_pos char(1),
    # visiting_player_3_id varchar(16),
    # visiting_player_3_name varchar(64),
    # visiting_player_3_pos char(1),
    # visiting_player_4_id varchar(16),
    # visiting_player_4_name varchar(64),
    # visiting_player_4_pos char(1),
    # visiting_player_5_id varchar(16),
    # visiting_player_5_name varchar(64),
    # visiting_player_5_pos char(1),
    # visiting_player_6_id varchar(16),
    # visiting_player_6_name varchar(64),
    # visiting_player_6_pos char(1),
    # visiting_player_7_id varchar(16),
    # visiting_player_7_name varchar(64),
    # visiting_player_7_pos char(1),
    # visiting_player_8_id varchar(16),
    # visiting_player_8_name varchar(64),
    # visiting_player_8_pos char(1),
    # visiting_player_9_id varchar(16),
    # visiting_player_9_name varchar(64),
    # visiting_player_9_pos char(1),
    # home_player_1_id varchar(16),
    # home_player_1_name varchar(64),
    # home_player_1_pos char(1),
    # home_player_2_id varchar(16),
    # home_player_2_name varchar(64),
    # home_player_2_pos char(1),
    # home_player_3_id varchar(16),
    # home_player_3_name varchar(64),
    # home_player_3_pos char(1),
    # home_player_4_id varchar(16),
    # home_player_4_name varchar(64),
    # home_player_4_pos char(1),
    # home_player_5_id varchar(16),
    # home_player_5_name varchar(64),
    # home_player_5_pos char(1),
    # home_player_6_id varchar(16),
    # home_player_6_name varchar(64),
    # home_player_6_pos char(1),
    # home_player_7_id varchar(16),
    # home_player_7_name varchar(64),
    # home_player_7_pos char(1),
    # home_player_8_id varchar(16),
    # home_player_8_name varchar(64),
    # home_player_8_pos char(1),
    # home_player_9_id varchar(16),
    # home_player_9_name varchar(64),
    # home_player_9_pos char(1),
    # additional_info varchar(128),
    # acq_info char(1), 
extraCreate="""CREATE TABLE extra (
    game_date date,
    game_num char(1),
    home_team varchar(16), 
    visiting_score_inning_10 smallint,
    visiting_score_inning_11 smallint,
    visiting_score_inning_12 smallint,
    visiting_score_inning_13 smallint,
    visiting_score_inning_14 smallint,
    visiting_score_inning_15 smallint,
    visiting_score_inning_16 smallint,
    visiting_score_inning_17 smallint,
    visiting_score_inning_18 smallint,
    visiting_score_inning_19 smallint,
    visiting_score_inning_20 smallint,
    visiting_score_inning_21 smallint,
    visiting_score_inning_22 smallint,
    visiting_score_inning_23 smallint,
    visiting_score_inning_24 smallint,
    visiting_score_inning_25 smallint,
    home_score_inning_10 smallint,
    home_score_inning_11 smallint,
    home_score_inning_12 smallint,
    home_score_inning_13 smallint,
    home_score_inning_14 smallint,
    home_score_inning_15 smallint,
    home_score_inning_16 smallint,
    home_score_inning_17 smallint,
    home_score_inning_18 smallint,
    home_score_inning_19 smallint,
    home_score_inning_20 smallint,
    home_score_inning_21 smallint,
    home_score_inning_22 smallint,
    home_score_inning_23 smallint,
    home_score_inning_24 smallint,
    home_score_inning_25 smallint,
    PRIMARY KEY(game_date, game_num, home_team)
)"""

completionCreate="""CREATE TABLE completion (
    game_date date,
    game_num char(1),
    home_team varchar(16), 
    completion_date date,
    completion_park varchar(16), 
    visitor_score_int smallint, 
    home_score_int smallint, 
    outs_int smallint, 
    PRIMARY KEY(game_date, game_num, home_team)
)"""

parksCreate="""CREATE TABLE parks (
    park_id char(5) PRIMARY KEY,
    park_name varchar(64),
    park_aka varchar(64),
    park_city varchar(64),
    park_state varchar(4),
    park_open date, 
    park_close date,
    park_league varchar(64),
    notes varchar(128)
)"""

teamsCreate="""CREATE TABLE teams(
    team_id varchar(8),
    team_league varchar(64),
    team_city varchar(64),
    team_nickname varchar(64),
    team_first smallint,
    team_last smallint
)"""

def createBoxscore(cur):
    try:
        cur.execute("DROP TABLE boxscore")
    except Exception as e:
        pass
    cur.execute(boxscoreCreate)

def createParks(cur):
    try:
        cur.execute("DROP TABLE parks")
    except Exception as e:
        pass
    cur.execute(parksCreate)

def createTeams(cur):
    try:
        cur.execute("DROP TABLE teams")
    except Exception as e:
        pass
    cur.execute(teamsCreate)

def createCompletion(cur):
    try:
        cur.execute("DROP TABLE completion")
    except Exception as e:
        pass
    cur.execute(completionCreate)

def createExtra(cur):
    try:
        cur.execute("DROP TABLE extra")
    except Exception as e:
        pass
    cur.execute(extraCreate)

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

    createParks(cur)
    createTeams(cur)
    createBoxscore(cur)    
    createCompletion(cur)
    createExtra(cur)
    conn.commit()
    conn.close()

