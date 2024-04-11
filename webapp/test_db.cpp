#include "db.h"


#include <iostream>
#include <string>


using namespace std;
using std::cout;
using std::endl;

int main(int argc, char *argv[]) {
    if (argc < 4)
        cout << endl << "Usage: test <yearStart>, <yearEnd>, <query string>";
    auto yearStart = std::atoi(argv[1]);
    auto yearEnd = std::atoi(argv[2]);
    auto qyStr = string(argv[3]);
    initQueryParams();
    sqlite3 *pdb = initDB(yearStart, yearEnd);
    query_result_t result;
    string resp, mimeType;
    std::unordered_map<std::string, std::string> teamsMap;
    /*
    handleParksRequest(pdb, qyStr, resp, mimeType);
    cout << resp;
    handleTeamsRequest(pdb, qyStr, resp, mimeType, teamsMap);
    cout << resp;
    */
    handleBoxRequest(pdb, qyStr, resp, mimeType, teamsMap);
    cout << resp;
    /* doQuery(pdb, "SELECT * from parks", params, result);
    for(auto row : result) {
        cout << endl;
        printVec(row);
    } */
}