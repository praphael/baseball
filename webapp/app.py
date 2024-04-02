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
# map of query to params to 
# first entry - SQL as used in first CTE WHERE clause, including possible renaming
# second entry - SQL as used in second WHERE clause
# third entry - representative value, used for type inference
# fourth entry - true/false, whether this is a "team" stat, to be used for appending 'home/visiting" to field name
QUERY_PARAMS= {"team": ["team", "team", "", True],
               "year": [YEAR_FIELD + " as year", "year", 0, False],
               "month": [MONTH_FIELD + " as month", "month", 0, False],
               "dow": ["game_day_of_week as dow", "dow", "", False]}

def addToWhereClause(qy, p, prms, s):
    prms += (p,)
    if len(prms) == 1:
        qy += " WHERE "
    else:
        qy += " AND "
    qy += (s + "=?")
    return qy, prms

@app.route("/agg")
def get_agg_stats():
    try:
        # build SQL query string from fields provided
        def buildStatQueryStr(stats, isHome):
            statQueryStr = ""
            h = "home"
            v = "visiting"
            fList = []
            for st in stats:
                # '_' prefix denotes sum opposing teams stat
                f = st
                isAgainst = False
                if st[0] == "_":
                    isAgainst = True
                    f = st[1:]
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

                    statQueryStr += fld
                    fList.append((f, isAgainst))
            return statQueryStr, fList
                
        # make common table expression base
        def makeCTEBase(homeOrAway, fieldQueryStr, fieldNames):
            base = " " + homeOrAway + "_t as (SELECT "
            homeOrVisit = homeOrAway
            if homeOrAway == "away":
                homeOrVisit = "visiting"
            for f in fieldNames:
                qp = QUERY_PARAMS[f]
                if qp[3]:
                    base += (homeOrVisit + "_")
                base += qp[0] 
                if qp[3]:
                    base += " as " + f
                base += ", "
            base += " COUNT(*) as gp"
            base += fieldQueryStr
            base += " FROM boxscore"
            return base
        
        def getQueryParams(args):
            fieldNames = []
            fieldValues = []
            for a in args:
                print("a=", a)
                if a in QUERY_PARAMS:
                    qp = QUERY_PARAMS[a]
                    fieldNames.append(a)
                    v = args.get(a)
                    # convert to integer
                    if(type(qp[2]) == type(int)):
                        v = int(v)
                    fieldValues.append(v)

            return fieldNames, fieldValues
        
        def buildCTEWhereClause(isHome, fieldNames):
            qy = " WHERE "
            first = True
            for f in fieldNames:
                if not first:
                    qy += " AND "
                first = False
                # if "team" stat
                qp = QUERY_PARAMS[f]
                if qp[3]:
                    if isHome:
                        qy += " home_"
                    else:
                        qy += " visiting_"
                qy += (qp[1] + "=? ")
            return qy


        args = request.args
        isHome = True
        isAway = True
        
        fieldNames, fieldValues = getQueryParams(args)
        print("fieldNames=", fieldNames)
        print("fieldValues=", fieldValues)
        qy = "WITH"
        stats = "R,_R"
        if "stats" in args:
            stats = args.get("stats")
        stats = stats.split(",")
        print("stats=", stats)
        
        statQueryStrH, statList = buildStatQueryStr(stats, True)
        statQueryStrA, statList = buildStatQueryStr(stats, False)
        qy_home = makeCTEBase("home", statQueryStrH, fieldNames)
        qy_away = makeCTEBase("away", statQueryStrA, fieldNames)

        prmsH = tuple()
        prmsA = tuple()
        whereClauseH = ""
        whereClauseA = ""
        if isHome:
            whereClauseH = buildCTEWhereClause(True, fieldNames)
            qy += qy_home + whereClauseH + ")"
            prmsH = tuple(fieldValues)
        if isAway:
            whereClauseA = buildCTEWhereClause(False, fieldNames)
            if isHome:
                qy += ", "
            qy += qy_away + whereClauseA + ")"
            prmsA = tuple(fieldValues)

        # if home and away selected, must do JOIN
        if isHome and isAway:
            qy += " SELECT " 
            for f in fieldNames:
                qp = QUERY_PARAMS[f]
                qy += ("h." + qp[1] + ", ")
            qy += "h.gp+a.gp as gp, "
            first = True
            for (st, isAgainst) in statList:
                if not first:
                    qy += ", "
                first = False
                if isAgainst:
                    st = "_" + st
                qy += " h." + st + "+" + "a." + st + " as "
                if isAgainst:
                    qy += "_"
                qy += st
            
            qy += " FROM home_t h inner join (SELECT "
            for f in fieldNames:
                qp = QUERY_PARAMS[f]
                qy += (qp[1] + ", ")
            qy += "gp, "
            first = True
            for (st, isAgainst) in statList:
                if not first:
                    qy += ", "
                first = False
                if isAgainst:
                    st = "_" + st
                qy += st
            qy += " FROM away_t) a"
            qy += " ON"
            first = True
            for f in fieldNames:
                if not first:
                    qy += " AND "
                first = False
                qp = QUERY_PARAMS[f]
                qy += " h." + qp[1] + "=a." + qp[1]
        elif isHome:
            qy += " SELECT * from home_t"
        elif isAway:
            qy += " SELECT * from away_t"

        print("query= ", qy)
        print("prms= ", prmsH + prmsA)
        r = appdb.executeQuery(db, qy, prmsH + prmsA)
        print(r)
        # make header
        hdr = fieldNames
        hdr.append("GP")
        for (st, isAgainst) in statList:
            fld = ""
            if isAgainst:
                fld = "_"
            fld += st
            hdr.append(fld)
        return json.dumps({"header": hdr, "result": r}), 200
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

