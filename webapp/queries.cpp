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

//const auto MONTH_FIELD = "CAST(substr(game_date,6,2) AS INTEGER)"s;
const auto MONTH_FIELD = "month"s;
//const auto YEAR_FIELD = "CAST(substr(game_date,0,5) AS INTEGER)"s;
const auto YEAR_FIELD = "year"s;
const auto DAY_FIELD = "CAST(substr(game_date,9,2) AS INTEGER)"s;
// field conditions
const auto DAYNIGHT_FIELD = "daynight"s;
const auto TEMP_FIELD = "temp"s;
const auto WINDSPEED_FIELD = "windspeed"s;
const auto WINDDIR_FiELD = "winddir"s;
const auto PRECIP_FIElD = "precip";
const auto SKY_FIELD = "sky";
const auto FIELDCOND_FIELD = "field_cond";

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
                  {"I9", "score_by_inning_9"},
                  {"I10", "score_by_inning_10"},
                  {"I11", "score_by_inning_11"},
                  {"I12", "score_by_inning_12"},
                  {"I13", "score_by_inning_13"},
                  {"I14", "score_by_inning_14"},
                  {"I15", "score_by_inning_15"} };



vector<string> QUERY_TYPES = {"All", "gamelog", "playergame", "situation"};

auto QUERY_PARAMS = unordered_map<string, q_params_t>();

// Note: Home/Away split not a query parameter because it has special handling
vector<string> QUERY_PARAMS_ORDER = {"year", "month", "dow", "date", "day", "season", "round", "team", "_team", 
                                     "league", "_league", "game", "_game",
                                     "park_id", "daynight", "temp", "windspeed",
                                     "winddir", "precip", "sky", "field_cond", "starttime",
                                     "attendance", "duration", "protest", "forfeit", 
                                     "batter", "pitcher", "batter_team", "pitcher_team",
                                     "fielder", "sit_inn", "sit_innhalf", "sit_outs",
                                     "sit_bat_tm_sco", "sit_pit_tm_sco", "sit_sco_diff", 
                                     "sit_bases", "sit_base_1", "sit_base_2", "sit_base_3", 
                                     "sit_bat_cnt", "sit_play_res", "sit_play_base",
                                     "sit_play_res2", "sit_play_base2", "sit_play_res3",
                                     "sit_play_base3", "sit_hit_loc", "sit_hit_type",
                                     "sit_outs_made", "sit_runs_sco"};

// const vector<string> SIT_QUERY_PARAMS = {"batter", "pitcher", "batter_team", "pitcher_team",
//                                      "sit_inn", "sit_innhalf", "sit_outs",
//                                      "sit_bat_tm_sco", "sit_pit_tm_sco", 
//                                      "sit_base_1", "sit_base_2", "sit_base_3", 
//                                      "sit_pit_cnt", "sit_play_res", "sit_play_base",
//                                      "sit_play_res2", "sit_play_base2", "sit_play_res3",
//                                      "sit_play_base3", "sit_hit_loc", "sit_hit_type",
//                                      "sit_outs_made", "sit_runs_sco", 
//                                      "play_result2", "play_base2",
//                                      "play_result3", "play_base3",
//                                      "ass1", "ass2", "ass3", "ass4", "ass5", "ass6", 
//                                      "po1", "po2", "po3", "err1", "err2", "err3",
//                                      "r1m1", "r1m1prm", "r1m2", "r1m2prm", "r1m1", "r1m1prm", "r1m3", "r1m3prm",
//                                      "r2m1", "r2m1prm", "r2m2", "r2m2prm", "r2m1", "r2m1prm", "r2m3", "r2m3prm",
//                                      "r3m1", "r3m1prm", "r3m2", "r3m2prm", "r3m1", "r3m1prm", "r2m3", "r2m3prm",
//                                      "br0_dst", "br0_out", "br1_dst", "br1_out",
//                                      "br2_dst", "br2_out", "br3_dst", "br3_out",
//                                      "br0_mod1", "br0_mod1_prm", "br0_mod2", "br0_mod2_prm",
//                                      "br0_mod3", "br0_mod3_prm", 
//                                      "br1_mod1", "br1_mod1_prm", "br1_mod2", "br1_mod2_prm",
//                                      "br1_mod3", "br1_mod3_prm", 
//                                      "br2_mod1", "br2_mod1_prm", "br2_mod2", "br2_mod2_prm",
//                                      "br2_mod3", "br2_mod3_prm", 
//                                      "br3_mod1", "br3_mod1_prm", "br3_mod2", "br3_mod2_prm",
//                                      "br3_mod3", "br3_mod3_prm" };
    

unordered_map<string, q_params_t>& initQueryParams() {
    QUERY_PARAMS.clear();
    QUERY_PARAMS["team"] = q_params_t{"team", valType::STR, true, {queryType::ALL}};
    QUERY_PARAMS["_team"] = q_params_t{"team", valType::STR, true, {queryType::ALL}};
    QUERY_PARAMS["year"] = q_params_t{YEAR_FIELD,  valType::INT_RANGE, false, {queryType::ALL}};
    QUERY_PARAMS["month"] = q_params_t{MONTH_FIELD, valType::INT, false, {queryType::ALL}};
    QUERY_PARAMS["dow"] =  q_params_t{"dow", valType::STR, false, {queryType::ALL}};
    QUERY_PARAMS["league"] = q_params_t{"league", valType::STR, true, {queryType::GAMELOG, queryType::PLAYERGAME}};
    QUERY_PARAMS["_league"] = q_params_t{"league", valType::STR, true, {queryType::GAMELOG, queryType::PLAYERGAME}};
    QUERY_PARAMS["park_id"] = q_params_t{"park", valType::STR, false, {queryType::ALL}};
    
    // game number (regular or post season series)
    QUERY_PARAMS["game"] = q_params_t{"game_num", valType::INT_RANGE, true, {queryType::ALL}};
    QUERY_PARAMS["_game"] = q_params_t{"game_num", valType::INT_RANGE, true, {queryType::ALL}};
    // "Reg" "Post" "Pre" "Other"
    QUERY_PARAMS["season"] = q_params_t{"season", valType::STR, false, {queryType::ALL}};
    // "", "Wildcard", "Division", "League", "World Series", "Playoff tiebreak"
    QUERY_PARAMS["round"] = q_params_t{"post_series", valType::STR, false, {queryType::ALL}};
    
    // 'day' or 'night'
    QUERY_PARAMS["daynight"] = q_params_t{"daynight", valType::STR, false, {queryType::ALL}};
    // conditions
    QUERY_PARAMS["temp"] = q_params_t{TEMP_FIELD, valType::INT_RANGE, false, {queryType::ALL}};
    QUERY_PARAMS["windspeed"] = q_params_t{WINDSPEED_FIELD, valType::INT_RANGE, false, {queryType::ALL}};
    QUERY_PARAMS["winddir"] = q_params_t{WINDDIR_FiELD, valType::STR, false, {queryType::ALL}};
    QUERY_PARAMS["precip"] = q_params_t{PRECIP_FIElD, valType::STR, false, {queryType::ALL}};
    QUERY_PARAMS["sky"] = q_params_t{SKY_FIELD, valType::STR, false, {queryType::ALL}};
    QUERY_PARAMS["field_cond"] = q_params_t{FIELDCOND_FIELD, valType::STR, false, {queryType::ALL}};
    QUERY_PARAMS["start_time"] = q_params_t{"start_time", valType::INT_RANGE, false, {queryType::ALL}};
    QUERY_PARAMS["attendance"] = q_params_t{"attendance", valType::INT_RANGE, false, {queryType::ALL}};
    QUERY_PARAMS["duration"] = q_params_t{"game_duration_min", valType::INT_RANGE, false, {queryType::ALL}};
    
    // protest/forfeit
    QUERY_PARAMS["protest"] = q_params_t{"protest", valType::STR, false, {queryType::ALL}};
    QUERY_PARAMS["forfeit"] = q_params_t{"forfeit", valType::STR, false, {queryType::ALL}};
    
    // numeric ids for players, either game stats or situation
    QUERY_PARAMS["batter"] = q_params_t{"batter_num_id", valType::INT, false, {queryType::PLAYERGAME, queryType::SITUATION}};
    QUERY_PARAMS["pitcher"] = q_params_t{"pitcher_num_id", valType::INT, false, {queryType::PLAYERGAME, queryType::SITUATION}};
    QUERY_PARAMS["fielder"] = q_params_t{"fielder_num_id", valType::INT, false, {queryType::PLAYERGAME, queryType::SITUATION}};
    QUERY_PARAMS["batter_team"] = q_params_t{"batter_team", valType::STR, false, {queryType::PLAYERGAME, queryType::SITUATION}};
    QUERY_PARAMS["pitcher_team"] = q_params_t{"pitcher_team", valType::STR, false, {queryType::PLAYERGAME, queryType::SITUATION}};
    
    // 'Left' or 'Right'
    QUERY_PARAMS["batter_side"] = q_params_t{"batter_side", valType::STR, false, {queryType::PLAYERGAME, queryType::SITUATION}};
    QUERY_PARAMS["pitcher_side"] = q_params_t{"pitcher_side", valType::STR, false, {queryType::PLAYERGAME, queryType::SITUATION}};
    // 1-25
    QUERY_PARAMS["sit_inn"] = q_params_t{"inning", valType::INT_RANGE, false, {queryType::SITUATION}};
    // B=bottom, T=top
    QUERY_PARAMS["sit_innhalf"] = q_params_t{"inning_half", valType::STR, false, {queryType::SITUATION}};
    // 0-2
    QUERY_PARAMS["sit_outs"] = q_params_t{"outs", valType::INT_RANGE, false, {queryType::SITUATION}};
    QUERY_PARAMS["sit_bat_tm_sco"] = q_params_t{"bat_team_score", valType::INT_RANGE, false, {queryType::SITUATION}};;
    QUERY_PARAMS["sit_pit_tm_sco"] = q_params_t{"pitch_team_score", valType::INT_RANGE, false, {queryType::SITUATION}};
    // batter team score - pitcher team score
    QUERY_PARAMS["sit_sco_diff"] = q_params_t{"(bat_team_score - pitch_team_score)", valType::INT_RANGE, false, {queryType::SITUATION}};
    QUERY_PARAMS["sit_bat_cnt"] = q_params_t{"bat_pitch_cnt", valType::STR, false, {queryType::SITUATION}};
    
    // string which describes a base situation
    // "empty"
    // "runners" = at least one on any base
    // "forceplay" = runner on first (don't ccare about other bases)
    // "risp" = at least one on second/third (don't care about first)
    // "loaded"        
    // "first", "second", "third" = exactly one runner on given base
    // "firrst+second", "first+third", "second+third"- exactly two runners on given bases
    QUERY_PARAMS["sit_bases"] = q_params_t{"bases", valType::STR, false, {queryType::SITUATION}};
    // either player ID, 0 for empty, -1 for occupied by any player 
    QUERY_PARAMS["sit_base_1"] = q_params_t{"first", valType::INT, false, {queryType::SITUATION}};
    QUERY_PARAMS["sit_base_2"] = q_params_t{"second", valType::INT, false, {queryType::SITUATION}};
    QUERY_PARAMS["sit_base_3"] = q_params_t{"third", valType::INT, false, {queryType::SITUATION}};

    QUERY_PARAMS["sit_play_res"] = q_params_t{"result", valType::STR, false, {queryType::SITUATION}};
    QUERY_PARAMS["sit_play_res2"] = q_params_t{"result2", valType::STR, false, {queryType::SITUATION}};
    QUERY_PARAMS["sit_play_res3"] = q_params_t{"result3", valType::STR, false, {queryType::SITUATION}};
    QUERY_PARAMS["sit_play_base"] = q_params_t{"base1", valType::STR, false, {queryType::SITUATION}};
    QUERY_PARAMS["sit_play_base2"] = q_params_t{"base2", valType::STR, false, {queryType::SITUATION}};
    QUERY_PARAMS["sit_play_base3"] = q_params_t{"base3", valType::STR, false, {queryType::SITUATION}};
    QUERY_PARAMS["sit_hit_loc"] = q_params_t{"hit_loc", valType::STR, false, {queryType::SITUATION}};
    QUERY_PARAMS["sit_hit_type"] = q_params_t{"hit_type", valType::STR, false, {queryType::SITUATION}};
    // 0-3
    QUERY_PARAMS["sit_outs_made"] = q_params_t{"outs_made", valType::INT_RANGE, false, {queryType::SITUATION}};
    // 0-4
    QUERY_PARAMS["sit_runs_sco"] = q_params_t{"runs_scored", valType::INT_RANGE, false, {queryType::SITUATION}};
    
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
// and whether they can be a part of aggregation (e.g, appear in GROUP BY)
vector<pair<string, bool>> SELECT_PARAMS_ORDER = { 
    {"year", true}, {"date", false}, {"month", true}, 
    {"day", "false"}, {"dow", true}, 
    {"num", false}, {"homeaway", true},
    {"pos", false}, {"seq", false},
    {"park", true}, 
    {"daynight", true}, {"temp", false}, {"windspeed", false},
    {"winddir", true}, {"precip", true}, {"sky", true}, 
    {"field_cond", true}, {"start_time", false},
    {"attendance", false}, {"duration", false},
    {"protest", true}, {"forfeit", true},
    {"game", true}, 
    {"league", true}, {"team", true}, {"score", false},
    { "_score", false}, {"_team", true}, {"_league", true},
    {"_game", true}, {"season", true}, {"round", true},
    {"batter", true},  {"batter_team", true},
    {"pitcher", true}, {"pitcher_team", true},
    {"fielder", true}, {"sit_inn", true},
    {"sit_innhalf", true}, {"sit_outs", true},
    {"sit_bat_tm_sco", true}, {"sit_pit_tm_sco", true}, 
    {"sit_sco_diff", true}, {"sit_bases", false}, 
    {"sit_base_1", false}, {"sit_base_2", false},
    {"sit_base_3", false}, {"sit_bat_cnt", true},
    {"sit_play_res", true}, {"sit_play_base", true},
    {"sit_play_res2", true}, {"sit_play_base2", true},
    {"sit_play_res3", true}, {"sit_play_base3", true},
    {"sit_hit_loc", true}, {"sit_hit_type", true},
    {"sit_outs_made", true}, {"sit_runs_sco", true} };

vector<pair<string, bool>> COND_PARAMS_ORDER = { 
    {"park", true}, 
    {"daynight", true}, {"temp", false}, {"windspeed", false},
    {"winddir", true}, {"precip", true}, {"sky", true}, 
    {"field_cond", true}, {"start_time", false},
    {"attendance", false}, {"duration", false},
    {"protest", true}, {"forfeit", true} };

vector<string> SIT_PARAMS_ORDER = {
    "batter", "batter_team", "batter_side", "batter_pos", "batter_seq", 
    "pitcher", "pitcher_team", "pitcher_side", "pitcher_seq", 
    "sit_inn", "sit_innhalf", "sit_outs", "sit_bat_tm_sco", "sit_pit_tm_sco", "sit_sco_diff", 
    "sit_bat_cnt", "sit_base_1", "sit_base_2", "sit_base_3",
    "out_play_res", "out_play_res2", "out_play_res3", "out_play_base", "out_play_base2", "out_play_base3",
    "out_hit_loc", "out_hit_type", "out_outs_made", "out_runs_sco",
    "ass1", "ass2", "ass3", "ass4", "ass5", "ass6",
    "po1", "po2", "po3", "err1", "err2", "err3", 
    "r1m1", "r1m1prm", "r1m2", "r1m2prm", "r1m3", "r1m3prm", 
    "br0_dst", "br0_out", "br1_dst", "br1_out", "br2_dst", "br2_out", "br3_dst", "br3_out", 
    "br0_mod1", "br0_mod1_prm", "br0_mod2", "br0_mod2_prm", "br0_mod3", "br0_mod3_prm",  
    "br1_mod1", "br1_mod1_prm", "br1_mod2", "br1_mod2_prm", "br1_mod3","br1_mod3_prm",
    "br2_mod1", "br2_mod1_prm", "br2_mod2", "br2_mod2_prm", "br2_mod3", "br2_mod3_prm", 
    "br3_mod1", "br3_mod1_prm", "br3_mod2", "br3_mod2_prm", "br3_mod3", "br3_mod3_prm" };

// composite stats
unordered_map<string, string> COMP_STATS;

void initCompStats() {
    COMP_STATS["BA"] = "SUM(H)/SUM(AB)"s;
    COMP_STATS["OBP"] = "(SUM(H) + SUM(BB) + SUM(IBB) + SUM(HBP))/(SUM(AB) + SUM(BB) + SUM(IBB) + SUM(HBP))"s;
    COMP_STATS["SLG"] = "(SUM(H) + 2*SUM(n2B) + 3*SUM(n3B) + 4*SUM(HR))/(SUM(AB)"s;
    COMP_STATS["OPS"] = "(SUM(H) + 2*SUM(n2B) + 3*SUM(n3B) + 4*SUM(HR))/(SUM(AB) + (SUM(H) + SUM(BB) + SUM(IBB) + SUM(HBP))/(SUM(AB) + SUM(BB) + SUM(IBB) + SUM(HBP))"s;
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

// build SQL query string from fields provided
string buildStatQueryStr(const vector<string>& stats, bool isHome, const string& agg, vector<string>& statList) {
    auto h = "home"s;
    auto v = "away"s;
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
                query += " away_";
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
               bool addCond,
               bool addParkInfo,
               const string agg,
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
    cout << endl << "makeCTE(" << __LINE__ << "): fieldNames=";
    printVec(fieldNames);
    
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
            query += (homeOrAway + "_");

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
                query += (homeOrAway + "_");

            query += qp.fieldSelector;
            if (qp.isTeam || g != qp.fieldSelector)
                query += " AS " + g;
            query += ", ";
        }
    }

    query += "game_id"s;
    selectFields.insert(selectFields.end(), {"team", "score", "_team", "_score"});
    selectFieldsSet.insert({"team", "score", "_team", "_score"});
    if (agg == "no") {
        query += ", year, month, "s + DAY_FIELD + " AS day, dow, dh_num AS num";
        selectFields.insert(selectFields.end(), {"year", "month", "day", "dow", "num", "game", "league", "_game", "_league"});
        selectFieldsSet.insert({"year", "month", "day", "dow", "num", "game", "league", "_game", "_league"});
    }
    
    if(isHome) {
        query += ", home_team AS team, away_team as _team";
        query += ", home_score AS score, away_score AS _score";
        if (agg == "no") {
            query += ", CAST(home_game_num AS integer) AS game, CAST(away_game_num AS integer) AS _game";
            query += ", home_league AS league, away_league as _league";
        }
    } else {
        query += ", away_team AS team, home_team as _team";
        query += ", away_score AS score, home_score AS _score";
        if (agg == "no") {
            query += ", CAST(away_game_num AS integer) AS game, CAST(home_game_num AS integer) AS _game";
            query += ", away_league as league, home_league AS _league";
        }
    }
       
    statList.clear();
    query += buildStatQueryStr(stats, isHome, "no", statList);
    if (addCond) {
        //selectFields.insert(selectFields.end(), { "park", "daynight", "start_time", "precip", "sky", "temp", "windspeed", "winddir", "field_cond", "attendance", "duration"});
        //selectFieldsSet.insert({ "park", "daynight", "start_time", "precip", "sky", "temp", "windspeed", "winddir", "field_cond", "attendance", "duration"});
        query += ", daynight, start_time, precip, temp, sky, windspeed, winddir, field_cond";
    }
    if (addParkInfo) {
         query += ", park, attendance, game_duration_min AS duration, win_pitcher AS win, loss_pitcher AS loss, save_pitcher AS save, gw_rbi, complete, forfeit, protest";
    }
    query += " FROM gamelog_view"s;
    query += buildCTEWhereClause(isHome, fieldNames, fieldValueMap, isOldTime, selectFields, prms);
    
    return query;
}

int getQueryParams(const json& args, 
                   vector<string>& fieldNames, 
                   unordered_map<string, field_val_t>& fieldValueMap,
                   unordered_set<string>& fieldNamesSet,
                   queryType qType,
                   string& errMsg) {
    
    for (const auto& k : QUERY_PARAMS_ORDER) {
        if (args.contains(k)) {
            auto qp = QUERY_PARAMS.at(k);
            cout << endl << "getQueryParams(" << __LINE__  <<  ") k=" << k << " qp.vType- " << qp.vType;
            fieldNames.push_back(k);
            if (!(qp.queryTypes.count(queryType::ALL) > 0) &&
                !(qp.queryTypes.count(qType) > 0)) {
                    errMsg = "Parameter '" + k + "' not allowed in query type '" + QUERY_TYPES[qType] + "'";
                    return 1;
            }
            
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
                       bool addCond,
                       bool addParkInfo, 
                       unordered_set<string>& selectFieldsSetOut) 
{       
    string query = " SELECT ";
    auto isFirst = true;
    const auto SKIP_COLS = unordered_set<string>({"homeaway", "team", "_team", "_league", "league"});
    for (auto p : SELECT_PARAMS_ORDER) {
        auto p_name = p.first;   // the parameter name
        auto p_isagg = p.second;  // whether this parameter can be part of aggregation

        // cout << endl << "makeFinalSelect: p_name=" << p_name << " p_isagg=" << p_isagg;
        // don't include 'home/away' label unless we are goruping
        //if(p_name == "homeaway" && !groupSet.count("homeaway") > 0)
        //    continue;

        
        if((selectFieldsSet.count(p_name) > 0 && (agg == "no" || p_isagg)) )
        {
            // skip 'homeaway' column if it is not in select or group
            if (agg != "no" && SKIP_COLS.count(p_name) > 0) {
                  if (groupSet.count(p_name) + fieldValueMap.count(p_name) == 0) 
                     continue;
                 // fieldValueMap.count("team") + groupSet.count("team") == 0)

            }
            
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
                query += "REPLACE(num, '0', ' ') AS num";
            }
            else {
                query += p_name;
                //query += "h." + p_name;
            // if(p_name == "park_id")
            //     query += ", p.park_name AS park";
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
                query += ", ROUND(1000*AVG(" + s + "))/1000.00 AS " + s;
        }
        else {
            for (auto s : statList)
                query += ", " + agg + "(" + s + ") AS " + s;
        }
    }
    else
        query += ", " + joinStr(statList, ", ");

    if (addCond) {
        query += ", daynight, start_time, precip, sky, temp, windspeed, winddir, field_cond";
        //selectFieldsSet.insert({ "park", "daynight", "start_time", "precip", "sky", "temp", "windspeed", "winddir", "field_cond", "attendance", "duration"});
        selectFieldsSetOut.insert({"daynight", "start_time", "precip", "sky", "temp", "windspeed", "winddir", "field_cond"});
    }

    if (addParkInfo) {
        query += ", park, attendance, duration, win, loss, save, gw_rbi, complete, forfeit, protest";
        selectFieldsSetOut.insert({"park", "attendance", "duration", "win", "loss", "save", "winddir", "gw_rbi", "complete", "forfeit", "protest"});
    }
        //selectFieldsSet.insert({ "park", "daynight", "start_time", "precip", "sky", "temp", "windspeed", "winddir", "field_cond", "attendance", "duration"});
    // in the case where team is not selected or grouped
    // then only join from home table
    if(fieldValueMap.count("team") + groupSet.count("team") == 0)
        query += " FROM home_t";
    else
        query += " FROM both_t";

    return query;
}

string makeOrderBy(const vector<string>& order,
                   const unordered_set<string>& selectFieldsSet,
                   const vector<string>& statList,
                   const string agg)
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
    if (agg == "no") {
        ordFilt.push_back("year");
        ordFilt.push_back("month");
        ordFilt.push_back("day");
        ordFilt.push_back("num");
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
                    bool addCond, 
                    bool addParkInfo,
                    bool isSplitYear, 
                    unordered_set<string>& selectFieldsSetOut)
{
    unordered_set<string> groupSet;
    for(auto g : group) groupSet.emplace(g);

    lastClause = makeFinalSelect(isSplitYear, selectFields, selectFieldsSet,
                                 fieldValueMap, statList, group, groupSet, agg,
                                 addCond, addParkInfo, selectFieldsSetOut);

    cout << endl << "buildLastClause: final_select=" << lastClause;

    // join park names
    /*
    auto isPark = fieldValueMap.count("park_id") > 0 || groupSet.count("park_id") > 0;
    if (isPark)
        lastClause += " INNER JOIN (SELECT * FROM parks) p ON h.park_id=p.park_id"s;
    */

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

int getArgs(string argstr, 
            args_t& args,
            json& j_args, 
            string& errMsg) {
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

    /* if (args.grp.size() == 0 && args.agg != "no") {
        errMsg = "At least one field must be grouped if there is am aggregation (total/average)";
        cerr << endl << errMsg;
        return 1;
    } */

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
    
    // type of statistics for player/game
    args.pgQryType = playerGameQueryType::BATTING;
    if (j_args.contains("pgqy_t")) {
        auto qT = j_args["pgqy_t"].get<string>();
        if (qT == "bat")
            args.pgQryType = playerGameQueryType::BATTING;
        else if (qT == "pit")
            args.pgQryType = playerGameQueryType::PITCHING;
        else if (qT == "fld")
            args.pgQryType = playerGameQueryType::FIELDING;
        else {
            errMsg = "bad value for pgqy_t" + qT;
            cerr << endl << "getArgs(" << __LINE__ << ") " << errMsg;
            return 1; 
        }

    }
    
    args.order = {"year,team,date"};
    if (j_args.contains("order")) {
        args.order = j_args["order"];
    }
    args.minGP = 0;
    if (j_args.contains("minGP")) {
        args.minGP = j_args["minGP"].get<int>();
    } 
    cout << endl << "getArgs(" << __LINE__ << "): minGP=" << args.minGP;

    args.minPlays = 0;
    if (j_args.contains("minPlays")) {
        args.minGP = j_args["minPlays"].get<int>();
    }

    args.excludeBaseRun = false;
    if (j_args.contains("excludeBaseRun")) {
        args.excludeBaseRun = j_args["excludeBaseRun"].get<bool>();
    }
    args.addCond = false;
    if (j_args.contains("addCond")) {
        args.addCond = j_args["addCond"].get<bool>();
    }

    args.addParkInfo = false;
    if (j_args.contains("addParkInfo")) {
        args.addParkInfo = j_args["addParkInfo"].get<bool>();
    }

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
    errMsg.clear();
    qy.clear();

    json j_args;
    auto err = getArgs(argstr, args, j_args, errMsg);
    if(err) return err;

    vector<string> fieldNames;
    unordered_map<string, field_val_t> fieldValueMap;
    unordered_set<string> fieldNamesSet, groupSet;
    err = getQueryParams(j_args, fieldNames, fieldValueMap, fieldNamesSet, queryType::GAMELOG, errMsg);
    if(err) return err;
    
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
    // add field conditions
    if(args.isHome) {
        qy += makeCTE(true, args.isOldTime, args.addCond, args.addParkInfo, args.agg, fieldNames, 
                     fieldValueMap, args.grp, args.stats, selectFields,
                     selectFieldsSet, statList, prms);
        qy += "), ";
    } else {
        // need empty set so both_t UNION makes sense
        qy += " home_t as (SELECT 1 WHERE 1=0), "; 
    }
    if(args.isAway) {
        qy += makeCTE(false, args.isOldTime, args.addCond, args.addParkInfo, args.agg, fieldNames,
                      fieldValueMap, args.grp, args.stats, selectFields,
                      selectFieldsSet, statList, prms);
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
                          selectFieldsSet, statList, args.grp, args.agg, 
                          args.addCond, args.addParkInfo, isSplitYear, selectFieldsSetOut);
    cout << endl << "lastClause=" << lastClause;
    
    // need to wrap around last select by another select, since the minGP cannot be selected for
    // in the same clause it is defined, and also for ordering to make sense (after aggregation)
    qy += " SELECT * FROM(" + lastClause + ")";
    if(args.agg != "no")
        qy += " WHERE gp > " + to_string(args.minGP);
    qy += makeOrderBy(args.order, selectFieldsSetOut, statList, args.agg);

    // add some extra to determine if there are more records available
    qy += " LIMIT " + to_string(args.limit+5);

    return err;
}

string renderHTMLTable(vector<string> headers, query_result_t result,
                       string opts, int limit) {
    auto tblAttr = ""s;
    auto tbAttr = ""s;
    auto trAttr = ""s;
    auto tdAttr = ""s;
    auto thAttr = ""s;
    std::stringstream ss;

    if (opts == "bs") {
        tblAttr = "class=\"table table-hover table-striped\""s;
        tbAttr = "table-group-divider"s;
        trAttr = "class=\"tr\""s;
        tdAttr = "class=\"td text-nowrap\""s;
        thAttr = "scope=\"row text-nowrap\""s;
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

// make common table expression
// fieldNames are names that appear in SELECT
string makeCTEPG(playerGameQueryType pgQryT, 
               bool isHome, 
               bool isOldTime,
               bool addCond,
               bool addParkInfo,
               const string agg,
               const vector<string>& fieldNames,
               const unordered_map<string, field_val_t> fieldValueMap,
               const vector<string>& group,
               const vector<string>& stats, 
               vector<string> &selectFields,   // output
               unordered_set<string> &selectFieldsSet,   // output
               vector<string> &statList,        // output
               vector<field_val_t> &prms)       // output
{
    auto tbl = "player_game_batting_view"s;
    if (pgQryT == playerGameQueryType::PITCHING)
        tbl = "player_game_pitching_view";
    else if (pgQryT == playerGameQueryType::FIELDING)
        tbl = "player_game_fielding_view";

    auto homeOrAway = "home"s;
    if (!isHome)
        homeOrAway = "away"s;

    auto query = " "s + homeOrAway + "_t AS (SELECT "s;
    cout << endl << "makeCTE(" << __LINE__ << "): fieldNames=";
    printVec(fieldNames);
    
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
        if (f == "batter") {
            query += "batter_name AS batter, ";
            continue;
        } 
        else if (f == "pitcher") {
            query += "pitcher_name AS pitcher, ";
            continue;
        }
        else if (f == "fielder") {
            query += "fielder_name AS fielder, ";
            continue;
        }
        
        auto qp = QUERY_PARAMS[f];
        if (qp.isTeam)
            query += (homeOrAway + "_");

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
                query += (homeOrAway + "_");

            query += qp.fieldSelector;
            if (qp.isTeam || g != qp.fieldSelector)
                query += " AS " + g;
            query += ", ";
        }
    }

    query += "game_id"s;
    if (agg == "no") {
        query += ", year, month, "s + DAY_FIELD + " AS day, dow, dh_num AS num";
        selectFields.insert(selectFields.end(), {"year", "month", "day", "dow", "num", "team", "_team"});
        selectFieldsSet.insert({"year", "month", "day", "dow", "num", "team", "_team"});
        if(isHome) {
           query += ", home_team AS team, away_team as _team";
        } else {
            query += ", away_team AS team, home_team as _team";
        }
        query += ", pos";
        selectFields.insert(selectFields.end(), {"pos"});
        selectFieldsSet.insert({"pos"});
        if (pgQryT != playerGameQueryType::PITCHING) {
            query += ", seq";
            selectFields.insert(selectFields.end(), {"seq"});
            selectFieldsSet.insert({"seq"});
        }
    }

    statList.clear();
    for(auto st : stats) {
        if (st[0] >= '0' && st[0] <= '9')
            st = "n" + st;
        statList.push_back(st);
        query += ", " + st;
    }
   // query += buildStatQueryStr(stats, isHome, "no", statList);
    if (addCond) {
        query += ", daynight, start_time, precip, sky, temp, windspeed, winddir, field_cond";
        selectFields.insert(selectFields.end(), {"daynight", "start_time", "precip", "sky", "temp", "windspeed", "winddir", "field_cond"});
        selectFieldsSet.insert({"daynight", "start_time", "precip", "sky", "temp", "windspeed", "winddir", "field_cond"});
    }

    if (addParkInfo) {
        query += ", park, attendance, duration, win, loss, save, gw_rbi, complete, forfeit, protest";
        selectFields.insert(selectFields.end(), {"park", "attendance", "duration", "win", "loss", "save", "winddir", "gw_rbi", "complete", "forfeit", "protest"});
        selectFieldsSet.insert({"park", "attendance", "duration", "win", "loss", "save", "winddir", "gw_rbi", "complete", "forfeit", "protest"});
    }
    
    query += " FROM "s + tbl;
    query += buildCTEWhereClause(isHome, fieldNames, fieldValueMap, isOldTime, selectFields, prms);
    if(isHome)
        query += " AND team=home_team";
    else 
        query += " AND team=away_team";
    return query;
}

string makeFinalSelectPG(bool isSplitYear, 
                       const vector<string>& selectFields,
                       const unordered_set<string>& selectFieldsSet,
                       const unordered_map<string, field_val_t>& fieldValueMap,
                       const vector<string>& statList,
                       const vector<string>& group,
                       const unordered_set<string>& groupSet,
                       string agg,
                       bool addCond, 
                       bool addParkInfo,
                       unordered_set<string>& selectFieldsSetOut) 
{       
    string query = " SELECT ";
    auto isFirst = true;
    const auto SKIP_COLS = unordered_set<string>({"homeaway", "team", "_team", "_league", "league"});
    for (auto p : SELECT_PARAMS_ORDER) {
        auto p_name = p.first;   // the parameter name
        auto p_isagg = p.second;  // whether this parameter can be part of aggregation

        // cout << endl << "makeFinalSelect: p_name=" << p_name << " p_isagg=" << p_isagg;
        // don't include 'home/away' label unless we are goruping
        //if(p_name == "homeaway" && !groupSet.count("homeaway") > 0)
        //    continue;

        
        if((selectFieldsSet.count(p_name) > 0 && (agg == "no" || p_isagg)) )
        {
            // skip 'homeaway' column if it is not in select or group
            if (agg != "no" && SKIP_COLS.count(p_name) > 0) {
                  if (groupSet.count(p_name) + fieldValueMap.count(p_name) == 0) 
                     continue;
                 // fieldValueMap.count("team") + groupSet.count("team") == 0)

            }
            
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
                query += "REPLACE(num, '0', ' ') AS num";
            }
            else {
                query += p_name;
                //query += "h." + p_name;
            // if(p_name == "park_id")
            //     query += ", p.park_name AS park";
            }
        }
    }
    // add on games played/records
    if(agg != "no") {
        query += ", COUNT(*) AS gp";
        selectFieldsSetOut.insert({"gp"});
        if(agg == "avg") {
            for (auto s : statList)
                query += ", ROUND(1000*AVG(" + s + "))/1000.00 AS " + s;
        }
        else {
            for (auto s : statList)
                query += ", " + agg + "(" + s + ") AS " + s;
        }
    }
    else
        query += ", " + joinStr(statList, ", ");

    if (addCond) {
        query += ", daynight, start_time, precip, sky, temp, windspeed, winddir, field_cond";
        selectFieldsSetOut.insert({"daynight", "start_time", "precip", "sky", "temp", "windspeed", "winddir", "field_cond"});
    }

    if (addParkInfo) {
        query += ", park, attendance, duration, win, loss, save, gw_rbi, complete, forfeit, protest";
        selectFieldsSetOut.insert({"park", "attendance", "duration", "win", "loss", "save", "winddir", "gw_rbi", "complete", "forfeit", "protest"});
    }
        //selectFieldsSet.insert({ "park", "daynight", "start_time", "precip", "sky", "temp", "windspeed", "winddir", "field_cond", "attendance", "duration"});
    // in the case where team is not selected or grouped
    // then only join from home table
    if(fieldValueMap.count("team") + groupSet.count("team") == 0)
        query += " FROM home_t";
    else
        query += " FROM both_t";

    return query;
}


int buildLastClausePG(string &lastClause, 
                    const unordered_map<string, field_val_t>& fieldValueMap,
                    const vector<string>& selectFields, 
                    const unordered_set<string>& selectFieldsSet,
                    const vector<string>& statList, 
                    vector<string>& group,
                    string agg,
                    bool addCond, 
                    bool addParkInfo, 
                    bool isSplitYear, 
                    unordered_set<string>& selectFieldsSetOut)
{
    unordered_set<string> groupSet;
    for(auto g : group) groupSet.emplace(g);

    lastClause = makeFinalSelectPG(isSplitYear, selectFields, selectFieldsSet,
                                 fieldValueMap, statList, group, groupSet, agg,
                                 addCond, addParkInfo, selectFieldsSetOut);

    cout << endl << "buildLastClause: final_select=" << lastClause;

    // join park names
    /*
    auto isPark = fieldValueMap.count("park_id") > 0 || groupSet.count("park_id") > 0;
    if (isPark)
        lastClause += " INNER JOIN (SELECT * FROM parks) p ON h.park_id=p.park_id"s;
    */

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


int buildPlayerGameSQLQuery(string argstr,
                            string &qy, vector<field_val_t>& prms,
                            string &errMsg, args_t& args) 
{
    errMsg.clear();
    qy.clear();

    json j_args;
    auto err = getArgs(argstr, args, j_args, errMsg);
    if(err) return err;

    vector<string> fieldNames;
    unordered_map<string, field_val_t> fieldValueMap;
    unordered_set<string> fieldNamesSet, groupSet;

    err = getQueryParams(j_args, fieldNames, fieldValueMap, fieldNamesSet, queryType::PLAYERGAME, errMsg);
    if(err) return err;

    // Basic strategy is to split up the query into two temp (CTE) tables home_t and away_t
    // then combine results.  We do this because many queries would not make sense unless we did
    // e.g. home aaway splits, groupings by team
    vector<string> selectFields, statList;
    unordered_set<string> selectFieldsSet;

    prms.clear();
    qy = "WITH"s;
    // add field conditions
    auto addCond = args.addCond;
    auto addParkInfo = args.addParkInfo;
    if(args.isHome) {
        qy += makeCTEPG(args.pgQryType, true, args.isOldTime, addCond, addParkInfo, args.agg, fieldNames, 
                     fieldValueMap, args.grp, args.stats, selectFields,
                     selectFieldsSet, statList, prms);
        qy += "), ";
    } else {
        // need empty set so both_t UNION makes sense
        qy += " home_t as (SELECT 1 WHERE 1=0), "; 
    }
    if(args.isAway) {
        qy += makeCTEPG(args.pgQryType, false, args.isOldTime, addCond, addParkInfo, args.agg, fieldNames,
                      fieldValueMap, args.grp, args.stats, selectFields,
                      selectFieldsSet, statList, prms);
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
    err = buildLastClausePG(lastClause, fieldValueMap, selectFields,
                          selectFieldsSet, statList, args.grp, 
                          args.agg, args.addCond, args.addParkInfo, isSplitYear, 
                          selectFieldsSetOut);
    cout << endl << "lastClause=" << lastClause;
    
    // need to wrap around last select by another select, since the minGP cannot be selected for
    // in the same clause it is defined, and also for ordering to make sense (after aggregation)
    qy += " SELECT * FROM(" + lastClause + ")";
    if(args.agg != "no")
        qy += " WHERE gp > " + to_string(args.minGP);
    qy += makeOrderBy(args.order, selectFieldsSetOut, statList, args.agg);

    // add some extra to determine if there are more records available
    qy += " LIMIT " + to_string(args.limit+5);

    return err;
}

// CTE clause for situation
std::string buildCTESitWhereClause(bool excludeBaseRun,
                                   bool addCond,
                                   bool addParkInfo,
                                   const vector<string>& fieldNames,
                                   const unordered_map<string, field_val_t> fieldValueMap,
                                   const vector<string>& selectFields,
                                   vector<field_val_t>& prms)  // output
{
    auto first = true;
    auto query = ""s;

    for (auto f : fieldNames) {
        cout << endl << "buildCTESitWhereClause: f=" << f;
        if (!first) 
            query += " AND ";
        else
            query = " WHERE ";
        first = false;
        
        auto qp = QUERY_PARAMS.at(f);
        
        if (f == "year") {
            query += (YEAR_FIELD + " BETWEEN ? AND ? ");
        }
        else if (qp.vType == valType::INT_RANGE) {
            query += (qp.fieldSelector + " BETWEEN ? AND ? ");
        }
        else {
            query += (qp.fieldSelector + "=? ");
        }
        prms.push_back(fieldValueMap.at(f));
    }

    if (excludeBaseRun) {
        query += " AND play_result NOT IN (SELECT * FROM play_baserun)";
    }

    return query;
}

// CTE for situation query
string makeCTESit(bool isHome,
                  bool excludeBaseRun,
                  bool addCond,
                  bool addParkInfo,
                  const vector<string>& fieldNames,
                  const unordered_map<string, field_val_t> fieldValueMap,
                  const vector<string>& group,
                  const string agg,
                  vector<string> &selectFields,   // output
                  unordered_set<string> &selectFieldsSet,   // output
                  vector<field_val_t> &prms)       // output
{
    auto homeOrAway = "away"s;
    auto awayOrHome = "home"s;
    if(isHome) {
        homeOrAway = "home"s;
        awayOrHome = "away"s;
    }
        
    auto query = " "s + homeOrAway + "_t AS (SELECT "s;
    cout << endl << "makeCTESit(" << __LINE__ << "): fieldNames=";
    printVec(fieldNames);
    
    // select everything for now
    selectFields.clear();
    selectFieldsSet.clear();
    query += "'"s + homeOrAway + "' AS homeaway, "s;
    selectFields.push_back("homeaway"s);
    selectFieldsSet.emplace("homeaway"s);

    for (auto f : fieldNames) {
        // since this is handled in home/away split
        // if(f == "team" || f == "_team" || f == "league" || f == "_league") continue;
        selectFields.push_back(f);
        selectFieldsSet.emplace(f);
        if(f == "team") {
            query += "batter_team AS team, ";
            continue;
        }
        else if(f == "_team") {
            query += "pitcher_team AS _team, ";
            continue;
        }
        else if(f == "league") {
            query += homeOrAway + f + " AS league, ";
            continue;
        }
        else if(f == "_league") {
            query += awayOrHome + f + " AS league, ";
            continue;
        }
        else if (f == "batter") {
            query += "batter_name AS batter, ";
            continue;
        } 
        else if (f == "pitcher") {
            query += "pitcher_name AS pitcher, ";
            continue;
        }
        
        auto qp = QUERY_PARAMS[f];

        query += qp.fieldSelector;
        if (qp.isTeam || f != qp.fieldSelector)
            query += " AS " + f;
        query += ", ";
    }

    // need to add fields group fields which were not in select
    for (auto g : group) {
        if(selectFieldsSet.count(g) == 0) {
            // since this is handled in home/away split
            // if(g == "team" || g == "_team" || g == "league" || g == "_league") continue;
            selectFields.push_back(g);
            selectFieldsSet.emplace(g);
            
            auto qp = QUERY_PARAMS[g];

            query += qp.fieldSelector;
            if (qp.isTeam || g != qp.fieldSelector)
                query += " AS " + g;
            query += ", ";
        }
    }


    query += "game_id, event_id";
    if (agg == "no") {
        query += ", year, month, "s + DAY_FIELD + " AS day, dow, num";

        selectFields.insert(selectFields.end(), {"year", "month", "day", "dow", "num"});
        selectFieldsSet.insert({"year", "month", "day", "dow", "num"});
    }

    for (auto &sit_p : SIT_PARAMS_ORDER) {
        if(selectFieldsSet.count(sit_p) == 0) {
            selectFields.push_back(sit_p);
            selectFieldsSet.emplace(sit_p);

            if (sit_p == "pitcher") {
                query += "pitcher_name AS pitcher, ";
            }
            else if(QUERY_PARAMS.count(sit_p) > 0) {
                auto qp = QUERY_PARAMS[sit_p];
                query += ", " + qp.fieldSelector;
                if(sit_p != qp.fieldSelector)
                    query += " AS " + sit_p;
            }
            else {
                query += ", " + sit_p;
            }
        }
    }

    query += " FROM game_situation_view"s;
    query += buildCTESitWhereClause(excludeBaseRun, addCond, addParkInfo, fieldNames, fieldValueMap, selectFields, prms);
    query += ")";

    return query;
}

string makeSitFinalSelect(bool isSplitYear,
                          bool addCond, 
                          bool addParkInfo,
                          const vector<string>& selectFields,
                          const unordered_set<string>& selectFieldsSet,
                          const unordered_map<string, field_val_t>& fieldValueMap,
                          const vector<string>& group,
                          const unordered_set<string>& groupSet,
                          string agg,
                          unordered_set<string>& selectFieldsSetOut) 
{       
string query = " SELECT ";
    auto isFirst = true;
    const auto SKIP_COLS = unordered_set<string>({"homeaway", "team", "_team", "_league", "league"});
    for (auto p : SELECT_PARAMS_ORDER) {
        auto p_name = p.first;   // the parameter name
        auto p_isagg = p.second;  // whether this parameter can be part of aggregation

        // cout << endl << "makeFinalSelect: p_name=" << p_name << " p_isagg=" << p_isagg;
        // don't include 'home/away' label unless we are goruping
        //if(p_name == "homeaway" && !groupSet.count("homeaway") > 0)
        //    continue;

        
        if((selectFieldsSet.count(p_name) > 0 && (agg == "no" || p_isagg)) )
        {
            // skip 'homeaway' column if it is not in select or group
            if (agg != "no" && SKIP_COLS.count(p_name) > 0) {
                  if (groupSet.count(p_name) + fieldValueMap.count(p_name) == 0) 
                     continue;
                 // fieldValueMap.count("team") + groupSet.count("team") == 0)

            }
            
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
                query += "REPLACE(num, '0', ' ') AS num";
            }
            else {
                query += p_name;
                //query += "h." + p_name;
            // if(p_name == "park_id")
            //     query += ", p.park_name AS park";
            }
        }
    }
    // add on games played/records
    if(agg != "no") {
        query += ", COUNT(*) AS plays";
        selectFieldsSetOut.insert({"plays"});
        // if(agg == "avg") {
        //     for (auto s : statList)
        //         query += ", ROUND(1000*AVG(" + s + "))/1000.00 AS " + s;
        // }
        // else {
        //     for (auto s : statList)
        //         query += ", " + agg + "(" + s + ") AS " + s;
        // }
    }
    // else
    //     query += ", " + joinStr(statList, ", ");

    if (addCond) {
        query += ", daynight, start_time, precip, sky, temp, windspeed, winddir, field_cond";
        selectFieldsSetOut.insert({"daynight", "start_time", "precip", "sky", "temp", "windspeed", "winddir", "field_cond"});
    }

    if (addParkInfo) {
        query += ", park, attendance, duration, win, loss, save, gw_rbi, complete, forfeit, protest";
        selectFieldsSetOut.insert({"park", "attendance", "duration", "win", "loss", "save", "winddir", "gw_rbi", "complete", "forfeit", "protest"});
    }
    //selectFieldsSet.insert({ "park", "daynight", "start_time", "precip", "sky", "temp", "windspeed", "winddir", "field_cond", "attendance", "duration"});
    // in the case where team is not selected or grouped
    // then only join from home table
    if(fieldValueMap.count("team") + groupSet.count("team") == 0)
        query += " FROM home_t";
    else
        query += " FROM both_t";

    // add on # of plays
    if(agg != "no") {
        query += ", COUNT(*) AS plays";
        
        selectFieldsSetOut.insert({"plays"});
    }

    query += " FROM both_t s";

    return query;
}

string makeSitOrderBy(const vector<string>& order,
                   const unordered_set<string>& selectFieldsSet)
{
    string order_clause = ""s;
    
    vector<string> ordFilt;
    for (auto o : order) {
        auto o1 = o.substr(0, o.size()-1);
        cout << endl << "makeSitOrderBy: o1=" << o1;
        
        auto o1_in_sfld = selectFieldsSet.count(o1) > 0;
        if (o1_in_sfld) {
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

int buildSitLastClause(string &lastClause, 
                    const unordered_map<string, field_val_t>& fieldValueMap,
                    const vector<string>& selectFields, 
                    const unordered_set<string>& selectFieldsSet,
                    vector<string>& group,
                    string agg,
                    bool isSplitYear, 
                    bool addCond, 
                    bool addParkInfo,
                    unordered_set<string>& selectFieldsSetOut)
{
    unordered_set<string> groupSet;
    for(auto g : group) groupSet.emplace(g);

    lastClause = makeSitFinalSelect(isSplitYear, addCond, addParkInfo, selectFields, selectFieldsSet,
                                 fieldValueMap, group, groupSet, agg, 
                                 selectFieldsSetOut);

    cout << endl << "buildSitLastClause: final_select=" << lastClause;

    return 0;
    // disabled for now -- fixed after fetch
    //if isTeam:
    //    qy += f" INNER JOIN (SELECT * FROM teams) t ON team=t.team_id"
}


int buildSituationSQLQuery(string argstr, string &qy, 
                           vector<field_val_t>& prms,
                           string &errMsg, args_t& args)
{
    errMsg.clear();
    qy.clear();
    json j_args;
    auto err = getArgs(argstr, args, j_args, errMsg);
    if(err) return err;

    vector<string> fieldNames;
    unordered_map<string, field_val_t> fieldValueMap;
    unordered_set<string> fieldNamesSet, groupSet;
    err = getQueryParams(j_args, fieldNames, fieldValueMap, fieldNamesSet, queryType::SITUATION, errMsg);
    if(err) return err;
    
    cout << endl << "buildSituationSQLQuery(" << __LINE__ << "): fieldValueMap=";
    for(auto [f, v] : fieldValueMap) {
        cout << f << ": " << v.asStr();
    }


    // in the case where years 1) appear in the selection, 
    // 2) there is a GROUP BY but
    // 3) year is not 'grp' 
    // then split year into two fields year_start and year_end
    vector<string> selectFields;
    unordered_set<string> selectFieldsSet;
    bool isSplitYear = false;
    if(fieldValueMap.count("year") > 0 && groupSet.count("year") == 0 
       && groupSet.size() > 0)
        isSplitYear = true;

    prms.clear();
    qy = "WITH"s;
    if(args.isHome) {
        qy += makeCTESit(true, args.excludeBaseRun, args.addCond,
                     args.addParkInfo, fieldNames, fieldValueMap,
                     args.grp, args.agg, selectFields, selectFieldsSet, prms);
        qy += ", ";
    } else {
        // need empty set so both_t UNION makes sense
        qy += " home_t as (SELECT 1 WHERE 1=0), "; 
    }
    if(args.isAway) {
         qy += makeCTESit(false, args.excludeBaseRun, args.addCond,
                     args.addParkInfo, fieldNames, fieldValueMap,
                     args.grp, args.agg, selectFields, selectFieldsSet, prms);
        qy += ", ";
       
    } else {
        // need empty set so both_t UNION makes sense
        qy += " away_t as (SELECT 1 WHERE 1=0), ";
    }
    qy += " both_t AS (SELECT * from home_t UNION SELECT * from away_t)";    
    
    cout << endl << "qy(CTE)=" << qy;
    // prmsH = tuple(fieldValues)prmsA = tuple(fieldValues)
    
    cout << endl << "buildSitSQLQuery: selectFields=";
    printVec(selectFields);
    cout << endl << "buildSitSQLQuery: prms=";
    for(auto p : prms)
        cout << endl << p.asStr();

    string lastClause;
    unordered_set<string> selectFieldsSetOut;
    err = buildSitLastClause(lastClause, fieldValueMap, selectFields,
                          selectFieldsSet, args.grp, args.agg,
                          isSplitYear, args.addCond, args.addParkInfo,
                          selectFieldsSetOut);
    cout << endl << "lastClause=" << lastClause;
    
    // need to wrap around last select by another select, since the minPlays cannot be selected for
    // in the same clause it is defined, and also for ordering to make sense (after aggregation)
    qy += " SELECT * FROM(" + lastClause + ")";
    if(args.agg != "no")
        qy += " WHERE plays > " + to_string(args.minPlays);
    qy += makeSitOrderBy(args.order, selectFieldsSetOut);

    // add some extra to determine if there are more records available
    qy += " LIMIT " + to_string(args.limit+5);

    return err;
}