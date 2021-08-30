from flask import Flask, request
import psycopg2

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/team_stats")
def get_team_stats():
    # Connect to an existing database
    conn = psycopg2.connect("dbname=baseball user=webuser password=webuser")
    cur = conn.cursor()
    qry = "SELECT team, seas_yr, seas_mon, gp, rs, ra, team_er, ind_er "
    qry += "FROM total_by_month "
    qry += "WHERE team='BAL' AND seas_yr=1980 AND seas_mon=8;"

    cur.execute(qry)
    
    resp = "<html><table><tr><th>TEAM<th>YEAR<th>MONTH<th>GP<th>RS<th>RA<th>TEAM_ER<th>INDIV_ER\n"
    
    tup = cur.fetchone()
    while tup is not None:
        resp += "<tr>"
        for x in tup:
            resp += "<td>" + str(x)
        resp += '\n'
        tup = cur.fetchone()    

    cur.close()
    conn.close()
    return resp