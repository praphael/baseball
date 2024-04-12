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

// Note: Home/Away split not a query parameter because it has special handling
vector<string> QUERY_PARAMS_ORDER = {"year", "team", "league", "month", "dow", "park"};
unordered_map<string, q_params_t>& initQueryParams() {
    QUERY_PARAMS.clear();
    QUERY_PARAMS["team"] = q_params_t{"team", valType::STR, true};
    QUERY_PARAMS["year"] = q_params_t{YEAR_FIELD,  valType::INT_RANGE, false};
    QUERY_PARAMS["month"] = q_params_t{MONTH_FIELD, valType::INT, false};
    QUERY_PARAMS["dow"] =  q_params_t{"game_day_of_week", valType::STR, false};
    QUERY_PARAMS["league"] = q_params_t{"league", valType::STR, true};
    QUERY_PARAMS["park"] = q_params_t{"park", valType::STR, false};
    
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

valType field_val_t::getValType() const { 
    return vType;
}

int field_val_t::asInt() const {
    if(vType == valType::INT)
        return v.i;
    else if(vType == valType::STR)
        return std::stoi(v.s);
    return 0;
}

// convert if necessary
std::string field_val_t::asStr() const {
    if(vType == valType::STR)
        return string(v.s);
    else if(vType == valType::INT)
        return std::to_string(v.i);
    else if(vType == valType::INT_RANGE) {
        if (v.rng.low != v.rng.high)
            return std::to_string(v.rng.low) + " to " + std::to_string(v.rng.high);
        else 
            return std::to_string(v.rng.low);
    }
    return "";
}

// this method only makes sense when underlying value is string
// because otherwise we would have to malloc, and it is not obvious ot the caller
const char* field_val_t::asCharPtr() const {
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

range_t field_val_t::asIntRange() const {
    return v.rng;
}

void field_val_t::setIntRange(int low, int high) {
    v.rng.low = low;
    v.rng.high = high;
    vType = valType::INT_RANGE;
}

string makeHomeAwayAvgQuery(string st) {
    stringstream hss, ass, ss;
    hss << "h.gp*h." << st << "/(1.0*(h.gp+a.gp))";
    auto h = hss.str();
    ass << "a.gp*a." << st << "/(1.0*(h.gp+a.gp))";
    auto a = ass.str();
    ss << "ROUND(1000*(" << h << " + " << a << "))/1000.0";
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
                fld = ", ROUND(1000*AVG(" + b + "_" + fName + "))/1000.00 AS ";
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
                   string agg, const vector<string>& grp, vector<string> &selectFields,
                   vector<int> &fieldsNotInSelect) {
    auto base = string(" ") + homeOrAway + "_t AS (SELECT ";
    cout << endl << "makeCTEBase(" << __LINE__ << "): grp=";
    printVec(grp);
    cout << "makeCTEBase(" << __LINE__ << "): fieldNames=";
    printVec(fieldNames);
    auto homeOrVisit = homeOrAway;
    selectFields.clear();
    
    if (homeOrAway == "away")
        homeOrVisit = "visiting";
    unordered_set<string> fieldNamesSet;
    int i=0;
    for (auto f : fieldNames) {
        fieldNamesSet.emplace(f);
        // if we are grouping by, do not select for this field unless it is in the group
        if(grp.size() == 0 || std::find(grp.begin(), grp.end(), f) != std::end(grp)) {
            selectFields.push_back(f);

            auto qp = QUERY_PARAMS[f];
            if (qp.isTeam)
                base += (homeOrVisit + "_");

            base += qp.fieldSelector;
            if (qp.isTeam || f != qp.fieldSelector)
                base += " AS " + f;
            base += ", ";
        } 
        else fieldsNotInSelect.push_back(i);
        i++;
    }
    auto nGroup = 0;
    // all in group must also
    for (auto g : grp) {
        // skip fields already in field names
        if(fieldNamesSet.count(g) > 0) continue;
        if (g == "homeaway") {
            char ch = toUpper(homeOrAway[0]);
            auto hOrA = ch + homeOrAway.substr(1);
            base += "'" + hOrA + "' AS homeoraway, ";
            selectFields.push_back("homeoraway");
            nGroup += 1;
        }
        else if(QUERY_PARAMS.count(g) > 0) {
            selectFields.push_back(g);
            auto qp = QUERY_PARAMS[g];
            if (qp.isTeam)
                base += homeOrVisit + "_";
            base += qp.fieldSelector;
            if (qp.isTeam || g != qp.fieldSelector)
                base += " AS " + g;
            
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
            else if(qp.vType == valType::INT_RANGE)
                fv.setIntRange(v["low"].get<int>(), v["high"].get<int>());
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

std::string buildCTEWhereClause(bool isHome, const vector<string>& fieldNames,
                           const vector<string>& grp, bool isOldTime,
                           const vector<string>& selectFields, int minGP,
                           const vector<int>& fieldsNotInSelect)
{
    auto first = true;
    auto qy = string("");
    if (!isOldTime) {
        qy = " WHERE " + YEAR_FIELD + " > 1902 ";
        first = false;
    }

    for (auto f : fieldNames) {
        if (!first) 
            qy += " AND ";
        else
            qy = " WHERE ";
        first = false;
        // if "team" stat
        auto qp = QUERY_PARAMS.at(f);
        if (qp.isTeam) {
            if (isHome)
                qy += " home_";
            else
                qy += " visiting_";
        }
        if (f == "year") {
            qy += (YEAR_FIELD + " BETWEEN ? AND ? ");
        }
        else {
            qy += (qp.fieldSelector + "=? ");
        }
    }

    if (grp.size() > 0) {
        qy += " GROUP BY ";
        first = true;
        auto groupBy = unordered_set<string>();
        // place all fields which are not aggregates in the "GROUP BY" clause
        // SQLITE3does not enforce this (PostgresSQL does), but it makes sense
        // fields which are not also in the "grp" do have a meaning if home/away
        // is both.
        // perform aggregate operation (sum/avg/etc.) after join
        /*
        for (auto f : fieldNames) {
            auto qp = QUERY_PARAMS.at(f);
            if (!first) 
                qy += ", ";
            first = false;
            qy += f;
            groupBy.emplace(f);
        } */
            
        for (auto g : grp) {
            if(groupBy.count(g) > 0) continue;
            if (QUERY_PARAMS.count(g) > 0) {
                auto qp = QUERY_PARAMS.at(g);
                if (!first)
                    qy += ", ";
                first = false;
                qy += g;
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

    if (minGP > 0 && (std::find(selectFields.begin(), selectFields.end(), "gp")
                      != std::end(selectFields))) {
        auto minGP_s = to_string(minGP);
        qy += " HAVING gp > " + minGP_s;
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

string makeFieldParkTeam(string x, string hOrA, bool isSplitYear)  {
    if (x == "park" && hOrA == "h.") 
        return string("p.park_name AS park");
    if (isSplitYear && x == "year")
        return string("min(" + hOrA + "year) AS year_begin, max(" + hOrA + "year) AS year_end");
    return string(hOrA) + x;
}

string makeFields (const vector<string>& selectFields, 
                   const vector<string>& fieldNames, 
                   const vector<field_val_t>& fieldValues, 
                   const vector<int>& fieldsNotInSelect,
                   const vector<string>& statList, 
                   string hOrA, bool isSplitYear) {
    vector<string> r;
    int i = 0, fnis = 0;
    
    for(auto f : selectFields) {
        // align the fields which were not included in the select statement
        // with their original relative position
        if(fnis < fieldsNotInSelect.size() && i == fieldsNotInSelect[fnis]) {
            auto fnisIdx = fieldsNotInSelect[fnis];
            r.push_back(makeFieldParkTeam("'" + fieldValues[fnisIdx].asStr() 
                                            + "' AS " + fieldNames[fnisIdx], "", isSplitYear));
            fnis++;                                          
        }
        r.push_back(makeFieldParkTeam(f, hOrA, isSplitYear));
        i++;
    }
    for(auto s : statList) {
        r.push_back(makeFieldParkTeam(s, hOrA, false));
    }
    return joinStr(r, ", ");
}

int makeHomeSelect(string &home_qy, 
                   bool isSplitYear, 
                   const vector<string>& fieldNames,
                   const vector<string>& selectFields,
                   const vector<int>& fieldsNotInSelect,
                   const vector<field_val_t>& fieldValues, 
                   const vector<string>& statList,
                   const vector<string>& grp,
                   string agg, 
                   bool isAway, 
                   unordered_set<string>& fieldsSummed,
                   unordered_set<string>& fieldsAveraged) 
{
    if (!isAway) {
        auto fields = makeFields(selectFields, fieldNames, fieldValues, fieldsNotInSelect, 
                                 statList, "h.", isSplitYear);
        home_qy = " SELECT " + fields + " FROM home_t h";
    }
    else {

        // no grouping or 'homeaway' is also in group
        if (agg == "no"s || std::find(selectFields.begin(), selectFields.end(), "homeoraway") != selectFields.end()) {
            // rewrite fields 
            auto fields = makeFields(selectFields, fieldNames, fieldValues, fieldsNotInSelect, 
                                     statList, "h.", isSplitYear);
            home_qy = " SELECT " + fields + " FROM home_t h";
        }
        // there is an aggregation, so we must also adjsut stats for home/away split
        else {
            auto makeFieldH = [&fieldsSummed, &fieldsAveraged, isSplitYear](string x) -> string {
                if (x == "gp") {
                    fieldsSummed.emplace("gp");
                    return "h.gp+a.gp AS gp";
                } 
                else if (x == "won") {
                    fieldsSummed.emplace("won");
                    return "h.won+a.won AS won";
                } 
                else if (x == "lost") {
                    fieldsSummed.emplace("lost");
                    return "h.lost+a.lost AS lost";
                } 
                else if (x == "rec") {
                    fieldsAveraged.emplace("rec");
                    return "ROUND(1000*h.rec+1000*a.rec)/2000 AS rec";
                } 
                else if (x == "park")
                    return "p.park_name AS park";
                // TODO, join tto team name for this year
                else if (x == "team")  
                    return "h.team";
                else if (x == "year" && isSplitYear)
                    return "min(h.year) as year_begin, max(h.year) as year_end";
                return "h." + x;
            };
            
            vector<string> r;
            int i = 0, fnis = 0;
            for(auto f : selectFields) {
                // align the fields which were not included in the select statement
                // with their original relative position
                if(fnis < fieldsNotInSelect.size() && i == fieldsNotInSelect[fnis]) {
                    auto fnisIdx = fieldsNotInSelect[fnis];
                    r.push_back("'" + fieldValues[fnisIdx].asStr() + "'" + " AS " 
                                + fieldNames[fnisIdx]);
                    fnis++;
                }
                r.push_back(makeFieldH(f));
                i++;
            }
            home_qy = " SELECT " + joinStr(r, ", ");
            
            for (auto st : statList) {
                home_qy += ", ";
                if (agg == "no" || agg == "sum") {
                    fieldsSummed.emplace(st);
                    home_qy += " h." + st + "+" + "a." + st ;
                }
                else if (agg == "avg") {
                    fieldsAveraged.emplace(st);
                    // for averages need to reweight/home away based on gams played
                    home_qy += makeHomeAwayAvgQuery(st);
                }
                home_qy += " AS " + st;
            }
            home_qy += " FROM home_t h";
        }
    }
    return 0;
}

int makeAwaySelect(string &away_qy,
                   bool isSplitYear, 
                   const vector<string>& fieldNames,
                   const vector<string>& selectFields,
                   const vector<int>& fieldsNotInSelect,
                   const vector<field_val_t>& fieldValues,
                   const vector<string>& statList,
                   const vector<string>& grp, 
                   string agg,
                   bool isHome,
                   bool isUnion)
{
    if (!isHome) {
        // pass "h" here so we get correct park behavior
        auto fields = makeFields(selectFields, fieldNames, fieldValues, fieldsNotInSelect,
                                 statList, "h.", isSplitYear);
        away_qy = " SELECT " + fields + " FROM away_t h";
    } 
    else {
        auto fields = makeFields(selectFields, fieldNames, fieldValues, fieldsNotInSelect, 
                                 statList, "", isSplitYear);
        if (isUnion)
            away_qy = " SELECT " + fields + " FROM away_t a";
        else
            away_qy = " (SELECT " + fields + " FROM away_t) a";
    }

    return 0;
}

int makeJoinOnClause(string &join_clause, string& on_clause,
                     bool isHome, bool isAway, 
                     const vector<string>& fieldNames,
                     const vector<string>& grp, 
                     string agg) 
{
    // join on fields which are not also in group
    auto joinSet = unordered_set<string>();
    // add all fieldNames
    for(auto g : grp) { 
        joinSet.emplace(g); 
    }

    join_clause = "";
    if(isHome && isAway) {
        join_clause = " INNER JOIN ";
        if (agg == "no" || joinSet.count("homeaway") > 0)
            join_clause = " UNION ";
        else if((fieldNames.size() + grp.size()) == 0) // should be only one row
            join_clause = " FULL JOIN ";
    }

    
    on_clause = "";
    if(join_clause == " INNER JOIN ") {        
        if(joinSet.size() > 0) { 
            on_clause = " ON";    
            auto first = true;
            for (auto j : joinSet) {
                if (!first)
                    on_clause += " AND ";
                first = false;
                auto qp = QUERY_PARAMS[j];
                on_clause += " h." + j + "=a." + j;
            }
        } 
        else {
            join_clause = "UNION";
        }
    }

    return 0;
}

int makeOrderBy(string &order_clause, const vector<string>& order,
                const vector<string>& selectFields,
                const vector<string>& stats,
                unordered_set<string> fieldsSummed,
                unordered_set<string> fieldsAveraged) 
{
    order_clause = "";
    vector<string> ordFilt;
    for (auto o : order) {
        auto o1 = o.substr(0, o.size()-1);
        cout << endl << "buildSQLQuery: o1=" << o1;
        
        auto o1_in_sfld = (find(selectFields.begin(), selectFields.end(), o1) != std::end(selectFields));
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
        order_clause = " ORDER BY " + joinStr(ordFilt, ", ");

    return 0;
}



int buildFinalSelect(string &final_select, 
                     const vector<string>& fieldNames, 
                     const vector<string>& selectFields, 
                     const vector<int>& fieldsNotInSelect,
                     const vector<field_val_t>& fieldValues, 
                     const vector<string>& statList, 
                     const vector<string>& grp,
                     const vector<string>& order,
                     string agg,
                     bool isHome,
                     bool isAway) 
{    // in the case where years 1) appear in the selection, 
    // 2) there is a GROUP BY but
    // 3) year is not 'grp' 
    // then split year into two fields year_start and year_end
    bool isSplitYear = false;
    if(find(selectFields.begin(), selectFields.end(), string("year")) == std::end(selectFields) && 
       grp.size() > 0 && find(grp.begin(), grp.end(), string("year")) != std::end(grp)) {
        isSplitYear = true;
    }

    unordered_set<string> fieldsSummed, fieldsAveraged;
    string home_qy = "", away_qy = "";
    int err = 0;
    if (isHome) {
        err = makeHomeSelect(home_qy, isSplitYear, fieldNames, selectFields, fieldsNotInSelect,
                             fieldValues, statList, grp, agg, isAway, fieldsSummed, fieldsAveraged);
        if(err) {
            cerr << endl << "buildFinalSelect(" <<  __LINE__  << "): error in makeHomeSelect err=" << err;
        }
    }

    /* make JOIN ... ON claues*/
    string join_clause = "", on_clause="";
    err = makeJoinOnClause(join_clause, on_clause, isHome, isAway, 
                           fieldNames, grp, agg);
    if (isAway) {
        err = makeAwaySelect(away_qy, isSplitYear, fieldNames, selectFields, fieldsNotInSelect, 
                             fieldValues, statList, grp, agg, isHome,
                             (join_clause == " UNION "s));
        if(err) {
            cerr << endl << "buildFinalSelect(" <<  __LINE__  << "): error in makeAwaySelect err= " << err;
        }
    }

    string order_by;
    err = makeOrderBy(order_by, order, selectFields, statList, fieldsSummed, fieldsAveraged);

    // join park names
    auto park_clause = ""s;
    auto isPark = std::find(fieldNames.begin(), fieldNames.end(), "park"s) != std::end(fieldNames)
                  || std::find(grp.begin(), grp.end(), "park"s) != std::end(grp);
    if (isPark)
        park_clause = " INNER JOIN (SELECT * FROM parks) p ON park=p.park_id"s;

    cout << endl << "isPark= " << isPark;
    final_select = home_qy + join_clause + away_qy + on_clause + park_clause + order_by;
    
    return 0;
    // disabled for now -- fixed after fetch
    //if isTeam:
    //    qy += f" INNER JOIN (SELECT * FROM teams) t ON team=t.team_id"
}

int getArgs(string argstr, args_t& args, json& j_args, string& errMsg) {
    j_args.clear();

    if(argstr.size() > 0) {
        try {
            j_args = json::parse(argstr);
        } catch (json::parse_error& ex) {
            errMsg = "getArgs: JSON parse error at byte " + std::to_string(static_cast<int>(ex.byte));
            cerr << errMsg << endl;
            return 1;
        }
    }
    cout << endl << "getArgs(" << __LINE__ << "): parsed args" << j_args;
    args.isHome = true;
    args.isAway = true;
    if (j_args.contains("homeaway")) {
        auto homeaway = j_args["homeaway"];
        if (homeaway == "home") {
            args.isHome = true;
            args.isAway = false;
        }
        else if(homeaway == "away") {
            args.isHome = false;
            args.isAway = true;         
        }   
    }
    cout << endl << "getArgs(" << __LINE__ << "): isHome= " << args.isHome;
    cout << " isAway=" << args.isAway;

    args.agg = string("sum");
    if (j_args.contains("aggregation")) {
        if (VALID_AGG.count(j_args["aggregation"]) > 0)
            args.agg = j_args["aggregation"];
    }
    cout << endl << "getArgs(" << __LINE__ << "): agg=" << args.agg;
    
    args.grp = vector<string>();
    if (j_args.contains("group")) {
        args.grp = j_args["group"];
    }
    cout << endl << "getArgs(" << __LINE__ << "): grp=";
    printVec(args.grp);

    if (args.grp.size() > 0 && args.agg == "no") {
        errMsg = "There must be an aggregation (total/average) if any stats grouped";
        cerr << endl << errMsg;
        return 1;
    }

    if (args.grp.size() == 0 && args.agg != "no") {
        errMsg = "At least one field must be grouped if there is am aggregation (total/average)";
        cerr << endl << errMsg;
        return 1;
    }

    args.isOldTime = false;
    if (j_args.contains("oldtime")) {
        args.isOldTime = j_args["oldtime"].get<bool>();
    }
    
    args.stats = {"R, _R"};
    if (j_args.contains("stats")) {
        args.stats = j_args["stats"];
    }
    cout << endl << "getArgs(" << __LINE__ << "): stats=";
    printVec(args.stats);
    
    args.order = {"year,team,date"};
    if (j_args.contains("order")) {
        args.order = j_args["order"];
    }
    args.minGP = 0;
    if (j_args.contains("minGP")) {
        args.minGP = j_args["minGP"].get<int>();
    }
    cout << endl << "getArgs(" << __LINE__ << "): minGP=" << args.minGP;

    args.limit = 100;
    if (j_args.contains("limit")) {
        args.limit = j_args["limit"].get<int>();
    }

    args.ret = "html";
    if (j_args.contains("ret")) {
        args.ret = j_args["ret"];
    }

    args.retopts = "bs";
    if (j_args.contains("retopts")) {
        args.retopts = j_args["retopts"];
    }

    return 0;
}

int buildSQLQuery(string argstr, string &qy, 
                  vector<field_val_t>& prms, string &errMsg, 
                  args_t& args) 
{
    json j_args;
    auto err = getArgs(argstr, args, j_args, errMsg);
    if(err) return err;

    vector<string> fieldNames;
    vector<field_val_t> fieldValues;
    getQueryParams(j_args, fieldNames, fieldValues);
    
    cout << endl << "buildSQLQuery(" << __LINE__ << "): fieldNames="; 
    printVec(fieldNames);
    cout << endl << "buildSQLQuery(" << __LINE__ << "): fieldValues=";
    for(auto f : fieldValues) {
        cout << f.asStr();
    }

    // in the case where results are not being selected or grouped by team,
    // select for home only
    if((find(fieldNames.begin(), fieldNames.end(), string("team")) == std::end(fieldNames)) 
       && find(args.grp.begin(), args.grp.end(), string("team")) == std::end(args.grp) && 
          find(args.grp.begin(), args.grp.end(), string("homeoraway")) == std::end(args.grp))
        args.isAway = false;
    prms.clear();
    prms.insert(prms.end(), fieldValues.begin(), fieldValues.end());
    

    // Basic strategy is to split up the query into two temp (CTE) tables home_t and away_t
    // then combine results.  We do this because many queries would not make sense unless we did
    // e.g. home aaway splits, groupings by team
    vector<string> statListA;
    vector<string> statListH;
    auto statQueryStrH = buildStatQueryStr(args.stats, true, args.agg, statListH);
    auto statQueryStrA = buildStatQueryStr(args.stats, false, args.agg, statListA);
    cout << endl << "buildSQLQuery(" << __LINE__ << "): statQueryStrH=" << statQueryStrH;
    cout << endl << "buildSQLQuery(" << __LINE__ << "): statListH=";
    printVec(statListH);
    cout << endl << "buildSQLQuery(" << __LINE__ << "): statQueryStrA=" << statQueryStrA;
    cout << endl << "buildSQLQuery(" << __LINE__ << "): statListA=";
    printVec(statListA);
    // print(f"statList=", statList)
    vector<string> selectFieldsH, selectFieldsA;
    vector<int> fieldsNotInSelectH, fieldsNotInSelectA;
    auto qy_home = makeCTEBase("home", statQueryStrH, fieldNames, args.agg, args.grp, 
                                selectFieldsH, fieldsNotInSelectH);
    auto qy_away = makeCTEBase("away", statQueryStrA, fieldNames, args.agg, args.grp,
                                selectFieldsA, fieldsNotInSelectA);
    cout << endl << "buildSQLQuery(" << __LINE__ << "): qy_home=" << qy_home; 
    cout << endl << "buildSQLQuery(" << __LINE__ << "): qy_away" << qy_away; 

    auto whereClauseH = string("");
    auto whereClauseA = string("");

    qy.clear();
    qy += string("WITH");
    if (args.isHome) {
        whereClauseH = buildCTEWhereClause(true, fieldNames, args.grp, args.isOldTime, 
                                           selectFieldsH, args.minGP, fieldsNotInSelectH);
        qy += qy_home + whereClauseH + ")";        
    }
    if (args.isAway) {
        if(args.isHome) {
            qy += ", ";
            auto prmsA = prms;
            prms.insert(prms.end(), prmsA.begin(), prmsA.end());            
        }
        whereClauseA = buildCTEWhereClause(false, fieldNames, args.grp, args.isOldTime,
                                           selectFieldsA, args.minGP, fieldsNotInSelectA);
        cout << endl << "qy (before away)=" << qy;
        qy += qy_away + whereClauseA + ")";        
        cout << endl << "qy (after away)=" << qy;
    }
    
    cout << endl << "qy=" << qy;
    // prmsH = tuple(fieldValues)prmsA = tuple(fieldValues)
    
    cout << endl << "buildSQLQuery: selectFieldsH="; 
    printVec(selectFieldsH);


    string final_select;
    err = buildFinalSelect(final_select, fieldNames, selectFieldsH, fieldsNotInSelectH,
                        fieldValues, statListH, args.grp, args.order, args.agg, 
                        args.isHome, args.isAway);
    
    qy += final_select;
    // add some extra to determine if there are more records available
    string limit_clause = " LIMIT " + to_string(args.limit+5);
    qy += limit_clause;

    return err;
}

string renderHTMLTable(vector<string> headers, query_result_t result,
                       string opts, int limit) {
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
    auto rn = 0;
    for (auto r : result) {
        ss << "<tr " << trAttr << ">";
        for (auto d : r) 
            ss << "<td " << tdAttr << ">" <<  d << "</td>";
        ss << "</tr>";
        rn += 1;
        if(rn == limit) break;
    }
    ss << "</tbody></table>";
    if(result.size() > rn)
        ss << "<span>(reached limit) more records available</span>";
    return ss.str();
}