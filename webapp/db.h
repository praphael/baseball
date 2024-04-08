#pragma once

#include <string>
#include <vector>
#include "sqlite3.h"
#include "queries.h"

sqlite3* initDB();

int doQuery(sqlite3 *pdb, std::string qy, 
            const std::vector<field_val_t>& params,
            query_result_t& result, std::vector<std::string>& columnNames, 
            std::string& errMsg);


int handleParksRequest(sqlite3 *pdb, const std::string &qy, std::string& resp);
int handleTeamsRequest(sqlite3 *pdb, const std::string &qy, std::string& resp);
int handleBoxRequest(sqlite3 *pdb, const std::string &qy, std::string& resp, std::string &mimeType);
