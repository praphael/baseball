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
using std::pair;

// for 's' suffix
using namespace std::string_literals;

const auto MONTH_FIELD = "CAST(substr(game_date,6,2) AS INTEGER)"s;
const auto YEAR_FIELD = "CAST(substr(game_date,0,5) AS INTEGER)"s;
// field conditions
const auto TEMP_FIELD = "CAST(substr(cond,0,5) AS INTEGER)"s;
const auto WINDSPEED_FIELD = "CAST(substr(cond,0,5) AS INTEGER)"s;
const auto WINDDIR_FiELD = "substr(cond,0,5)"s;
const auto PRECIP_FIElD = "substr(cond,0,5)"s;
const auto SKY_FIELD = "substr(cond,0,5)"s;
const auto FIELDCOND_FIELD = "substr(cond,0,5)"s;


const auto VALID_AGG = unordered_set<string>{"no", "sum", "avg", "max", "min", "count"};

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
vector<string> QUERY_PARAMS_ORDER = {"year", "team", "_team", "league", "_league", 
                                     "month", "dow", "park_id", "park", "game",
                                     "game_type", "day_night", "temp", "windspeed",
                                     "winddir", "precip", "sky", "fieldcond", "batter",
                                     "pitcher", "sit_inn", "sit_innhalf", "sit_outs",
                                     "sit_bat_tm_sco", "sit_pit_tm_sco", "sit_sco_diff", 
                                     "sit_base_1", "sit_base_2", "sit_base_3", 
                                     "sit_pit_cnt", "sit_bat_res", "sit_bat_res2",
                                     "sit_bat_res3", "sit_bat_base", "sit_bat_base2",
                                     "sit_bat_base3", "sit_hit_loc", "sit_hit_type",
                                     "sit_outs_made", "sit_runs_sco"};

unordered_map<string, q_params_t>& initQueryParams() {
    QUERY_PARAMS.clear();
    QUERY_PARAMS["team"] = q_params_t{"team", valType::STR, true};
    QUERY_PARAMS["_team"] = q_params_t{"team", valType::STR, true};
    QUERY_PARAMS["year"] = q_params_t{YEAR_FIELD,  valType::INT_RANGE, false};
    QUERY_PARAMS["month"] = q_params_t{MONTH_FIELD, valType::INT, false};
    QUERY_PARAMS["dow"] =  q_params_t{"game_day_of_week", valType::STR, false};
    QUERY_PARAMS["league"] = q_params_t{"league", valType::STR, true};
    QUERY_PARAMS["_league"] = q_params_t{"league", valType::STR, true};
    QUERY_PARAMS["park_id"] = q_params_t{"park", valType::STR, false};
    
    // game number (regular or post season series)
    // note to be confunsed with "game_num" which is the double header number
    QUERY_PARAMS["game"] = q_params_t{"game_num", valType::INT, true};
    // R = regular season, W=wildcard, D=division serie, L=league championship S=world series
    QUERY_PARAMS["game_type"] = q_params_t{"game_type", valType::STR, false};
    // D for day, N for neight
    QUERY_PARAMS["day_night"] = q_params_t{"day_night", valType::STR, false};
    // conditions
    QUERY_PARAMS["temp"] = q_params_t{TEMP_FIELD, valType::INT_RANGE, false};
    QUERY_PARAMS["windspeed"] = q_params_t{WINDSPEED_FIELD, valType::INT_RANGE, false};
    QUERY_PARAMS["winddir"] = q_params_t{WINDDIR_FiELD, valType::INT_RANGE, false};
    QUERY_PARAMS["precip"] = q_params_t{PRECIP_FIElD, valType::STR, false};
    QUERY_PARAMS["sky"] = q_params_t{SKY_FIELD, valType::STR, false};
    QUERY_PARAMS["fieldcond"] = q_params_t{FIELDCOND_FIELD, valType::STR, false};

    // numeric ids for players
    QUERY_PARAMS["batter"] = q_params_t{"batter_id", valType::INT, false};
    QUERY_PARAMS["pitcher"] = q_params_t{"pitcher_id", valType::INT, false};
    // 1-25
    QUERY_PARAMS["sit_inn"] = q_params_t{"inning", valType::INT_RANGE, false};
    // B=bottom, T=top
    QUERY_PARAMS["sit_innhalf"] = q_params_t{"inning_half", valType::STR, false};
    // 0-2
    QUERY_PARAMS["sit_outs"] = q_params_t{"outs", valType::INT_RANGE, false};
    QUERY_PARAMS["sit_bat_tm_sco"] = q_params_t{"bat_team_score", valType::INT_RANGE, false};
    QUERY_PARAMS["sit_pit_tm_sco"] = q_params_t{"pitch_team_score", valType::INT_RANGE, false};
    // batter team score - pitcher team score
    QUERY_PARAMS["sit_sco_diff"] = q_params_t{"score_diff", valType::INT_RANGE, false};
    
    // either player ID, 0 for empty, -1 for occupied by any player 
    QUERY_PARAMS["sit_base_1"] = q_params_t{"bases_first", valType::INT, false};
    QUERY_PARAMS["sit_base_2"] = q_params_t{"bases_second", valType::INT, false};
    QUERY_PARAMS["sit_base_3"] = q_params_t{"bases_third", valType::INT, false};

    QUERY_PARAMS["sit_pit_cnt"] = q_params_t{"pitch_cnt", valType::STR, false};
    QUERY_PARAMS["sit_bat_res"] = q_params_t{"bat_result", valType::STR, false};
    QUERY_PARAMS["sit_bat_res2"] = q_params_t{"bat_result2", valType::STR, false};
    QUERY_PARAMS["sit_bat_res3"] = q_params_t{"bat_result3", valType::STR, false};
    QUERY_PARAMS["sit_bat_base"] = q_params_t{"bat_base", valType::STR, false};
    QUERY_PARAMS["sit_bat_base2"] = q_params_t{"bat_base2", valType::STR, false};
    QUERY_PARAMS["sit_bat_base3"] = q_params_t{"bat_base3", valType::STR, false};
    QUERY_PARAMS["sit_hit_loc"] = q_params_t{"hit_loc", valType::STR, false};
    QUERY_PARAMS["sit_hit_type"] = q_params_t{"hit_type", valType::STR, false};
    // 0-3
    QUERY_PARAMS["sit_outs_made"] = q_params_t{"outs_made", valType::INT_RANGE, false};
    // 0-4
    QUERY_PARAMS["sit_runs_sco"] = q_params_t{"runs_scored", valType::INT_RANGE, false};
    
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

// order of select parameters in final select statement
vector<pair<string, bool>> SELECT_PARAMS_ORDER = { {"year", true}, {"date", false}, {"month", true}, 
                                       {"dow", true}, {"park_id", true}, {"num", false},
                                       {"homeaway", true}, {"team", true}, {"league", true}, {"score", false},
                                        {"_team", true}, {"_league", true}, { "_score", false} };


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

// build SQL query string from fields provided
string buildStatQueryStr(const vector<string>& stats, bool isHome, const string& agg, vector<string>& statList) {
    auto h = "home"s;
    auto v = "visiting"s;
    auto statQueryStr = ""s;
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
            if(agg == "no") { // # no aggregaton
                fld = ", " + b + "_" + fName + " AS ";
            }
            else if (agg == "avg") {
                fld = ", ROUND(1000*AVG(" + b + "_" + fName + "))/1000.00 AS ";
            }
            else { // use aggregation name
                fld = ", " + agg + "(" + b + "_" + fName + ") AS ";
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

std::string buildCTEWhereClause(bool isHome, 
                                const vector<string>& fieldNames,
                                const unordered_map<string, field_val_t> fieldValueMap,
                                bool isOldTime,
                                const vector<string>& selectFields,
                                vector<field_val_t>& prms)  // output
{
    auto first = true;
    auto query = ""s;
    if (!isOldTime) {
        query = " WHERE " + YEAR_FIELD + " > 1902 ";
        first = false;
    }

    for (auto f : fieldNames) {
        cout << endl << "buildCTEWhereClause: f=" << f;
        if (!first) 
            query += " AND ";
        else
            query = " WHERE ";
        first = false;
        
        auto qp = QUERY_PARAMS.at(f);
        if (qp.isTeam) {
            bool isOpp = (f[0]== '_');
            if (isHome != isOpp)
                query += " home_";
            else // both are true 
                query += " visiting_";
        }
        if (f == "year") {
            query += (YEAR_FIELD + " BETWEEN ? AND ? ");
        }
        else {
            query += (qp.fieldSelector + "=? ");
        }
        prms.push_back(fieldValueMap.at(f));
    }

    return query;
}

// make common table expression
// fieldNames are names that appear in SELECT
string makeCTE(bool isHome, 
               bool isOldTime,
               const vector<string>& fieldNames,
               const unordered_map<string, field_val_t> fieldValueMap,
               const vector<string>& group,
               const vector<string>& stats, 
               vector<string> &selectFields,   // output
               unordered_set<string> &selectFieldsSet,   // output
               vector<string> &statList,        // output
               vector<field_val_t> &prms)       // output
{
    auto homeOrAway = "home"s;
    if (!isHome)
        homeOrAway = "away"s;

    auto query = " "s + homeOrAway + "_t AS (SELECT "s;
    cout << endl << "makeCTEBase(" << __LINE__ << "): fieldNames=";
    printVec(fieldNames);
    auto homeOrVisit = homeOrAway;
    if (homeOrAway == "away")
        homeOrVisit = "visiting"s;
    
    selectFields.clear();
    selectFieldsSet.clear();
    query += "'"s + homeOrAway + "' AS homeaway, "s;
    selectFields.push_back("homeaway"s);
    selectFieldsSet.emplace("homeaway"s);
    for (auto f : fieldNames) {
        // since this is handled in home/away split
        if(f == "team" || f == "_team" || f == "league" || f == "_league") continue;
        selectFields.push_back(f);
        selectFieldsSet.emplace(f);
        
        auto qp = QUERY_PARAMS[f];
        if (qp.isTeam)
            query += (homeOrVisit + "_");

        query += qp.fieldSelector;
        if (qp.isTeam || f != qp.fieldSelector)
            query += " AS " + f;
        query += ", ";
        
    }
    // need to add fields group fields which were not in select
    for (auto g : group) {
        if(selectFieldsSet.count(g) == 0) {
            // since this is handled in home/away split
            if(g == "team" || g == "_team" || g == "league" || g == "_league") continue;
            selectFields.push_back(g);
            selectFieldsSet.emplace(g);
            
            auto qp = QUERY_PARAMS[g];
            if (qp.isTeam)
                query += (homeOrVisit + "_");

            query += qp.fieldSelector;
            if (qp.isTeam || g != qp.fieldSelector)
                query += " AS " + g;
            query += ", ";
        }
    }

    query += " game_date AS date, game_num AS num";
    selectFields.insert(selectFields.end(), {"date", "num", "team", "league", "score"});
    selectFieldsSet.insert({"date", "num", "team", "league", "score"});
    if(isHome) {
        query += ", home_team AS team, visiting_team as _team";
        query += ", home_league AS league, visiting_league as _league";
        query += ", home_score AS score, visiting_score AS _score";
    } else {
        query += ", visiting_team AS team, home_team as _team";
        query += ", visiting_league as league, home_league AS _league";
        query += ", visiting_score AS score, home_score AS _score";
    }

    // used for counting wins/losess and gropings by team/league
    selectFields.insert(selectFields.end(), {"_team", "_score", "_league"});
    selectFieldsSet.insert( {"_team", "_score", "_league"});    

    statList.clear();
    query += buildStatQueryStr(stats, isHome, "no", statList);
    query += " FROM boxscore"s;
    query += buildCTEWhereClause(isHome, fieldNames, fieldValueMap, isOldTime, selectFields, prms);
    
    return query;
}

int getQueryParams(const json& args, 
                   vector<string>& fieldNames, 
                   unordered_map<string, field_val_t>& fieldValueMap,
                   unordered_set<string>& fieldNamesSet) {
    
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
            fieldValueMap[k] = fv;
            cout << endl << "getQueryParams(" << __LINE__  <<  ") added " << k << "=" << fv.asStr();
        }
    }
    return 0;
}
    
using result_t = vector<vector<string> >;

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

string makeFinalSelect(bool isSplitYear, 
                       const vector<string>& selectFields,
                       const unordered_set<string>& selectFieldsSet,
                       const unordered_map<string, field_val_t>& fieldValueMap,
                       const vector<string>& statList,
                       const vector<string>& group,
                       const unordered_set<string>& groupSet,
                       string agg,
                       unordered_set<string>& selectFieldsSetOut) 
{       
    string query = " SELECT ";
    auto isFirst = true;
    for (auto p : SELECT_PARAMS_ORDER) {
        auto p_name = p.first;   // the parameter name
        auto p_isagg = p.second;  // whether this parameter can be part of aggregation

        cout << endl << "makeFinalSelect: p_name=" << p_name << " p_isagg=" << p_isagg;
        // don't include 'home/away' label unless we are goruping
        //if(p_name == "homeaway" && !groupSet.count("homeaway") > 0)
        //    continue;

        
        if((selectFieldsSet.count(p_name) > 0 && (agg == "no" || p_isagg)) )
        {
            // skip 'homeaway' column if it is not in select or group
            if (p_name == "homeaway" && (groupSet.count(p_name) + fieldValueMap.count(p_name)) == 0)
                continue;
            
            // remove team from aggregations, if not part of the selection or grouping
            if (agg != "no" && (p_name == "team" || p_name == "_team") 
                && (fieldValueMap.count(p_name) + groupSet.count(p_name) == 0))
                continue;
            // exclude league and opposing league if we're not selecting by team
            if (agg != "no" && (p_name == "league") 
                && (fieldValueMap.count(p_name) + groupSet.count(p_name) 
                    + fieldValueMap.count("team") + groupSet.count("team") == 0))
                continue;
            if (agg != "no" && (p_name == "_league") 
                && (fieldValueMap.count(p_name) + groupSet.count(p_name) 
                    + fieldValueMap.count("_team") + groupSet.count("_team") == 0))
                continue;

            if(!isFirst)
                query += ", "s;
            isFirst = false;
            if(p_name == "year" && isSplitYear) {
                query += "'"s + fieldValueMap.at("year").asStr() + "' AS year";
                // do not add to selectFieldsSetOut since it is just extraneous column
                continue;
            }
            selectFieldsSetOut.emplace(p_name);
            if(p_name == "num") {
                query += "REPLACE(h.num, '0', ' ') AS num";
            }
            else {
            query += "h." + p_name;
            if(p_name == "park_id")
                query += ", p.park_name AS park";
            }
        }
    }
    // add on games played/records
    if(agg != "no") {
        query += ", COUNT(*) AS gp";
        query += ", SUM(score > _score) AS won";
        query += ", SUM(_score > score) AS lost";
        query += ", ROUND(1000*SUM(score > _score)/(1.0*COUNT(*)))/1000.00 AS rec";
        selectFieldsSetOut.insert({"gp", "won", "lost", "rec"});
        if(agg == "avg") {
            for (auto s : statList)
                query += ", ROUND(1000*AVG(h." + s + "))/1000.00 AS " + s;
        }
        else {
            for (auto s : statList)
                query += ", " + agg + "(h." + s + ") AS " + s;
        }
    }
    else
        query += ", h." + joinStr(statList, ", h.");

    // in the case where team is not selected or grouped
    // then only join from home table
    if(fieldValueMap.count("team") + groupSet.count("team") == 0)
        query += " FROM home_t h";
    else
        query += " FROM both_t h";

    return query;
}

string makeOrderBy(const vector<string>& order,
                   const unordered_set<string>& selectFieldsSet,
                   const vector<string>& statList)
{
    string order_clause = ""s;
    unordered_set<string> statsSet;
    for(auto s : statList) {
        statsSet.emplace(s);
    }
    vector<string> ordFilt;
    for (auto o : order) {
        auto o1 = o.substr(0, o.size()-1);
        cout << endl << "makeOrderBy: o1=" << o1;
        
        auto o1_in_sfld = selectFieldsSet.count(o1) > 0;
        auto o1_in_st = statsSet.count(o1) > 0;
        if (o1_in_sfld || o1_in_st) {
            auto ordstr = o1;
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

    return order_clause;
}

int buildLastClause(string &lastClause, 
                    const unordered_map<string, field_val_t>& fieldValueMap,
                    const vector<string>& selectFields, 
                    const unordered_set<string>& selectFieldsSet,
                    const vector<string>& statList, 
                    vector<string>& group,
                    string agg,
                    bool isSplitYear, 
                    unordered_set<string>& selectFieldsSetOut)
{
    unordered_set<string> groupSet;
    for(auto g : group) groupSet.emplace(g);

    lastClause = makeFinalSelect(isSplitYear, selectFields, selectFieldsSet,
                                 fieldValueMap, statList, group, groupSet, agg, 
                                 selectFieldsSetOut);

    cout << endl << "buildLastClause: final_select=" << lastClause;

    // join park names
    auto isPark = fieldValueMap.count("park_id") > 0 || groupSet.count("park_id") > 0;
    if (isPark)
        lastClause += " INNER JOIN (SELECT * FROM parks) p ON h.park_id=p.park_id"s;

    if(group.size() > 0) {
        auto itr = std::find(group.begin(), group.end(), "park_id"s);
        // replace "park_id" in group with "park_name"
        if(itr != group.end())
            *itr = "park";
        lastClause += " GROUP BY " + joinStr(group, ", ");
    }

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
    unordered_map<string, field_val_t> fieldValueMap;
    unordered_set<string> fieldNamesSet, groupSet;
    getQueryParams(j_args, fieldNames, fieldValueMap, fieldNamesSet);
    
    cout << endl << "buildSQLQuery(" << __LINE__ << "): fieldValueMap=";
    for(auto [f, v] : fieldValueMap) {
        cout << f << ": " << v.asStr();
    }
    
    // Basic strategy is to split up the query into two temp (CTE) tables home_t and away_t
    // then combine results.  We do this because many queries would not make sense unless we did
    // e.g. home aaway splits, groupings by team
    vector<string> selectFields, statList;
    unordered_set<string> selectFieldsSet;

    prms.clear();
    qy = "WITH"s;
    if(args.isHome) {
        qy += makeCTE(true, args.isOldTime, fieldNames, fieldValueMap, args.grp,
                      args.stats, selectFields, selectFieldsSet, statList, prms);
        qy += "), ";
    } else {
        // need empty set so both_t UNION makes sense
        qy += " home_t as (SELECT 1 WHERE 1=0), "; 
    }
    if(args.isAway) {
        qy += makeCTE(false, args.isOldTime, fieldNames, fieldValueMap, args.grp,
                     args.stats, selectFields, selectFieldsSet, statList, prms);
        qy += "), ";
    } else {
        // need empty set so both_t UNION makes sense
        qy += " away_t as (SELECT 1 WHERE 1=0), ";
    }
    qy += " both_t AS (SELECT * from home_t UNION SELECT * from away_t)";
    cout << endl << "qy(CTE)=" << qy;
    // prmsH = tuple(fieldValues)prmsA = tuple(fieldValues)
    
    cout << endl << "buildSQLQuery: selectFields=";
    printVec(selectFields);
    cout << endl << "buildSQLQuery: prms=";
    for(auto p : prms)
        cout << endl << p.asStr();

    // in the case where years 1) appear in the selection, 
    // 2) there is a GROUP BY but
    // 3) year is not 'grp' 
    // then split year into two fields year_start and year_end
    bool isSplitYear = false;
    if(fieldValueMap.count("year") > 0 && groupSet.count("year") == 0 
       && groupSet.size() > 0)
        isSplitYear = true;
    string lastClause;
    unordered_set<string> selectFieldsSetOut;
    err = buildLastClause(lastClause, fieldValueMap, selectFields,
                          selectFieldsSet, statList, args.grp, 
                          args.agg, isSplitYear, selectFieldsSetOut);
    cout << endl << "lastClause=" << lastClause;
    
    // need to wrap around last select by another select, since the minGP cannot be selected for
    // in the same clause it is defined, and also for ordering to make sense (after aggregation)
    qy += " SELECT * FROM(" + lastClause + ")";
    if(args.agg != "no")
        qy += " WHERE gp > " + to_string(args.minGP);
    qy += makeOrderBy(args.order, selectFieldsSetOut, statList);

    // add some extra to determine if there are more records available
    qy += " LIMIT " + to_string(args.limit+5);

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

int buildPlayerGameSQLQuery(string argstr,
                            string &qy, vector<field_val_t>& prms,
                            string &errMsg, args_t& args) 
{
    json j_args;
    auto err = getArgs(argstr, args, j_args, errMsg);
    if(err) return err;

    return 0;
}

int buildSituationSQLQuery(string argstr,
                           string &qy, vector<field_val_t>& prms,
                           string &errMsg, args_t& args)
{
    json j_args;
    auto err = getArgs(argstr, args, j_args, errMsg);
    if(err) return err;

    return 0;
}