DROP TABLE IF EXISTS home_er;
DROP TABLE IF EXISTS visiting_er;
DROP TABLE IF EXISTS total_er;
DROP TABLE IF EXISTS home_er_gm_num;
DROP TABLE IF EXISTS visiting_er_gm_num;

CREATE TABLE home_er AS
    SELECT home_team AS team, 
        EXTRACT(YEAR FROM game_date) AS game_year, 
        EXTRACT(MONTH FROM game_date) AS game_month, 
        count(*) AS gp, 
        sum(visiting_score) AS ra, 
        sum(home_team_earned_runs) AS t_er, 
        sum(home_indiv_earned_runs) AS i_er, 
        sum(3 * ceil((game_len_outs::float / 3) / 2)) AS outs, 
        sum(home_errors) as err
    FROM boxscore
    WHERE home_team_earned_runs IS NOT NULL
    GROUP BY home_team, EXTRACT(YEAR FROM game_date), EXTRACT (MONTH FROM game_date);

CREATE TABLE visiting_er AS
    SELECT visiting_team AS team, 
        EXTRACT(YEAR FROM game_date) AS game_year, 
        EXTRACT(MONTH FROM game_date) AS game_month,
        count(*) AS gp, 
        sum(home_score) AS ra, 
        sum(visiting_team_earned_runs) AS t_er, 
        sum(visiting_indiv_earned_runs) AS i_er, 
        sum(game_len_outs - 3 * ceil((game_len_outs::float / 3) / 2)) AS outs,
        sum(visiting_errors) as err
    FROM boxscore
    WHERE visiting_team_earned_runs IS NOT NULL
    GROUP BY visiting_team, EXTRACT(YEAR FROM game_date), EXTRACT (MONTH FROM game_date);

CREATE TABLE total_er AS
    SELECT home_er.team AS team, 
        home_er.game_year AS game_year, 
        home_er.game_month AS game_month,
        home_er.gp + visiting_er.gp AS gp, 
        home_er.ra + visiting_er.ra AS ra, 
        home_er.t_er + visiting_er.t_er AS t_er, 
        home_er.i_er + visiting_er.i_er AS i_er, 
        home_er.outs + visiting_er.outs AS outs, 
        (home_er.outs + visiting_er.outs)::float / 3 AS ip, 
        (home_er.ra + visiting_er.ra) / 
        ((home_er.outs + visiting_er.outs)::float / 3 / 9) AS ra_9,
        (home_er.t_er + visiting_er.t_er) / 
        ((home_er.outs + visiting_er.outs)::float / 3 / 9) AS t_era,
        (home_er.i_er + visiting_er.i_er) / 
        ((home_er.outs + visiting_er.outs)::float / 3 / 9) AS i_era,
        (home_er.err + visiting_er.err) as err
    FROM  home_er, visiting_er
    WHERE home_er.team  = visiting_er.team
        AND home_er.game_year = visiting_er.game_year
        AND home_er.game_month = visiting_er.game_month;

SELECT team, game_year as year, game_month as mon, gp, 
    to_char(ip, '9999.99') as ip, 
    ra, t_er, i_er, 
    to_char(ra_9, '99.99') ra_9, 
    to_char(t_era, '99.99') tm_era, 
    to_char(i_era, '99.99') ind_era, 
    err as e
FROM total_er
WHERE gp > 5 ORDER BY i_era DESC limit 20;
