
#pragma once 

#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <iostream>
#include <sstream>

#include "json.hpp"

using json = nlohmann::json;

using query_result_t = std::vector<std::vector<std::string>>;
                  

enum valType {NOT_SET, INT, STR};
class field_val_t {    
private:
    // 0 == integer, 1 == string
    valType vType = NOT_SET;
    union {
        int i;
        char s[256];
    } v;

public:
    valType getValType();
    int asInt();
    std::string asStr();
    const char* asCharPtr();
    void setInt(int val);
    void setStr(std::string val);
};

// map of query to params to 
// first entry - SQL as used in first CTE WHERE clause, including possible renaming
// second entry - SQL as used in second WHERE clause
//third entry - representative value, used for type inference
// fourth entry - true/false, whether this is a "team" stat, to be used for appending 'home/visiting" to field name
struct q_params_t {
    std::string firstClause;
    std::string secondClause;
    valType vType; // 0 = int, 1 - string
    bool isTeam;
};

std::unordered_map<std::string, q_params_t>& initQueryParams();
int buildSQLQuery(std::string argstr,
                  std::string &qy, std::vector<field_val_t>& prms,
                  std::string &errMsg, json& args);

std::vector<std::string> splitStr(const std::string& input, char delimiter);

int getQueryParams(const json& args,
                    std::vector<std::string>& fieldNames,
                    std::vector<field_val_t>& fieldValues);

std::string buildCTEWhereClause(bool isHome, std::vector<std::string> fieldNames, 
                                std::vector<std::string> grp,
                                bool isOldTime);

std::string renderHTMLTable(std::vector<std::string> headers, query_result_t result, std::string opts);

template <typename T> void printVec (std::vector<T> vec) {
    for(auto v : vec) std::cout << " " << v;
};

bool isNumberChar(char c);
char toUpper(char c);