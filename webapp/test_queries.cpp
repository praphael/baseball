#include "queries.h"

#include <iomanip>
#include <iostream>
#include <string>
#include <type_traits>

using namespace std;

int main(int argc, char *argv[]) {
    if (argc < 1)
        cout <<  endl << "Usage: test <query string>";

    auto qp = initQueryParams();
    for (auto [k, v] : qp )
        cout << endl << "count(" << k << ")=" << qp.count(k);
    
    auto vec = splitStr(argv[1], '&');
    cout << endl << " args split= ";
    printVec(vec);
    unordered_map<string, string> mp;
    for(auto v : vec) {
        auto a = splitStr(v, '=');
        cout << " a=";
        printVec(a);
        mp[a[0]] = a[1];
    }

    auto err = 0;
    vector<string> fieldNames;
    vector<field_val_t> prms, fieldVals;
    string qy, errMsg;

    err = getQueryParams(mp, fieldNames, fieldVals);
    if(err) {
        cout << endl << "getQueryParams returned " << err;
        exit(1);
    }
    cout << endl << "fieldNames= ";
    printVec(fieldNames);
    cout << endl << "prms= ";    
    for (auto& v: fieldVals) {
        cout << " " << v.asCharPtr();
    }
    err = buildSQLQuery(mp, qy, prms, errMsg);
    cout << endl;
    cout << endl << "err= " << err << "errMsg=" << errMsg;
    cout << endl << "qy= " << qy;
    cout << endl << "prms= " << qy;
    for (auto& v: prms) {
        cout << " " << v.asCharPtr();
    }
    return err;
}