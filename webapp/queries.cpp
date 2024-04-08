#include "queries.h"

#include <algorithm>

using std::vector;
using std::string;
using std::unordered_map;
using std::cout;
using std::unordered_set;
using std::to_string;
using std::stringstream;
using std::endl;
using std::find;

const auto MONTH_FIELD = string("CAST(substr(game_date,6,2) AS INTEGER)");
const auto YEAR_FIELD = string("CAST(substr(game_date,0,5) AS INTEGER)");

const unordered_map<string, string> FIELD_NAME_MAP =     
                { {"R", "score"},
                  {"AB", "at_bats"},
                  {"H", "hits"},
                  {"2B", "doubles"},
                  {"3B", "triples"},
                  {"HR", "home_runs"},
                  {"RBI", "rbi"},
                  {"SH", "sac_hit"},
                  {"SF", "sac_fly"},
                  {"HBP", "hit_by_pitch"},
                  {"BB", "walks"},
                  {"IBB", "int_walks"},
                  {"K", "strikeouts"},
                  {"SB", "stolen_bases"},
                  {"CS", "caught_stealing"},
                  {"GIDP", "gidp"},
                  {"CI", "catcher_interference"},
                  {"LOB", "left_on_base"},
                  {"ERI", "indiv_earned_runs"},
                  {"ERT", "team_earned_runs"},
                  {"WP", "wild_pitches"},
                  {"BLK", "balks"},
                  {"PO", "putouts"},
                  {"A", "assists"},
                  {"E", "errors"},
                  {"PB", "passed_balls"},
                  {"DP", "double_plays"},
                  {"TP", "triple_plays"},
                  {"I1", "score_by_inning_1"},
                  {"I2", "score_by_inning_2"},
                  {"I3", "score_by_inning_3"},
                  {"I4", "score_by_inning_4"},
                  {"I5", "score_by_inning_5"},
                  {"I6", "score_by_inning_6"},
                  {"I7", "score_by_inning_7"},
                  {"I8", "score_by_inning_8"},
                  {"I9", "score_by_inning_9"} };


auto QUERY_PARAMS = unordered_map<string, q_params_t>();

unordered_map<string, q_params_t>& initQueryParams() {
    QUERY_PARAMS.clear();
    QUERY_PARAMS["team"] = q_params_t{"team", "team", 1, true};
    QUERY_PARAMS["year"] = q_params_t{YEAR_FIELD + " as year", "year", 0, false};
    QUERY_PARAMS["month"] = q_params_t{MONTH_FIELD + " as month", "month", 0, false};
    QUERY_PARAMS["dow"] =  q_params_t{"game_day_of_week as dow", "dow", 1, false};
    QUERY_PARAMS["league"] = q_params_t{"league", "league", 1, true};
    QUERY_PARAMS["park"] = q_params_t{"park", "park", 1, false};
    /*
               {"inn1", {"score_by_inning_1", "inn1", 0, true},
               {"inn2", {"score_by_inning_2", "inn2", 0, true},
               {"inn3", {"score_by_inning_3", "inn3", 0, true},
               {"inn4", {"score_by_inning_4", "inn4", 0, true},
               {"inn5", {"score_by_inning_5", "inn5", 0, true},
               {"inn6", {"score_by_inning_6", "inn6", 0, true},
               {"inn7", {"score_by_inning_7", "inn7", 0, true},
               {"inn8", {"score_by_inning_8", "inn8", 0, true},
               {"inn9", {"score_by_inning_9", "inn9", 0, true}
               } 
               */
    return QUERY_PARAMS;
}



int field_val_t::valType() { 
    return vType;
}

int field_val_t::asInt() {
    return static_cast<int>(*bytes);
}

char* field_val_t::asCharPtr() {
    return bytes;
}

std::string field_val_t::asStr() {
    return std::string(bytes);
}

void field_val_t::setInt(int v) {
    *bytes = v;
    vType = 0;
}

void field_val_t::setStr(std::string s) {
    int i=0;
    for(auto c : s) { 
        bytes[i++] = c;
        if(i > 126) break;
    }
    // null terminate
    bytes[i] = 0;
    vType = 1;
}



string make_dt_ms_str(int dt_ms) {
    return to_string(dt_ms);
}

bool isNumberChar(char c) {
    return (c >= '0' && c <= '9');
}

char toUpper(char c) {
    if (c >= 'a' && c <= 'z')
        return c + 'A';
    return c;
}

string makeHomeAwayAvgQuery(string st) {
    stringstream hss, ass, ss;
    hss << "h.gp*h." << st << "/(1.0*(h.gp+a.gp))";
    auto h = hss.str();
    ass << "a.gp*a." << st << "/(1.0*(h.gp+a.gp))";
    auto a = ass.str();
    ss << "trunc(100*(" << h << " + " << a << "))/100.0";
    return ss.str();
}


// build SQL query string from fields provided
string buildStatQueryStr(const vector<string>& stats, bool isHome, const string& agg, vector<string>& statList) {
    auto h = string("home");
    auto v = string("visiting");
    auto statQueryStr = string("");
    statList.clear();
    cout << endl << "buildStatQueryStr agg=" << agg;
    for (auto st : stats) {
        /// '_' prefix denotes sum opposing teams stat
        auto f = st;
        auto isAgainst = false;
        if (st[0] == '_') {
            isAgainst = true;
            f = st.substr(1);
        }
        if (FIELD_NAME_MAP.count(f) > 0) {
            auto fName = FIELD_NAME_MAP.at(f);
            auto b = v;
            auto ob = h;
            if (isHome) {
                b = h;
                ob = v;
            }
            if (isAgainst)
                b = ob; // # switch
            string fld;
            if (agg == "avg") {
                fld = ", trunc(100*avg(" + b + "_" + fName + "))/100.00 as ";
            }
            else if(agg == "no") { // # no aggregaton
                fld = ", " + b + "_" + fName + " as ";
            }
            else { // # use sum as default
                fld = ", sum(" + b + "_" + fName + ") as ";
            }
            st = f;
            if (isAgainst)
                st = "_" + f;
            else if (isNumberChar(f[0]))
                st = "n" + f;
            fld += st;

            statQueryStr += fld;
            statList.push_back(st);
        }
    }
            
    return statQueryStr;
}

// make common table expression base
// fieldNames are names that appear in SELECT
string makeCTEBase(string homeOrAway, string fieldQueryStr, const vector<string>& fieldNames,
                   string agg, const vector<string>& grp, vector<string> &selectFields) {
    auto base = string(" ") + homeOrAway + "_t as (SELECT ";
    cout << endl << "makeCTEBase grp=";
    printVec(grp);
    cout << "makeCTEBase fieldNames=";
    printVec(fieldNames);
    auto homeOrVisit = homeOrAway;
    selectFields.clear();
    
    if (homeOrAway == "away")
        homeOrVisit = "visiting";
    for (auto f : fieldNames) {
        selectFields.push_back(f);
        auto qp = QUERY_PARAMS[f];
        if (qp.isTeam)
            base += (homeOrVisit + "_");

        base += qp.firstClause;
        if (qp.isTeam)
            base += " as " + f;
        base += ", ";
    }
    auto nGroup = 0;
    for (auto g : grp) {
        if (g == "homeaway") {
            char ch = toUpper(homeOrAway[0]);
            auto hOrA = ch + homeOrAway.substr(1);
            base += "'" + hOrA + "' as homeoraway, ";
            selectFields.push_back("homeoraway");
            nGroup += 1;
        }
        else if(QUERY_PARAMS.count(g) > 0) {
            selectFields.push_back(g);
            auto qp = QUERY_PARAMS[g];
            if (qp.isTeam)
                base += homeOrVisit + "_";
            base += qp.firstClause;
            if (qp.isTeam)
                base += " as " + g;
            base += ", ";
            nGroup += 1;
        }
    }
    if ((agg != "no") || (nGroup > 0)) {
        base += " COUNT(*) as gp";
        selectFields.push_back("gp");
    }
    else {
        base += " game_date as date, game_num as num, home_team as home, visiting_team as away";
        selectFields.insert(selectFields.end(), {"date", "num", "home", "away"});
    }

    base += fieldQueryStr;
    base += string(" FROM boxscore");
    
    return base;
}

int getQueryParams(unordered_map<string, string> args, 
                    vector<string>& fieldNames, 
                    vector<field_val_t>& fieldValues) {
    for (auto [k, v] : args) {
        cout << endl << "getQueryParams: '" << k << "' '" << v << "'";
        if (QUERY_PARAMS.count(k) > 0) {
            auto qp = QUERY_PARAMS.at(k);
            fieldNames.push_back(k);
            
            auto v = args.at(k);
            field_val_t fv;
            
            //  convert to integer
            if(qp.type == 0)
                fv.setInt(stoi(v));
            else 
                fv.setStr(v);
            fieldValues.push_back(fv);
        }
    }
    return 0;
}

string buildCTEWhereClause(bool isHome, vector<string> fieldNames, vector<string> grp,
                           bool isOldTime) {
    auto first = true;
    auto qy = string("");
    if (!isOldTime) {
        char s[256];
        qy = " WHERE " + YEAR_FIELD + " > 1902 ";
        first = false;
    }

    for (auto f : fieldNames) {
        if (!first) 
            qy += " AND ";
        else
            qy = string(" WHERE ");
        first = false;
        // if "team" stat
        auto qp = QUERY_PARAMS.at(f);
        if (qp.isTeam) {
            if (isHome)
                qy += " home_";
            else
                qy += " visiting_";
        }
        qy += (qp.secondClause + "=? ");
    }

    if (grp.size() > 0) {
        qy += " GROUP BY ";
        first = true;
        for (auto f : fieldNames) {
            auto qp = QUERY_PARAMS.at(f);
            if (!first) 
                qy += ", ";
            first = false;
            qy += qp.secondClause;
        }
            
        for (auto g : grp) {
            if (QUERY_PARAMS.count(g) > 0) {
                auto qp = QUERY_PARAMS.at(g);
                if (!first)
                    qy += ", ";
                first = false;
                qy += qp.secondClause;
            }
        }
    }
    return qy;
}
    
using result_t = vector<vector<string> >;

const auto VALID_AGG = unordered_set<string>{"no", "sum", "avg"};

std::vector<std::string> splitStr(const std::string& input, char delimiter) {
    std::vector<std::string> tokens;
    std::stringstream ss(input);
    std::string token;

    while (std::getline(ss, token, delimiter)) {
        tokens.push_back(token);
    }

    return tokens;
}

std::string joinStr(const std::vector<std::string>& elements, const std::string& delimiter) {
    std::stringstream ss;
    bool isFirst = true;

    for (const auto& element : elements) {
        if (!isFirst) {
            ss << delimiter; // Add delimiter before adding the element (not before the first element)
        }
        ss << element;
        isFirst = false;
    }

    return ss.str(); // Convert stringstream to string and return
}

int buildSQLQuery(unordered_map<string, string> args, string &qy, 
                  vector<field_val_t>& prms, string &errMsg) {
    bool isHome = true;
    bool isAway = true;
    if (args.count("homeaway") > 0) {
        auto homeaway = args.at("homeaway");
        if (homeaway == "home") {
            isHome = true;
            isAway = false;
        }
        else if(homeaway == "away") {
            isHome = false;
            isAway = true;         
        }   
    }
    auto agg = string("sum");
    if (args.count("agg") > 0) {
        if (VALID_AGG.count(args.at("agg")) > 0)
            agg = args.at("agg");
    }

    bool isOldTime = false;    
    auto grp = vector<string>();
    if (args.count("gro") > 0) {
        auto g = args.at("grp");
        grp = splitStr(g, ',');
    }
    cout << endl << "grp=";
    printVec(grp);

    if (args.count("oldtime") > 0) {
        isOldTime = stoi(args.at("premod"));
    }
    
    auto stats_str = string("R,_R");
    if (args.count("stats") > 0) {
        stats_str = args.at("stats");
    }
    auto stats = splitStr(stats_str, ',');
    cout << endl << "stats=";
    printVec(stats);
    
    auto order_str = string("year,team,date");
    if (args.count("order") > 0) {
        order_str = args.at("order");
    }
    auto order = splitStr(order_str, ',');
    cout << endl << "order=";
    printVec(order);
    
    vector<string> fieldNames;
    vector<field_val_t> fieldValues;
    getQueryParams(args, fieldNames, fieldValues);
    
    // in the case where results are not being selected or grouped by team,
    // select for home only
    if((find(fieldNames.begin(), fieldNames.end(), string("team")) == std::end(fieldNames)) 
       && find(grp.begin(), grp.end(), string("team")) == std::end(grp))
        isAway = false;
    prms.clear();
    prms.insert(prms.end(), fieldValues.begin(), fieldValues.end());

    cout << endl <<"fieldNames="; 
    printVec(fieldNames);
    // cout << endl << "fieldValues=";
    // printVec(fieldValues);
    
    vector<string> statListA;
    vector<string> statListH;
    auto statQueryStrH = buildStatQueryStr(stats, true, agg, statListH);
    auto statQueryStrA = buildStatQueryStr(stats, false, agg, statListA);
    cout << endl << "statQueryStrH=" << statQueryStrH;
    cout << endl << "statListH=";
    printVec(statListH);
    cout << endl << "statQueryStrA=" << statQueryStrA;
    cout << endl << "statListA=";
    printVec(statListA);
    // print(f"statList=", statList)
    vector<string> selectFieldsH;
    vector<string> selectFieldsA;
    auto qy_home = makeCTEBase("home", statQueryStrH, fieldNames, agg, grp, selectFieldsH);
    auto qy_away = makeCTEBase("away", statQueryStrA, fieldNames, agg, grp, selectFieldsA);
    cout << endl << "qy_home=" << qy_home; 
    cout << endl << "qy_away" << qy_away; 

    auto whereClauseH = string("");
    auto whereClauseA = string("");

    qy.clear();
    qy += string("WITH");
    if (isHome) {
        whereClauseH = buildCTEWhereClause(true, fieldNames, grp, isOldTime);
        qy += qy_home + whereClauseH + ")";        
    }
    if (isAway) {
        whereClauseA = buildCTEWhereClause(false, fieldNames, grp, isOldTime);
        if(isHome) {
            qy += ", ";
            auto prmsA = prms;
            prms.insert(prms.end(), prmsA.begin(), prmsA.end());            
        }
        qy += qy_away + whereClauseA + ")";        
    }
        
    // prmsH = tuple(fieldValues)prmsA = tuple(fieldValues)

    // if park is part of query, JOIN with park names
    bool isPark = false;
    if(find(selectFieldsH.begin(), selectFieldsH.end(), string("park")) != std::end(selectFieldsH))
        isPark = true;

    // currently don't join team names but keeping here as 
    bool isTeam = false;
    if(find(selectFieldsH.begin(), selectFieldsH.end(), string("team")) != std::end(selectFieldsH))
        isTeam = true;

    auto makeFieldParkTeam = [](string x) -> string {
        if (x == "park")
            return string("p.park_name AS park");
        return string("h.") + x;
    };
        
    cout << endl << "selectFieldsH="; 
    printVec(selectFieldsH);

    // fields which have perfomed h.f + a.f
    // for use in ordering
    auto fieldsSummed = unordered_set<string>();
    auto fieldsAveraged = unordered_set<string>();
    // if home and away selected, must do JOIN (unless no aggregation)
    if (isHome && isAway) {
        if ((agg == string("no")) && ((fieldNames.size() + grp.size()) == 0) 
            || (find(grp.begin(), grp.end(), string("homeaway")) != std::end(grp))) {
            // rewrite fields for join on park
            if (isPark || isTeam) { 
                vector<string> r;
                for(auto f : selectFieldsH) {
                    r.push_back(makeFieldParkTeam(f));
                }
                auto fields = joinStr(r, ", ");
                qy += " SELECT " + fields +"  FROM home_t h UNION SELECT * FROM away_t";
            }
            else
                qy += " SELECT * FROM home_t h UNION SELECT * FROM away_t";
        }
        else {
            auto fields = joinStr(selectFieldsH, ",");
            auto makeFieldH = [&fieldsSummed](string x) -> string {
                if (x == "gp") {
                    fieldsSummed.emplace("gp");
                    return "h.gp+a.gp as gp";
                } 
                else if (x == "park")
                    return "p.park_name as park";
                else if (x == "team")
                    return "h.team";
                return "h." + x;
            };
            
            vector<string> r;
            for(auto f : selectFieldsH) {
                r.push_back(makeFieldH(f));
            }
            qy += " SELECT " + joinStr(r, ", ");
            
            for (auto st : statListH) {
                qy += ", ";
                if (agg == "no" || agg == "sum") {
                    fieldsSummed.emplace(st);
                    qy += " h." + st + "+" + "a." + st ;
                }
                else if (agg == "avg") {
                    fieldsAveraged.emplace(st);
                    // for averages need to reweight/home away based on gams played
                    qy += makeHomeAwayAvgQuery(st);
                }
                qy += " as " + st;
            }
            qy += " FROM home_t h";
            if((fieldNames.size() + grp.size()) == 0) 
                qy += " FULL JOIN ";
            else
                qy += " INNER JOIN ";
            qy += " (SELECT ";

            //def makeFieldA(x):
            //    return f"{x}"
            qy += joinStr(selectFieldsA, ", ");
            for(auto st : statListH)
                qy += ", " + st;
            qy += " FROM away_t) a";
            if((fieldNames.size() + grp.size()) > 0) {
                qy += " ON";
                auto first = true;
                for (auto f : fieldNames) {
                    if (!first)
                        qy += " AND ";
                    first = false;
                    auto qp = QUERY_PARAMS[f];
                    qy += " h." + qp.secondClause + "=a." + qp.secondClause;
                }
                for (auto g : grp) {
                    if (!first)
                        qy += " AND ";
                    first = false;
                    auto qp = QUERY_PARAMS.at(g);
                    qy += " h." + qp.secondClause + "=a." + qp.secondClause;
                }
            }
            
            //qy += " AND h.date=a.date AND h.num=a.num"
            //qy += " AND h.home=a.home AND h.away=a.away"
        }
    }
    else if(isHome) {
        if (isPark || isTeam) {
            vector<string> r;
            for(auto f : selectFieldsH) {
                r.push_back(makeFieldParkTeam(f));
            }
            auto fields = joinStr(r, ", ");
            
            fields += ", " + joinStr(statListH,  ", ");
            qy += " SELECT " + fields + " from home_t h";
        }
        else
            qy += " SELECT * from home_t h";
    }
    else { // away only
        if (isPark || isTeam) {
            vector<string> r;
            for(auto f : selectFieldsA) {
                r.push_back(makeFieldParkTeam(f));
            }
            auto fields = joinStr(r, ", ");
            
            fields += ", " + joinStr(statListA,  ", ");
            qy += " SELECT " + fields + " from away_t h";
        }
        else
            qy += " SELECT * from away_t h";
    }

    // join park names
    if (isPark)
        qy += " INNER JOIN (SELECT * FROM parks) p ON h.park=p.park_id";
    // disabled for now -- fixed after fetch
    //if isTeam:
    //    qy += f" INNER JOIN (SELECT * FROM teams) t ON team=t.team_id"
    vector<string> ordFilt;
    for (auto o : order) {
        auto o1 = o.substr(0, o.size()-2);
        cout << endl << "o1=" << o1;
        
        auto o1_in_sfld = (find(selectFieldsH.begin(), selectFieldsH.end(), o1) != std::end(selectFieldsH));
        auto o1_in_st = (find(stats.begin(), stats.end(), o1) != std::end(stats));
        if (o1_in_sfld || o1_in_st) {
            auto ordstr = string("");
            if (fieldsAveraged.count(o1) > 0) 
                ordstr = makeHomeAwayAvgQuery(o1);
            else {
                ordstr = "h." + o1;
                auto o1_in_fs = (fieldsSummed.count(o1) > 0);
                if (o1_in_fs)
                    ordstr += "+a." + o1;
            }
            auto lastc = o[o.size()-1];
            if (lastc == '<') 
                ordstr += " ASC";
            else
                ordstr += " DESC";
            ordFilt.push_back(ordstr);
        }
    }
    if (ordFilt.size() > 0)
        qy += " ORDER BY " + joinStr(ordFilt, ", ");
    qy += " LIMIT 101"; 

    if (grp.size() > 0 && agg == string("no")) {
        errMsg = "There must be an aggregation (total/average) if any stats grouped";
        return 1;        
    }
    errMsg.clear();
    return 0;
}

string renderHTMLTable(vector<string> headers, query_result_t result, string opts) {
    auto tblAttr = string("");
    auto tbAttr = string("");
    auto trAttr = string("");
    auto tdAttr = string("");
    auto thAttr = string("");
    std::stringstream ss;

    if (opts == "bs") {
        tblAttr = string("class=\"table table-hover table-striped\"");
        tbAttr = string("table-group-divider");
        trAttr = string("class=\"tr\"");
        tdAttr = string("class=\"td\"");
        thAttr = string("scope=\"row\"");
    }

    ss << "<table" << tblAttr << ">";
    ss << "<thead><tr>";
    for (auto hdr : headers) {
        ss << "<th" << thAttr << ">" << hdr << "</th>";
    }
    ss << "</tr></thead><tbody" << tblAttr << ">";
    for (auto r : result) {
        ss << "<tr " << trAttr << ">";
        for (auto d : r) 
            ss << "<td " << tdAttr << ">" <<  d << "</td>";
        ss << "</tr>";
    }
    ss << "</tbody></table>";
    return ss.str();
}


/*
    cout << ("prms= ", prmsH + prmsA)
    
        cout << errMsg;
        print(errMsg)
        resp = make_response(errMsg, 400);
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

    dt_preproc = datetime.now() - t_preproc_start

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
        print(r[0:5])
        
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
        */