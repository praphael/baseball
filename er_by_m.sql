SELECT team, seas_yr, seas_mon, gp, 
    to_char(ip, '9999.99') as ip, 
    ra, team_er, ind_er, 
    to_char(ra_9, '99.99') ra_9, 
    to_char(team_era, '99.99') team_era, 
    to_char(ind_era, '99.99') indiv_era, 
    err as e
FROM total_by_month
WHERE gp > 5 AND ip is NOT NULL 
ORDER BY ind_era DESC limit 20;
