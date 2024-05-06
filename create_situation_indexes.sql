CREATE TABLE game_info2 AS SELECT * FROM game_info_view;

CREATE INDEX game_info2_idx1 ON game_info2(game_id);
CREATE INDEX game_info2_idx2 ON game_info2(year, month);
CREATE INDEX game_info2_idx3 ON game_info2(home_team);
CREATE INDEX game_info2_idx4 ON game_info2(away_team);

CREATE INDEX pl_game_bat_idx1 ON player_game_batting(game_id);
CREATE INDEX pl_game_bat_idx2 ON player_game_batting(batter_num_id);
CREATE INDEX pl_game_bat_idx3 ON player_game_batting(team);
CREATE INDEX pl_game_fld_idx1 ON player_game_fielding(game_id);
CREATE INDEX pl_game_fld_idx2 ON player_game_fielding(fielder_num_id);
CREATE INDEX pl_game_fld_idx3 ON player_game_fielding(team);
CREATE INDEX pl_game_pit_idx1 ON player_game_pitching(game_id);
CREATE INDEX pl_game_pit_idx2 ON player_game_pitching(pitcher_num_id);
CREATE INDEX pl_game_pit_idx3 ON player_game_pitching(team);

CREATE INDEX game_sit_idx1 ON game_situation(game_id, event_id);
CREATE INDEX game_sit_idx2 ON game_situation(batter_num_id);
CREATE INDEX game_sit_idx3 ON game_situation(pitcher_num_id);

CREATE INDEX game_sit_bases_idx ON game_situation_bases(game_id, event_id);
CREATE INDEX game_sit_result2_idx ON game_situation_result2(game_id, event_id);
CREATE INDEX game_sit_result3_idx ON game_situation_result3(game_id, event_id);

CREATE INDEX game_sit_fld_ass_idx ON game_situation_fielder_assist(game_id, event_id);
CREATE INDEX game_sit_fld_po_idx ON game_situation_fielder_putout(game_id, event_id);
CREATE INDEX game_sit_fld_err_idx ON game_situation_fielder_error(game_id, event_id);
CREATE INDEX game_sit_fld_fld_idx ON game_situation_fielder_fielded(game_id, event_id);

CREATE INDEX game_sit_r1_mod_idx ON game_situation_result1_mod(game_id, event_id);
CREATE INDEX game_sit_r2_mod_idx ON game_situation_result2_mod(game_id, event_id);
CREATE INDEX game_sit_r3_mod_idx ON game_situation_result3_mod(game_id, event_id);

CREATE INDEX game_sit_base_run_idx ON game_situation_base_run(game_id, event_id);
CREATE INDEX game_sit_base_run_mod_idx ON game_situation_base_run_mod(game_id, event_id);
