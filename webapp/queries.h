
#pragma once 

#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <iostream>
#include <sstream>
#include <set>

#include "json.hpp"

using json = nlohmann::json;

using query_result_t = std::vector<std::vector<std::string>>;

enum valType {NOT_SET, INT, STR, INT_RANGE};
enum queryType {ALL, GAMELOG, PLAYERGAME, SITUATION};
enum playerGameQueryType {BATTING, PITCHING, FIELDING};

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
    playerGameQueryType pgQryType;
    // min games played for gamelog or player game queries
    unsigned int minGP; 

    // min plays for situation
    // since this includes SB/CS/WP/PB/DI/OA
    // it is not necessarily PA/BF unless 
    // excludeBaseRun is true
    unsigned int minPlays; 

    // whether to exclude plays that
    // are purely baserunning
    // e.g. SB/CS/WP/PB/DI/OA
    bool excludeBaseRun;

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
    // types of queries where this param makes sense
    // one or more of "gamelog", "playergame", "situation"
    std::set<queryType> queryTypes;
};

std::unordered_map<std::string, q_params_t>& initQueryParams();
int buildSQLQuery(std::string argstr,
                  std::string &qy, std::vector<field_val_t>& prms,
                  std::string &errMsg, args_t& args);

int buildPlayerGameSQLQuery(std::string argstr,
                            std::string &qy, std::vector<field_val_t>& prms,
                            std::string &errMsg, args_t& args);

int buildSituationSQLQuery(std::string argstr,
                           std::string &qy, std::vector<field_val_t>& prms,
                           std::string &errMsg, args_t& args);

std::vector<std::string> splitStr(const std::string& input, char delimiter);

std::string renderHTMLTable(std::vector<std::string> headers, query_result_t result,
                            std::string opts, int limit);

template <typename T> void printVec (std::vector<T> vec) {
    for(auto v : vec) std::cout << " " << v;
};

bool isNumberChar(char c);
char toUpper(char c);