#include "baseball_tables.h"

col_info_t parksCol = col_info_t();
col_info_t teamsCol = col_info_t();
col_info_t boxCol = col_info_t();


void initTableInfo() {
    parksCol.push_back({"park_id", 1}); // char(5) PRIMARY KEY,
    parksCol.push_back({"park_name", 1}); // varchar(64),
    parksCol.push_back({"park_aka", 1}); // varchar(64),
    parksCol.push_back({"park_city", 1});  // varchar(64),
    parksCol.push_back({"park_state", 1}); // varchar(4),
    parksCol.push_back({"park_open", 1});   //date,
    parksCol.push_back({"park_close", 1}); // date,
    parksCol.push_back({"park_league", 1});  // varchar(64),
    parksCol.push_back({"notes", 1}); // varchar(128)

    teamsCol.push_back({"team_id", 1});  // varchar(8),
    teamsCol.push_back({"team_league", 1}); // varchar(64),
    teamsCol.push_back({"team_city", 1}); // varchar(64),
    teamsCol.push_back({"team_nickname", 1}); // varchar(64),
    teamsCol.push_back({"team_first", 0}); // smallint,
    teamsCol.push_back({"team_last", 0}); // smallint

    boxCol.push_back({"game_date", 1}); //date,
    boxCol.push_back({"game_num", 1}); // char(1),
    boxCol.push_back({"game_day_of_week", 1}); // char(3),
    boxCol.push_back({"visiting_team", 1}); // varchar(4),
    boxCol.push_back({"visiting_league", 1}); // varchar(4),
    boxCol.push_back({"visiting_game_num", 0}); // smallint,
    boxCol.push_back({"home_team", 1}); // varchar(4),
    boxCol.push_back({"home_league", 1}); // varchar(4),
    boxCol.push_back({"home_game_num", 0}); // smallint,
    boxCol.push_back({"visiting_score", 0}); // smallint,
    boxCol.push_back({"home_score", 0}); // smallint,
    boxCol.push_back({"game_len_outs", 0}); // smallint,
    boxCol.push_back({"day_night", 1}); // char(1),
    boxCol.push_back({"completed", 0}); // boolean,
    boxCol.push_back({"forfeit", 1}); // varchar(1),
    boxCol.push_back({"protest", 1}); // varchar(2),
    boxCol.push_back({"park", 1}); // varchar(16),
    boxCol.push_back({"attendance", 0}); // integer,
    boxCol.push_back({"game_time_minutes", 0}); // smallint,
    
    boxCol.push_back({"visiting_score_inning_1", 0}); // smallint,
    boxCol.push_back({"visiting_score_inning_2", 0}); // smallint,
    boxCol.push_back({"visiting_score_inning_3", 0}); // smallint,
    boxCol.push_back({"visiting_score_inning_4", 0}); //smallint,
    boxCol.push_back({"visiting_score_inning_5", 0}); // smallint,
    boxCol.push_back({"visiting_score_inning_6", 0}); // smallint,
    boxCol.push_back({"visiting_score_inning_7", 0}); // smallint,
    boxCol.push_back({"visiting_score_inning_8", 0}); // smallint,
    boxCol.push_back({"visiting_score_inning_9", 0}); // smallint,
    boxCol.push_back({"home_score_inning_1", 0}); // smallint,
    boxCol.push_back({"home_score_inning_2", 0}); // smallint,
    boxCol.push_back({"home_score_inning_3", 0}); // smallint,
    boxCol.push_back({"home_score_inning_4", 0}); // smallint,
    boxCol.push_back({"home_score_inning_5", 0}); // smallint,
    boxCol.push_back({"home_score_inning_6", 0}); // smallint,
    boxCol.push_back({"home_score_inning_7", 0}); // smallint,
    boxCol.push_back({"home_score_inning_8", 0}); // smallint,
    boxCol.push_back({"home_score_inning_9", 0}); // smallint,
    boxCol.push_back({"visiting_at_bats", 0}); // smallint,
    boxCol.push_back({"visiting_hits", 0}); // smallint,
    boxCol.push_back({"visiting_doubles", 0}); // smallint,
    boxCol.push_back({"visiting_triples", 0}); // smallint,
    boxCol.push_back({"visiting_home_runs", 0}); //
    boxCol.push_back({"visiting_rbi", 0}); //
    boxCol.push_back({"visiting_sac_hit", 0}); // smallint,
    boxCol.push_back({"visiting_sac_fly", 0}); // smallint,
    boxCol.push_back({"visiting_hit_by_pitch", 0}); // smallint,
    boxCol.push_back({"visiting_walks", 0}); //
    boxCol.push_back({"visiting_int_walks", 0}); // smallint,
    boxCol.push_back({"visiting_strikeouts", 0}); // smallint,
    boxCol.push_back({"visiting_stolen_bases", 0}); // smallint,
    boxCol.push_back({"visiting_caught_stealing", 0}); // smallint,
    boxCol.push_back({"visiting_gidp", 0}); // smallint,
    boxCol.push_back({"visiting_catcher_interference", 0}); // smallint,
    boxCol.push_back({"visiting_left_on_base", 0}); // smallint,
    boxCol.push_back({"visiting_pitchers_used", 0}); // smallint,
    boxCol.push_back({"visiting_indiv_earned_runs", 0}); // smallint,
    boxCol.push_back({"visiting_team_earned_runs", 0}); // smallint,
    boxCol.push_back({"visiting_wild_pitches", 0}); // smallint,
    boxCol.push_back({"visiting_balks", 0}); // smallint,
    boxCol.push_back({"visiting_putouts", 0}); // smallint,
    boxCol.push_back({"visiting_assists", 0}); // smallint,
    boxCol.push_back({"visiting_errors", 0}); // smallint,
    boxCol.push_back({"visiting_passed_balls", 0}); // smallint,
    boxCol.push_back({"visiting_double_plays", 0}); // smallint,
    boxCol.push_back({"visiting_triple_plays", 0}); // smallint,
    
    boxCol.push_back({"home_at_bats", 0}); // smallint,
    boxCol.push_back({"home_hits", 0}); // smallint,
    boxCol.push_back({"home_doubles", 0}); // smallint,
    boxCol.push_back({"home_triples", 0}); // smallint,
    boxCol.push_back({"home_home_runs", 0}); // smallint,
    boxCol.push_back({"home_rbi", 0}); // smallint,
    boxCol.push_back({"home_sac_hit", 0}); // smallint,
    boxCol.push_back({"home_sac_fly", 0}); // smallint,
    boxCol.push_back({"home_hit_by_pitch", 0}); // smallint,
    boxCol.push_back({"home_walks", 0}); // smallint,
    boxCol.push_back({"home_int_walks", 0}); // smallint,
    boxCol.push_back({"home_strikeouts", 0}); // smallint,
    boxCol.push_back({"home_stolen_bases", 0}); // smallint,
    boxCol.push_back({"home_caught_stealing", 0}); // smallint,
    boxCol.push_back({"home_gidp", 0}); // smallint,
    boxCol.push_back({"home_catcher_interference", 0}); // smallint,
    boxCol.push_back({"home_left_on_base", 0}); // smallint,
    boxCol.push_back({"home_pitchers_used", 0}); // smallint,
    boxCol.push_back({"home_indiv_earned_runs", 0}); // smallint,
    boxCol.push_back({"home_team_earned_runs", 0}); // smallint,
    boxCol.push_back({"home_wild_pitches", 0}); // smallint,
    boxCol.push_back({"home_balks", 0}); //,
    boxCol.push_back({"home_putouts", 0}); // smallint,
    boxCol.push_back({"home_assists", 0}); // smallint,
    boxCol.push_back({"home_errors", 0}); // smallint,
    boxCol.push_back({"home_passed_balls", 0}); // smallint,
    boxCol.push_back({"home_double_plays", 0}); // smallint,
    boxCol.push_back({"home_triple_plays", 0}); // smallint,

    /*  Don't nee this info for now
    boxCol.push_back({"umpire_home_plate_id", 1}); // varchar(16),
    boxCol.push_back({"umpire_home_plate_name", 1}); // varchar(64),
    boxCol.push_back({"umpire_1b_id", 1}); // varchar(16),
    boxCol.push_back({"umpire_1b_name", 1}); // varchar(64),
    boxCol.push_back({"umpire_2b_id", 1}); // varchar(16),
    boxCol.push_back({"umpire_2b_name", 1}); // varchar(64),
    boxCol.push_back({"umpire_3b_id", 1}); // varchar(16),
    boxCol.push_back({"umpire_3b_name", 1}); // varchar(64),
    boxCol.push_back({"umpire_lf_id", 1}); // varchar(16),
    boxCol.push_back({"umpire_lf_name", 1}); // varchar(64),
    boxCol.push_back({"umpire_rf_id", 1}); // varchar(16),
    boxCol.push_back({"umpire_rf_name", 1}); // varchar(64),
    boxCol.push_back({"visiting_manager_id", 1}); // varchar(16),
    boxCol.push_back({"visiting_manager_name", 1}); // varchar(64),
    boxCol.push_back({"home_manager_id", 1}); // varchar(16),
    boxCol.push_back({"home_manager_name", 1}); // varchar(64),
    boxCol.push_back({"winning_pitcher_id", 1}); // varchar(16),
    boxCol.push_back({"winning_pitcher_name", 1}); // varchar(64),
    boxCol.push_back({"losing_pitcher_id", 1}); // varchar(16),
    boxCol.push_back({"losing_pitcher_name", 1}); // varchar(64),
    boxCol.push_back({"saving_pitcher_id", 1}); // varchar(16),
    boxCol.push_back({"saving_pitcher_name", 1}); // varchar(64),
    boxCol.push_back({"game_winning_rbi_batter_id", 1}); // varchar(16),
    boxCol.push_back({"game_winning_rbi_batter_name", 1}); // varchar(64),
    boxCol.push_back({"visiting_starting_pitcher_id", 1}); // varchar(16),
    boxCol.push_back({"visiting_starting_pitcher_name", 1}); // varchar(64),
    boxCol.push_back({"home_starting_pitcher_id", 1}); // varchar(16),
    boxCol.push_back({"home_starting_pitcher_name", 1}); //varchar(64),
    
    boxCol.push_back({"visiting_player_1_id", 1}); // varchar(16),
    boxCol.push_back({"visiting_player_1_name", 1}); // varchar(64),
    boxCol.push_back({"visiting_player_1_pos", 1}); // char(1),
    boxCol.push_back({"visiting_player_2_id", 1}); // varchar(16),
    boxCol.push_back({"visiting_player_2_name", 1}); // varchar(64),
    boxCol.push_back({"visiting_player_2_pos", 1}); // char(1),
    boxCol.push_back({"visiting_player_3_id", 1}); // varchar(16),
    boxCol.push_back({"visiting_player_3_name", 1}); // varchar(64),
    boxCol.push_back({"visiting_player_3_pos", 1}); // char(1),
    boxCol.push_back({"visiting_player_4_id", 1}); // varchar(16),
    boxCol.push_back({"visiting_player_4_name", 1}); // varchar(64),
    boxCol.push_back({"visiting_player_4_pos", 1}); // char(1),
    boxCol.push_back({"visiting_player_5_id", 1}); // varchar(16),
    boxCol.push_back({"visiting_player_5_name", 1}); // varchar(64),
    boxCol.push_back({"visiting_player_5_pos", 1}); // char(1),
    boxCol.push_back({"visiting_player_6_id", 1}); // varchar(16),
    boxCol.push_back({"visiting_player_6_name", 1}); // varchar(64),
    boxCol.push_back({"visiting_player_6_pos", 1}); // char(1),
    boxCol.push_back({"visiting_player_7_id", 1}); // varchar(16),
    boxCol.push_back({"visiting_player_7_name", 1}); // varchar(64),
    boxCol.push_back({"visiting_player_7_pos", 1}); // char(1),
    boxCol.push_back({"visiting_player_8_id", 1}); // varchar(16),
    boxCol.push_back({"visiting_player_8_name", 1}); // varchar(64),
    boxCol.push_back({"visiting_player_8_pos", 1}); // char(1),
    boxCol.push_back({"visiting_player_9_id", 1}); // varchar(16),
    boxCol.push_back({"visiting_player_9_name", 1}); // varchar(64),
    boxCol.push_back({"visiting_player_9_pos", 1}); // char(1),
    boxCol.push_back({"home_player_1_id ", 1}); //varchar(16),
    boxCol.push_back({"home_player_1_name", 1}); // varchar(64),
    boxCol.push_back({"home_player_1_pos", 1}); // char(1),
    boxCol.push_back({"home_player_2_id", 1}); //varchar(16),
    boxCol.push_back({"home_player_2_name", 1}); // varchar(64),
    boxCol.push_back({"home_player_2_pos", 1}); // char(1),
    boxCol.push_back({"home_player_3_id", 1}); // varchar(16),
    boxCol.push_back({"home_player_3_name", 1}); // varchar(64),
    boxCol.push_back({"home_player_3_pos", 1}); // char(1),
    boxCol.push_back({"home_player_4_id", 1}); // varchar(16),
    boxCol.push_back({"home_player_4_name", 1}); // varchar(64),
    boxCol.push_back({"home_player_4_pos", 1}); // char(1),
    boxCol.push_back({"home_player_5_id", 1}); // varchar(16),
    boxCol.push_back({"home_player_5_name", 1}); // varchar(64),
    boxCol.push_back({"home_player_5_pos", 1}); // char(1),
    boxCol.push_back({"home_player_6_id", 1}); // varchar(16),
    boxCol.push_back({"home_player_6_name", 1}); //varchar(64),
    boxCol.push_back({"home_player_6_pos", 1}); // char(1),
    boxCol.push_back({"home_player_7_id", 1}); // varchar(16),
    boxCol.push_back({"home_player_7_name", 1}); // varchar(64),
    boxCol.push_back({"home_player_7_pos", 1}); // char(1),
    boxCol.push_back({"home_player_8_id", 1}); // varchar(16),
    boxCol.push_back({"home_player_8_name", 1}); // varchar(64),
    boxCol.push_back({"home_player_8_pos", 1}); // char(1),
    boxCol.push_back({"home_player_9_id", 1}); // varchar(16),
    boxCol.push_back({"home_player_9_name", 1}); // varchar(64),
    boxCol.push_back({"home_player_9_pos", 1}); // char(1),
    boxCol.push_back({"additional_info", 1}); // varchar(128),
    boxCol.push_back({"acq_info", 1}); //
    */
}

const char* CREATE_PARKS = "CREATE TABLE parks ("
"    park_id char(5) PRIMARY KEY,"
"    park_name varchar(64),"
"    park_aka varchar(64),"
"    park_city varchar(64),"
"    park_state varchar(4),"
"    park_open date,"
"    park_close date,"
"    park_league varchar(64),"
"    notes varchar(128))";

const char* CREATE_TEAMS = "CREATE TABLE teams("
"    team_id varchar(8),"
"    team_league varchar(64),"
"    team_city varchar(64),"
"    team_nickname varchar(64),"
"    team_first smallint,"
"    team_last smallint)";

const char* CREATE_BOXSCORE = "CREATE TABLE boxscore ("
"    game_date date,"
"    game_num char(1),"
"    game_day_of_week char(3),"
"    visiting_team varchar(4),"
"    visiting_league varchar(4),"
"    visiting_game_num smallint,"
"    home_team varchar(4),"
"    home_league varchar(4),"
"    home_game_num smallint,"
"    visiting_score smallint,"
"    home_score smallint,"
"    game_len_outs smallint,"
"    day_night char(1),"
"    completed boolean,"
"    forfeit varchar(1),"
"    protest varchar(2),"
"    park varchar(16),"
"    attendance integer,"
"    game_time_minutes smallint,"
"    visiting_score_inning_1 smallint,"
"    visiting_score_inning_2 smallint,"
"    visiting_score_inning_3 smallint,"
"    visiting_score_inning_4 smallint,"
"    visiting_score_inning_5 smallint,"
"    visiting_score_inning_6 smallint,"
"    visiting_score_inning_7 smallint,"
"    visiting_score_inning_8 smallint,"
"    visiting_score_inning_9 smallint,"
"    home_score_inning_1 smallint,"
"    home_score_inning_2 smallint,"
"    home_score_inning_3 smallint,"
"    home_score_inning_4 smallint,"
"    home_score_inning_5 smallint,"
"    home_score_inning_6 smallint,"
"    home_score_inning_7 smallint,"
"    home_score_inning_8 smallint,"
"    home_score_inning_9 smallint,"
"    visiting_at_bats smallint,"
"    visiting_hits smallint,"
"    visiting_doubles smallint,"
"    visiting_triples smallint,"
"    visiting_home_runs smallint,"
"    visiting_rbi smallint,"
"    visiting_sac_hit smallint,"
"    visiting_sac_fly smallint,"
"    visiting_hit_by_pitch smallint,"
"    visiting_walks smallint,"
"    visiting_int_walks smallint,"
"    visiting_strikeouts smallint,"
"    visiting_stolen_bases smallint,"
"    visiting_caught_stealing smallint,"
"    visiting_gidp smallint,"
"    visiting_catcher_interference smallint,"
"    visiting_left_on_base smallint,"
"    visiting_pitchers_used smallint,"
"    visiting_indiv_earned_runs smallint,"
"    visiting_team_earned_runs smallint,"
"    visiting_wild_pitches smallint,"
"    visiting_balks smallint,"
"    visiting_putouts smallint,"
"    visiting_assists smallint,"
"    visiting_errors smallint,"
"    visiting_passed_balls smallint,"
"    visiting_double_plays smallint,"
"    visiting_triple_plays smallint,"
"    home_at_bats smallint,"
"    home_hits smallint,"
"    home_doubles smallint,"
"    home_triples smallint,"
"    home_home_runs smallint,"
"    home_rbi smallint,"
"    home_sac_hit smallint,"
"    home_sac_fly smallint,"
"    home_hit_by_pitch smallint,"
"    home_walks smallint,"
"    home_int_walks smallint,"
"    home_strikeouts smallint,"
"    home_stolen_bases smallint,"
"    home_caught_stealing smallint,"
"    home_gidp smallint,"
"    home_catcher_interference smallint,"
"    home_left_on_base smallint,"
"    home_pitchers_used smallint,"
"    home_indiv_earned_runs smallint,"
"    home_team_earned_runs smallint,"
"    home_wild_pitches smallint,"
"    home_balks smallint,"
"    home_putouts smallint,"
"    home_assists smallint,"
"    home_errors smallint,"
"    home_passed_balls smallint,"
"    home_double_plays smallint,"
"    home_triple_plays smallint,"
/*  Don't need this info for now
"    umpire_home_plate_id varchar(16),"
"    umpire_home_plate_name varchar(64),"
"    umpire_1b_id varchar(16),"
"    umpire_1b_name varchar(64),"
"    umpire_2b_id varchar(16),"
"    umpire_2b_name varchar(64),"
"    umpire_3b_id varchar(16),"
"    umpire_3b_name varchar(64),"
"    umpire_lf_id varchar(16),"
"    umpire_lf_name varchar(64),"
"    umpire_rf_id varchar(16),"
"    umpire_rf_name varchar(64),"
"    visiting_manager_id varchar(16),"
"    visiting_manager_name varchar(64),"
"    home_manager_id varchar(16),"
"    home_manager_name varchar(64),"
"    winning_pitcher_id varchar(16),"
"    winning_pitcher_name varchar(64),"
"    losing_pitcher_id varchar(16),"
"    losing_pitcher_name varchar(64),"
"    saving_pitcher_id varchar(16),"
"    saving_pitcher_name varchar(64),"
"    game_winning_rbi_batter_id varchar(16),"
"    game_winning_rbi_batter_name varchar(64),"
"    visiting_starting_pitcher_id varchar(16),"
"    visiting_starting_pitcher_name varchar(64),"
"    home_starting_pitcher_id varchar(16),"
"    home_starting_pitcher_name varchar(64),"
"    visiting_player_1_id varchar(16),"
"    visiting_player_1_name varchar(64),"
"    visiting_player_1_pos char(1),"
"    visiting_player_2_id varchar(16),"
"    visiting_player_2_name varchar(64),"
"    visiting_player_2_pos char(1),"
"    visiting_player_3_id varchar(16),"
"    visiting_player_3_name varchar(64),"
"    visiting_player_3_pos char(1),"
"    visiting_player_4_id varchar(16),"
"    visiting_player_4_name varchar(64),"
"    visiting_player_4_pos char(1),"
"    visiting_player_5_id varchar(16),"
"    visiting_player_5_name varchar(64),"
"    visiting_player_5_pos char(1),"
"    visiting_player_6_id varchar(16),"
"    visiting_player_6_name varchar(64),"
"    visiting_player_6_pos char(1),"
"    visiting_player_7_id varchar(16),"
"    visiting_player_7_name varchar(64),"
"    visiting_player_7_pos char(1),"
"    visiting_player_8_id varchar(16),"
"    visiting_player_8_name varchar(64),"
"    visiting_player_8_pos char(1),"
"    visiting_player_9_id varchar(16),"
"    visiting_player_9_name varchar(64),"
"    visiting_player_9_pos char(1),"
"    home_player_1_id varchar(16),"
"    home_player_1_name varchar(64),"
"    home_player_1_pos char(1),"
"    home_player_2_id varchar(16),"
"    home_player_2_name varchar(64),"
"    home_player_2_pos char(1),"
"    home_player_3_id varchar(16),"
"    home_player_3_name varchar(64),"
"    home_player_3_pos char(1),"
"    home_player_4_id varchar(16),"
"    home_player_4_name varchar(64),"
"    home_player_4_pos char(1),"
"    home_player_5_id varchar(16),"
"    home_player_5_name varchar(64),"
"    home_player_5_pos char(1),"
"    home_player_6_id varchar(16),"
"    home_player_6_name varchar(64),"
"    home_player_6_pos char(1),"
"    home_player_7_id varchar(16),"
"    home_player_7_name varchar(64),"
"    home_player_7_pos char(1),"
"    home_player_8_id varchar(16),"
"    home_player_8_name varchar(64),"
"    home_player_8_pos char(1),"
"    home_player_9_id varchar(16),"
"    home_player_9_name varchar(64),"
"    home_player_9_pos char(1),"
"    additional_info varchar(128),"
"    acq_info char(1),"
 */
"    PRIMARY KEY(game_date, game_num, home_team))";