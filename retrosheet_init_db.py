#!/usr/bin/python3

allTables = dict()
allViews = dict()

#"aardd001","Aardsma","David Allan","David","12/27/1981","Denver","Colorado","USA","04/06/2004","08/23/2015",,,,,,,,,,,"R","R","6-05",200,,,,,,,,,
allTables["player"]="""CREATE TABLE player (
    player_num_id smallint PRIMARY KEY,
    player_id char(8) NOT NULL,
    name_last char(64) NOT NULL,
    name_first char(64) NOT NULL,
    name_other char(64) NOT NULL,
    birth date,
    birth_city char(64),
    birth_state char(64),
    birth_country char(64),
    debut date,
    last_game date,
    manager_debut date,
    manager_last_game date,
    coach_debut date,
    coach_last_game date,
    ump_debut date,
    ump_last_game date,
    death date,
    death_city char(64),
    death_state char(64),
    death_country char(64),
    bats char(1),
    throws char(1),
    height char(8),
    weight smallint,
    cemetary char(64),
    cemetary_city char(64),
    cemetary_state char(64),
    cemetary_country char(64),
    cemetary_note char(64),
    birth_name char(64),
    name_change char(64),
    bat_change char(1),
    hall_of_fame char(3)
) WITHOUT ROWID
"""


allTables["park"]="""CREATE TABLE park (
    park_num_id smallint PRIMARY_KEY,
    park_id char(5),
    park_name varchar(64),
    park_aka varchar(64),
    park_city varchar(64),
    park_state varchar(4),
    park_open date, 
    park_close date,
    park_league varchar(64),
    notes varchar(128)
)"""

allTables["team"]="""CREATE TABLE team (
    team_num_id smallint PRIMARY KEY,
    team_id varchar(8),
    team_league varchar(64),
    team_city varchar(64),
    team_nickname varchar(64),
    team_first smallint,
    team_last smallint
)"""


# cond bits
# 0 : day (0)  night(1)
# 1-3: field cond: 000 unknown 001 dry, 010 damp 011 wet 100 Soaked, 
# 4-6: precip: 000 U=unknown; 001 N=none, 010 Z=drizzle 011 R=rain, 100 S=showers, 101 W=snow 
# 7-9: sky: 000 U=unknown; 001 S=sunny 010 C=cloudy, 011 D=dome, 100 N=night, 101 O=overcast 
# 10-13: winddir = 0000 U=unknown. 0001 FC=fromcf, 0010 FL=fromlf, 0011 FR=fromrf, 
#           0100 LR=ltor, 0101 RT=rtol, 0110 TC=tocf, 0111 TL=tolf, 1000 TR=torf,
# 14-19: windspeed+1, 0= unknnwn value 
# 20-27: temp:  7 bits (0-128) 0 = unknown value Temperature is in degrees Fahrenheit with 0 being the not known value.

# attendance value=0 for 1st game of double-headers also
#flags 
# 0: has_pitch_cnt
# 1: has_pitch_seq
# 2: htbf
# 3: use_dh
# 4-5: tiebreakbase, e.g. 2
# 6: completed
# 7-8: forfeit 
#    00 = none 
#    01 "V" -- the game was forfeited to the visiting team
#    10 "H" -- the game was forfeited to the home team
#    11 "T" -- the game was ruled a no-decision
# 9-11: protest 
#   000 = none
#   001 "P" -- the game was protested by an unidentified team
#   010 "V" -- a disallowed protest was made by the visiting team
#   011 "H" -- a disallowed protest was made by the home team
#   100 "X" -- an upheld protest was made by the visiting team
#   101 "Y" -- an upheld protest was made by the home team

# game_type_num flags
# 0-2: 0=regular, 1= post, 2 (10)=pre, 3 (11) other exhibition
# 3-5: postseason type: 0=not postseason 1:wildcard, 2=division, 3=league champsionship, 4=world series
# 6-7: 0=single game (not double header), 1=game 1 of DH, 2=game 2 of DH, 3=game 3 of TH
# 8-11: innings_sched

# game_datetime
# 0-12: start time in minutes from 12 AM (military time)
# 13-15: day in month
# 16-18: day in week, Sun=0, Mon=1, etc.
# 20-23: month
# 24-31: year - 1870   
allTables["game_info"]="""CREATE TABLE game_info (
    game_id integer PRIMARY KEY,
    game_datetime integer NOT NULL,
    game_type_num smallint NOT NULL,    
    away_team smallint NOT NULL,
    away_game_num smallint NOT NULL,
    home_team smallint NOT NULL,    
    home_game_num smallint NOT NULL,
    flags smallint NOT NULL,
    park smallint NOT NULL,
    attendance integer NOT NULL,
    cond integer NOT NULL,
    game_duration_min smallint NOT NULL,
    scorer smallint NOT NULL,
    ump_home smallint NOT NULL,
    ump_1b smallint NOT NULL, 
    ump_2b smallint NOT NULL, 
    ump_3b smallint NOT NULL,
    ump_lf smallint NOT NULL,
    ump_rf smallint NOT NULL,
    win_pitcher smallint NOT NULL,
    loss_pitcher smallint NOT NULL,
    save_pitcher smallint NOT NULL, 
    gw_rbi smallint NOT NULL,
    FOREIGN KEY(win_pitcher) REFERENCES player(player_num_id),
    FOREIGN KEY(loss_pitcher) REFERENCES player(player_num_id),
    FOREIGN KEY(save_pitcher) REFERENCES player(player_num_id),
    FOREIGN KEY(gw_rbi) REFERENCES player(player_num_id),
    FOREIGN KEY(park) REFERENCES park(park_num_id),
    FOREIGN KEY(away_team) REFERENCES team(team_num_id),
    FOREIGN KEY(home_team) REFERENCES team(team_num_id)
) WITHOUT ROWID
"""

allTables["ump"] = """CREATE TABLE ump (
    ump_num_id smallint PRIMARY KEY,
    ump_id char(8),
    ump_name char(64)
)"""

allTables["scorer"] = """CREATE TABLE scorer (
    scorer_num_id smallint PRIMARY KEY,
    scorer_id char(8),
    scorer_name char(64)
)"""

allTables["gamelog"] = """CREATE TABLE gamelog (
    game_id integer PRIMARY KEY,
    away_score smallint NOT NULL,
    home_score smallint NOT NULL,
    game_len_outs smallint NOT NULL,
    away_score_inning_123 smallint NOT NULL,
    away_score_inning_456 smallint NOT NULL,
    away_score_inning_789 smallint NOT NULL,
    home_score_inning_123 smallint NOT NULL,
    home_score_inning_456 smallint NOT NULL,
    home_score_inning_789 smallint NOT NULL,
    away_at_bats_hits smallint NOT NULL,
    away_doubles_triples smallint NOT NULL, 
    away_home_runs_rbi smallint NOT NULL,
    away_sac_hit_sac_fly smallint NOT NULL,
    away_hit_by_pitch_walks smallint NOT NULL,
    away_int_walks_strikeouts smallint NOT NULL,
    away_stolen_bases_caught_stealing smallint NOT NULL,
    away_gidp_catcher_interference smallint NOT NULL,
    away_left_on_base_pitchers_used smallint NOT NULL,
    away_indiv_earned_runs_team_earned_runs smallint NOT NULL,
    away_wild_pitches_balks smallint NOT NULL,
    away_putouts_assists smallint NOT NULL,
    away_errors_passed_balls smallint NOT NULL,
    away_double_plays_triple_plays smallint NOT NULL,
    home_at_bats_hits smallint NOT NULL, 
    home_doubles_triples smallint NOT NULL, 
    home_home_runs_rbi smallint NOT NULL,
    home_sac_hit_sac_fly smallint NOT NULL,
    home_hit_by_pitch_walks smallint NOT NULL,
    home_int_walks_strikeouts smallint NOT NULL,
    home_stolen_bases_caught_stealing smallint NOT NULL,
    home_gidp_catcher_interference smallint NOT NULL,
    home_left_on_base_pitchers_used smallint NOT NULL,
    home_indiv_earned_runs_team_earned_runs smallint NOT NULL,
    home_wild_pitches_balks smallint NOT NULL,
    home_putouts_assists smallint NOT NULL,
    home_error_passed_balls smallint NOT NULL,
    home_double_plays_triple_plays smallint NOT NULL
) WITHOUT ROWID"""

# excluded data from boxscores, not present in game_info
    # additional_info varchar(128),
    # acq_info char(1), 

allTables["extra"]="""CREATE TABLE extra (
    game_id integer PRIMARY KEY,
    away_score_inning_101112 smallint NOT NULL,
    away_score_inning_131415 smallint NOT NULL,
    away_score_inning_161718 smallint NOT NULL,
    away_score_inning_192021 smallint NOT NULL,
    away_score_inning_222324 smallint NOT NULL,
    away_score_inning_252627 smallint NOT NULL,
    home_score_inning_101112 smallint NOT NULL,
    home_score_inning_131415 smallint NOT NULL,
    home_score_inning_161718 smallint NOT NULL,
    home_score_inning_192021 smallint NOT NULL,
    home_score_inning_222324 smallint NOT NULL,
    home_score_inning_252627 smallint NOT NULL,
    FOREIGN KEY(game_id) REFERENCES gamelog(game_id)
) """

allTables["completion"]="""CREATE TABLE completion (
    game_id integer PRIMARY KEY,
    completion_date date NOT NULL,
    completion_park char(4) NOT NULL,
    visitor_score_int smallint NOT NULL,
    home_score_int smallint NOT NULL,
    outs_int smallint NOT NULL,
    FOREIGN KEY(game_id) REFERENCES game_info(game_id),
    FOREIGN KEY(completion_park) REFERENCES park(park_num_id)
)"""


# bat_pos 0=P, or 1-9 
# field_pos 0=DH, 1=pitcher, 2=catcher, 3=first base, 4=second base, 5=third base
#  6=short stop 7=left field 8=center field, 9=right field, 
#  10=pinch runner 11=pinch hitter
allTables["event_start"]="""CREATE TABLE event_start (
    game_id_event_id integer PRIMARY KEY,
    player_id smallint,
    team smallint,
    bat_pos_field_pos smallint,
    FOREIGN KEY(player_id) REFERENCES player(player_num_id)
)
"""

# play_id - substituted occured after play_id
# for subs, field_pos is same as starters, 0=DH, 10=pinch hit, 11=pinch run
allTables["event_sub"]="""CREATE TABLE event_sub (
    game_id_event_id integer PRIMARY KEY,
    player_id smallint,
    team smallint,
    bat_pos_field_pos smallint,
    FOREIGN KEY(player_id) REFERENCES player(player_num_id)
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
#    PRIMARY KEY(game_id_event_id)
allTables["event_com"]="""CREATE TABLE event_com (
    game_id_event_id integer PRIMARY KEY,
    com char(256)
)"""

# AP    appeal play
# BP    pop up bunt
# BG    ground ball bunt
# BGDP  bunt grounded into double play
# BINT  batter interference
# BL    line drive bunt
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

# batter-count = (balls << 2) + strikes
#     PRIMARY KEY(game_id_event_id),
allTables["event_play"]="""CREATE TABLE event_play (
    game_id_event_id integer PRIMARY KEY,
    team smallint,
    player_id smallint,
    inning_batter_count smallint,
    pitch_seq char(32),
    play char(64),

    FOREIGN KEY(player_id) REFERENCES player(player_num_id)
)"""


# adjustments
# adj_type  B=batter, P=pitcher, R-pitcher responsiblity
#     PRIMARY KEY(game_id_event_id),

allTables["event_player_adj"]="""CREATE TABLE event_player_adj (
    game_id_event_id integer PRIMARY KEY,
    player_id smallint,
    adj_type smallint,
    adj smallint,
    FOREIGN KEY(player_id) REFERENCES player(player_num_id)
)
"""
# PRIMARY KEY(game_id_event_id)
allTables["event_lineup_adj"]="""CREATE TABLE event_lineup_adj (
    game_id_event_id integer PRIMARY KEY,
    team_id smallint,
    adj smmallint
)
"""

#     PRIMARY KEY(game_id_event_id),
allTables["event_data_er"]="""CREATE TABLE event_data_er (
    game_id_event_id integer PRIMARY KEY,
    player_id smallint,
    er smallint,    
    FOREIGN KEY(player_id) REFERENCES player(player_num_id)
)
"""

###### value tables ######

allTables["day_in_week"] = """CREATE TABLE day_in_week (
    num smallint,
    desc char(3)
)"""

allTables["month"] = """CREATE TABLE month (
    num smallint,
    desc char(3)
)"""

allTables["season"] = """CREATE TABLE season (
    num smallint NOT NULL,
    desc char(8) NOT NULL
)"""

allTables["postseason_series"] = """CREATE TABLE postseason_series (
    num smallint NOT NULL,
    desc char(8) NOT NULL
)"""

allTables["winddir"] = """CREATE TABLE winddir (
    num smallint NOT NULL,
    desc char(8) NOT NULL
)"""

allTables["fieldcond"] = """CREATE TABLE fieldcond (
    num smallint NOT NULL,
    desc char(8) NOT NULL
)"""

allTables["sky"] = """CREATE TABLE sky (
    num smallint,
    desc char(8)
)"""

allTables["precip"] = """CREATE TABLE precip (
    num smallint,
    desc char(8)
)"""

allTables["forfeit"] = """CREATE TABLE forfeit (
    num smallint,
    desc char(8)
)"""

allTables["protest"] = """CREATE TABLE protest (
    num smallint,
    desc char(8)
)"""

allTables["daynight"] = """CREATE TABLE daynight (
    num smallint,
    desc char(8)
)"""
#####  views  #####

allViews["game_info_view"] = """CREATE VIEW game_info_view AS SELECT
        i.game_id,
        (game_datetime >> 24)+1870 AS year,
        mn.desc AS month,
        31 & (game_datetime >> 13) AS day,
        dinw.desc AS day_of_week,
        4095 & game_datetime AS start_time,
        seas.desc AS season,
        post.desc AS post_series,
        (3 & (game_type_num >> 6)) AS dh_num,
        atm.team_nickname AS away_team, 
        i.away_game_num,
        htm.team_nickname AS home_team, 
        i.home_game_num,
        prk.park_name AS park,
        i.attendance,
        i.game_duration_min,
        dn.desc AS daynight,
        fc.desc AS field_cond,
        pr.desc AS precip,
        sk.desc AS sky,
        wd.desc AS winddir,
        31 & (cond >> 14) AS windspeed,
        255 & (cond >> 20) AS temp,
        wpit.name_last AS win_pitcher,
        lpit.name_last AS loss_pitcher,
        spit.name_last AS save_pitcher,
        gwr.name_last AS gw_rbi
    FROM game_info i
    INNER JOIN (SELECT * FROM month) mn
    ON mn.num=(15 & (i.game_datetime >> 20))
    INNER JOIN (SELECT * FROM day_in_week) dinw
    ON dinw.num=(7 & (i.game_datetime >> 16) )
    INNER JOIN (SELECT * FROM season) seas
    ON seas.num=(7 & i.game_type_num)
    INNER JOIN (SELECT * FROM postseason_series) post
    ON post.num=(7 & (i.game_type_num >> 3) )
    INNER JOIN (SELECT * FROM daynight) dn
    ON dn.num=(1 & i.cond) 
    INNER JOIN (SELECT * FROM fieldcond) fc
    ON fc.num=(7 & i.cond >> 1)
    INNER JOIN (SELECT * FROM precip) pr
    ON pr.num=(7 & i.cond >> 4)
    INNER JOIN (SELECT * FROM sky) sk
    ON sk.num=(7 & (i.cond >> 7) )
    INNER JOIN (SELECT * FROM winddir) wd
    ON wd.num=(7 & (i.cond >> 10) )
    INNER JOIN (SELECT * FROM team) htm
    ON htm.team_num_id=home_team
    INNER JOIN (SELECT * FROM team) atm
    ON atm.team_num_id=away_team
    INNER JOIN (SELECT * FROM player) wpit
    ON wpit.player_num_id=i.win_pitcher
    INNER JOIN (SELECT * FROM player) lpit
    ON lpit.player_num_id=i.loss_pitcher
    INNER JOIN (SELECT * FROM player) spit
    ON spit.player_num_id=i.save_pitcher
    INNER JOIN (SELECT * FROM player) gwr
    ON gwr.player_num_id=i.gw_rbi
    INNER JOIN (SELECT * FROM park) prk
    ON prk.park_num_id=i.park
"""

allViews["gamelog_view"] = """CREATE VIEW gamelog_view AS SELECT
    l.game_id,
    l.away_score,
    l.home_score,
    l.game_len_outs,
    v.year,
    v.month,
    v.day,
    v.day_of_week,
    v.start_time,
    v.season,
    v.post_series,
    v.dh_num,
    v.away_team, 
    v.away_league,
    v.away_game_num,
    v.home_team, 
    v.home_league,
    v.home_game_num,
    v.park,
    v.attendance,
    v.game_duration_min,
    v.field_cond,
    v.precip,
    v.sky,
    v.winddir,
    v.windspeed,
    v.temp,
    v.win_pitcher,
    v.loss_pitcher,
    v.save_pitcher,
    v.gw_rbi,
    31 & l.away_score_inning_12345 AS away_score_inning_1,
    (31 << 5) & l.away_score_inning_12345 AS away_score_inning_2,
    (31 << 10) & l.away_score_inning_12345 AS away_score_inning_3,
    (31 << 15) & l.away_score_inning_12345 AS away_score_inning_4,
    (31 << 20) & l.away_score_inning_12345 AS away_score_inning_5,
    31 & l.away_score_inning_6789 AS away_score_inning_6,
    (31 << 5) & l.away_score_inning_6789 AS away_score_inning_7,
    (31 << 10) & l.away_score_inning_6789 AS away_score_inning_8,
    (31 << 15) & l.away_score_inning_6789 AS away_score_inning_9,
    15 & e.away_score_inning_101112 AS away_score_inning_10,
    (15 << 4) & e.away_score_inning_101112 AS away_score_inning_11,
    (15 << 8) & e.away_score_inning_101112 AS away_score_inning_12,
    15 & e.away_score_inning_131415 AS away_score_inning_13,
    (15 << 4) & e.away_score_inning_131415 AS away_score_inning_14,
    (15 << 8) & e.away_score_inning_131415 AS away_score_inning_15,
    15 & e.away_score_inning_161718 AS away_score_inning_16,
    (15 << 4) & l.away_score_inning_161718 AS away_score_inning_17,
    (15 << 8) & l.away_score_inning_161718 AS away_score_inning_18,
    15 & e.away_score_inning_192021 AS away_score_inning_19,
    (15 << 4) & e.away_score_inning_192021 AS away_score_inning_20,
    (15 << 8) & e.away_score_inning_192021 AS away_score_inning_21,
    15 & e.away_score_inning_222324 AS away_score_inning_22,
    (15 << 4) & e.away_score_inning_222324 AS away_score_inning_23,
    (15 << 8) & e.away_score_inning_222324 AS away_score_inning_24,
    255 & l.away_at_bats_hits AS away_at_bats,
    (255 << 8) & l.away_at_bats_hits AS away_hits,
    255 & l.away_doubles_triples AS away_doubles,
    (255 << 8) & l.away_doubles_triples AS away_triples,
    255 & l.away_home_runs_rbi AS away_home_runs,
    (255 << 8) & l.away_home_runs_rbi AS away_home_rbi,
    255 & l.away_sac_hit_sac_fly AS away_sac_hit,
    (255 << 8) & l.away_sac_hit_sac_fly AS away_sac_fly,
    255 & l.away_hit_by_pitch_walks AS away_hit_by_pitch,
    (255 << 8) & l.away_hit_by_pitch_walks AS away_walks,
    255 & l.away_int_walks_strikeouts AS away_int_walks,
    (255 << 8) & l.away_int_walks_strikeouts AS away_strikeouts,
    255 & l.away_stolen_bases_caught_stealing AS away_stolen_bases,
    (255 << 8) & l.away_stolen_bases_caught_stealing AS away_caught_stealing,
    255 & l.away_gidp_catcher_interference AS away_gidp,
    (255 << 8) & l.away_gidp_catcher_interference AS away_gidp,
    255 & l.away_left_on_base_pitchers_used AS away_left_on_base,
    (255 << 8) & l.away_left_on_base_pitchers_used AS away_pitchers_used,
    255 & l.away_indiv_earned_runs_team_earned_runs AS away_indiv_earned_runs,
    (255 << 8) & l.away_indiv_earned_runs_team_earned_runs AS away_team_earned_runs,
    255 & l.away_wild_pitches_balks AS away_wild_pitches,
    (255 << 8) & l.away_wild_pitches_balks AS away_balks,
    255 & l.away_putouts_assists AS away_putouts,
    (255 << 8) & l.away_putouts_assists AS away_assists,
    255 & l.away_errors_passed_balls AS away_errors,
    (255 << 8) & l.away_errors_passed_balls AS away_passed_balls,
    255 & l.away_double_plays_triple_plays AS away_double_plays, 
    (255 << 8) & l.away_double_plays_triple_plays AS away_triple_plays, 
    31 & l.home_score_inning_12345 AS home_score_inning_1,
    (31 << 5) & l.home_score_inning_12345 AS home_score_inning_2,
    (31 << 10) & l.home_score_inning_12345 AS home_score_inning_3,
    (31 << 15) & l.home_score_inning_12345 AS home_score_inning_4,
    (31 << 20) & l.home_score_inning_12345 AS home_score_inning_5,
    31 & l.home_score_inning_6789 AS home_score_inning_6,
    (31 << 5) & l.home_score_inning_6789 AS home_score_inning_7,
    (31 << 10) & l.home_score_inning_6789 AS home_score_inning_8,
    (31 << 15) & l.home_score_inning_6789 AS home_score_inning_9,
    15 & e.home_score_inning_101112 AS home_score_inning_10,
    (15 << 4) & e.home_score_inning_101112 AS home_score_inning_11,
    (15 << 8) & e.home_score_inning_101112 AS home_score_inning_12,
    15 & e.home_score_inning_131415 AS home_score_inning_13,
    (15 << 4) & e.home_score_inning_131415 AS home_score_inning_14,
    (15 << 8) & e.home_score_inning_131415 AS home_score_inning_15,
    15 & e.home_score_inning_161718 AS home_score_inning_16,
    (15 << 4) & e.home_score_inning_161718 AS home_score_inning_17,
    (15 << 8) & e.home_score_inning_161718 AS home_score_inning_18,
    15 & e.home_score_inning_192021 AS home_score_inning_19,
    (15 << 4) & e.home_score_inning_192021 AS home_score_inning_20,
    (15 << 8) & e.home_score_inning_192021 AS home_score_inning_21,
    15 & e.home_score_inning_222324 AS home_score_inning_22,
    (15 << 4) & e.home_score_inning_222324 AS home_score_inning_23,
    (15 << 8) & e.home_score_inning_222324 AS home_score_inning_24,
    255 & l.home_at_bats_hits AS home_at_bats,
    (255 << 8) & l.home_at_bats_hits AS home_hits,
    255 & l.home_doubles_triples AS home_doubles,
    (255 << 8) & l.home_doubles_triples AS home_triples,
    255 & l.home_home_runs_rbi AS home_home_runs,
    (255 << 8) & l.home_home_runs_rbi AS home_home_rbi,
    255 & l.home_sac_hit_sac_fly AS home_sac_hit,
    (255 << 8) & l.home_sac_hit_sac_fly AS home_sac_fly,
    255 & l.home_hit_by_pitch_walks AS home_hit_by_pitch,
    (255 << 8) & l.home_hit_by_pitch_walks AS home_walks,
    255 & l.home_int_walks_strikeouts AS home_int_walks,
    (255 << 8) & l.home_int_walks_strikeouts AS home_strikeouts,
    255 & l.home_stolen_bases_caught_stealing AS home_stolen_bases,
    (255 << 8) & l.home_stolen_bases_caught_stealing AS home_caught_stealing,
    255 & l.home_gidp_catcher_interference AS home_gidp,
    (255 << 8) & l.home_gidp_catcher_interference AS home_gidp,
    255 & l.home_left_on_base_pitchers_used AS home_left_on_base,
    (255 << 8) & l.home_left_on_base_pitchers_used AS home_pitchers_used,
    255 & l.home_indiv_earned_runs_team_earned_runs AS home_indiv_earned_runs,
    (255 << 8) & l.home_indiv_earned_runs_team_earned_runs AS home_team_earned_runs,
    255 & l.home_wild_pitches_balks AS home_wild_pitches,
    (255 << 8) & l.home_wild_pitches_balks AS home_balks,
    255 & l.home_putouts_assists AS home_putouts,
    (255 << 8) & l.home_putouts_assists AS home_assists,
    255 & l.home_errors_passed_balls AS home_errors,
    (255 << 8) & l.home_errors_passed_balls AS home_passed_balls,
    255 & l.home_double_plays_triple_plays AS home_double_plays, 
    (255 << 8) & l.home_double_plays_triple_plays AS home_triple_plays
    FROM gamelog l
    INNER JOIN (SELECT * FROM extra) e
    ON l.game_id=e.game_id
    INNER JOIN (SELECT * FROM game_info_view) v
    ON e.game_id=v.game_id
"""

allValues = dict()
allValues["day_in_week"] = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
allValues["month"] = ("", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
allValues["season"] = ("Reg", "Post", "Pre", "Other")
# 0=not postseason 1:wildcard, 2=division, 3=league champsionship, 4=world series
allValues["postseason_series"] = ("", "Wildcard", "Division", "League", "World Series")

allValues["daynight"] = ("Day", "Night")
allValues["fieldcond"] = ("", "Dry", "Damp", "Wet", "Soaked")
allValues["precip"] = ("", "None", "Drizzle", "Rain", "Showers", "Snow")
allValues["sky"] = ("", "Sunny", "Cloudy", "Overcast", "Dome", "Night")
allValues["winddir"] = ("", "From CF", "From LF", "From RF", "LF to RF")
allValues["winddir"] += ("RF to LF", "To CF", "To LF", "To RF")
allValues["forfeit"] = ("", "Away", "Home", "No Decision")
allValues["protest"] = ("", "Unidentified", "Disallow Away", "Disallow Home", "Upheld Away", "Upheld Home")


# dummy value for player, park and team with pkay value of 0
# to satisify FOREIGN KEY constraings but avoid NULL values
def insertDummyValues(cur):
    stmt = "INSERT INTO player VALUES(0, '', '', '', '', '', '', '', ''"
    stmt += ", '', '', '', '', '', '', '', '', '', '', '', '', '', ''"
    stmt += ", 0, '', '', '', '', '', '', '', '', '', '')"
    cur.execute(stmt)
    stmt = "INSERT INTO park VALUES(0, '', '', '', '', '', '', '', '', '')"
    cur.execute(stmt)
    stmt = "INSERT INTO team VALUES(0, '', '', '', '', '', '')"
    cur.execute(stmt)


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
        #print(createStmt)
        cur.execute(createStmt)

    for tbl, vals in allValues.items():
        i = 0
        for v in vals:
            stmt = f"INSERT INTO {tbl} VALUES({i}, '{v}')"
            #print(stmt)
            cur.execute(stmt)
            i += 1
    
    insertDummyValues(cur)
    conn.commit()
    conn.close()
