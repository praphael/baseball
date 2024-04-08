#pragma once

#include <string>
#include <utility>
#include <vector>


using col_t = std::pair<std::string, int>;
using col_info_t = std::vector<col_t>;
extern col_info_t parksCol;
extern col_info_t teamsCol;
extern col_info_t boxCol;

void initTableInfo();

extern const char* CREATE_PARKS;
extern const char* CREATE_TEAMS;
extern const char* CREATE_BOXSCORE;

