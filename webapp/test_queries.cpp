#include "queries.h"

#include <iomanip>
#include <iostream>
#include <string>
#include <type_traits>

using namespace std;

// for 's' operator
using namespace std::string_literals;

auto box_queries = vector<string>();
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
    box_queries.push_back("{\"aggregation\":\"no\"}");
    auto qy = "{\"team\":\"BAL\", \"year\": {\"low\":2022, \"high\":2022}"s;
    qy += ", group:[\"month\"]}";
    box_queries.push_back(qy);
    playergame_queries.push_back("{}");
    situation_queries.push_back("{}");
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

    for(auto qy : box_queries) {
        err = buildSQLQuery(qy, sql_qy, prms, errMsg, args);
        cout << endl;
        cout << endl << "qy= " << qy;
        cout << endl << "err= " << err << " errMsg=" << errMsg;
        cout << endl << "sql_qy= " << sql_qy;        
        cout << endl << "prms= ";
        for (auto& v: prms) {
            cout << " " << v.asStr();
        }
    }

    for(auto qy : playergame_queries) {
        err = buildPlayerGameSQLQuery(qy, sql_qy, prms, errMsg, args);
        cout << endl;
        cout << endl << "qy= " << qy;
        cout << endl << "err= " << err << " errMsg=" << errMsg;
        cout << endl << "sql_qy= " << sql_qy;        
        cout << endl << "prms= ";
        for (auto& v: prms) {
            cout << " " << v.asStr();
        }
    }

    for(auto qy : situation_queries) {
        err = buildSituationSQLQuery(qy, sql_qy, prms, errMsg, args);
        cout << endl;
        cout << endl << "qy= " << qy;
        cout << endl << "err= " << err << " errMsg=" << errMsg;
        cout << endl << "sql_qy= " << sql_qy;        
        cout << endl << "prms= ";
        for (auto& v: prms) {
            cout << " " << v.asStr();
        }
    }

    return err;
}