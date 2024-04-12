
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
                  

enum valType {NOT_SET, INT, STR, INT_RANGE};

struct range_t {
    int low;
    int high;
};

class field_val_t {    
private:
    // 0 == integer, 1 == string
    valType vType = NOT_SET;
    union {
        int i;
        char s[256];
        range_t rng;
    } v;

public:
    valType getValType() const;
    int asInt() const;
    range_t asIntRange() const;
    std::string asStr() const;
    const char* asCharPtr() const;
    void setInt(int val);
    void setStr(std::string val);
    void setIntRange(int low, int high);
};

struct args_t {
    bool isHome;
    bool isAway;
    std::string agg;
    std::vector<std::string> grp;
    bool isOldTime;
    std::vector<std::string> stats;
    std::vector<std::string> order;
    unsigned int minGP;
    unsigned int limit;
    std::string ret;
    std::string retopts;
};

// parameter types
struct q_params_t {
    // SQL for selecting this column in table, including funciton call,etc.
    std::string fieldSelector; 
    valType vType; 
    bool isTeam; // whether is team-dependent field, e.g. score
};

std::unordered_map<std::string, q_params_t>& initQueryParams();
int buildSQLQuery(std::string argstr,
                  std::string &qy, std::vector<field_val_t>& prms,
                  std::string &errMsg, args_t& args);

std::vector<std::string> splitStr(const std::string& input, char delimiter);

int getQueryParams(const json& args,
                    std::vector<std::string>& fieldNames,
                    std::vector<field_val_t>& fieldValues);

std::string buildCTEWhereClause(bool isHome, const std::vector<std::string>& fieldNames, 
                                const std::vector<std::string>& grp,
                                bool isOldTime, const std::vector<std::string>& selectFields,
                                int minGP, const std::vector<int>& fieldsNotInSelect);

std::string renderHTMLTable(std::vector<std::string> headers, query_result_t result,
                            std::string opts, int limit);

template <typename T> void printVec (std::vector<T> vec) {
    for(auto v : vec) std::cout << " " << v;
};

bool isNumberChar(char c);
char toUpper(char c);