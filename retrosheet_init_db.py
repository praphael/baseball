#!/usr/bin/python3

allTables = dict()
# game_type R=regular E=exhibition P=preseason A=allstar O=playoff S=worldseries
#   L=lcs D=divisionseries C=wildcard H=championship 
allTables["boxscore"] = """CREATE TABLE boxscore (
    game_id integer PRIMARY KEY,
    game_type char(1), 
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
    home_triple_plays smallint    
) WITHOUT ROWID"""

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

allTables["extra"]="""CREATE TABLE extra (
    game_id integer PRIMARY KEY,
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
    home_score_inning_25 smallint
) """

allTables["completion"]="""CREATE TABLE completion (
    game_id integer PRIMARY KEY,
    completion_date date,
    completion_park varchar(16),
    visitor_score_int smallint,
    home_score_int smallint,
    outs_int smallint
)"""

allTables["parks"]="""CREATE TABLE parks (
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

allTables["teams"]="""CREATE TABLE teams (
    team_id varchar(8),
    team_league varchar(64),
    team_city varchar(64),
    team_nickname varchar(64),
    team_first smallint,
    team_last smallint
)"""

#"aardd001","Aardsma","David Allan","David","12/27/1981","Denver","Colorado","USA","04/06/2004","08/23/2015",,,,,,,,,,,"R","R","6-05",200,,,,,,,,,
allTables["player"]="""CREATE TABLE player (
    player_num_id smallint PRIMARY KEY, 
    player_id char(8),
    name_last varchar(64),
    name_first varchar(64),
    name_other varchar(64),
    birth date,
    birth_city varchar(64),
    birth_state varchar(64),
    birth_country varchar(64),
    debut date,
    last_game date,
    manager_debut date,
    manager_last_game date,
    coach_debut date,
    coach_last_game date,
    ump_debut date,
    ump_last_game date,
    death date,
    death_city varchar(64),
    death_state varchar(64),
    death_country varchar(64),
    bats char(1),
    throws char(1),
    height varchar(16),
    weight smallint,
    cemetary varchar(64),
    cemetary_city varchar(64),
    cemetary_state varchar(64),
    cemetary_country varchar(64),
    cemetary_note varchar(64),
    birth_name varchar(64),
    name_change varchar(64),
    bat_change char(1),
    hall_of_fame char(3)
) WITHOUT ROWID
"""

# bat_pos P(pitcher), or 1-9 
# field_pos 1=pitcher, 2=catcher, 3=first base, 4=second base, 5=third base
#  6=short stop 7=left field 8=center field, 9=right field, D=designed hitter
allTables["event_start"]="""CREATE TABLE event_start (
    game_id integer,
    event_id smallint,
    player_id smallint,
    team varchar(4),
    bat_pos char(1),
    field_pos char(1),
    PRIMARY KEY(game_id, event_id)
)
"""

# play_id - substituted occured after play_id
# for subs, field_pos is same as starters, or 'R' for pinch runner and 'H' for pinch hitter
allTables["event_sub"]="""CREATE TABLE event_sub (
    game_id integer,
    event_id smallint,
    player_id smallint,
    team varchar(4),
    bat_pos char(1),
    field_pos char(1),
    PRIMARY KEY(game_id, event_id)
)
"""

# pitch sequence data 
# outcome
#    +  following pickoff throw by the catcher
#    *  indicates the following pitch was blocked by the catcher
#    .  marker for play not involving the batter
#    1  pickoff throw to first
#    2  pickoff throw to second
#    3  pickoff throw to third
#    >  Indicates a runner going on the pitch
#    A  automatic strike, usually for pitch timer violation
#    B  ball
#    C  called strike
#    F  foul
#    H  hit batter
#    I  intentional ball
#    K  strike (unknown type)
#    L  foul bunt
#    M  missed bunt attempt
#    N  no pitch (on balks and interference calls)
#    O  foul tip on bunt
#    P  pitchout
#    Q  swinging on pitchout
#    R  foul ball on pitchout
#    S  swinging strike
#    T  foul tip
#    U  unknown or missed pitch
#    V  called ball because pitcher went to his mouth or automatic ball on intentional walk or
#       pitch timer violation
#    X  ball put into play by batter
#    Y  ball put into play on pitchout

# communications from broadcasts
allTables["event_com"]="""CREATE TABLE event_com (
    game_id integer,
    event_id smallint,
    com varchar(256),
    PRIMARY KEY(game_id, event_id)
)"""

# batter_count = 00 (first pitch), 10, 21, etc.
#    uses char to save space
# outcome two char code
#    retrosheet code (if different) description
# code made use '_' to fill both chars
#    AP    appeal play
#    BP    pop up bunt
#    BG    ground ball bunt
# BD BGDP  bunt grounded into double play
# BI BINT  batter interference
#    BL    line drive bunt
# BO BOOT  batting out of turn
#    BP    bunt pop up
# BD BPDP  bunt popped into double play
#    BR    runner hit by batted ball
# C_ C     called third strike
#    COUB  courtesy batter
#    COUF  courtesy fielder
#    COUR  courtesy runner
#    DP    unspecified double play
#    E$    error on $
# F_ F     fly
# FD FDP   fly ball double play
# FU FINT  fan interference
#    FL    foul
#    FO    force out
# G_ G     ground ball
# GD GDP   ground ball double play
# GT GTP   ground ball triple play
#    IF    infield fly rule
# IN INT   interference
# IH IPHR  inside the park home run
# L_ L     line drive
# LD LDP   lined into double play
# LT LTP   lined into triple play
# MR MREV  manager challenge of call on the field
# ND NDP   no double play credited for this play
# OB OBS   obstruction (fielder obstructing a runner)
# PF P     pop fly
# PS PASS  a runner passed another runner and was called out
# RE R$    relay throw from the initial fielder to $ with no out made
# RI RINT  runner interference
#    SF    sacrifice fly
#    SH    sacrifice hit (bunt)
#    TH    throw
# T% TH%   throw to base %
#    TP    unspecified triple play
# UI UINT  umpire interference
# UR UREV  umpire review of call on the field
allTables["event_play"]="""CREATE TABLE event_play (
    game_id integer,
    event_id smallint,
    inning smallint,
    team varchar(4),
    player_id smallint,
    batter_count char(2),
    pitch_seq varchar(32),
    play varchar(64),
    PRIMARY KEY(game_id, event_id)
)"""


# adjustments
# adj_type  B=batter, P=pitcher, R-pitcher responsiblity
allTables["event_player_adj"]="""CREATE TABLE event_player_adj (
    game_id integer,
    event_id smallint,
    player_id smallint,
    adj_type char(1),
    adj char(1),
    PRIMARY KEY(game_id, event_id)
)
"""

allTables["event_lineup_adj"]="""CREATE TABLE event_lineup_adj (
    game_id integer,
    event_id smallint,
    team_id varchar(5),
    adj char(1),
    PRIMARY KEY(game_id, event_id)
)
"""

allTables["event_data_er"]="""CREATE TABLE event_data_er (
    game_id integer,
    event_id smallint,
    player_id smallint,
    smallint er,    
    PRIMARY KEY(game_id, event_id)
)
"""

# field cond: D=dry, S=soaked, W=wet, A=damp, U=unknown;
# precip: Z=drizzle, N=none, R=rain, S=showers, W=snow, U=unknown;
# sky: C=cloudy, D=dome, N=night, O=overcast, S=sunny, U=unknown;
# winddir = FC=fromcf, FL=fromlf, FR=fromrf, LR=ltor, RT=rtol, TC=tocf, TL=tolf, TR=torf, U=unknown.
# Temp(erature) is in degrees Fahrenheit with 0 being the not known value.
# An unknown windspeed is indicated by -1.
# attendance value=0 for 1st game of double-headers also
# game_type R=regular E=exhibition P=preseason A=allstar P=playoff S=worldseries
#   L=lcs D=divisionseries W=wildcard H=championship

allTables["game_info"]="""CREATE TABLE game_info (
    game_id integer PRIMARY KEY,
    time_start_mil smallint,
    daynight char(1),
    innings_sched smallint,
    tiebreak_base char(1),
    use_dh boolean,
    has_pitch_cnt boolean,
    has_pitch_seq boolean,
    home_team_bat_first boolean,
    fieldcond char(1),
    precip char(1),
    sky char(1),
    temp smallint,
    winddir char(1),
    windspeed smallint,
    game_len_mins smallint,
    attendance integer,
    scorer char(8),
    ump_home char(8),
    ump_1b char(8),
    ump_2b char(8),
    ump_3b char(8),
    ump_lf char(8),
    ump_rf char(8),
    win_pitcher char(8),
    loss_pitcher char(8),
    save_pitcher char(8),
    gw_rbi char(8)
)    
"""


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
