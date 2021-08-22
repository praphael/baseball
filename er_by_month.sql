DROP TABLE IF EXISTS home_er_by_month;
DROP TABLE IF EXISTS visiting_er_by_month;
DROP TABLE IF EXISTS total_er_by_month;

CREATE TABLE home_er_by_month AS
    SELECT home_team AS team, sum(home_team_earned_runs) AS er, EXTRACT(YEAR FROM game_date) AS game_year, EXTRACT (MONTH FROM game_date) AS game_month, count(*) AS num_games
    FROM boxscore
    WHERE home_team_earned_runs IS NOT NULL
    GROUP BY home_team, EXTRACT(YEAR FROM game_date), EXTRACT (MONTH FROM game_date);

CREATE TABLE visiting_er_by_month AS
    SELECT visiting_team AS team, sum(visiting_team_earned_runs) AS er, EXTRACT(YEAR FROM game_date) AS game_year, EXTRACT (MONTH FROM game_date) AS game_month, count(*) AS num_games
    FROM boxscore
    WHERE visiting_team_earned_runs IS NOT NULL
    GROUP BY visiting_team, EXTRACT(YEAR FROM game_date), EXTRACT (MONTH FROM game_date);    

CREATE TABLE total_er_by_month AS
    SELECT team, SUM(er) as er, game_month, game_year, SUM(num_games) AS num_games, CAST(SUM(er) AS FLOAT) / SUM(num_games) as era
    FROM (
        SELECT * 
        FROM home_er_by_month
        UNION 
        SELECT *
        FROM visiting_er_by_month
    ) tmp
    GROUP BY team, game_month, game_year;
