#!/usr/bin/python3
import sys
import os

allTables = dict()
allViews = dict()

#"aardd001","Aardsma","David Allan","David","12/27/1981","Denver","Colorado","USA","04/06/2004","08/23/2015",,,,,,,,,,,"R","R","6-05",200,,,,,,,,,
allTables["player"]="""CREATE TABLE player (
    player_num_id smallint PRIMARY KEY,
    player_id char(8),
    name_last char(64) NOT NULL,
    name_first char(64) NOT NULL,
    name_other char(64) NOT NULL,
    birth char(12),
    birth_city char(64),
    birth_state char(64),
    birth_country char(64),
    debut char(12),
    last_game char(12),
    manager_debut char(12),
    manager_last_game char(12),
    coach_debut char(12),
    coach_last_game char(12),
    ump_debut char(12),
    ump_last_game char(12),
    death char(12),
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
) """ # WITHOUT ROWID

allTables["park"]="""CREATE TABLE park (
    park_id char(5) PRIMARY KEY,
    park_name varchar(64),
    park_aka varchar(64),
    park_city varchar(64),
    park_state varchar(4),
    park_open char(12), 
    park_close char(12),
    park_league varchar(64),
    notes varchar(128)
)"""

allTables["team"]="""CREATE TABLE team (
    team_id char(3) PRIMARY KEY,
    team_league varchar(64),
    team_city varchar(64),
    team_nickname varchar(64),
    team_first smallint,
    team_last smallint
)"""

allTables["umpire"] = """CREATE TABLE umpire (
    ump_num_id smallint PRIMARY KEY,
    ump_id char(8),
    ump_name_last char(64),
    ump_name_first char(64)
)"""

allTables["scorer"] = """CREATE TABLE scorer (
    scorer_num_id smallint PRIMARY KEY,
    scorer_id char(8),
    scorer_name char(64)
)"""

# cond bits
# 0 : day (0)  night(1)
# 1-3: field cond: 000 unknown 001 dry, 010 damp 011 wet 100 Soaked, 
# 4-6: precip: 000 U=unknown; 001 N=none, 010 Z=drizzle 011 R=rain, 100 S=showers, 101 W=snow 
# 7-9: sky: 000 U=unknown; 001 S=sunny 010 C=cloudy, 011 D=dome, 100 N=night, 101 O=overcast 
# 10-13: winddir = 0000 U=unknown. 0001 FC=fromcf, 0010 FL=fromlf, 0011 FR=fromrf, 
#           0100 LR=ltor, 0101 RT=rtol, 0110 TC=tocf, 0111 TL=tolf, 1000 TR=torf,
# 14-20: windspeed+1, 0= unknnwn value 
# 21-27: temp:  7 bits (0-128) 0 = unknown value Temperature is in degrees Fahrenheit with 0 being the not known value.

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

# game_type_num 
# 0-2: 0=regular, 1= post, 2 (10)=pre, 3 (11) other exhibition
# 3-5: postseason type: 0=not postseason 1:wildcard, 2=division, 3=league champsionship, 4=world series
# 6-7: 0=single game (not double header), 1=game 1 of DH, 2=game 2 of DH, 3=game 3 of TH
# 8-11: innings_sched
 
# store year/month as separate fields for easier search/indexing
allTables["game_info"]="""CREATE TABLE game_info (
    game_id integer PRIMARY KEY,
    game_date char(12) NOT NULL,
    year smallint NOT NULL,
    month smallint NOT NULL,
    dow smallint,
    start_time smallint,
    game_type_num smallint NOT NULL,    
    away_team char(3) NOT NULL,
    away_league char(3),
    away_division char(8),
    away_game_num smallint,
    home_team char(3) NOT NULL,
    home_league char(3),
    home_division char(8),
    home_game_num smallint,
    flags smallint NOT NULL,
    park char(5) NOT NULL,
    attendance integer,
    cond integer,
    game_duration_min smallint,
    scorer_num_id smallint,
    ump_home_num_id smallint,
    ump_1b_num_id smallint,
    ump_2b_num_id smallint,
    ump_3b_num_id smallint,
    ump_lf_num_id smallint,
    ump_rf_num_id smallint,
    win_pitcher_num_id smallint,
    loss_pitcher_num_id smallint,
    save_pitcher_num_id smallint,
    gw_rbi_num_id smallint,
    FOREIGN KEY(win_pitcher_num_id) REFERENCES player(player_num_id),
    FOREIGN KEY(loss_pitcher_num_id) REFERENCES player(player_num_id),
    FOREIGN KEY(save_pitcher_num_id) REFERENCES player(player_num_id),
    FOREIGN KEY(gw_rbi_num_id) REFERENCES player(player_num_id),
    FOREIGN KEY(scorer_num_id) REFERENCES scorer(scorer_num_id), 
    FOREIGN KEY(ump_home_num_id) REFERENCES ump(ump_num_id), 
    FOREIGN KEY(ump_1b_num_id) REFERENCES ump(ump_num_id), 
    FOREIGN KEY(ump_2b_num_id) REFERENCES ump(ump_num_id), 
    FOREIGN KEY(ump_3b_num_id) REFERENCES ump(ump_num_id), 
    FOREIGN KEY(ump_lf_num_id) REFERENCES ump(ump_num_id), 
    FOREIGN KEY(ump_rf_num_id) REFERENCES ump(ump_num_id), 
    FOREIGN KEY(park) REFERENCES park(park_id),
    FOREIGN KEY(away_team) REFERENCES team(team_id),
    FOREIGN KEY(home_team) REFERENCES team(team_id)
)
"""
# WITHOUT ROWID



allTables["gamelog"] = """CREATE TABLE gamelog (
    game_id integer PRIMARY KEY,
    away_score smallint NOT NULL,
    home_score smallint NOT NULL,
    game_len_outs smallint NOT NULL,
    away_at_bats smallint,
    away_hits smallint,
    away_doubles smallint,
    away_triples smallint,
    away_home_runs smallint,
    away_rbi smallint, 
    away_sac_hit smallint,
    away_sac_fly smallint,
    away_hit_by_pitch smallint,
    away_walks smallint,
    away_int_walks smallint,
    away_strikeouts smallint,
    away_stolen_bases smallint,
    away_caught_stealing smallint,
    away_gidp smallint,
    away_catcher_interference smallint,
    away_left_on_base smallint,
    away_pitchers_used smallint,
    away_indiv_earned_runs smallint,
    away_team_earned_runs smallint,
    away_wild_pitches smallint,
    away_balks smallint,
    away_putouts smallint,
    away_assists smallint,
    away_errors smallint,
    away_passed_balls smallint,
    away_double_plays smallint,
    away_triple_plays smallint,
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
 )""" # WITHOUT ROWID

# excluded data from boxscores, not present in game_info
    # additional_info varchar(128),
    # acq_info char(1), 

allTables["score_by_inning"]="""CREATE TABLE score_by_inning (
    game_id integer,
    inning smallint,
    home_score smallint,
    away_score smallint,
    PRIMARY KEY(game_id, inning),
    FOREIGN KEY(game_id) REFERENCES gamelog(game_id)
) """

allTables["completion"]="""CREATE TABLE completion (
    game_id integer PRIMARY KEY,
    completion_date char(12) NOT NULL,
    completion_park char(5) NOT NULL,
    visitor_score_int smallint NOT NULL,
    home_score_int smallint NOT NULL,
    outs_int smallint NOT NULL,
    FOREIGN KEY(game_id) REFERENCES game_info(game_id),
    FOREIGN KEY(completion_park) REFERENCES park(park_id)
)"""


# bat_pos 0=P, or 1-9 
# field_pos 0=DH, 1=pitcher, 2=catcher, 3=first base, 4=second base, 5=third base
#  6=short stop 7=left field 8=center field, 9=right field, 
#  10=pinch runner 11=pinch hitter
allTables["event_start"]="""CREATE TABLE event_start (
    game_id integer,
    event_id smallint,
    player_num_id smallint,
    team char(3),
    bat_pos smallint,
    field_pos smallint,
    PRIMARY KEY(game_id, event_id),
    FOREIGN KEY(player_num_id) REFERENCES player(player_num_id)
)
"""

# play_id - substituted occured after play_id
# for subs, field_pos is same as starters, 0=DH, 10=pinch hit, 11=pinch run
allTables["event_sub"]="""CREATE TABLE event_sub (
    game_id integer,
    event_id smallint,
    player_num_id smallint,
    team char(3),
    bat_pos smallint,
    field_pos smallint,
    PRIMARY KEY(game_id, event_id),
    FOREIGN KEY(player_num_id) REFERENCES player(player_num_id)
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
    game_id integer,
    event_id smallint,
    com char(256),
    PRIMARY KEY(game_id, event_id)
)"""

# AP    appeal play
# BP    pop up bunt
# BG    ground ball bunt
# BGDP  bunt grounded into double play
# BINT  batter interference
# BL    line drive bunt
# BOOT  batting out of turn
# BP    bunt pop up
# BPDP  bunt popped into double play
# BR    runner hit by batted ball
# C     called third strike
# COUB  courtesy batter
# COUF  courtesy fielder
# COUR  courtesy runner
# DP    unspecified double play
# E$    error on $
# F     fly
# FDP   fly ball double play
# FINT  fan interference
# FL    foul
# FO    force out
# G     ground ball
# GDP   ground ball double play
# GTP   ground ball triple play
# IF    infield fly rule
# INT   interference
# IPHR  inside the park home run
# L     line drive
# LDP   lined into double play
# LTP   lined into triple play
# MREV  manager challenge of call on the field
# NDP   no double play credited for this play
# OBS   obstruction (fielder obstructing a runner)
# P     pop fly
# PASS  a runner passed another runner and was called out
# R$    relay throw from the initial fielder to $ with no out made
# RINT  runner interference
# SF    sacrifice fly
# SH    sacrifice hit (bunt)
# TH    throw
# TH%   throw to base %
# TP    unspecified triple play
# UINT  umpire interference
# UREV  umpire review of call on the field

# batter-count = (balls << 2) + strikes
#     PRIMARY KEY(game_id_event_id),
allTables["event_play"]="""CREATE TABLE event_play (
    game_id integer,
    event_id smallint,
    team char(3),
    player_num_id smallint,
    inning smallint,
    batter_count char(2),
    pitch_seq char(32),
    play char(64),
    PRIMARY KEY(game_id, event_id),
    FOREIGN KEY(player_num_id) REFERENCES player(player_num_id)
)"""


# adjustments
# adj_type  0=batter, 1=runner, 2=pitcher, 3:pitcher responsiblity
#     PRIMARY KEY(game_id_event_id),

allTables["event_player_adj"]="""CREATE TABLE event_player_adj (
    game_id integer,
    event_id smallint,
    player_num_id smallint,
    adj_type smallint,
    adj char(1),
    PRIMARY KEY(game_id, event_id),
    FOREIGN KEY(player_num_id) REFERENCES player(player_num_id)
)
"""
# PRIMARY KEY(game_id_event_id)
allTables["event_lineup_adj"]="""CREATE TABLE event_lineup_adj (
    game_id integer,
    event_id smallint,
    team_id char(3),
    adj smallint,
    PRIMARY KEY(game_id, event_id)
)
"""

#     PRIMARY KEY(game_id_event_id),
allTables["event_data_er"]="""CREATE TABLE event_data_er (
    game_id integer,
    event_id smallint,
    player_num_id smallint,
    er smallint,
    PRIMARY KEY(game_id, event_id),
    FOREIGN KEY(player_num_id) REFERENCES player(player_num_id)
)
"""

###### value tables ######

allTables["day_in_week"] = """CREATE TABLE day_in_week (
    num smallint PRIMARY KEY,
    d char(3) NOT NULL
)"""

allTables["month"] = """CREATE TABLE month (
    num smallint PRIMARY KEY,
    d char(3) NOT NULL
)"""

allTables["season"] = """CREATE TABLE season (
    num smallint PRIMARY KEY,
    d char(16) NOT NULL
)"""

allTables["postseason_series"] = """CREATE TABLE postseason_series (
    num smallint PRIMARY KEY,
    d char(16) NOT NULL
)"""

allTables["winddir"] = """CREATE TABLE winddir (
    num smallint PRIMARY KEY,
    d char(16) NOT NULL
)"""

allTables["fieldcond"] = """CREATE TABLE fieldcond (
    num smallint PRIMARY KEY,
    d char(16) NOT NULL
)"""

allTables["sky"] = """CREATE TABLE sky (
    num smallint PRIMARY KEY,
    d char(16) NOT NULL
)"""

allTables["precip"] = """CREATE TABLE precip (
    num smallint PRIMARY KEY,
    d char(16) NOT NULL
)"""

allTables["forfeit"] = """CREATE TABLE forfeit (
    num smallint PRIMARY KEY,
    d char(16) NOT NULL
)"""

allTables["protest"] = """CREATE TABLE protest (
    num smallint PRIMARY KEY,
    d char(16) NOT NULL
)"""

allTables["daynight"] = """CREATE TABLE daynight (
    num smallint PRIMARY KEY,
    d char(16) NOT NULL
)"""

allTables["play_desc"] = """CREATE TABLE play_desc (
    k char(5) PRIMARY KEY,
    d char(32) NOT NULL
)"""

allTables["mod_desc"] = """CREATE TABLE mod_desc (
    k char(5) PRIMARY KEY,
    d char(32) NOT NULL
)"""

allTables["field_pos_desc"] = """CREATE TABLE field_pos_desc (
    pos smallint PRIMARY KEY,
    d char(32) NOT NULL
)"""

#####  views  #####

allViews["game_info_view"] = """CREATE VIEW game_info_view AS SELECT
        i.game_id,
        i.game_date,
        i.year,
        i.month,
        i.dow,
        i.start_time,
        seas.d AS season,
        post.d AS post_series,
        (3 & (game_type_num >> 6)) AS dh_num,
        atm.team_id AS away_team, 
        atm.team_city AS away_team_city, 
        atm.team_nickname AS away_team_name, 
        i.away_league,
        i.away_division,
        i.away_game_num,
        htm.team_id AS home_team, 
        htm.team_city AS home_team_city, 
        htm.team_nickname AS home_team_name,
        i.home_league,
        i.home_division,
        i.home_game_num,
        i.park AS park_id,
        prk.park_name AS park,
        i.attendance,
        i.game_duration_min AS duration,
        dn.d AS daynight,
        fc.d AS field_cond,
        pr.d AS precip,
        sk.d AS sky,
        wd.d AS winddir,
        127 & (cond >> 14) AS windspeed,
        127 & (cond >> 21) AS temp,
        (1 & (flags >> 2)) AS home_team_bat_first,
        (1 & (flags >> 3)) AS use_dh,
        (3 & (flags >> 4)) AS tiebreakbase,
        (1 & (flags >> 6)) AS complete,
        (15 & (game_type_num >> 8)) AS inn_sched, 
        forf.d AS forfeit,
        prot.d AS protest,
        wpit.name_last||', '||SUBSTR(wpit.name_other, 0, 2) AS win_pitcher,
        lpit.name_last||', '||SUBSTR(lpit.name_other, 0, 2) AS loss_pitcher,
        spit.name_last||', '||SUBSTR(spit.name_other, 0, 2) AS save_pitcher,
        gwr.name_last||', '||SUBSTR(gwr.name_other, 0, 2) AS gw_rbi
    FROM game_info i
    LEFT JOIN (SELECT * FROM season) seas
    ON seas.num=(7 & i.game_type_num)
    LEFT JOIN (SELECT * FROM postseason_series) post
    ON post.num=(7 & (i.game_type_num >> 3) )
    LEFT JOIN (SELECT * FROM daynight) dn
    ON dn.num=(1 & i.cond) 
    LEFT JOIN (SELECT * FROM fieldcond) fc
    ON fc.num=(7 & (i.cond >> 1))
    LEFT JOIN (SELECT * FROM precip) pr
    ON pr.num=(7 & (i.cond >> 4))
    LEFT JOIN (SELECT * FROM sky) sk
    ON sk.num=(7 & (i.cond >> 7) )
    LEFT JOIN (SELECT * FROM winddir) wd
    ON wd.num=(7 & (i.cond >> 10) )
    LEFT JOIN (SELECT * FROM team) htm
    ON htm.team_id=i.home_team
    LEFT JOIN (SELECT * FROM team) atm
    ON atm.team_id=i.away_team
    LEFT JOIN (SELECT * FROM player) wpit
    ON wpit.player_num_id=i.win_pitcher_num_id
    LEFT JOIN (SELECT * FROM player) lpit
    ON lpit.player_num_id=i.loss_pitcher_num_id
    LEFT JOIN (SELECT * FROM player) spit
    ON spit.player_num_id=i.save_pitcher_num_id
    LEFT JOIN (SELECT * FROM player) gwr
    ON gwr.player_id=i.gw_rbi_num_id
    LEFT JOIN (SELECT * FROM park) prk
    ON prk.park_id=i.park
    LEFT JOIN (SELECT * FROM forfeit) forf
    ON forf.num=(3 & (i.flags >> 7))
    LEFT JOIN (SELECT * FROM protest) prot
    ON prot.num=(7 & (i.flags >> 9))
"""

game_info_view_clickhouse = """CREATE VIEW game_info_view AS SELECT
        i.game_id,
        i.game_date,
        i.year,
        i.month,
        i.dow,
        i.start_time,
        seas.d AS season,
        post.d AS post_series,
        bitAnd(3, bitShiftRight(game_type_num, 6)) AS dh_num,
        atm.team_id AS away_team, 
        atm.team_city AS away_team_city, 
        atm.team_nickname AS away_team_name, 
        i.away_league,
        i.away_division,
        i.away_game_num,
        htm.team_id AS home_team, 
        htm.team_city AS home_team_city, 
        htm.team_nickname AS home_team_name,
        i.home_league,
        i.home_division,
        i.home_game_num,
        i.park AS park_id,
        prk.park_name AS park,
        i.attendance,
        i.game_duration_min AS duration,
        dn.d AS daynight,
        fc.d AS field_cond,
        pr.d AS precip,
        sk.d AS sky,
        wd.d AS winddir,
        bitAnd(127, bitShiftRight(cond, 14)) AS windspeed,
        bitAnd(127, bitShiftRight(cond, 21)) AS temp,
        bitAnd(1, bitShiftRight(flags, 2)) AS home_team_bat_first,
        bitAnd(1, bitShiftRight(flags, 3)) AS use_dh,
        bitAnd(3, bitShiftRight(flags, 4)) AS tiebreakbase,
        bitAnd(1, bitShiftRight(flags, 6)) AS complete,
        forf.d AS forfeit,
        prot.d AS protest,
        wpit.name_last||', '||SUBSTR(wpit.name_other, 1, 2) AS win_pitcher,
        lpit.name_last||', '||SUBSTR(lpit.name_other, 1, 2) AS loss_pitcher,
        spit.name_last||', '||SUBSTR(spit.name_other, 1, 2) AS save_pitcher,
        gwr.name_last||', '||SUBSTR(gwr.name_other, 1, 2) AS gw_rbi
    FROM game_info i
    LEFT JOIN (SELECT * FROM season) seas
    ON seas.num=bitAnd(7, i.game_type_num)
    LEFT JOIN (SELECT * FROM postseason_series) post
    ON post.num=bitAnd(7, bitShiftRight(i.game_type_num, 3))
    LEFT JOIN (SELECT * FROM daynight) dn
    ON dn.num=bitAnd(1, i.cond) 
    LEFT JOIN (SELECT * FROM fieldcond) fc
    ON fc.num=bitAnd(7, bitShiftRight(i.cond, 1))
    LEFT JOIN (SELECT * FROM precip) pr
    ON pr.num=bitAnd(7, bitShiftRight(i.cond, 4))
    LEFT JOIN (SELECT * FROM sky) sk
    ON sk.num=bitAnd(7, bitShiftRight(i.cond, 7))
    LEFT JOIN (SELECT * FROM winddir) wd
    ON wd.num=bitAnd(7, bitShiftRight(i.cond, 10))
    LEFT JOIN (SELECT * FROM team) htm
    ON htm.team_id=i.home_team
    LEFT JOIN (SELECT * FROM team) atm
    ON atm.team_id=i.away_team
    LEFT JOIN (SELECT * FROM player) wpit
    ON wpit.player_num_id=i.win_pitcher_num_id
    LEFT JOIN (SELECT * FROM player) lpit
    ON lpit.player_num_id=i.loss_pitcher_num_id
    LEFT JOIN (SELECT * FROM player) spit
    ON spit.player_num_id=i.save_pitcher_num_id
    LEFT JOIN (SELECT * FROM player) gwr
    ON gwr.player_num_id=i.gw_rbi_num_id
    LEFT JOIN (SELECT * FROM park) prk
    ON prk.park_id=i.park
    LEFT JOIN (SELECT * FROM forfeit) forf
    ON forf.num=bitAnd(3, bitShiftRight(i.flags, 7))
    LEFT JOIN (SELECT * FROM protest) prot
    ON prot.num=bitAnd(7, bitShiftRight(i.flags, 9))
"""

allViews["gamelog_view"] = """CREATE VIEW gamelog_view AS SELECT
    l.game_id,
    l.away_score,
    l.home_score,
    l.game_len_outs,
    i.game_date,
    i.year,
    i.month,
    i.dow,
    i.start_time,
    i.season,
    i.post_series,
    i.dh_num,
    i.away_team, 
    i.away_team_city, 
    i.away_team_name, 
    i.away_league,
    i.away_game_num,
    i.home_team,
    i.home_team_city, 
    i.home_team_name,
    i.home_league,
    i.home_game_num,
    i.park,
    i.attendance,
    i.game_duration_min AS duration,
    i.daynight,
    i.field_cond,
    i.precip,
    i.sky,
    i.winddir,
    i.windspeed,
    i.temp,
    i.home_team_bat_first,
    i.use_dh,
    i.complete,
    i.forfeit,
    i.protest,
    i.win_pitcher,
    i.loss_pitcher,
    i.save_pitcher,
    i.gw_rbi,
    l.away_at_bats,
    l.away_hits,
    l.away_doubles,
    l.away_triples,
    l.away_home_runs,
    l.away_rbi, 
    l.away_sac_hit,
    l.away_sac_fly,
    l.away_hit_by_pitch,
    l.away_walks,
    l.away_int_walks,
    l.away_strikeouts,
    l.away_stolen_bases,
    l.away_caught_stealing,
    l.away_gidp,
    l.away_catcher_interference,
    l.away_left_on_base,
    l.away_pitchers_used,
    l.away_indiv_earned_runs,
    l.away_team_earned_runs,
    l.away_wild_pitches,
    l.away_balks,
    l.away_putouts,
    l.away_assists,
    l.away_errors,
    l.away_passed_balls,
    l.away_double_plays,
    l.away_triple_plays,
    l.home_at_bats,
    l.home_hits, 
    l.home_doubles,
    l.home_triples, 
    l.home_home_runs,
    l.home_rbi,
    l.home_sac_hit,
    l.home_sac_fly,
    l.home_hit_by_pitch,
    l.home_walks,
    l.home_int_walks,
    l.home_strikeouts,
    l.home_stolen_bases,
    l.home_caught_stealing,
    l.home_gidp,
    l.home_catcher_interference,
    l.home_left_on_base,
    l.home_pitchers_used,
    l.home_indiv_earned_runs,
    l.home_team_earned_runs,
    l.home_wild_pitches, 
    l.home_balks,
    l.home_putouts,
    l.home_assists,
    l.home_errors,
    l.home_passed_balls,
    l.home_double_plays,
    l.home_triple_plays,
    s1.home_score AS h1,
    s1.away_score AS a1,
    s2.home_score AS h2,
    s2.away_score AS a2,
    s3.home_score AS h3,
    s3.away_score AS a3,
    s4.home_score AS h4,
    s4.away_score AS a4,
    s5.home_score AS h5,
    s5.away_score AS a5,
    s6.home_score AS h6,
    s6.away_score AS a6,
    s7.home_score AS h7,
    s7.away_score AS a7,
    s8.home_score AS h8,
    s8.away_score AS a8,
    s9.home_score AS h9,
    s9.away_score AS a9,
    s10.home_score AS h10,
    s10.away_score AS a10,
    s11.home_score AS h11,
    s11.away_score AS a11,
    s12.home_score AS h12,
    s12.away_score AS a12,
    s13.home_score AS h13,
    s13.away_score AS a13,
    s14.home_score AS h14,
    s14.away_score AS a14,
    s15.home_score AS h15,
    s15.away_score AS a15,
    s16.home_score AS h16,
    s16.away_score AS a16,
    s17.home_score AS h17,
    s17.away_score AS a17,
    s18.home_score AS h18,
    s18.away_score AS a18,
    s19.home_score AS h19,
    s19.away_score AS a19,
    s20.home_score AS h20,
    s20.away_score AS a20,
    s21.home_score AS h21,
    s21.away_score AS a21,
    s22.home_score AS h22,
    s22.away_score AS a22,
    s23.home_score AS h23,
    s23.away_score AS a23,
    s24.home_score AS h24,
    s24.away_score AS a24,
    s25.home_score AS h25,
    s25.away_score AS a25
    FROM gamelog l
    LEFT JOIN (SELECT * FROM game_info_view) i
    ON l.game_id=i.game_id    
    LEFT JOIN (SELECT * FROM score_by_inning) s1
    ON l.game_id=s1.game_id AND s1.inning=1
    LEFT JOIN (SELECT * FROM score_by_inning) s2
    ON l.game_id=s2.game_id AND s2.inning=2
    LEFT JOIN (SELECT * FROM score_by_inning) s3
    ON l.game_id=s3.game_id AND s3.inning=3
    LEFT JOIN (SELECT * FROM score_by_inning) s4
    ON l.game_id=s4.game_id AND s4.inning=4
    LEFT JOIN (SELECT * FROM score_by_inning) s5
    ON l.game_id=s5.game_id AND s5.inning=5
    LEFT JOIN (SELECT * FROM score_by_inning) s6
    ON l.game_id=s6.game_id AND s6.inning=6
    LEFT JOIN (SELECT * FROM score_by_inning) s7
    ON l.game_id=s7.game_id AND s7.inning=7
    LEFT JOIN (SELECT * FROM score_by_inning) s8
    ON l.game_id=s8.game_id AND s8.inning=8
    LEFT JOIN (SELECT * FROM score_by_inning) s9
    ON l.game_id=s9.game_id AND s9.inning=9
    LEFT JOIN (SELECT * FROM score_by_inning) s10
    ON l.game_id=s10.game_id AND s10.inning=10
    LEFT JOIN (SELECT * FROM score_by_inning) s11
    ON l.game_id=s11.game_id AND s11.inning=11
    LEFT JOIN (SELECT * FROM score_by_inning) s12
    ON l.game_id=s12.game_id AND s12.inning=12
    LEFT JOIN (SELECT * FROM score_by_inning) s13
    ON l.game_id=s13.game_id AND s13.inning=13
    LEFT JOIN (SELECT * FROM score_by_inning) s14
    ON l.game_id=s14.game_id AND s14.inning=14
    LEFT JOIN (SELECT * FROM score_by_inning) s15
    ON l.game_id=s15.game_id AND s15.inning=15
    LEFT JOIN (SELECT * FROM score_by_inning) s16
    ON l.game_id=s16.game_id AND s16.inning=16
    LEFT JOIN (SELECT * FROM score_by_inning) s17
    ON l.game_id=s17.game_id AND s17.inning=17
    LEFT JOIN (SELECT * FROM score_by_inning) s18
    ON l.game_id=s18.game_id AND s18.inning=18
    LEFT JOIN (SELECT * FROM score_by_inning) s19
    ON l.game_id=s19.game_id AND s19.inning=19
    LEFT JOIN (SELECT * FROM score_by_inning) s20
    ON l.game_id=s20.game_id AND s20.inning=20
    LEFT JOIN (SELECT * FROM score_by_inning) s21
    ON l.game_id=s21.game_id AND s21.inning=21
    LEFT JOIN (SELECT * FROM score_by_inning) s22
    ON l.game_id=s22.game_id AND s22.inning=22
    LEFT JOIN (SELECT * FROM score_by_inning) s23
    ON l.game_id=s23.game_id AND s23.inning=23
    LEFT JOIN (SELECT * FROM score_by_inning) s24
    ON l.game_id=s24.game_id AND s24.inning=24
    LEFT JOIN (SELECT * FROM score_by_inning) s25
    ON l.game_id=s25.game_id AND s25.inning=25        
"""

allTables["player_game_batting"] = """CREATE TABLE player_game_batting (
    game_id integer,
    batter_num_id smallint,
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
    INTF smallint,
    PRIMARY KEY(game_id, batter_num_id, pos),
    FOREIGN KEY(batter_num_id) REFERENCES player(player_num_id)    
)"""

allTables["player_game_fielding"] = """CREATE TABLE player_game_fielding (
    game_id integer,
    fielder_num_id smallint,
    team char(3),
    pos smallint,
    seq smallint,
    IF3 smallint,
    PO smallint,
    A smallint,
    E smallint,
    DP smallint,
    TP smallint,
    PB smallint,
    PRIMARY KEY(game_id, fielder_num_id, pos, seq),
    FOREIGN KEY(fielder_num_id) REFERENCES player(player_num_id)    
)"""

allTables["player_game_pitching"] = """CREATE TABLE player_game_pitching (
    game_id integer,
    pitcher_num_id smallint,
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
    PRIMARY KEY(game_id, pitcher_num_id, seq),
    FOREIGN KEY(pitcher_num_id) REFERENCES player(player_num_id)    
)"""

# inning = inning + (inning_half << 6)
allTables["game_situation"] = """CREATE TABLE game_situation (
    game_id integer,
    event_id smallint,
    batter_num_id smallint NOT NULL,
    pitcher_num_id smallint NOT NULL,
    inning smallint NOT NULL,
    inning_half char(1) NOT NULL,
    outs smallint NOT NULL,
    bat_pitch_cnt char(2),
    bat_team_score smallint NOT NULL,
    pitch_team_score smallint NOT NULL,
    play_result char(3),
    play_base smallint,
    hit_loc char(3),
    hit_type char(1),
    outs_made smallint,
    runs_scored smallint,
    PRIMARY KEY(game_id, event_id),
    FOREIGN KEY(batter_num_id) REFERENCES player(player_num_id),   
    FOREIGN KEY(pitcher_num_id) REFERENCES player(player_num_id)    
)"""

allTables["game_situation_bases"] = """CREATE TABLE game_situation_bases (
    game_id integer,   
    event_id smallint,   
    bases_first smallint,
    bases_second smallint,
    bases_third smallint,
    PRIMARY KEY(game_id, event_id),
    FOREIGN KEY(bases_first) REFERENCES player(player_num_id),    
    FOREIGN KEY(bases_second) REFERENCES player(player_num_id),    
    FOREIGN KEY(bases_third) REFERENCES player(player_num_id)
)"""

allTables["game_situation_result2"] = """CREATE TABLE game_situation_result2 (
    game_id integer,
    event_id smallint,
    play_result char(3),
    play_base smallint,
    PRIMARY KEY(game_id, event_id)
)"""

allTables["game_situation_result3"] = """CREATE TABLE game_situation_result3 (
    game_id integer,
    event_id smallint,
    play_result char(3),
    play_base smallint,
    PRIMARY KEY(game_id, event_id)
)"""

allTables["game_situation_fielder_assist"] = """CREATE TABLE game_situation_fielder_assist (
    game_id integer,
    event_id smallint,
    fielder_num_id smallint,
    seq smallint,
    PRIMARY KEY(game_id, event_id, fielder_num_id, seq),
    FOREIGN KEY(fielder_num_id) REFERENCES player(player_num_id)
)"""

allTables["game_situation_fielder_putout"] = """CREATE TABLE game_situation_fielder_putout (
    game_id integer,
    event_id smallint,
    fielder_num_id smallint,
    seq smallint,
    PRIMARY KEY(game_id, event_id, fielder_num_id, seq),
    FOREIGN KEY(fielder_num_id) REFERENCES player(player_num_id)
)"""

allTables["game_situation_fielder_error"] = """CREATE TABLE game_situation_fielder_error (
    game_id integer,
    event_id smallint,
    fielder_num_id smallint,
    seq smallint,
    PRIMARY KEY(game_id, event_id, fielder_num_id, seq),
    FOREIGN KEY(fielder_num_id) REFERENCES player(player_num_id)
)"""

allTables["game_situation_fielder_fielded"] = """CREATE TABLE game_situation_fielder_fielded (
    game_id integer,
    event_id smallint,
    fielder_num_id smallint,
    seq smallint,
    PRIMARY KEY(game_id, event_id, fielder_num_id, seq),
    FOREIGN KEY(fielder_num_id) REFERENCES player(player_num_id)
)"""

allTables["game_situation_result1_mod"] = """CREATE TABLE game_situation_result1_mod (
    game_id integer,
    event_id smallint,
    seq smallint,
    mod char(4),
    prm varchar(8),
    PRIMARY KEY(game_id, event_id, seq)
)"""

allTables["game_situation_result2_mod"] = """CREATE TABLE game_situation_result2_mod (
    game_id integer,
    event_id smallint,
    seq smallint,
    mod char(4),
    prm varchar(8),
    PRIMARY KEY(game_id, event_id, seq)
)"""

allTables["game_situation_result3_mod"] = """CREATE TABLE game_situation_result3_mod (
    game_id integer,
    event_id smallint,
    seq smallint,
    mod char(4),
    prm varchar(8),
    PRIMARY KEY(game_id, event_id, seq)
)"""

allTables["game_situation_base_run"] = """CREATE TABLE game_situation_base_run (
    game_id integer,
    event_id smallint,
    src smallint, 
    dst smallint,
    out boolean,
    PRIMARY KEY(game_id, event_id, src)
)"""

allTables["game_situation_base_run_mod"] = """CREATE TABLE game_situation_base_run_mod (
    game_id integer,
    event_id smallint,
    src smallint,
    seq smallint,
    mod char(4),
    prm varchar(8),
    PRIMARY KEY(game_id, event_id, src, seq)
)"""

allTables["game_situation_coms"] = """CREATE TABLE game_situation_coms (
    game_id integer,
    event_id smallint,
    com_id smallint,
    PRIMARY KEY(game_id, event_id, com_id)
)"""


allTables["play_baserun"] = """ CREATE TABLE play_baserun (
    play char(4) PRIMARY KEY
)"""

allTables["left_right"] = """ CREATE TABLE left_right (
    lr char(1) PRIMARY KEY,
    d char(6)
)"""

# select * from player_game_batting_view where batter_num_id=20415;
allViews["player_game_batting_view"] = """CREATE VIEW player_game_batting_view AS SELECT
    b.game_id, 
    b.batter_num_id, 
    pl.name_other||' '||pl.name_last AS batter_name,
    b.team,
    b.pos, 
    b.seq,
    i.game_date,
    i.year,
    i.month,
    i.dow,
    i.start_time,
    i.season,
    i.post_series,
    i.dh_num,
    i.away_team, 
    i.away_team_city, 
    i.away_team_name, 
    i.away_league,
    i.away_game_num,
    i.home_team,
    i.home_team_city, 
    i.home_team_name,
    i.home_league,
    i.home_game_num,
    i.park,
    i.attendance,
    i.game_duration_min AS duration,
    i.daynight,
    i.field_cond,
    i.precip,
    i.sky,
    i.winddir,
    i.windspeed,
    i.temp,
    i.home_team_bat_first,
    i.use_dh,
    i.complete,
    i.forfeit,
    i.protest,
    i.win_pitcher,
    i.loss_pitcher,
    i.save_pitcher,
    i.gw_rbi,
    b.AB,
    b.R,
    b.H,
    b.n2B,
    b.n3B,
    b.HR,
    b.RBI,
    b.SH,
    b.SF,
    b.HBP,
    b.BB,
    b.IBB,
    b.K,
    b.SB,
    b.CS,
    b.GIDP,
    b.INTF
    FROM player_game_batting b
    LEFT JOIN game_info_view i
    ON b.game_id=i.game_id    
    LEFT JOIN player pl
    ON b.batter_num_id=pl.player_num_id
"""

allViews["player_game_fielding_view"] = """CREATE VIEW player_game_fielding_view AS SELECT
    f.game_id,
    f.fielder_num_id,
    pl.name_other||' '||pl.name_last AS fielder_name,
    f.team,
    fld_pos_d.d AS pos,
    f.seq,
    i.game_date,
    i.year,
    i.month,
    i.dow,
    i.start_time,
    i.season,
    i.post_series,
    i.dh_num,
    i.away_team, 
    i.away_team_city, 
    i.away_team_name, 
    i.away_league,
    i.away_game_num,
    i.home_team,
    i.home_team_city, 
    i.home_team_name,
    i.home_league,
    i.home_game_num,
    i.park,
    i.attendance,
    i.game_duration_min AS duration,
    i.daynight,
    i.field_cond,
    i.precip,
    i.sky,
    i.winddir,
    i.windspeed,
    i.temp,
    i.home_team_bat_first,
    i.use_dh,
    i.complete,
    i.forfeit,
    i.protest,
    i.win_pitcher,
    i.loss_pitcher,
    i.save_pitcher,
    i.gw_rbi,
    f.IF3,
    f.PO,
    f.A,
    f.E,
    f.DP,
    f.TP,
    f.PB
    FROM player_game_fielding f
    LEFT JOIN game_info_view i
    ON f.game_id=i.game_id
    LEFT JOIN player pl
    ON f.fielder_num_id=pl.player_num_id
    LEFT JOIN field_pos_desc fld_pos_d
    ON fld_pos_d.pos=f.pos
"""

allViews["player_game_pitching_view"] = """CREATE VIEW player_game_pitching_view AS SELECT
    p.game_id,
    p.pitcher_num_id, 
    pl.name_other||' '||pl.name_last AS pitcher_name,
    p.team,
    p.seq,
    i.game_date,
    i.year,
    i.month,
    i.dow,
    i.start_time,
    i.season,
    i.post_series,
    i.dh_num,
    i.away_team, 
    i.away_team_city, 
    i.away_team_name, 
    i.away_league,
    i.away_game_num,
    i.home_team,
    i.home_team_city, 
    i.home_team_name,
    i.home_league,
    i.home_game_num,
    i.park,
    i.attendance,
    i.game_duration_min AS duration,
    i.daynight,
    i.field_cond,
    i.precip,
    i.sky,
    i.winddir,
    i.windspeed,
    i.temp,
    i.home_team_bat_first,
    i.use_dh,
    i.complete,
    i.forfeit,
    i.protest,
    i.win_pitcher,
    i.loss_pitcher,
    i.save_pitcher,
    i.gw_rbi, 
    p.IP3,  
    p.NOOUT,
    p.BF,
    p.H,
    p.n2B,
    p.n3B,
    p.HR,
    p.R,
    p.ER,
    p.BB,
    p.IBB,
    p.K,
    p.HBP,
    p.WP,
    p.BK,
    p.SH,
    p.SF
    FROM player_game_pitching p
    LEFT JOIN game_info_view i
    ON p.game_id=i.game_id
    LEFT JOIN player pl
    ON p.pitcher_num_id=pl.player_num_id
"""

allViews["game_situation_view"] = """CREATE VIEW game_situation_view AS SELECT
    s.game_id,
    s.event_id,
    i.game_date,
    i.year,
    i.month,
    i.dow,
    i.season,
    i.post_series,
    i.dh_num AS num,
    i.away_team, 
    i.away_league,
    i.away_game_num,
    i.home_team,    
    i.home_league,
    i.home_game_num,
    i.park,
    i.attendance,
    i.start_time,
    i.game_duration_min AS duration,
    i.daynight,
    i.field_cond,
    i.precip,
    i.sky,
    i.winddir,
    i.windspeed,
    i.temp,
    s.batter_num_id,
    pgb.team AS batter_team,
    pgb.pos AS batter_pos,
    pgb.seq AS batter_seq,
    bat.name_last||' '||bat.name_other AS batter_name,
    bat_lr.d AS batter_side,
    s.pitcher_num_id,
    pgp.team AS pitcher_team,
    pgp.seq AS pitcher_seq,
    pit.name_last||' '||pit.name_other AS pitcher_name,
    pit_lr.d AS pitcher_side,
    s.inning,
    s.inning_half,
    s.outs,
    s.bat_pitch_cnt,
    s.bat_team_score,
    s.pitch_team_score,
    r1_d.d AS result1,
    s.play_base AS base1,
    s.hit_loc,
    s.hit_type,
    s.outs_made,
    s.runs_scored,

    brun1.name_last||' '||SUBSTR(brun1.name_other, 0, 2) AS first,
    brun2.name_last||' '||SUBSTR(brun2.name_other, 0, 2) AS second,
    brun3.name_last||' '||SUBSTR(brun3.name_other, 0, 2) AS third,
    
    r2_d.d AS result2, 
    r2.play_base AS base2,
    r3_d.d AS result3, 
    r3.play_base AS base3,

    fldr_a1.name_last||' '||SUBSTR(fldr_a1.name_other, 0, 2) AS ass1,
    fldr_a2.name_last||' '||SUBSTR(fldr_a2.name_other, 0, 2) AS ass2,
    fldr_a3.name_last||' '||SUBSTR(fldr_a3.name_other, 0, 2) AS ass3,
    fldr_a4.name_last||' '||SUBSTR(fldr_a4.name_other, 0, 2) AS ass4,
    fldr_a5.name_last||' '||SUBSTR(fldr_a5.name_other, 0, 2) AS ass5,
    fldr_a6.name_last||' '||SUBSTR(fldr_a6.name_other, 0, 2) AS ass6,

    fldr_po1.name_last||' '||SUBSTR(fldr_po1.name_other, 0, 2) AS po1,
    fldr_po2.name_last||' '||SUBSTR(fldr_po2.name_other, 0, 2) AS po2,
    fldr_po3.name_last||' '||SUBSTR(fldr_po3.name_other, 0, 2) AS po3,
    
    fldr_e1.name_last||' '||SUBSTR(fldr_e1.name_other, 0, 2) AS err1,
    fldr_e2.name_last||' '||SUBSTR(fldr_e2.name_other, 0, 2) AS err2,
    fldr_e3.name_last||' '||SUBSTR(fldr_e3.name_other, 0, 2) AS err3,    

    r1m1_d.d AS r1m1,
    r1m1.prm AS r1m1prm,
    r1m2_d.d AS r1m2,
    r1m2.prm AS r1m2prm,
    r1m3_d.d AS r1m3,
    r1m3.prm AS r1m3prm,

    br0.dst AS br0_dst,
    br0.out AS br0_out,
    br1.dst AS br1_dst,
    br1.out AS br1_out,
    br2.dst AS br2_dst,
    br2.out AS br2_out,
    br3.dst AS br3_dst,
    br3.out AS br3_out,

    br0_m1.mod AS br0_mod1,
    br0_m1.prm AS br0_mod1_prm,
    br0_m2.mod AS br0_mod2,
    br0_m2.prm AS br0_mod2_prm,
    br0_m3.mod AS br0_mod3,
    br0_m3.prm AS br0_mod3_prm, 

    br1_m1.mod AS br1_mod1,
    br1_m1.prm AS br1_mod1_prm, 
    br1_m2.mod AS br1_mod2,
    br1_m2.prm AS br1_mod2_prm, 
    br1_m3.mod AS br1_mod3,
    br1_m3.prm AS br1_mod3_prm, 

    br2_m1.mod AS br2_mod1,
    br2_m1.prm AS br2_mod1_prm, 
    br2_m2.mod AS br2_mod2,
    br2_m2.prm AS br2_mod2_prm, 
    br2_m3.mod AS br2_mod3,
    br2_m3.prm AS br2_mod3_prm, 

    br3_m1.mod AS br3_mod1,
    br3_m1.prm AS br3_mod1_prm, 
    br3_m2.mod AS br3_mod2,
    br3_m2.prm AS br3_mod2_prm, 
    br3_m3.mod AS br3_mod3,
    br3_m3.prm AS br3_mod3_prm

    FROM game_situation s

    LEFT JOIN game_info_view i
    ON s.game_id=i.game_id
    LEFT JOIN game_situation_bases b
    ON s.game_id=b.game_id AND s.event_id=b.event_id

    LEFT JOIN game_situation_result2 r2
    ON s.game_id=r2.game_id AND s.event_id=r2.event_id
    LEFT JOIN game_situation_result3 r3
    ON s.game_id=r3.game_id AND s.event_id=r3.event_id

    LEFT JOIN play_desc r1_d
    ON s.play_result=r1_d.k
    LEFT JOIN play_desc r2_d
    ON r2.play_result=r2_d.k
    LEFT JOIN play_desc r3_d
    ON r3.play_result=r3_d.k
    
    LEFT JOIN game_situation_fielder_assist fa1
    ON s.game_id=fa1.game_id AND fa1.seq=1 AND s.event_id=fa1.event_id
    LEFT JOIN game_situation_fielder_assist fa2
    ON s.game_id=fa2.game_id AND fa2.seq=2 AND s.event_id=fa2.event_id
    LEFT JOIN game_situation_fielder_assist fa3
    ON s.game_id=fa3.game_id AND fa3.seq=3 AND s.event_id=fa3.event_id
    LEFT JOIN game_situation_fielder_assist fa4
    ON s.game_id=fa4.game_id AND fa4.seq=4 AND s.event_id=fa4.event_id
    LEFT JOIN game_situation_fielder_assist fa5
    ON s.game_id=fa5.game_id AND fa5.seq=5 AND s.event_id=fa5.event_id
    LEFT JOIN game_situation_fielder_assist fa6
    ON s.game_id=fa6.game_id AND fa6.seq=6 AND s.event_id=fa6.event_id
    
    LEFT JOIN game_situation_fielder_putout fpo1
    ON s.game_id=fpo1.game_id AND fpo1.seq=1 AND s.event_id=fpo1.event_id
    LEFT JOIN game_situation_fielder_putout fpo2
    ON s.game_id=fpo2.game_id AND fpo2.seq=2 AND s.event_id=fpo2.event_id
    LEFT JOIN game_situation_fielder_putout fpo3
    ON s.game_id=fpo3.game_id AND fpo3.seq=3 AND s.event_id=fpo3.event_id

    LEFT JOIN game_situation_fielder_error fe1
    ON s.game_id=fe1.game_id AND fe1.seq=1 AND s.event_id=fe1.event_id
    LEFT JOIN game_situation_fielder_error fe2
    ON s.game_id=fe2.game_id AND fe2.seq=2 AND s.event_id=fe2.event_id
    LEFT JOIN game_situation_fielder_error fe3
    ON s.game_id=fe3.game_id AND fe3.seq=3 AND s.event_id=fe3.event_id
    
    LEFT JOIN game_situation_result1_mod r1m1
    ON s.game_id=r1m1.game_id AND r1m1.seq=1 AND s.event_id=r1m1.event_id
    LEFT JOIN game_situation_result1_mod r1m2
    ON s.game_id=r1m2.game_id AND r1m2.seq=2 AND s.event_id=r1m2.event_id
    LEFT JOIN game_situation_result1_mod r1m3
    ON s.game_id=r1m3.game_id AND r1m3.seq=3 AND s.event_id=r1m3.event_id    
    

    LEFT JOIN mod_desc r1m1_d 
    ON r1m1.mod=r1m1_d.k
    LEFT JOIN mod_desc r1m2_d 
    ON r1m2.mod=r1m2_d.k
    LEFT JOIN mod_desc r1m3_d 
    ON r1m3.mod=r1m3_d.k

    LEFT JOIN game_situation_base_run br0
    ON s.game_id=br0.game_id AND br0.src=0 AND s.event_id=br0.event_id
    LEFT JOIN game_situation_base_run br1
    ON s.game_id=br1.game_id AND br1.src=1 AND s.event_id=br1.event_id
    LEFT JOIN game_situation_base_run br2
    ON s.game_id=br2.game_id AND br2.src=2 AND s.event_id=br2.event_id 
    LEFT JOIN game_situation_base_run br3
    ON s.game_id=br3.game_id AND br3.src=3 AND s.event_id=br3.event_id    
    
    LEFT JOIN game_situation_base_run_mod br0_m1
    ON s.game_id=br0_m1.game_id AND br0_m1.seq=1 AND s.event_id=br0_m1.event_id
    LEFT JOIN game_situation_base_run_mod br0_m2
    ON s.game_id=br0_m2.game_id AND br0_m2.seq=2 AND s.event_id=br0_m2.event_id
    LEFT JOIN game_situation_base_run_mod br0_m3
    ON s.game_id=br0_m3.game_id AND br0_m3.seq=3 AND s.event_id=br0_m3.event_id
    
    LEFT JOIN game_situation_base_run_mod br1_m1
    ON s.game_id=br1_m1.game_id AND br1_m1.seq=1 AND s.event_id=br1_m1.event_id
    LEFT JOIN game_situation_base_run_mod br1_m2
    ON s.game_id=br1_m2.game_id AND br1_m2.seq=2 AND s.event_id=br1_m2.event_id
    LEFT JOIN game_situation_base_run_mod br1_m3
    ON s.game_id=br1_m3.game_id AND br1_m3.seq=3 AND s.event_id=br1_m3.event_id

    LEFT JOIN game_situation_base_run_mod br2_m1
    ON s.game_id=br2_m1.game_id AND br2_m1.seq=1 AND s.event_id=br2_m1.event_id
    LEFT JOIN game_situation_base_run_mod br2_m2
    ON s.game_id=br2_m2.game_id AND br2_m2.seq=2 AND s.event_id=br2_m2.event_id
    LEFT JOIN game_situation_base_run_mod br2_m3
    ON s.game_id=br2_m3.game_id AND br2_m3.seq=3 AND s.event_id=br2_m3.event_id

    LEFT JOIN game_situation_base_run_mod br3_m1
    ON s.game_id=br3_m1.game_id AND br3_m1.seq=1 AND s.event_id=br3_m1.event_id
    LEFT JOIN game_situation_base_run_mod br3_m2
    ON s.game_id=br3_m2.game_id AND br3_m2.seq=2 AND s.event_id=br3_m2.event_id
    LEFT JOIN game_situation_base_run_mod br3_m3
    ON s.game_id=br3_m3.game_id AND br3_m3.seq=3 AND s.event_id=br3_m3.event_id
    
    LEFT JOIN player bat
    ON bat.player_num_id=s.batter_num_id
    LEFT JOIN player pit
    ON pit.player_num_id=s.pitcher_num_id

    LEFT JOIN player brun1
    ON brun1.player_num_id=b.bases_first
    LEFT JOIN player brun2
    ON brun2.player_num_id=b.bases_second
    LEFT JOIN player brun3
    ON brun3.player_num_id=b.bases_third

    LEFT JOIN player fldr_a1
    ON fldr_a1.player_num_id=fa1.fielder_num_id
    LEFT JOIN player fldr_a2
    ON fldr_a2.player_num_id=fa2.fielder_num_id
    LEFT JOIN player fldr_a3
    ON fldr_a3.player_num_id=fa3.fielder_num_id
    LEFT JOIN player fldr_a4
    ON fldr_a4.player_num_id=fa4.fielder_num_id
    LEFT JOIN player fldr_a5
    ON fldr_a5.player_num_id=fa5.fielder_num_id
    LEFT JOIN player fldr_a6
    ON fldr_a6.player_num_id=fa6.fielder_num_id
    
    LEFT JOIN player fldr_po1
    ON fldr_po1.player_num_id=fpo1.fielder_num_id
    LEFT JOIN player fldr_po2
    ON fldr_po2.player_num_id=fpo2.fielder_num_id
    LEFT JOIN player fldr_po3
    ON fldr_po3.player_num_id=fpo3.fielder_num_id

    LEFT JOIN player fldr_e1
    ON fldr_e1.player_num_id=fe1.fielder_num_id
    LEFT JOIN player fldr_e2
    ON fldr_e2.player_num_id=fe2.fielder_num_id
    LEFT JOIN player fldr_e3
    ON fldr_e3.player_num_id=fe3.fielder_num_id

    LEFT JOIN player_game_batting pgb 
    ON s.batter_num_id=pgb.batter_num_id AND pgb.game_id=s.game_id
    LEFT JOIN player_game_pitching pgp
    ON s.pitcher_num_id=pgp.pitcher_num_id AND pgp.game_id=s.game_id
    LEFT JOIN left_right bat_lr 
    ON bat.bats=bat_lr.lr AND bat.player_num_id=bat.player_num_id
    LEFT JOIN left_right pit_lr 
    ON pit.bats=pit_lr.lr AND pit.player_num_id=pit.player_num_id   
"""

game_situation_view_clickhouse = """CREATE VIEW game_situation_view AS SELECT
    s.game_id,
    s.event_id,
    i.game_date,
    i.year,
    i.month,
    i.dow,
    i.season,
    i.post_series,
    i.dh_num AS num,
    i.away_team, 
    i.away_league,
    i.away_game_num,
    i.home_team,    
    i.home_league,
    i.home_game_num,
    i.park,
    i.attendance,
    i.start_time,
    i.game_duration_min AS duration,
    i.daynight,
    i.field_cond,
    i.precip,
    i.sky,
    i.winddir,
    i.windspeed,
    i.temp,
    s.batter_num_id,
    pgb.team AS batter_team,
    pgb.pos AS batter_pos,
    pgb.seq AS batter_seq,
    bat.name_last||' '||bat.name_other AS batter,
    bat_lr.d AS batter_side,
    s.pitcher_num_id,
    pgp.team AS pitcher_team,
    pgp.seq AS pitcher_seq,
    pit.name_last||' '||pit.name_other AS pitcher,
    pit_lr.d AS pitcher_side,
    s.inning,
    s.inning_half,
    s.outs,
    s.bat_pitch_cnt,
    s.bat_team_score,
    s.pitch_team_score,
    s.play_result,
    s.play_base,
    s.hit_loc,
    s.hit_type,
    s.outs_made,
    s.runs_scored,

    brun1.name_last||' '||SUBSTR(brun1.name_other, 1, 2) AS first,
    brun2.name_last||' '||SUBSTR(brun2.name_other, 1, 2) AS second,
    brun3.name_last||' '||SUBSTR(brun3.name_other, 1, 2) AS third,
    
    r2.play_result AS play_result2,
    r2.play_base AS play_base2,
    r3.play_result AS play_result3,
    r3.play_base AS play_base3,

    fldr_a1.name_last||' '||SUBSTR(fldr_a1.name_other, 1, 2) AS ass1,
    fldr_a2.name_last||' '||SUBSTR(fldr_a2.name_other, 1, 2) AS ass2,
    fldr_a3.name_last||' '||SUBSTR(fldr_a3.name_other, 1, 2) AS ass3,
    fldr_a4.name_last||' '||SUBSTR(fldr_a4.name_other, 1, 2) AS ass4,
    fldr_a5.name_last||' '||SUBSTR(fldr_a5.name_other, 1, 2) AS ass5,
    fldr_a6.name_last||' '||SUBSTR(fldr_a6.name_other, 1, 2) AS ass6,

    fldr_po1.name_last||' '||SUBSTR(fldr_po1.name_other, 1, 2) AS po1,
    fldr_po2.name_last||' '||SUBSTR(fldr_po2.name_other, 1, 2) AS po2,
    fldr_po3.name_last||' '||SUBSTR(fldr_po3.name_other, 1, 2) AS po3,
    
    fldr_e1.name_last||' '||SUBSTR(fldr_e1.name_other, 1, 2) AS err1,
    fldr_e2.name_last||' '||SUBSTR(fldr_e2.name_other, 1, 2) AS err2,
    fldr_e3.name_last||' '||SUBSTR(fldr_e3.name_other, 1, 2) AS err3,    

    r1m1.mod AS r1m1,
    r1m1.prm AS r1m1prm,
    r1m2.mod AS r1m2,
    r1m2.prm AS r1m2prm,
    r1m3.mod AS r1m3,
    r1m3.prm AS r1m3prm,

    br0.dst AS br0_dst,
    br0.out AS br0_out,
    br1.dst AS br1_dst,
    br1.out AS br1_out,
    br2.dst AS br2_dst,
    br2.out AS br2_out,
    br3.dst AS br3_dst,
    br3.out AS br3_out,

    br0_m1.mod AS br0_mod1,
    br0_m1.prm AS br0_mod1_prm,
    br0_m2.mod AS br0_mod2,
    br0_m2.prm AS br0_mod2_prm,
    br0_m3.mod AS br0_mod3,
    br0_m3.prm AS br0_mod3_prm, 

    br1_m1.mod AS br1_mod1,
    br1_m1.prm AS br1_mod1_prm, 
    br1_m2.mod AS br1_mod2,
    br1_m2.prm AS br1_mod2_prm, 
    br1_m3.mod AS br1_mod3,
    br1_m3.prm AS br1_mod3_prm, 

    br2_m1.mod AS br2_mod1,
    br2_m1.prm AS br2_mod1_prm, 
    br2_m2.mod AS br2_mod2,
    br2_m2.prm AS br2_mod2_prm, 
    br2_m3.mod AS br2_mod3,
    br2_m3.prm AS br2_mod3_prm, 

    br3_m1.mod AS br3_mod1,
    br3_m1.prm AS br3_mod1_prm, 
    br3_m2.mod AS br3_mod2,
    br3_m2.prm AS br3_mod2_prm, 
    br3_m3.mod AS br3_mod3,
    br3_m3.prm AS br3_mod3_prm

    FROM game_situation s

    LEFT JOIN game_info_view i
    ON s.game_id=i.game_id
    LEFT JOIN game_situation_bases b
    ON s.game_id=b.game_id AND s.event_id=b.event_id

    LEFT JOIN game_situation_result2 r2
    ON s.game_id=r2.game_id AND s.event_id=r2.event_id
    LEFT JOIN game_situation_result3 r3
    ON s.game_id=r3.game_id AND s.event_id=r3.event_id
    
    LEFT JOIN game_situation_fielder_assist fa1
    ON s.game_id=fa1.game_id AND fa1.seq=1 AND s.event_id=fa1.event_id
    LEFT JOIN game_situation_fielder_assist fa2
    ON s.game_id=fa2.game_id AND fa2.seq=2 AND s.event_id=fa2.event_id
    LEFT JOIN game_situation_fielder_assist fa3
    ON s.game_id=fa3.game_id AND fa3.seq=3 AND s.event_id=fa3.event_id
    LEFT JOIN game_situation_fielder_assist fa4
    ON s.game_id=fa4.game_id AND fa4.seq=4 AND s.event_id=fa4.event_id
    LEFT JOIN game_situation_fielder_assist fa5
    ON s.game_id=fa5.game_id AND fa5.seq=5 AND s.event_id=fa5.event_id
    LEFT JOIN game_situation_fielder_assist fa6
    ON s.game_id=fa6.game_id AND fa6.seq=6 AND s.event_id=fa6.event_id
    
    LEFT JOIN game_situation_fielder_putout fpo1
    ON s.game_id=fpo1.game_id AND fpo1.seq=1 AND s.event_id=fpo1.event_id
    LEFT JOIN game_situation_fielder_putout fpo2
    ON s.game_id=fpo2.game_id AND fpo2.seq=2 AND s.event_id=fpo2.event_id
    LEFT JOIN game_situation_fielder_putout fpo3
    ON s.game_id=fpo3.game_id AND fpo3.seq=3 AND s.event_id=fpo3.event_id

    LEFT JOIN game_situation_fielder_error fe1
    ON s.game_id=fe1.game_id AND fe1.seq=1 AND s.event_id=fe1.event_id
    LEFT JOIN game_situation_fielder_error fe2
    ON s.game_id=fe2.game_id AND fe2.seq=2 AND s.event_id=fe2.event_id
    LEFT JOIN game_situation_fielder_error fe3
    ON s.game_id=fe3.game_id AND fe3.seq=3 AND s.event_id=fe3.event_id
    
    LEFT JOIN game_situation_result1_mod r1m1
    ON s.game_id=r1m1.game_id AND r1m1.seq=1 AND s.event_id=r1m1.event_id
    LEFT JOIN game_situation_result1_mod r1m2
    ON s.game_id=r1m2.game_id AND r1m2.seq=2 AND s.event_id=r1m2.event_id
    LEFT JOIN game_situation_result1_mod r1m3
    ON s.game_id=r1m3.game_id AND r1m3.seq=3 AND s.event_id=r1m3.event_id    
    
    LEFT JOIN game_situation_base_run br0
    ON s.game_id=br0.game_id AND br0.src=0 AND s.event_id=br0.event_id
    LEFT JOIN game_situation_base_run br1
    ON s.game_id=br1.game_id AND br1.src=1 AND s.event_id=br1.event_id
    LEFT JOIN game_situation_base_run br2
    ON s.game_id=br2.game_id AND br2.src=2 AND s.event_id=br2.event_id 
    LEFT JOIN game_situation_base_run br3
    ON s.game_id=br3.game_id AND br3.src=3 AND s.event_id=br3.event_id    
    
    LEFT JOIN game_situation_base_run_mod br0_m1
    ON s.game_id=br0_m1.game_id AND br0_m1.seq=1 AND s.event_id=br0_m1.event_id
    LEFT JOIN game_situation_base_run_mod br0_m2
    ON s.game_id=br0_m2.game_id AND br0_m2.seq=2 AND s.event_id=br0_m2.event_id
    LEFT JOIN game_situation_base_run_mod br0_m3
    ON s.game_id=br0_m3.game_id AND br0_m3.seq=3 AND s.event_id=br0_m3.event_id
    
    LEFT JOIN game_situation_base_run_mod br1_m1
    ON s.game_id=br1_m1.game_id AND br1_m1.seq=1 AND s.event_id=br1_m1.event_id
    LEFT JOIN game_situation_base_run_mod br1_m2
    ON s.game_id=br1_m2.game_id AND br1_m2.seq=2 AND s.event_id=br1_m2.event_id
    LEFT JOIN game_situation_base_run_mod br1_m3
    ON s.game_id=br1_m3.game_id AND br1_m3.seq=3 AND s.event_id=br1_m3.event_id

    LEFT JOIN game_situation_base_run_mod br2_m1
    ON s.game_id=br2_m1.game_id AND br2_m1.seq=1 AND s.event_id=br2_m1.event_id
    LEFT JOIN game_situation_base_run_mod br2_m2
    ON s.game_id=br2_m2.game_id AND br2_m2.seq=2 AND s.event_id=br2_m2.event_id
    LEFT JOIN game_situation_base_run_mod br2_m3
    ON s.game_id=br2_m3.game_id AND br2_m3.seq=3 AND s.event_id=br2_m3.event_id

    LEFT JOIN game_situation_base_run_mod br3_m1
    ON s.game_id=br3_m1.game_id AND br3_m1.seq=1 AND s.event_id=br3_m1.event_id
    LEFT JOIN game_situation_base_run_mod br3_m2
    ON s.game_id=br3_m2.game_id AND br3_m2.seq=2 AND s.event_id=br3_m2.event_id
    LEFT JOIN game_situation_base_run_mod br3_m3
    ON s.game_id=br3_m3.game_id AND br3_m3.seq=3 AND s.event_id=br3_m3.event_id
    
    LEFT JOIN player bat
    ON bat.player_num_id=s.batter_num_id
    LEFT JOIN player pit
    ON pit.player_num_id=s.pitcher_num_id

    LEFT JOIN player brun1
    ON brun1.player_num_id=b.bases_first
    LEFT JOIN player brun2
    ON brun2.player_num_id=b.bases_second
    LEFT JOIN player brun3
    ON brun3.player_num_id=b.bases_third

    LEFT JOIN player fldr_a1
    ON fldr_a1.player_num_id=fa1.fielder_num_id
    LEFT JOIN player fldr_a2
    ON fldr_a2.player_num_id=fa2.fielder_num_id
    LEFT JOIN player fldr_a3
    ON fldr_a3.player_num_id=fa3.fielder_num_id
    LEFT JOIN player fldr_a4
    ON fldr_a4.player_num_id=fa4.fielder_num_id
    LEFT JOIN player fldr_a5
    ON fldr_a5.player_num_id=fa5.fielder_num_id
    LEFT JOIN player fldr_a6
    ON fldr_a6.player_num_id=fa6.fielder_num_id
    
    LEFT JOIN player fldr_po1
    ON fldr_po1.player_num_id=fpo1.fielder_num_id
    LEFT JOIN player fldr_po2
    ON fldr_po2.player_num_id=fpo2.fielder_num_id
    LEFT JOIN player fldr_po3
    ON fldr_po3.player_num_id=fpo3.fielder_num_id

    LEFT JOIN player fldr_e1
    ON fldr_e1.player_num_id=fe1.fielder_num_id
    LEFT JOIN player fldr_e2
    ON fldr_e2.player_num_id=fe2.fielder_num_id
    LEFT JOIN player fldr_e3
    ON fldr_e3.player_num_id=fe3.fielder_num_id

    LEFT JOIN player_game_batting pgb 
    ON s.batter_num_id=pgb.batter_num_id AND pgb.game_id=s.game_id
    LEFT JOIN player_game_pitching pgp
    ON s.pitcher_num_id=pgp.pitcher_num_id AND pgp.game_id=s.game_id
    LEFT JOIN left_right bat_lr 
    ON bat.bats=bat_lr.lr AND bat.player_num_id=bat.player_num_id
    LEFT JOIN left_right pit_lr 
    ON pit.bats=pit_lr.lr AND pit.player_num_id=pit.player_num_id   
"""
allValues = dict()
allValues["day_in_week"] = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
allValues["month"] = ("", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
allValues["season"] = ("Reg", "Post", "Pre", "Other")
# 0=not postseason 1:wildcard, 2=division, 3=league champsionship, 4=world series
allValues["postseason_series"] = ("", "Wildcard", "Division", "League", "World Series", "Playoff tiebreak")

allValues["daynight"] = ("Day", "Night")
allValues["fieldcond"] = ("", "Dry", "Damp", "Wet", "Soaked")
allValues["precip"] = ("", "None", "Drizzle", "Rain", "Showers", "Snow")
allValues["sky"] = ("", "Sunny", "Cloudy", "Overcast", "Dome", "Night")
allValues["winddir"] = ("", "From CF", "From LF", "From RF", "LF to RF")
allValues["winddir"] += ("RF to LF", "To CF", "To LF", "To RF")
allValues["forfeit"] = ("", "Away", "Home", "No Decision")
allValues["protest"] = ("", "Unidentified", "Disallow Away", "Disallow Home", "Upheld Away", "Upheld Home")
allValues["field_pos_desc"] = ("Designated Hitter", "Pitcher", "Catcher", "First Base", "Second Base", "Third Base", "Shortstop", "Left Field", "Center Field", "Right Field")

play_baserun = ("SB", "CS", "PO", "POCS", "DI", "OA")

playDesc = dict()
playDesc["BB"] = "Walk"
playDesc["S"] = "Single"
playDesc["O"] = "Out"
playDesc["FC"] = "Fielders choice"
playDesc["HBP"] = "Hit by pitch"
playDesc["K"] = "Strikeout"
playDesc["D"] = "Double"
playDesc["DGR"] = "Double (ground rule)"
playDesc["E"] = "Error"
playDesc["BK"] = "Balk"
playDesc["WP"] = "Wild pitch"
playDesc["PO"] = "Pick off"
playDesc["SB"] = "Stolen base"
playDesc["FO"] = "Force out"
playDesc["IBB"] = "Intentional walk"
playDesc["PB"] = "Passed ball"
playDesc["CS"] = "Caught stealng"
playDesc["T"] = "Triple"
playDesc["HR"] = "Home run"
playDesc["FLE"] = "Foul ball error"
playDesc["POCS"] = "Picked off/caught stealing"
playDesc["OA"] = "Other advance"
playDesc["DI"] = "Defensive indifference"
playDesc["CI"] = "Catcher interference"


modDesc = dict()

modDesc["SH"] = "Sac hit"
modDesc["C"] = "Called strike"
modDesc["G"] = "Ground ball"
modDesc["F"] = "Fly ball"
modDesc["TH"] = "Throw"
modDesc["FO"] = "Force out"
modDesc["FL"] = "Foul"
modDesc["L"] = "Line drive"
modDesc["P"] = "Pop up"
modDesc["LDP"] = "Lined into double play"
modDesc["GDP"] = "Ground into double play"
modDesc["BG"] = "Bunt ground ball"
modDesc["DP"] = "Doulbe play"
modDesc["BINT"] = "Batter interference"
modDesc["BP"] = "Bunt pop-up"
modDesc["SF"] = "Sac fly"
modDesc["IPHR"] = "Inside the park home run"
modDesc["INT"] = "Interference"
modDesc["BF"] = "Bunt foul"
modDesc["BR"] = ""
modDesc["E"] = "Error"
modDesc["AP"] = "Appeal"
modDesc["TP"] = "Triple play"
modDesc["UINT"] = "Umpire interference"
modDesc["IF"] = "Infield fly"
modDesc["NDP"] = "No double play credit"
modDesc["FDP"] = "Fly ball double play"
modDesc["LTP"] = "Lined into triple play"
modDesc["COUR"] = "Courtesy batter"
modDesc["OBS"] = "Obstruction"
modDesc["TH"] = "Throw"
modDesc["BL"] = "Bunt line drive"
modDesc["R"] = "Relay throw"
modDesc["BPDP"] = "Bunt pop-up double play"
modDesc["RINT"] = "Runner interference"
modDesc["GTP"] = "Ground into triple play"
modDesc["PASS"] = "Runner passed"
modDesc["BOOT"] = "Boot"
modDesc["COUF"] = "Courtesy fielder"
modDesc["FDP"] = "Fly ball double play"
modDesc["BGDP"] = "Bunt ground ball double play"
modDesc["FINT"] = "Fan interference"
modDesc["UREV"] = "Umpire review"
modDesc["MREV"] = "Manager review"


# add WITHOUT ROWID to these tables
tablesWithoutROWID = ["player", "umpire", "game_info", "gamelog", "event_play",
                      "event_start", "event_sub", "event_com",
                      "player_game_batting", "player_game_pitching",
                      "player_game_fielding",
                      "game_situation", "game_situation_bases",
                      "game_situation_result1_mod", "game_situation_result2_mod",
                      "game_situation_result3_mod",
                      "game_situation_baserun", "game_situation_baserun_mod"
                      "game_situation_result2", "game_situation_fielder_assist",
                      "game_situation_fielder_putout", "game_situation_fielder_error",
                      "game_situation_result1_mod", "game_situation_result2_mod"]


def insertDummyValues(cur):
    stmt = "INSERT INTO park VALUES("
    stmt += "'unkwn', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)"
    cur.execute(stmt)

    # dummy player ID to satisfy FOREIGN KEY constraint
    stmt = "INSERT INTO player (player_num_id, player_id, name_last, name_first, name_other) VALUES("
    stmt += "0, NULL, '', '', '')"
    cur.execute(stmt)
        
if __name__ == "__main__":
    db = "sqlite"    

    if len(sys.argv) > 1:
        db = sys.argv[1]
    if db == "sqlite":
        import sqlite3
        # clear file
        os.remove("baseball.db")

        conn = sqlite3.connect("baseball.db")
        cur = conn.cursor()
    elif db == "postgres":
        import psycopg
        # Connect to an existing database
        conn = psycopg.connect("dbname=postgres user=postgres")
        cur = conn.cursor()
    elif db == "clickhouse":
        from clickhouse_driver import Client
        client = Client(host='localhost')
        cur = client
        allViews["game_info_view"] = game_info_view_clickhouse
        allViews["game_situation_view"] = game_situation_view_clickhouse
    else:
        print("unrecognized db", db)
        exit()

    for table, createStmt in allTables.items():
        try:
            if db in ("postgres", "clickhouse"):
                #print(f"dropping table {table}")
                cur.execute(f"DROP TABLE IF EXISTS {table}")
                if db == "postgres":
                    conn.commit()
        except Exception as e:
            pass
        #print(createStmt)
        print("creating table ", table)
        if db == "sqlite":
            createStmt += " WITHOUT ROWID"
             
        #print(createStmt)
        cur.execute(createStmt)

    for view, createStmt in allViews.items():
        try:
            if db in ("postgres", "clickhouse"):
                cur.execute(f"DROP VIEW IF EXISTS {view}")
        except Exception as e:
            pass
        #print(createStmt)
        print("creating view ", view)
        #print(createStmt)
        cur.execute(createStmt)

    print("inserting values")
    for tbl, vals in allValues.items():
        i = 0
        for v in vals:
            stmt = f"INSERT INTO {tbl} VALUES({i}, '{v}')"
            #print(stmt)
            cur.execute(stmt)
            i += 1
    for p in play_baserun:
        stmt = f"INSERT INTO play_baserun VALUES('{p}')"
        #print(stmt)
        cur.execute(stmt)

    stmt = "INSERT INTO left_right VALUES('L', 'Left')"
    cur.execute(stmt)
    stmt = "INSERT INTO left_right VALUES('R', 'Right')"
    cur.execute(stmt)
    stmt = "INSERT INTO left_right VALUES('S', 'Switch')"
    cur.execute(stmt)

    for k, v in playDesc.items():
        stmt = "INSERT INTO play_desc VALUES(" 
        stmt += f"'{k}', '{v}')"
        cur.execute(stmt)

    for k, v in modDesc.items():
        stmt = "INSERT INTO mod_desc VALUES(" 
        stmt += f"'{k}', '{v}')"
        cur.execute(stmt)


    insertDummyValues(cur)
    if db != "clickhouse":
        conn.commit()
        conn.close()
