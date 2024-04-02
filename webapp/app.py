from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta, timezone
import argparse
import json
import logging
import appdb
from traceback import print_exception

app = Flask(__name__)
db = appdb.DB.sqlite

MONTH_FIELD = "CAST(substr(game_date,6,2) AS INTEGER)"
YEAR_FIELD = "CAST(substr(game_date,0,5) AS INTEGER)"

FIELD_NAME_MAP = {"R":"score",
                  "AB":"at_bats", 
                  "H":"hits",
                  "2B":"doubles",
                  "3B":"triples",
                  "HR":"home_runs",
                  "RBI":"rbi", 
                  "SH":"sac_hit",
                  "SF":"sac_fly",
                  "HBP":"hit_by_pitch",
                  "BB":"walks",
                  "IBB":"int_walks",
                  "K":"strikeouts", 
                  "SB":"stolen_bases",
                  "CS":"caught_stealing", 
                  "GIDP":"gidp",
                  "CI":"catcher_interference", 
                  "LOB":"left_on_base",
                  "ERI":"indiv_earned_runs",
                  "ERT":"team_earned_runs",
                  "WP":"wild_pitches",
                  "BLK":"balks",
                  "PO":"putouts",
                  "A":"assists",
                  "E":"errors",
                  "PB":"passed_balls",
                  "DP":"double_plays",
                  "TP":"triple_plays"}

def addToWhereClause(qy, p, prms, s):
    prms += (p,)
    if len(prms) == 1:
        qy += " WHERE "
    else:
        qy += " AND "
    qy += (s + "=?")
    return qy, prms

@app.route("/agg/<team>/<year>/<month>")
def get_agg_stats(team=None, year=None, month=None):
    try:
        # build SQL query string from fields provided
        def buildFields(args, isHome):
            fieldQueryStr = ""
            h = "home"
            v = "visiting"
            fList = []
            for a in args:
                # '_' prefix denotes sum opposing teams stat
                f = a
                isAgainst = False
                if a[0] == "_":
                    isAgainst = True
                    f = a[1:]
                if f in FIELD_NAME_MAP:
                    fName = FIELD_NAME_MAP[f]
                    b = v
                    ob = h
                    if isHome:
                        b = h
                        ob = v
                    if isAgainst:
                        b = ob # switch
                    fld = ", sum(" + b + "_" + fName + ") as "
                    if isAgainst:
                        fld += "_"
                    fld += f

                    fieldQueryStr += fld
                    fList.append((f, isAgainst))
            return fieldQueryStr, fList
                
        # make common table expression base
        def makeCTEBase(homeOrAway, fieldQueryStr):
            base = " " + homeOrAway + "_t as (SELECT COUNT(*) as gp"
            base += fieldQueryStr
            base += " FROM boxscore"
            return base

        args = request.args
        isHome = True
        isAway = True
        
        if team is None and "team" in args:
            team = args["team"]
        if year is None and "year" in args:
            year = args["year"]
            #substr(game_date,0,5)
        if month is None and "month" in args:
            month = args["month"]
            #substr(game_date,6,2)
        if year is not None:
            year = int(year)
        if month is not None:
            month = int(month)
        qy = "WITH"
        q="R,_R"
        if hasattr(args, "q"):
            q = args.q
        qf = q.split(",")
        fQueryStrH, fieldList = buildFields(qf, True)
        fQueryStrA, fieldList = buildFields(qf, False)
        qy_home = makeCTEBase("home", fQueryStrH)
        qy_away = makeCTEBase("away", fQueryStrA)

        prmsH = tuple()
        prmsA = tuple()
        whereClauseH = ""
        whereClauseA = ""
        if team is not None:
            if isHome:
                whereClauseH, prmsH = addToWhereClause(whereClauseH, team, prmsH, "home_team")
            if isAway:
                whereClauseA, prmsA = addToWhereClause(whereClauseA, team, prmsA, "visiting_team")
        if month is not None:
            if isHome:
                whereClauseH, prmsH = addToWhereClause(whereClauseH, month, prmsH, MONTH_FIELD)
            if isAway:
                whereClauseA, prmsA = addToWhereClause(whereClauseA, month, prmsA, MONTH_FIELD)
        if year is not None:
            if isHome:
                whereClauseH, prmsH = addToWhereClause(whereClauseH, year, prmsH, YEAR_FIELD)
            if isAway:
                whereClauseA, prmsA = addToWhereClause(whereClauseA, year, prmsA, YEAR_FIELD)
        if isHome:
            qy += qy_home + whereClauseH + ")"
        if isAway:
            if isHome:
                qy += ", "
            qy += qy_away + whereClauseA + ")"

        # if home and away selected, sum all fields
        if isHome and isAway:
            qy += " SELECT h.gp+a.gp as gp, "
            first = True
            for (f, isAgainst) in fieldList:
                if not first:
                    qy += ", "
                first = False
                if isAgainst:
                    f = "_" + f
                qy += " h." + f + "+" + "a." + f + " as "
                if isAgainst:
                    qy += "_"
                qy += f
            
            qy += " FROM home_t h join (SELECT gp, "
            first = True
            for (f, isAgainst) in fieldList:
                if not first:
                    qy += ", "
                first = False
                if isAgainst:
                    f = "_" + f
                qy += f
            qy += " FROM away_t) a"
        elif isHome:
            qy += " SELECT * from home_t"
        elif isAway:
            qy += " SELECT * from away_t"

        print("query= ", qy)
        print("prms= ", prmsH + prmsA)
        r = appdb.executeQuery(db, qy, prmsH + prmsA)
        print(r)
        return json.dumps({"ret": r}), 200
    except Exception as e:
        print_exception(e)
        return str(e), 500

if __name__ == '__main__':
    defaultHost = '127.0.0.1'
    defaultPort = 5000
    parser = argparse.ArgumentParser(
                    prog='app.py',
                    description='Baseball stats server in Flask',
                    epilog='T')
    parser.add_argument('-o', '--host', default=defaultHost) 
    parser.add_argument('-p', '--port', default=defaultPort) 
    parser.add_argument('-d', '--debug', default=False, action='store_true') 
    parser.add_argument('-b', '--database', default='sqlite') 
    parser.add_argument('-k', '--key', required=True) 
    args = parser.parse_args()
    db = appdb.supportedDBs[args.database]
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.secret_key = args.key

    app.run(host=args.host, port=args.port, debug=args.debug)

