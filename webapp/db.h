#pragma once

#include <string>
#include <vector>
#include "sqlite3.h"
#include "queries.h"
#include "trie.h"

constexpr auto MIME_JSON = "application/json";
constexpr auto MIME_HTML = "text/html";
constexpr auto MIME_TEXT = "text/plain";

sqlite3* initDB(int yearStart, int yearEnd);

int doQuery(sqlite3 *pdb, std::string qy, 
            const std::vector<field_val_t>& params,
            query_result_t& result, std::vector<std::string>& columnNames, 
            std::string& errMsg);

int handleParksRequest(sqlite3 *pdb, const std::string &qy, std::string& resp, std::string &mimeType);
int handleTeamsRequest(sqlite3 *pdb, const std::string &qy, std::string& resp, std::string &mimeType, 
                       std::unordered_map<std::string, std::string>& teamsMap );
int handleGamelogRequest(sqlite3 *pdb, const std::string &qy, std::string& resp, std::string &mimeType,
                         const std::unordered_map<std::string, std::string>& teamsMap );

// get names of players given partial name
int handlePlayerRequest(sqlite3 *pdb, const std::string &qy, std::string& resp, 
                        std::string &mimeType, 
                        NameTrie & playerLastTrie,
                        NameTrie & playerOtherTrie,
                        std::unordered_map<int, std::string>& playerIDMap );

// per-game player stats, aggregated 
int handlePlayerGameRequest(sqlite3 *pdb, const std::string &qy, std::string& resp, std::string &mimeType,
                            const std::unordered_map<std::string, std::string>& teamsMap,
                            const std::unordered_map<int, std::string>& playerIDMap );

int handleSituationRequest(sqlite3 *pdb, const std::string &qy, std::string& resp, std::string &mimeType,
                          const std::unordered_map<std::string, std::string>& teamsMap,
                          const std::unordered_map<int, std::string>& playerIDMap );

