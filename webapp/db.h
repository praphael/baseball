#pragma once

#include <string>
#include <vector>
#include "sqlite3.h"
#include "queries.h"

sqlite3* initDB(int yearStart, int yearEnd);

int doQuery(sqlite3 *pdb, std::string qy, 
            const std::vector<field_val_t>& params,
            query_result_t& result, std::vector<std::string>& columnNames, 
            std::string& errMsg);


int handleParksRequest(sqlite3 *pdb, const std::string &qy, std::string& resp, std::string &mimeType);
int handleTeamsRequest(sqlite3 *pdb, const std::string &qy, std::string& resp, std::string &mimeType, 
                       std::unordered_map<std::string, std::string>& teamsMap );
int handleBoxRequest(sqlite3 *pdb, const std::string &qy, std::string& resp, std::string &mimeType,
                    const std::unordered_map<std::string, std::string>& teamsMap );
