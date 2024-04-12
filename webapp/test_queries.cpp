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
    args_t args;
    
    auto err = 0;
    vector<string> fieldNames;
    vector<field_val_t> prms, fieldVals;
    string qy, errMsg;
    
   /* err = getQueryParams(args, fieldNames, fieldVals);
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
    */
    err = buildSQLQuery(argv[1], qy, prms, errMsg, args);
    cout << endl;
    cout << endl << "err= " << err << "errMsg=" << errMsg;
    cout << endl << "qy= " << qy;
    cout << endl << "prms= ";
    for (auto& v: prms) {
        cout << " " << v.asCharPtr();
    }
    return err;
}