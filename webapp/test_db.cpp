#include "db.h"


#include <iostream>
#include <string>


using namespace std;
using std::cout;
using std::endl;

int main(int argc, char *argv[]) {
    if (argc < 1)
        cout <<  endl << "Usage: test <query string>";

    initQueryParams();
    sqlite3 *pdb = initDB();
    vector<field_val_t> params;
    query_result_t result;
    string resp, mimeType;
    std::unordered_map<std::string, std::string> teamsMap;
    handleParksRequest(pdb, "", resp, mimeType);
    cout << resp;
    handleTeamsRequest(pdb, "", resp, mimeType, teamsMap);
    cout << resp;
    handleBoxRequest(pdb, "", resp, mimeType, teamsMap);
    cout << resp;
    /* doQuery(pdb, "SELECT * from parks", params, result);
    for(auto row : result) {
        cout << endl;
        printVec(row);
    } */
}