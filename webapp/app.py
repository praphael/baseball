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
API_ROOT = "/baseball/api"

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
                  "TP":"triple_plays",
                  "I1":"score_by_inning_1",
                  "I2":"score_by_inning_2",
                  "I3":"score_by_inning_3",
                  "I4":"score_by_inning_4",
                  "I5":"score_by_inning_5",
                  "I6":"score_by_inning_6",
                  "I7":"score_by_inning_7",
                  "I8":"score_by_inning_8",
                  "I9":"score_by_inning_9"}
                  
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

def isNumberChar(c):
    return ord(c) in range(ord('0'), ord('9')+1)

def toUpper(c):
    if ord(c) in range(ord('a'), ord('z')+1):
        return chr(ord('A') + ord(c) - ord('a'))
    return c

def makeHomeAwayAvgQuery(st):
    h = f"h.{st}/(1.0*(h.gp+a.gp))"
    a = f"a.{st}/(1.0*(h.gp+a.gp))"
    avg = f"trunc(100*({h} + {a}))/100.0"
    return avg

def addToWhereClause(qy, p, prms, s):
    prms += (p,)
    if len(prms) == 1:
        qy += " WHERE "
    else:
        qy += " AND "
    qy += (s + "=?")
    return qy, prms

# build SQL query string from fields provided
def buildStatQueryStr(stats, isHome, agg):
    statQueryStr = ""
    h = "home"
    v = "visiting"
    statList = []
    print("buildStatQueryStr agg=", agg)
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
            st = f
            if isAgainst:
                st = "_" + f
            elif isNumberChar(f[0]):
                st = "n" + f
            fld += st

            statQueryStr += fld
            statList.append(st)
            
    return statQueryStr, statList

# make common table expression base
# fieldNames are names that appear in SELECT
def makeCTEBase(homeOrAway, fieldQueryStr, fieldNames, agg, grp):
    base = " " + homeOrAway + "_t as (SELECT "
    print("makeCTEBase grp=", grp)
    print("makeCTEBase fieldNames=", fieldNames)
    homeOrVisit = homeOrAway
    selectFields = []
    
    if homeOrAway == "away":
        homeOrVisit = "visiting"
    for f in fieldNames:
        selectFields.append(f)
        qp = QUERY_PARAMS[f]
        if qp[3]:
            base += (homeOrVisit + "_")
        base += qp[0] 
        if qp[3]:
            base += " as " + f
        base += ", "
    nGroup = 0
    for g in grp:
        if g == "homeaway":
            hOrA = toUpper(homeOrAway[0]) + homeOrAway[1:]
            base += f"'{hOrA}' as homeoraway, "
            selectFields.append("homeoraway")
            nGroup += 1
        elif g in QUERY_PARAMS:
            selectFields.append(g)
            qp = QUERY_PARAMS[g]
            if qp[3]:
                base += (homeOrVisit + "_")
            base += qp[0] 
            if qp[3]:
                base += " as " + g
            base += ", "
            nGroup += 1
    if agg != "no" or nGroup > 0:
        base += " COUNT(*) as gp"
        selectFields.append("gp")
    else: 
        base += " game_date as date, game_num as num, home_team as home, visiting_team as away"
        selectFields.extend(["date", "num", "home", "away"])

    base += fieldQueryStr
    base += " FROM boxscore"
    
    return base, selectFields

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

def buildCTEWhereClause(isHome, fieldNames, grp, isOldTime):
    first = True
    qy = ""
    if not isOldTime:
        qy = f" WHERE {YEAR_FIELD} > 1902 "
        first = False

    for f in fieldNames:
        if not first:
            qy += " AND "
        else:
            qy = " WHERE "
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

@app.route(API_ROOT+"/box", methods=["OPTIONS"])
def options_box():
    resp = make_response("OK", 200)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    return resp

@app.route(API_ROOT+"/parks", methods=["OPTIONS"])
def options_parks():
    resp = make_response("OK", 200)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    return resp

@app.route(API_ROOT+"/teams", methods=["OPTIONS"])
def options_teams():
    resp = make_response("OK", 200)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    return resp

@app.route(API_ROOT+"/teams")
def get_teams():
    try: 
        args = request.args
        since = 1900
        if "since" in args:
            since = int(args.get("since"))
        qy = """SELECT DISTINCT t.team_id, t.team_league, t.team_city, 
                team_nickname, team_first, team_last  
                FROM teams t 
                INNER JOIN boxscore b 
                ON t.team_id=b.home_team WHERE team_last > ?
                """
        r, query_times = appdb.executeQuery(db, qy, (since,))
        fn = lambda t: t[0] + ": " + str(int((t[1].microseconds)/1000)) + " ms"
        l = list(map(fn, query_times))
        print("/teams query successful times= ", l)
        hdr = ("team_id", "team_league", "team_city",
               "team_nickname", "team_first", "team_last")
        app.team_names = dict()
        for row in r:
            app.team_names[row[0]] = row[2] + " " + row[3]
        resp = make_response(json.dumps({"header": hdr, "result": r}), 200)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    except Exception as e:
        print("query failed e=", e)
        errMsg = "Query failed exception: " + str(e) + "\n"
        errMsg += ("query: " + qy)
        resp = make_response(errMsg, 500)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

@app.route(API_ROOT+"/parks")
def get_parks():
    try: 
        args = request.args
        since = 1900
        if "since" in args:
            since = int(args.get("since"))
        qy = """SELECT DISTINCT p.park_id, p.park_name, 
            p.park_aka, p.park_city, p.park_state,
            p.park_open, p.park_close, p.park_league, p.notes
             FROM parks p
             INNER JOIN boxscore b 
             ON p.park_id=b.park
            WHERE CAST(substr(p.park_open, 7) AS INTEGER) > ?"""
        r, query_times = appdb.executeQuery(db, qy, (since,))
        fn = lambda t: t[0] + ": " + str(int((t[1].microseconds)/1000)) + " ms"
        l = list(map(fn, query_times))
        print("/parks query successful times= ", l)
        hdr = ("park_id","park_name","park_aka", "park_city",
                "park_state", "park_open", "park_close",
                "park_league", "notes")
        resp = make_response(json.dumps({"header": hdr, "result": r}), 200)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    except Exception as e:
        print("query failed e=", e)
        errMsg = "Query failed exception: " + str(e) + "\n"
        errMsg += ("query: " + qy)
        resp = make_response(errMsg, 500)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

@app.route(API_ROOT+"/box")
def get_box_stats():
    try:
        t_preproc_start = datetime.now()
        print(datetime.now())
        args = request.args
        print("args=", args)
        isHome = True
        isAway = True
        if "homeaway" in args:
            homeaway = args.get("homeaway")
            if homeaway == "home":
                isHome = True
                isAway = False
            elif homeaway == "away":
                isHome = False
                isAway = True            
        agg = "sum"
        if "agg" in args:
            if args.get("agg") in ('no', 'sum', 'avg'):
                agg = args.get("agg")
            
        grp = []
        if "grp" in args:
            grp = args.get("grp")
            grp = grp.split(",")

        isOldTime = False
        if "oldtime" in args:
            isOldTime = args.get("premod")
            isOldTime = bool(int(isOldTime))
            

        fieldNames, fieldValues = getQueryParams(args)
        print("grp=", grp)
        print("fieldNames=", fieldNames)
        print("fieldValues=", fieldValues)

        qy = "WITH"
        stats = "R,_R"
        if "stats" in args:
            stats = args.get("stats")
        stats = stats.split(",")
        order="year,team,date"
        if "order" in args:
            order = args.get("order")
        order = order.split(",")

        print("stats=", stats)

        statQueryStrH, statList = buildStatQueryStr(stats, True, agg)
        statQueryStrA, statList = buildStatQueryStr(stats, False, agg)
        print(f"statList=", statList)
        qy_home, selectFieldsH = makeCTEBase("home", statQueryStrH, fieldNames, agg, grp)
        qy_away, selectFieldsA = makeCTEBase("away", statQueryStrA, fieldNames, agg, grp)
        print(f"selectFieldsH=", selectFieldsH)        
        prmsH = tuple()
        prmsA = tuple()
        whereClauseH = ""
        whereClauseA = ""
        if isHome:
            whereClauseH = buildCTEWhereClause(True, fieldNames, grp, isOldTime)
            qy += qy_home + whereClauseH + ")"
            prmsH = tuple(fieldValues)
        if isAway:
            whereClauseA = buildCTEWhereClause(False, fieldNames, grp, isOldTime)
            if isHome:
                qy += ", "
            qy += qy_away + whereClauseA + ")"
            prmsA = tuple(fieldValues)

        # if park is part of query, JOIN with park names
        isPark = False
        if "park" in selectFieldsH:
            isPark = True
        isTeam = False
        if "team" in selectFieldsH:
            isTeam = True

        def makeFieldParkTeam(x):
            if x == "park":
                return f"p.park_name AS park"
            return f"h.{x}"
            
        print(f"selectFieldsH=", selectFieldsH)
        # fields which have perfomed h.f + a.f
        # for use in ordering
        fieldsSummed = set()
        fieldsAveraged = set()
        # if home and away selected, must do JOIN (unless no aggregation)
        if isHome and isAway:
            if (agg == "no" and len(grp) == 0) or "homeaway" in grp:
                # rewrite fields for join on park
                if isPark or isTeam:
                    fields = ", ".join(list(map(makeFieldParkTeam, selectFieldsH)))
                    fields += ", " + ", ".join(statList)
                    qy += f" SELECT {fields} FROM home_t h UNION SELECT * FROM away_t"
                else:
                    qy += f" SELECT * FROM home_t h UNION SELECT * FROM away_t"
            else:
                fields = ",".join(selectFieldsH)
                def makeFieldH(x):
                    if x == "gp":
                        fieldsSummed.add("gp")
                        return f"h.gp+a.gp as gp"
                    elif x == "park":
                        return f"p.park_name as park"
                    elif x == "team":
                        return f"h.team"
                    return f"h.{x}"
                
                qy += " SELECT " + ", ".join(list(map(makeFieldH, selectFieldsH)))
                  
                #first = True
                for st in statList:
                    #if not first:
                    qy += ", "
                    #first = False
                    # join home/away
                    if agg == 'no' or agg == "sum":
                        fieldsSummed.add(st)
                        qy += " h." + st + "+" + "a." + st 
                    elif agg == "avg":
                        fieldsAveraged.add(st)
                        # for averages need to reweight/home away based on gams played
                        qy += makeHomeAwayAvgQuery(st)
                    qy += " as " + st
                
                qy += " FROM home_t h"
                #if agg == "no":
                #    qy += " UNION "
                #else:
                qy += " INNER JOIN "
                qy += " (SELECT "

                def makeFieldA(x):
                    return f"{x}"
                qy += ", ".join(list(map(makeFieldA, selectFieldsA)))
                for st in statList:
                    qy += ", " + st
                qy += " FROM away_t) a"
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
            if isPark or isTeam:
                fields = ", ".join(list(map(makeFieldParkTeam, selectFieldsH)))
                fields += ", " + ", ".join(statList)
                qy += f" SELECT {fields} from home_t h"
            else:
                qy += f" SELECT * from home_t h"
        elif isAway:
            if isPark or isTeam:
                fields = ", ".join(list(map(makeFieldParkTeam, selectFieldsA)))
                fields += ", " + ", ".join(statList)
                qy += f" SELECT {fields} from away_t h"
            else:
                qy += f" SELECT * from away_t h"

        if isPark:
            qy += f" INNER JOIN (SELECT * FROM parks) p ON h.park=p.park_id"
        #if isTeam:
        #    qy += f" INNER JOIN (SELECT * FROM teams) t ON team=t.team_id"
        ordFilt = []
        print("order=", order)
        print("stats=", stats)
        print("selectFieldsH=", selectFieldsH)
        for o in order:
            o1 = o[:-1]
            print("o1=", o1)
            if o1 in selectFieldsH or o1 in stats:
                if o1 in fieldsAveraged:
                    ordstr = makeHomeAwayAvgQuery(o1)
                else:
                    ordstr = "h." + o1
                    if o1 in fieldsSummed:
                        ordstr += "+a." + o1
                if o[-1] == "<":
                    ordstr += " ASC"
                else:
                    ordstr += " DESC"
                ordFilt.append(ordstr)
        if len(ordFilt) > 0:
            qy += " ORDER BY " + ", ".join(ordFilt)
        qy += " LIMIT 101" 

        print("query= ", qy)
        print("prms= ", prmsH + prmsA)
        if len(grp) > 0 and agg == 'no':
            errMsg = "There must be an aggregation (total/average) if any stats grouped"
            print(errMsg)
            resp = make_response(errMsg, 400)
            resp.headers["Access-Control-Allow-Origin"] = "*"
            return resp

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
        #print(r)
        
        # make header for table
        hdr = selectFieldsH
        for st in statList:
            hdr.append(st)

        # rename fields which started with '_' or number
        for i in range(len(hdr)):
            if hdr[i] == "homeoraway":
                hdr[i] = "Home/Away"
            elif hdr[i][0] == "n" and isNumberChar(hdr[i][1]):
                hdr[i] = hdr[i][1:]
            elif hdr[i][0] == "_":
                hdr[i] = "opp" + hdr[i][1:]
            else:
                h = hdr[i][1:]
                hdr[i] = toUpper(hdr[i][0]) + h

        # fix month from number to string value
        if "Month" in hdr or "Team" in hdr:
            monthIdx = -1
            teamIdx = -1
            if "Month" in hdr:
                monthIdx = hdr.index("Month")
            if "Team" in hdr:
                teamIdx = hdr.index("Team")
            if teamIdx >= 0 and not hasattr(app, 'team_name'):
                get_teams()
            i = 0
            for t in r:
                r2 = list(t)
                if monthIdx >= 0:
                    month = calendar.month_name[t[monthIdx]]
                    r2[monthIdx] = month
                if t[teamIdx] in app.team_names:
                    team = app.team_names[t[teamIdx]]
                    r2[teamIdx] = team

                r[i] = tuple(r2)
                i += 1
            #print("r(fixed month)=", r)

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

