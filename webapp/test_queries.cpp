#include "queries.h"

#include <iomanip>
#include <iostream>
#include <string>
#include <type_traits>

using namespace std;

// for 's' operator
using namespace std::string_literals;

auto gamelog_queries = vector<string>();
auto player_queries = vector<string>();
auto playergame_queries = vector<string>();
auto situation_queries = vector<string>();

// /box JSON format:
// params:
//    team:'BAL', 'NYA', etc.  _team: opposing team
//    year: {low:<num>, high:<num>}, 
//    month: <num>(3..11)
//    park_id: 
//    dow: 'Sun', 'Mon', etc.
//    homeaway: 'Home', 'Away'
//    league: "AL", _league (opposing team leage)
// aggregation: no, sum, avg, max, min, count
// group: [<param>, <param>, etc.]
// oldtime: 1 for < 1903 stats
// minGP: <num>
// stats: "H", "R", "RBI", etc.
// order: [<param> followed by '>' or '<', <param> ...]
// ret: 'html', 'json'
// retopt: 'bs' (for html, render Bootstrap)
// limit: <num>

void initQueryStrings() {
    const auto cma = ", "s;
    const auto opbr = "{"s;
    const auto clbr = "}"s;
    const auto teamBAL = "\"team\":\"BAL\""s;
    const auto bat_teamBOS = "\"batter_team\":\"BOS\""s;
    const auto agg_no = "\"aggregation\":\"no\""s;
    const auto agg_sum = "\"aggregation\":\"sum\""s;
    const auto agg_avg = "\"aggregation\":\"avg\""s;
    const auto baberuth_bid = "\"batter_id\":20415"s;
    const auto waltjohs_pid = "\"pitcher_id\":11839"s;
    const auto year2022 = "\"year\": {\"low\":2022, \"high\":2022}"s;
    const auto year_rng = "\"year\": {\"low\":2012, \"high\":2022}"s;
    const auto mnth_jun = "\"month\": 6"s;
    const auto grp_mnth = "\"group\":[\"month\"]";
    const auto grp_opp_team = "\"group\":[\"_team\"]";
    const auto grp_year = "\"group\":[\"year\"]";
    const auto grp_batter = "\"group\":[\"batter_id\"]";
    const auto limit10 = "\"limit\": 10";

    gamelog_queries.push_back(opbr + agg_no + clbr);    
    auto qy = opbr + agg_sum + cma + teamBAL + cma + year2022 + cma + grp_mnth + clbr;
    gamelog_queries.push_back(qy);
    qy = opbr + teamBAL + cma + year2022 + cma + grp_mnth + clbr;
    gamelog_queries.push_back(qy);
    qy = opbr + agg_sum + cma + baberuth_bid + cma + grp_year + clbr;
    playergame_queries.push_back(qy);
    qy = opbr + teamBAL + cma + year2022 + cma + mnth_jun + cma + grp_opp_team + clbr;
    playergame_queries.push_back(qy);
    
    qy = opbr + agg_no + cma + baberuth_bid + cma + waltjohs_pid + clbr;
    situation_queries.push_back(qy);
    qy = opbr + agg_sum + cma + bat_teamBOS + cma + year2022 + cma + grp_mnth + clbr;
    situation_queries.push_back(qy);

}

int main(int argc, char *argv[]) {
    string qy;    

    auto qp = initQueryParams();
    initQueryStrings();
    args_t args;
    
    auto err = 0;
    vector<string> fieldNames;
    vector<field_val_t> prms, fieldVals;
    string sql_qy, errMsg;

    for(auto qy : gamelog_queries) {
        err = err | buildSQLQuery(qy, sql_qy, prms, errMsg, args);
        cout << endl;
        cout << endl << "(gamelog) qy= " << qy;
        cout << endl << "err= " << err << " errMsg=" << errMsg;
        if (err) exit(1);
        cout << endl << "sql_qy= " << sql_qy;        
        cout << endl << "prms= ";
        for (auto& v: prms) {
            cout << " " << v.asStr();
        }
    }

    for(auto qy : playergame_queries) {
        err = err | buildPlayerGameSQLQuery(qy, sql_qy, prms, errMsg, args);
        cout << endl;
        cout << endl << "(playergame) qy= " << qy;
        cout << endl << "err= " << err << " errMsg=" << errMsg;
        if (err) exit(1);
        cout << endl << "sql_qy= " << sql_qy;        
        cout << endl << "prms= ";
        for (auto& v: prms) {
            cout << " " << v.asStr();
        }
    }

    for(auto qy : situation_queries) {
        err = err | buildSituationSQLQuery(qy, sql_qy, prms, errMsg, args);
        cout << endl;
        cout << endl << "(situation) qy= " << qy;
        cout << endl << "err= " << err << " errMsg=" << errMsg;
        if (err) exit(1);
        cout << endl << "sql_qy= " << sql_qy;        
        cout << endl << "prms= ";
        for (auto& v: prms) {
            cout << " " << v.asStr();
        }
    }

    return err;
}