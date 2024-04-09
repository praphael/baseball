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
using std::cerr;

// for 's' suffix
using namespace std::string_literals;

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

vector<string> QUERY_PARAMS_ORDER = {"year", "team", "league", "month", "dow", "park"};
unordered_map<string, q_params_t>& initQueryParams() {
    QUERY_PARAMS.clear();
    QUERY_PARAMS["team"] = q_params_t{"team", "team", valType::STR, true};
    QUERY_PARAMS["year"] = q_params_t{YEAR_FIELD + " as year", "year", valType::INT, false};
    QUERY_PARAMS["month"] = q_params_t{MONTH_FIELD + " as month", "month", valType::INT, false};
    QUERY_PARAMS["dow"] =  q_params_t{"game_day_of_week as dow", "dow", valType::STR, false};
    QUERY_PARAMS["league"] = q_params_t{"league", "league", valType::STR, true};
    QUERY_PARAMS["park"] = q_params_t{"park", "park", valType::STR, false};
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

bool isNumberChar(char c) {
    return (c >= '0' && c <= '9');
}

char toUpper(char c) {
    if (c >= 'a' && c <= 'z')
        return (c-'a') + 'A';
    return c;
}

int field_val_t::valType() { 
    return vType;
}

int field_val_t::asInt() {
    if(vType == valType::INT)
        return v.i;
    else if(vType == valType::STR)
        return std::stoi(v.s);
    return 0;
}

// convert if necessary
std::string field_val_t::asStr() {
    if(vType == valType::STR)
        return string(v.s);
    else if(vType == valType::INT)
        return std::to_string(v.i);
    return "";
}

// this method only makes sense when underlying value is string
// because otherwise we would have to malloc, and it is not obvious ot the caller
const char* field_val_t::asCharPtr() {
    if(vType == valType::STR)
        return v.s;
    return nullptr;
}


void field_val_t::setInt(int val) {
    vType = valType::INT;
    v.i = val;
}

void field_val_t::setStr(std::string val) {
    vType = valType::STR;
    std::strcpy(v.s, val.c_str());
}

string makeHomeAwayAvgQuery(string st) {
    stringstream hss, ass, ss;
    hss << "h.gp*h." << st << "/(1.0*(h.gp+a.gp))";
    auto h = hss.str();
    ass << "a.gp*a." << st << "/(1.0*(h.gp+a.gp))";
    auto a = ass.str();
    ss << "ROUND(100*(" << h << " + " << a << "))/100.0";
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
                fld = ", ROUND(100*AVG(" + b + "_" + fName + "))/100.00 AS ";
            }
            else if(agg == "no") { // # no aggregaton
                fld = ", " + b + "_" + fName + " AS ";
            }
            else { // # use sum as default
                fld = ", SUM(" + b + "_" + fName + ") AS ";
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
    auto base = string(" ") + homeOrAway + "_t AS (SELECT ";
    cout << endl << "makeCTEBase(" << __LINE__ << "): grp=";
    printVec(grp);
    cout << "makeCTEBase(" << __LINE__ << "): fieldNames=";
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
        base += " COUNT(*) as gp,";
        selectFields.push_back("gp");
        auto sc1 = "home_score"s;
        auto sc2 = "visiting_score"s;
        if(homeOrAway == "away") {
            sc1 = sc2;
            sc2 = "home_score";
        }
        base += " SUM(" + sc1 + ">" + sc2 + ") AS won,";
        selectFields.push_back("won");
        base += " SUM(" + sc2 + ">" + sc1 + ") AS lost,";
        selectFields.push_back("lost");
        base += " ROUND(1000*SUM(" + sc1 + ">" + sc2 + ")/(1.0*COUNT(*)))/1000.000 AS rec";
        selectFields.push_back("rec");
    }
    else {
        base += " game_date as date, game_num as num, home_team as home, visiting_team as away";
        selectFields.insert(selectFields.end(), {"date", "num", "home", "away"});
    }

    base += fieldQueryStr;
    base += string(" FROM boxscore");
    
    return base;
}

int getQueryParams(const json& args, 
                   vector<string>& fieldNames, 
                   vector<field_val_t>& fieldValues) {
    
    for (const auto& k : QUERY_PARAMS_ORDER) {
        if (args.contains(k)) {
            auto qp = QUERY_PARAMS.at(k);
            cout << endl << "getQueryParams(" << __LINE__  <<  ") k=" << k << " qp.vType- " << qp.vType;
            fieldNames.push_back(k);
            
            auto v = args[k];
            cout << endl << "getQueryParams(" << __LINE__  <<  ") v= " << v;
            field_val_t fv;
            
            // convert to integer
            if(qp.vType == valType::INT)
                fv.setInt(v.get<int>());
            else if(qp.vType == valType::STR)
                fv.setStr(v.get<string>());
            else {
                cerr << endl << "getQueryParams(" << __LINE__  <<  ") unknown type " << qp.vType;
                return 1;
            }
            cout << endl << "getQueryParams(" << __LINE__  <<  ") fv.setXXX() successful";
            fieldValues.push_back(fv);
            cout << endl << "getQueryParams(" << __LINE__  <<  ") added " << k << "=" << fv.asStr();
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
            } else {
                if (!first)
                    qy += ", ";
                first = false;
                if (g == "homeaway")
                    qy += "homeoraway";
                else
                    qy += g;
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

int buildSQLQuery(string argstr, string &qy, 
                  vector<field_val_t>& prms, string &errMsg, 
                  json& args) {

    args.clear();

    if(argstr.size() > 0) {
        try {
            args = json::parse(argstr);
        } catch (json::parse_error& ex) {
            errMsg = "JSON parse error at byte " + std::to_string(static_cast<int>(ex.byte));
            cerr << errMsg << endl;
            return 1;
        }
    }
    cout << endl << "buildSQLQuery(" << __LINE__ << "): parsed args" << args;
    bool isHome = true;
    bool isAway = true;
    if (args.contains("homeaway")) {
        auto homeaway = args["homeaway"];
        if (homeaway == "home") {
            isHome = true;
            isAway = false;
        }
        else if(homeaway == "away") {
            isHome = false;
            isAway = true;         
        }   
    }
    cout << endl << "buildSQLQuery(" << __LINE__ << "): isHome= " << isHome << " isAway=" << isAway;

    auto agg = string("sum");
    if (args.contains("aggregation")) {
        if (VALID_AGG.count(args["aggregation"]) > 0)
            agg = args["aggregation"];
    }
    cout << endl << "buildSQLQuery(" << __LINE__ << "): agg=" << agg;
    
    auto grp = vector<string>();
    if (args.contains("group")) {
        grp = args["group"];
    }
    cout << endl << "buildSQLQuery(" << __LINE__ << "): grp=";
    printVec(grp);

    bool isOldTime = false;
    if (args.contains("oldtime")) {
        isOldTime = args["oldtime"];
    }
    
    vector<string> stats = {"R, _R"};
    if (args.contains("stats")) {
        stats = args["stats"];
    }
    cout << endl << "buildSQLQuery(" << __LINE__ << "): stats=";
    printVec(stats);
    
    vector<string> order = {"year,team,date"};
    if (args.contains("order")) {
        order = args["order"];
    }
    cout << endl << "buildSQLQuery(" << __LINE__ << "): order=";
    printVec(order);
    
    vector<string> fieldNames;
    vector<field_val_t> fieldValues;
    getQueryParams(args, fieldNames, fieldValues);
    
    cout << endl << "buildSQLQuery(" << __LINE__ << "): fieldNames="; 
    printVec(fieldNames);
    cout << endl << "buildSQLQuery(" << __LINE__ << "): fieldValues=";
    for(auto f : fieldValues) {
        cout << f.asStr();
    }

    // in the case where results are not being selected or grouped by team,
    // select for home only
    if((find(fieldNames.begin(), fieldNames.end(), string("team")) == std::end(fieldNames)) 
       && find(grp.begin(), grp.end(), string("team")) == std::end(grp))
        isAway = false;
    prms.clear();
    prms.insert(prms.end(), fieldValues.begin(), fieldValues.end());
    
    vector<string> statListA;
    vector<string> statListH;
    auto statQueryStrH = buildStatQueryStr(stats, true, agg, statListH);
    auto statQueryStrA = buildStatQueryStr(stats, false, agg, statListA);
    cout << endl << "buildSQLQuery(" << __LINE__ << "): statQueryStrH=" << statQueryStrH;
    cout << endl << "buildSQLQuery(" << __LINE__ << "): statListH=";
    printVec(statListH);
    cout << endl << "buildSQLQuery(" << __LINE__ << "): statQueryStrA=" << statQueryStrA;
    cout << endl << "buildSQLQuery(" << __LINE__ << "): statListA=";
    printVec(statListA);
    // print(f"statList=", statList)
    vector<string> selectFieldsH;
    vector<string> selectFieldsA;
    auto qy_home = makeCTEBase("home", statQueryStrH, fieldNames, agg, grp, selectFieldsH);
    auto qy_away = makeCTEBase("away", statQueryStrA, fieldNames, agg, grp, selectFieldsA);
    cout << endl << "buildSQLQuery(" << __LINE__ << "): qy_home=" << qy_home; 
    cout << endl << "buildSQLQuery(" << __LINE__ << "): qy_away" << qy_away; 

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
        
    cout << endl << "buildSQLQuery: selectFieldsH="; 
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
            if (isPark) { 
                vector<string> r;
                for(auto f : selectFieldsH) {
                    r.push_back(makeFieldParkTeam(f));
                }
                for(auto s : stats) {
                    r.push_back(makeFieldParkTeam(s));
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
                    return "h.gp+a.gp AS gp";
                } 
                if (x == "won") {
                    fieldsSummed.emplace("won");
                    return "h.won+a.won AS won";
                } 
                if (x == "lost") {
                    fieldsSummed.emplace("lost");
                    return "h.lost+a.lost AS lost";
                } 
                else if (x == "park")
                    return "p.park_name AS park";
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
        if (isPark) {
            vector<string> r;
            for(auto f : selectFieldsH) {
                r.push_back(makeFieldParkTeam(f));
            }
            auto fields = joinStr(r, ", ");
            
            fields += ", " + joinStr(statListH,  ", ");
            qy += " SELECT " + fields + " FROM home_t h";
        }
        else
            qy += " SELECT * FROM home_t h";
    }
    else { // away only
        if (isPark) {
            vector<string> r;
            for(auto f : selectFieldsA) {
                r.push_back(makeFieldParkTeam(f));
            }
            auto fields = joinStr(r, ", ");
            
            fields += ", " + joinStr(statListA,  ", ");
            qy += " SELECT " + fields + " FROM away_t h";
        }
        else
            qy += " SELECT * FROM away_t h";
    }

    // join park names
    if (isPark)
        qy += " INNER JOIN (SELECT * FROM parks) p ON h.park=p.park_id";
    // disabled for now -- fixed after fetch
    //if isTeam:
    //    qy += f" INNER JOIN (SELECT * FROM teams) t ON team=t.team_id"
    vector<string> ordFilt;
    for (auto o : order) {
        auto o1 = o.substr(0, o.size()-1);
        cout << endl << "buildSQLQuery: o1=" << o1;
        
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

    ss << "<table " << tblAttr << ">";
    ss << "<thead><tr>";
    for (auto hdr : headers) {
        ss << "<th " << thAttr << ">" << hdr << "</th>";
    }
    ss << "</tr></thead><tbody " << tblAttr << ">";
    if(result.size() == 0) {
        ss << "<tr>(no data)</tr>";
    }
    for (auto r : result) {
        ss << "<tr " << trAttr << ">";
        for (auto d : r) 
            ss << "<td " << tdAttr << ">" <<  d << "</td>";
        ss << "</tr>";
    }
    ss << "</tbody></table>";
    return ss.str();
}