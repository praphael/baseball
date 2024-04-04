from flask import Flask, make_response, request, render_template, redirect, url_for
from datetime import datetime, timedelta, timezone
import calendar
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
               "dow": ["game_day_of_week as dow", "dow", "", False],
               "league": ["league", "league", "", True],
               "park": ["park", "park", "", False],
               "inn1": ["score_by_inning_1", "inn1", 0, True],
               "inn2": ["score_by_inning_2", "inn2", 0, True],
               "inn3": ["score_by_inning_3", "inn3", 0, True],
               "inn4": ["score_by_inning_4", "inn4", 0, True],
               "inn5": ["score_by_inning_5", "inn5", 0, True],
               "inn6": ["score_by_inning_6", "inn6", 0, True],
               "inn7": ["score_by_inning_7", "inn7", 0, True],
               "inn8": ["score_by_inning_8", "inn8", 0, True],
               "inn9": ["score_by_inning_9", "inn9", 0, True]
               }

def make_dt_ms_str(dt):
    return str(int(dt.microseconds / 1000))

def addToWhereClause(qy, p, prms, s):
    prms += (p,)
    if len(prms) == 1:
        qy += " WHERE "
    else:
        qy += " AND "
    qy += (s + "=?")
    return qy, prms

# build SQL query string from fields provided
def buildStatQueryStr(stats, isHome, agg="sum"):
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
            if agg == "avg":
                fld = f", trunc(100*{agg}(" + b + "_" + fName + "))/100.00 as "
            elif agg == "no":   # no aggregaton
                fld = f", " + b + "_" + fName + " as "
            else:  # use sum as default
                fld = f", sum(" + b + "_" + fName + ") as "
            if isAgainst:
                fld += "_"
            fld += f

            statQueryStr += fld
            fList.append((f, isAgainst))
            
    return statQueryStr, fList

# make common table expression base
def makeCTEBase(homeOrAway, fieldQueryStr, fieldNames, agg, grp):
    base = " " + homeOrAway + "_t as (SELECT "
    print("makeCTEBase grp=", grp)
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
    for g in grp:
        if g in QUERY_PARAMS:
            qp = QUERY_PARAMS[g]
            if qp[3]:
                base += (homeOrVisit + "_")
            base += qp[0] 
            if qp[3]:
                base += " as " + g
            base += ", "
    if agg != "no":
        base += " COUNT(*) as gp"
    else: 
        base += " game_date as date, game_num as num, home_team as home, visiting_team as away"
    base += fieldQueryStr
    base += " FROM boxscore"
    
    return base

def getQueryParams(args):
    fieldNames = []
    fieldValues = []
    for a in args:
        if a in QUERY_PARAMS:
            qp = QUERY_PARAMS[a]
            fieldNames.append(a)
            v = args.get(a)
            # convert to integer
            if(type(qp[2]) == type(int)):
                v = int(v)
            fieldValues.append(v)

    return fieldNames, fieldValues

def buildCTEWhereClause(isHome, fieldNames, grp):
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

    if len(grp) > 0: 
        qy += " GROUP BY "
        first = True
        for f in fieldNames:
            qp = QUERY_PARAMS[f]
            if not first:
                qy += ", "
            first = False
            qy += qp[1]
            
        for g in grp:
            if g in QUERY_PARAMS:
                qp = QUERY_PARAMS[g]
                if not first:
                    qy += ", "
                first = False
                qy += qp[1] 
    return qy    
    
def renderHTMLTable(headers, result, opts):
    tblAttr=''
    tbAttr=''
    trAttr=''
    tdAttr=''
    thAttr=''
    if opts == "-bs":
        tblAttr='class="table table-hover table-striped"'
        tbAttr='table-group-divider'
        trAttr='class="tr"'
        tdAttr='class="td"'
        thAttr='scope="row"'
                
    h = f"<table {tblAttr}>"
    h += f"<thead><tr>"
    for hdr in headers:
        h += (f"<th {thAttr}>" + hdr + "</th>")
    h += f"</tr></thead><tbody{tbAttr}>"
    for r in result:
        h += f"<tr {trAttr}>"
        for d in r:
            h += f"<td {tdAttr}>" + str(d) + "</td>"
        h += "</tr>"
    h += "</tbody></table>"
    return h

@app.route("/box", methods=["OPTIONS"])
def options_box():
    resp = make_response("OK", 200)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    return resp

@app.route("/box")
def get_box_stats():
    try:
        t_preproc_start = datetime.now()
        print(datetime.now())
        args = request.args
        isHome = True
        isAway = True
        if "home" in args:
            isHome = bool(args.get("home"))
            isAway = False
        if "away" in args:
            if "home" not in args:
                isHome = False
            isAway = bool(args.get("away"))
        agg = "sum"
        if "agg" in args:
            agg = args.get("agg")
        grp = []
        if "grp" in args:
            grp = args.get("grp")
            grp = grp.split(",")

        fieldNames, fieldValues = getQueryParams(args)
        print("grp=", grp)
        print("fieldNames=", fieldNames)
        print("fieldValues=", fieldValues)
        commonNames = set(grp).intersection(set(fieldNames))
        if len(commonNames) > 0:
            errMsg = "Error '" + "', '".join(commonNames) + "' cannot appear in both field and group"
            print(errMsg)
            resp = make_response(errMsg, 400)
            resp.headers["Access-Control-Allow-Origin"] = "*"
            return resp

        qy = "WITH"
        stats = "R,_R"
        if "stats" in args:
            stats = args.get("stats")
        stats = stats.split(",")
        print("stats=", stats)

        statQueryStrH, statList = buildStatQueryStr(stats, True, agg)
        statQueryStrA, statList = buildStatQueryStr(stats, False, agg)
        qy_home = makeCTEBase("home", statQueryStrH, fieldNames, agg, grp)
        qy_away = makeCTEBase("away", statQueryStrA, fieldNames, agg, grp)

        prmsH = tuple()
        prmsA = tuple()
        whereClauseH = ""
        whereClauseA = ""
        if isHome:
            whereClauseH = buildCTEWhereClause(True, fieldNames, grp)
            qy += qy_home + whereClauseH + ")"
            prmsH = tuple(fieldValues)
        if isAway:
            whereClauseA = buildCTEWhereClause(False, fieldNames, grp)
            if isHome:
                qy += ", "
            qy += qy_away + whereClauseA + ")"
            prmsA = tuple(fieldValues)

        # if home and away selected, must do JOIN (unless no aggregation)
        if isHome and isAway:
            if agg == "no":
                qy += " SELECT * from home_t UNION SELECT * from away_t"
            else:
                qy += " SELECT " 
                for f in fieldNames:
                    qp = QUERY_PARAMS[f]
                    qy += ("h." + qp[1] + ", ")
                for g in grp:
                    qp = QUERY_PARAMS[g]
                    qy += f"h.{qp[1]}, "
                qy += "h.gp+a.gp as gp, "
                first = True
                for (st, isAgainst) in statList:
                    if not first:
                        qy += ", "
                    first = False
                    if isAgainst:
                        st = "_" + st
                    # separate out home/away    
                    if agg == "sum":
                        qy += " h." + st + "+" + "a." + st 
                    elif agg == "average":
                        # for averages need to reweight/home away based on gams played
                        qy += f" trunc(100*(h.{st}/(1.0*(h.gp+a.gp)) + a.{st}/(1.0*(h.gp+a.gp))))/100.0"
                    qy += " as "
                    if isAgainst:
                        qy += "_"
                    qy += st
                
                qy += " FROM home_t h"
                if agg == "no":
                    qy += " UNION "
                else:
                    qy += " INNER JOIN "
                qy += " (SELECT "

                for f in fieldNames:
                    qp = QUERY_PARAMS[f]
                    qy += (F"{qp[1]}, ")
                for g in grp:
                    qy += (g + ", ")
                if agg == "no":
                    qy += "date, num, home, away, "
                else:
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
                # JOIN conditions
                if agg != "no":
                    qy += " ON"
                    first = True
                    for f in fieldNames:
                        if not first:
                            qy += " AND "
                        first = False
                        qp = QUERY_PARAMS[f]
                        qy += " h." + qp[1] + "=a." + qp[1]
                    for g in grp:
                        if not first:
                            qy += " AND "
                        first = False
                        qp = QUERY_PARAMS[g]
                        qy += f" h.{qp[1]}=a.{qp[1]}"
                
                    #qy += " AND h.date=a.date AND h.num=a.num"
                    #qy += " AND h.home=a.home AND h.away=a.away"
        elif isHome:
            qy += " SELECT * from home_t"
        elif isAway:
            qy += " SELECT * from away_t"

        qy += " LIMIT 101" 
        print("query= ", qy)
        print("prms= ", prmsH + prmsA)
        dt_preproc = datetime.now() - t_preproc_start
        try: 
            r, query_times = appdb.executeQuery(db, qy, prmsH + prmsA)
            fn = lambda t: t[0] + ": " + str(int((t[1].microseconds)/1000)) + " ms"
            l = list(map(fn, query_times))
            print("query successful times= ", l)
        except Exception as e:
            print("query failed e=", e)
            errMsg = "Query failed exception: " + str(e) + "\n"
            errMsg += ("query: " + qy)
            resp = make_response(errMsg, 500)
            resp.headers["Access-Control-Allow-Origin"] = "*"
            return resp
        t_postproc_start = datetime.now()
        print(r)
        # make header
        hdr = fieldNames
        if grp is not None:
            hdr.extend(grp)
        if agg != "no":
            hdr.append("GP")
        else:
            hdr.extend(["date", "num", "home", "away"])
        for (st, isAgainst) in statList:
            fld = ""
            if isAgainst:
                fld = "_"
            fld += st
            
            hdr.append(fld)

        # fix month from numer to string value
        if "month" in hdr:
            monthIdx = hdr.index("month")
            i = 0
            for t in r:
                r2 = list(t)
                month = calendar.month_name[t[monthIdx]]
                r2[monthIdx] = month
                r[i] = tuple(r2)
                i += 1
            print("r(fixed month)=", r)

        ret = "json"
        if "ret" in args:
            ret = args.get("ret")
        print("ret=", ret)
        
        if ret.startswith("html"):
            opts=ret[4:]
            resp = make_response(renderHTMLTable(hdr, r, opts), 200)
        else:
            resp = make_response(json.dumps({"header": hdr, "result": r}), 200)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        dt_postproc = datetime.now() - t_postproc_start
        dt_pre = make_dt_ms_str(dt_preproc)
        dt_post = make_dt_ms_str(dt_postproc)
        dt_query = make_dt_ms_str(query_times[0][1])
        print(f"Times: Pre: {dt_pre} Query: {dt_query} Post: {dt_post}")
        return resp 
    except Exception as e:
        print_exception(e)
        resp = make_response(str(e), 500)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

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

