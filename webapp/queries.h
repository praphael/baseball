
#pragma once 

#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <iostream>
#include <sstream>

using query_result_t = std::vector<std::vector<std::string>>;
                  
// map of query to params to 
// first entry - SQL as used in first CTE WHERE clause, including possible renaming
// second entry - SQL as used in second WHERE clause
//third entry - representative value, used for type inference
// fourth entry - true/false, whether this is a "team" stat, to be used for appending 'home/visiting" to field name
struct q_params_t {
    std::string firstClause;
    std::string secondClause;
    int type; // 0 = int, 1 - string
    bool isTeam;
};

class field_val_t {
    // 0 == integer, 1 == string
    int vType;
    char bytes[128];

public:
    const static int NOT_SET = -1;
    const static int INT = 0;
    const static int STR = 1;

    field_val_t() : vType(NOT_SET) { bytes[0] = 0; };
    int valType();
    int asInt();
    char* asCharPtr();
    std::string asStr();
    void setInt(int v);
    void setStr(std::string s);
};

std::unordered_map<std::string, q_params_t>& initQueryParams();
int buildSQLQuery(std::unordered_map<std::string, std::string> args,
                  std::string &qy, std::vector<field_val_t>& prms,
                  std::string &errMsg);

std::vector<std::string> splitStr(const std::string& input, char delimiter);

int getQueryParams(std::unordered_map<std::string, std::string> args,
                    std::vector<std::string>& fieldNames,
                    std::vector<field_val_t>& fieldValues);

std::string buildCTEWhereClause(bool isHome, std::vector<std::string> fieldNames, 
                                std::vector<std::string> grp,
                                bool isOldTime);

std::string renderHTMLTable(std::vector<std::string> headers, query_result_t result, std::string opts);

template <typename T> void printVec (std::vector<T> vec) {
    for(auto v : vec) std::cout << " " << v;
};