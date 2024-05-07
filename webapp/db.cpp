#include <iostream>
#include <cstring>
#include <sstream>

#include "db.h"
#include "baseball_tables.h"


using std::string;
using std::vector;
using std::cout;
using std::cerr;
using std::endl;
using std::unordered_map;
using std::to_string;

// for 's' operator
using namespace std::string_literals;

//------------------------------------------------------------------------------
void copyTable(sqlite3* pdb, const std::string qy, col_info_t& colInfo,
             const char *tbl, sqlite3* pdb_mem, int maxRows) {
    sqlite3_stmt *pstmt, *instmt;
    const char *pzTail;

    auto err = sqlite3_prepare_v2(pdb, qy.c_str(), qy.size(), &pstmt, &pzTail); 

    auto ins_str = std::string("INSERT INTO ");
    ins_str.append(tbl);
    ins_str.append(" (");
    for(int i=0; i<colInfo.size()-1; i++) {
        auto pr = colInfo[i];
        ins_str.append(pr.first);
        ins_str.append(", ");
    }
    ins_str.append(colInfo[colInfo.size()-1].first);
    ins_str.append(") VALUES(");
    auto ins_base = ins_str;
    for(int i=0; i<colInfo.size()-1; i++) {
        ins_str.append("?, ");
    }
    ins_str.append("?)");
    err = sqlite3_prepare_v2(pdb, ins_str.c_str(), ins_str.size(),
                             &instmt, &pzTail); 
    // std::cout << std::endl << "ins_str= " << ins_str;

    if (err != SQLITE_OK) {
        cerr << std::endl << "copyTable: could not prepare insert statement " << err;
        cerr << std::endl << pzTail;
        exit(1);
    }                             

    //std::cout << std::endl << "sqlite3_prepare_v2 err=" << err;
    err = sqlite3_step(pstmt);
    if (err != SQLITE_ROW) {
        cerr << std::endl << "copyTable: sqlite3_step() err=" << err;
        exit(1);
    }
    int row = 0;
    int i = 0;
    while (row < maxRows && err != SQLITE_DONE) {
        //std::cout << std::endl;
        // err = sqlite3_prepare_v2(pdb_mem, qy.c_str(), qy.size(), &pstmt, &pzTail); 
        if (err == SQLITE_ROW) {
            auto ins_s = ins_base;
            for(int c=0; c<colInfo.size(); c++) {
                auto pr = colInfo[c];
                //std::cout << std::endl << "c= " << c << " field=" << pr.first;
                
                if (pr.second == 0) {
                    if (sqlite3_column_type(pstmt, c) == SQLITE_NULL) {
                        ins_s += "NULL";
                        err = sqlite3_bind_null(instmt, c+1);
                        if (err != SQLITE_OK) {
                            cerr << std::endl << "copyTable: sqlite3_bind_null failed err=" << err << " c=" << c;
                            exit(1);
                        }
                    }
                    else {
                        auto n = sqlite3_column_int(pstmt, c);
                        ins_s += std::to_string(n);
                        err = sqlite3_bind_int(instmt, c+1, n);
                        if (err != SQLITE_OK) {
                            cerr << std::endl << "copyTable: sqlite3_bind_int failed err=" << err << " c=" << c;
                            exit(1);
                        }
                    }
                    if (c < colInfo.size()-1)
                        ins_s += ", ";
                    else ins_s += ")";
                    
                }
                else { // pr.second == 1 (string type)

                    auto r = (sqlite3_column_text(pstmt, c));
                    if (r == nullptr) {
                       ins_s += "NULL";
                       err = sqlite3_bind_null(instmt, c+1);
                       //err = sqlite3_bind_text(instmt, c+1, "", 1, SQLITE_TRANSIENT);
                        if (err != SQLITE_OK) {
                            cerr << endl << "copyTable: sqlite3_bind_null failed err=" << err << " c=" << c;
                            exit(1);
                        }
                    }
                    else {
                        auto txt = reinterpret_cast<const char*>(r);
                        auto s = string(txt);
                        int pos = 0, nxtpos = 0;
                        // insert extra '
                        const char ch = '\'';
                        while((nxtpos = s.find(ch, pos)) != std::string::npos) {
                            if(s[nxtpos+1] != ch) {
                                s.insert(nxtpos, "\'");
                            }
                            pos = nxtpos+2;
                        }
                        //if(pos != 0)
                        //    std::cout << std::endl << "'" << txt << "' replaced by '" << s << "'";
                        //std::cout << std::endl << txt;
                        ins_s += "'"; ins_s += s; ins_s += "' ";
                        //std::cout << std::endl << "2 " << ins_s;
                        // TODO investigate potential memory leak
                        err = sqlite3_bind_text(instmt, c+1, s.c_str(), s.size(), SQLITE_TRANSIENT);
                        if (err != SQLITE_OK) {
                            cerr << std::endl << "copyTable: sqlite3_bind_text failed err=" << err << " c=" << c;
                            cerr << std::endl << " s=" << s;
                            cerr << std::endl << " ins_s=" << ins_s;
                            exit(1);
                        }
                    }
                    if (c < colInfo.size()-1)
                        ins_s += ", ";
                    else ins_s += ")";
                }
            } 
            
            //std::cout << std::endl << ins_s;
            sqlite3_stmt *ins_stmt;
            err = sqlite3_prepare_v2(pdb_mem, ins_s.c_str(), ins_s.size(),
                                     &ins_stmt, &pzTail); 
            if (err != SQLITE_OK) {
                cerr << std::endl << "copyTable: could not prepare err=" << err << " row=" << row;
                exit(1);
            }
            err = sqlite3_step(ins_stmt);
            if (err != SQLITE_DONE) {
                cerr << std::endl << "copyTable: could not insert err=" << err << " row=" << row;
                cerr << std::endl << " ins_s=" << ins_s;
                exit(1);
            }
            sqlite3_finalize(ins_stmt);

            err = sqlite3_reset(instmt);
            // if (row > 220000) std::cout << std::endl << "fetched row=" << row;
            row++;
        } else {
            cerr << "copyTable: could not get row i=" << i << " row=" << row;
            cerr << " err=" << err;
        }      

        //std::cout << std::endl << "calling sqlite3_step";
        err = sqlite3_step(pstmt);
        i++;
    }
    cout << std::endl << "copyTable: done fetched " << row << " rows" << std::endl;
    sqlite3_finalize(pstmt);
    sqlite3_finalize(instmt);
}


int doQuery(sqlite3 *pdb, std::string qy, const vector<field_val_t>& prms,
            query_result_t& result, std::vector<std::string>& columnNames, 
            string& errMsg) {
    sqlite3_stmt *pstmt;
    const char *pzTail;

    errMsg.clear();

    auto err = sqlite3_prepare_v2(pdb, qy.c_str(), qy.size(), &pstmt, &pzTail); 
    if (err != SQLITE_OK) {
        errMsg = "doQuery(" + to_string(__LINE__) + "): could not prepare query statement "s;
        // create more meaningful error message
        // back up 30 characters, and advance forward same amount
        int nch=0;
        char *e = const_cast<char*>(pzTail);
        char *b = e;
        while (nch < 30 && b != qy.c_str()) {
            nch++;
            b--;
            if(*e != 0) e++;
        }
        // null terminate 
        *e = 0;
        errMsg.push_back('\n');
        errMsg += string(b); errMsg.push_back('\n');
        for(int i=nch; i>0; i--) errMsg.push_back(' ');
        errMsg.push_back('^'); errMsg.push_back('\n'); 
        for(int i=nch; i>0; i--) errMsg.push_back(' ');
        errMsg.push_back('|'); errMsg.push_back('\n'); 
        for(int i=nch; i>0; i--) errMsg.push_back(' ');
        errMsg += "\nerror here";
        for(int i=nch-10; i>0; i--) errMsg.push_back('-');
        errMsg.push_back('+');

        cerr << std::endl << errMsg << err;
        cerr << std::endl << "qy=\"" << qy << "\"";
        return(1);
    }

    /* bind parametes */
    int c = 1;
    for (auto p : prms) {
        cout << endl << "doQuery ("  << __LINE__ << ") p=" << p.asStr();
        if (p.getValType() == valType::INT) {
            err = sqlite3_bind_int(pstmt, c, p.asInt());
            if (err != SQLITE_OK) {
                errMsg = "doQuery(" + to_string(__LINE__) + "): sqlite3_bind_int failed err="s;
                errMsg += to_string(err)+ " c=" + to_string(c);
                cerr << endl << errMsg;
                return 2;
            }
        }
        else if (p.getValType() == valType::STR) {
            auto sp = p.asStr();
            // wrap in single quotes
            // auto s = "\'" + sp + "\'";
            // TODO: investigate potential memory leak here
            err = sqlite3_bind_text(pstmt, c, sp.c_str(), sp.size(), SQLITE_TRANSIENT);
            if (err != SQLITE_OK) {
                errMsg = "doQuery(" + to_string(__LINE__) + "): sqlite3_bind_text() failed err="s;
                errMsg += to_string(err) + " c=" + to_string(c);
                cerr << endl << errMsg;
                return 3;
            }
        } else if (p.getValType() == valType::INT_RANGE) {
            auto rng = p.asIntRange();
            err = sqlite3_bind_int(pstmt, c, rng.low);
            if (err != SQLITE_OK) {
                errMsg = "doQuery(" + to_string(__LINE__) + "): sqlite3_bind_int failed err="s;
                errMsg += to_string(err)+ " c=" + to_string(c);
                cerr << endl << errMsg;
                return 4;
            }
            c += 1;
            err = sqlite3_bind_int(pstmt, c, rng.high);
            if (err != SQLITE_OK) {
                errMsg = "doQuery(" + to_string(__LINE__) + "): sqlite3_bind_int failed err="s;
                errMsg += to_string(err)+ " c=" + to_string(c);
                cerr << endl << errMsg;
                return 5;
            }
        } else {
            errMsg = "doQuery(" + to_string(__LINE__) + "): unknown type "s + to_string(p.getValType());
            cerr << endl << errMsg;
            return 6;  // unknown type
        }
        c++;
    }

    auto stmt_str = sqlite3_expanded_sql(pstmt);
    cout << endl << "doQuery(" << __LINE__ << " query=" << stmt_str;
    sqlite3_free(stmt_str);

    result.clear();
    columnNames.clear();
    //std::cout << std::endl << "sqlite3_prepare_v2 err=" << err;
    err = sqlite3_step(pstmt);
    if (err != SQLITE_ROW) {
        // errMsg += "doQuery: sqlite3_step() err=" + to_string(err);
        cerr << endl << "doQuery no data stmt_str='" << stmt_str << "'";
        return 0;
    }
    
    int row = 0;
    int i = 0;
    while (err != SQLITE_DONE) {
        vector<string> r;
        //std::cout << std::endl;
        // err = sqlite3_prepare_v2(pdb_mem, qy.c_str(), qy.size(), &pstmt, &pzTail); 
        if (err == SQLITE_ROW) {
            auto numCols = sqlite3_column_count(pstmt);
            for(int c=0; c<numCols; c++) {
                if(row == 0)
                    columnNames.push_back(sqlite3_column_name(pstmt, c));
                auto colType = sqlite3_column_type(pstmt, c);
                if (colType == SQLITE_NULL) {
                    r.push_back("NULL");
                }
                else if (colType == SQLITE_INTEGER) {
                    auto n = sqlite3_column_int(pstmt, c);
                    r.push_back(std::to_string(n));
                }
                else if (colType == SQLITE_TEXT) {
                    auto txt = sqlite3_column_text(pstmt, c);
                    r.push_back(string(reinterpret_cast<const char*>(txt)));
                } 
                else if (colType == SQLITE_FLOAT) {
                    auto fp = sqlite3_column_double(pstmt, c);
                    std::stringstream ss;
                    ss << std::fixed << std::setprecision(3) << fp;
                    std::string s = ss.str();
                    r.push_back(s);
                } else {
                    errMsg = "doQuery: unknown column type " + to_string(colType) + " at c=" + to_string(c);
                    cerr << endl << errMsg;
                    return 5;
                }
            }
            result.push_back(r);
            row++;
        } else {
            std::cout << endl << "doQuery: could not get row i=" << i << " row=" << row << " err=" << err;
        }
         
        err = sqlite3_step(pstmt);
        i++;
    }
    cout << endl << "doQuery: done fetched " << row << " rows" << std::endl;
    sqlite3_finalize(pstmt);

    return 0;
}

sqlite3* initDB(int yearStart, int yearEnd) {
    initTableInfo();
    sqlite3 *pdb, *pdb_mem;
    
    const auto qyTeams = std::string("SELECT * from teams");
    const auto qyParks = std::string("SELECT * from parks");
    auto err = sqlite3_open("baseball.db", &pdb);
    if(err != SQLITE_OK) {
        cerr << endl << "initDB: Could not open 'baseball.db', exiting";
        exit(1);
    }
    return pdb;  // don't copy to mem for now

    err = sqlite3_open(":memory:", &pdb_mem);
    if(err != SQLITE_OK) {
        cerr << endl << "initDB: Could not open memory db, exiting";
        exit(1);
    }
    char *errMsg = new char[256];
    err = sqlite3_exec(pdb_mem, CREATE_PARKS, nullptr, nullptr, &errMsg);
    if(err != SQLITE_OK) {
        cerr << endl << "initDB: Could not create table 'parks";
        exit(1);
    }
    err = sqlite3_exec(pdb_mem, CREATE_TEAMS, nullptr, nullptr, &errMsg);
    if(err != SQLITE_OK) {
        cerr << endl << "initDB: Could not create table 'teams";
        exit(1);
    }
    err = sqlite3_exec(pdb_mem, CREATE_BOXSCORE, nullptr, nullptr, &errMsg);
    if(err != SQLITE_OK) {
        cerr << endl << "initDB: Could not create table 'boxscore";
        exit(1);
    }
    copyTable(pdb, qyTeams, teamsCol, "teams", pdb_mem, 600);
    copyTable(pdb, qyParks, parksCol, "parks", pdb_mem, 1000);
    for (auto yr=yearStart; yr<=yearEnd; yr++) {
        auto qyBox = std::string("SELECT * from boxscore WHERE CAST(substr(game_date,0,5) AS INTEGER) == ") + std::to_string(yr);
        cout << endl << "initDB: getting year" << yr;
        copyTable(pdb, qyBox, boxCol, "boxscore", pdb_mem, 100000);
    }

    cout << endl << "initDB: closing db";
    sqlite3_close(pdb);
    cout << endl << "initDB: done";

    return pdb_mem;
}

int makeArgMap(string qy, unordered_map<string, string>& args) {
    args.clear();
    auto fields = splitStr(qy, '&');
    for (auto prm : fields) {
        auto a = splitStr(prm, '=');
        if (a.size() > 2) return 1;
        auto v = string("");
        if (a.size() > 1)
            v = a[1];
        args[a[0]] = v;
    }
    return 0;
}

string makeJSONresponse(vector<string> columnNames, query_result_t result, int limit) {
    string r;
    r += "{ \"headers\": [";
    for(auto c : columnNames) {
        r += "\"" + c + "\",";
    }
    r.pop_back();
    r += "], \"result\": [";
    int rn = 0;
    for(auto row : result) {
        r += "[";
        for(auto fld : row) {
            r += "\"" + fld + "\",";
        }
        r.pop_back();
        r += "],";
        rn += 1;
        if(rn >= limit) break;
    }
    r.pop_back();
    r += "], ";
    r += "\"hasMore\": ";
    if (result.size() > rn) {
        r += "true";
    } else {
        r += "false";
    }

    r += " }";
    return r;
}

string make_dt_ms_str(int dt_ms) {
    return to_string(dt_ms);
}

void fixColumnNames(vector<string>& colummNames) {
    for(auto& col : colummNames) {
        cout << endl << "col= " << col;
        if(col.size() > 1) {
            if (col == "_team") {
                col = "Opponent";
            }
            else if (col == "_league") {
                col = "OppLg";
            }
            else if (col == "league") {
                col = "Lg";
            }
            else if (col == "_score") {
                col = "OppSc";
            }
            else if (col == "_game") {
                col = "OppGm";
            }
            else if (col == "num") {
                col = "N";
            }
            else if (col == "month") {
                col = "Mon";
            }
            // statistics with '_' replace with 'opp'
            else if(col[0] == '_') {
                col.replace(0, 1, "opp");
            }
            // stats prepened with 'n' so SQL works
            else if(isNumberChar(col[1])) {
                // delete first char
                col.erase(col.begin());
            }
            else if (col == "dow") {
                col = "DoW";
            }
            else if (col == "homeaway") {
                col = "H/A";
            }
            else {
                col[0] = toUpper(col[0]);
            }

            // replace '_' with spaces
            auto idx = size_t{0};
            while ((idx = col.find('_')) != string::npos) col[idx++] = ' ';
        }
        cout << "->" << col;
    }
}

string getDOW(string dow) {
    if(dow == "0") return "Sun";
    if(dow == "1") return "Mon";
    if(dow == "2") return "Tue";
    if(dow == "3") return "Wed";
    if(dow == "4") return "Thu";
    if(dow == "5") return "Fri";
    if(dow == "6") return "Sat";    
    return dow;
}

string getMonth(string month) {
    if(month == "3") return "Mar";
    if(month == "4") return "Apr";
    if(month == "5") return "May";
    if(month == "6") return "Jun";
    if(month == "7") return "Jul";
    if(month == "8") return "Aug";
    if(month == "9") return "Sep";
    if(month == "10") return "Oct";
    return month;
}

void fixResults(const vector<string>& colummNames, query_result_t& results, 
                const unordered_map<string, string>& teamsMap) {
    for (auto& row : results) {
        auto c = 0;
        
        for(auto& col : colummNames) {
            auto oldVal = row[c];
            if(col == "month") {                
                row[c] = getMonth(oldVal);
            }
            else if(col == "team" || col == "_team") {
                if (teamsMap.count(oldVal) > 0)
                    row[c] = teamsMap.at(oldVal);
            }
            else if(col == "dow") {       
                row[c] = getDOW(oldVal);
            }
            else if(col == "game" || col == "_game") {
                cout << endl << col << " " << row[c];
            }

            if(row[c] != oldVal)
                cout << endl << oldVal << "->" << row[c];
            c++;
        }
    }
}

int handleParksRequest(sqlite3 *pdb, const string &qy, string& resp, string& mimeType) {
    string qry = "SELECT DISTINCT p.park_id, p.park_name," 
            "p.park_aka, p.park_city, p.park_state,"
            "p.park_open, p.park_close, p.park_league, p.notes"
            " FROM park p"
            " INNER JOIN (SELECT year, park FROM game_info) i"
            " ON p.park_id=i.park"
            " WHERE i.year > ?";
    
    auto yearSince = 1902;
    vector<field_val_t> prms;
    field_val_t fv;
    fv.setInt(yearSince);
    prms.push_back(fv);

    query_result_t result;
    vector<string> columnNames;
    int err = doQuery(pdb, qry, prms, result, columnNames, resp);
    if (err) return err;
    resp = makeJSONresponse(columnNames, result, result.size());
    mimeType = MIME_JSON;
    return 0;
}

int handleTeamsRequest(sqlite3 *pdb, const string &qy, string& resp, string& mimeType, 
                       unordered_map<string, string>& teamsMap ) {
    string qry = "SELECT DISTINCT t.team_id, t.team_league, t.team_city," 
                 "t.team_nickname, t.team_first, t.team_last " 
                 " FROM team t" 
                 " INNER JOIN (SELECT home_team FROM game_info2) i" 
                 " ON t.team_id=i.home_team WHERE t.team_last > ? ORDER BY t.team_last";
    
    auto yearSince = 1902;
    vector<field_val_t> prms;
    field_val_t fv;
    fv.setInt(yearSince);
    prms.push_back(fv);

    query_result_t result;
    vector<string> columnNames;
    int err = doQuery(pdb, qry, prms, result, columnNames, resp);
    for (auto& row : result) {
        if (teamsMap.count(row[0]) > 0) {
            cerr << endl << "duplicate team id=" << row[0];
        }
        teamsMap[row[0]] = row[3];
    }
    if (err) return err;
    resp = makeJSONresponse(columnNames, result, result.size());
    mimeType = MIME_JSON;
    return 0;
}

int handleGamelogRequest(sqlite3 *pdb, const string &qy, string& resp, string &mimeType,
                    const unordered_map<string, string>& teamsMap)
{
    string gmlog_qry;
    vector<field_val_t> prms;
    args_t args;
    cout << endl << "handleGamelogRequest( " << __LINE__ << "): calling buildSQLQuery() qy=" << qy;
    auto err = buildSQLQuery(qy, gmlog_qry, prms, resp, args);
    cout << endl << "handleGamelogRequest( " << __LINE__ << "): gmlog_qry=" << gmlog_qry;
    if(err) { 
        cerr << endl << "handleGamelogRequest( " << __LINE__ << "): buildSQLQuery failed err=";
        cerr << err;
        mimeType = MIME_TEXT;
        return 400;
    }
    query_result_t result;
    vector<string> columnNames;
    resp.clear();
    err = doQuery(pdb, gmlog_qry, prms, result, columnNames, resp);
    cout << endl << "handleGamelogRequest( " << __LINE__ << "): doQuery err=" << err;
    if (err) {
         cerr << endl << "handleGamelogRequest( " << __LINE__ << "): doQuery failed err=";
         cerr << err;
         mimeType = MIME_TEXT;
         return 500;
    }
    
    cout << endl << "handleGamelogRequest( " << __LINE__ << "): doQuery returned " << result.size() << " rows";

    auto retType = args.ret;
    try { 
        cout << endl << "handleGamelogRequest( " << __LINE__ << "): fixing results";
        fixResults(columnNames, result, teamsMap);
    } catch (std::exception e) {
        cerr << endl << "exception fixing results: " << e.what();
    }
    try {
        cout << endl << "handleGamelogRequest( " << __LINE__ << "): fixing column names";
        fixColumnNames(columnNames);
    } catch (std::exception e) {
        cerr << endl << "exception fixing column names: " << e.what();
    }
    cout << endl << "handleGamelogRequest( " << __LINE__ << "): retType=" << retType;
    if(retType == "json") {
        resp = makeJSONresponse(columnNames, result, args.limit);
        mimeType = MIME_JSON;
    }
    else if(retType == "html") {
        resp = renderHTMLTable(columnNames, result, args.retopts, args.limit);
        mimeType = MIME_HTML;
    } else {
        resp = "invalid ret '" + retType + "'";
        mimeType = MIME_TEXT;
        return 400;
    } 

    return 0;
}

int handlePlayerRequest(sqlite3 *pdb, const string &qy,
                        string& resp, string &mimeType,
                        NameTrie& playerLastTrie,
                        NameTrie& playerOtherTrie,
                        unordered_map<int, string>& playerIDMap)
{
    // initialize
    query_result_t result;
    vector<string> columnNames;
    int err = 0;
    resp.clear();
    if (playerIDMap.size() == 0) {
        auto qy = "SELECT name_last, name_other, player_num_id FROM player";
        err = doQuery(pdb, qy, {}, result, columnNames, resp);
        if(err) { 
            cerr << endl << "handlePlayerRequest( " << __LINE__ << "): doQuery failed err=";
            cerr << err;
            mimeType = MIME_TEXT;
            return 400;
        }
        for (const auto& row : result) {
            //cout << endl << "adding " << row[0] << " " << row[1];
            //cout << " " << row[2];
            int id = stoi(row[2]);
            auto last = string(row[0]);
            auto other = string(row[1]);
            //cout << endl << "last";
            addToTrie(playerLastTrie, last, id);
            //cout << endl << "first";
            addToTrie(playerOtherTrie, other, id);
            playerIDMap[id] = other + " " + last;
        }
    }
    auto idSet = std::set<int>();
    vector<string> s;
    s.push_back(qy);
    auto last = qy;
    auto first = qy;
    if(qy.find_first_of(',') != string::npos) {
        s = splitStr(qy, ',');
        last = s[0];
        first = s[1];
    }
    else if(qy.find_first_of(' ') != string::npos) {
        s = splitStr(qy, ' ');
        first = s[0];
        last = s[1];
    }

    cout << endl; printVec(s);
    if (last != first) {
        auto ids1 = findInTrie(playerLastTrie, last);
        auto ids2 = findInTrie(playerOtherTrie, first);
        
        // only add player if both first and last match
        for(auto x : ids1) {
            if (std::find(std::begin(ids2), std::end(ids2), x) != std::end(ids2))
                idSet.emplace(x);
        }
    }
    else {
        auto ids1 = findInTrie(playerLastTrie, qy);
        auto ids2 = findInTrie(playerOtherTrie, qy);
        // merge IDs
        idSet.insert(ids1.begin(), ids1.end());
        idSet.insert(ids2.begin(), ids2.end());
    }
    

    // build JSON response
    resp += "{ \"players\":[";
    for(auto id : idSet) 
        resp += "[\"" + playerIDMap[id] + "\", " + to_string(id) + "],";
    // remove last comma
    if (resp.back() == ',') 
        resp.pop_back();
    resp += "]}";
    mimeType = MIME_JSON;

    return 0;
}

int handlePlayerGameRequest(sqlite3 *pdb, const std::string &qy, std::string& resp, std::string &mimeType,
                            const std::unordered_map<std::string, std::string>& teamsMap )
{
    string player_qry;
    vector<field_val_t> prms;
    args_t args;
    cout << endl << "handlePlayerGameRequest( " << __LINE__ << "): calling buildPlayerGameSQLQuery() qy=" << qy;
    auto err = buildPlayerGameSQLQuery(qy, player_qry, prms, resp, args);
    cout << endl << "handlePlayerGameRequest( " << __LINE__ << "): player_qry=" << player_qry;
    if(err) { 
        cerr << endl << "handlePlayerGameRequest( " << __LINE__ << "): buildPlayerGameSQLQuery failed err=";
        cerr << err;
        return 400;
    }
    query_result_t result;
    vector<string> columnNames;
    resp.clear();
    err = doQuery(pdb, player_qry, prms, result, columnNames, resp);
    cout << endl << "handlePlayerGameRequest( " << __LINE__ << "): doQuery err=" << err;
    if (err) {
         cerr << endl << "handlePlayerGameRequest( " << __LINE__ << "): doQuery failed err=";
         cerr << err;
         mimeType = MIME_TEXT;
         return 500;
    }
    
    cout << endl << "handlePlayerGameRequest( " << __LINE__ << "): doQuery returned " << result.size() << " rows";

    auto retType = args.ret;
    try { 
        cout << endl << "handlePlayerGameRequest( " << __LINE__ << "): fixing results";
        fixResults(columnNames, result, teamsMap);
    } catch (std::exception e) {
        cerr << endl << "exception fixing results: " << e.what();
    }
    try {
        cout << endl << "handlePlayerGameRequest( " << __LINE__ << "): fixing column names";
        fixColumnNames(columnNames);
    } catch (std::exception e) {
        cerr << endl << "exception fixing column names: " << e.what();
    }
    cout << endl << "handlePlayerGameRequest( " << __LINE__ << "): retType=" << retType;
    if(retType == "json") {
        resp = makeJSONresponse(columnNames, result, args.limit);
        mimeType = MIME_JSON;
    }
    else if(retType == "html") {
        resp = renderHTMLTable(columnNames, result, args.retopts, args.limit);
        mimeType = MIME_HTML;
    } else {
        resp = "invalid ret '" + retType + "'";
        mimeType = MIME_TEXT;
        return 400;
    } 

    return 0;
}

int handleSituationRequest(sqlite3 *pdb, const std::string &qy, std::string& resp, std::string &mimeType,
                          const std::unordered_map<std::string, std::string>& teamsMap )
{
    string situation_qry;
    vector<field_val_t> prms;
    args_t args;
    cout << endl << "handleSituationRequest( " << __LINE__ << "): calling buildSituationSQLQuery() qy=" << qy;
    auto err = buildSituationSQLQuery(qy, situation_qry, prms, resp, args);
    cout << endl << "handleSituationRequest( " << __LINE__ << "): situation_qry=" << situation_qry;
    if(err) { 
        cerr << endl << "handleSituationRequest( " << __LINE__ << "): buildSituationSQLQuery failed err=";
        cerr << err;
        return 400;
    }
    query_result_t result;
    vector<string> columnNames;
    resp.clear();
    err = doQuery(pdb, situation_qry, prms, result, columnNames, resp);
    cout << endl << "handleSituationRequest( " << __LINE__ << "): doQuery err=" << err;
    if (err) {
         cerr << endl << "handleSituationRequest( " << __LINE__ << "): doQuery failed err=";
         cerr << err;
         return 500;
    }
    
    cout << endl << "handleSituationRequest( " << __LINE__ << "): doQuery returned " << result.size() << " rows";

    auto retType = args.ret;
    try { 
        cout << endl << "handleSituationRequest( " << __LINE__ << "): fixing results";
        fixResults(columnNames, result, teamsMap);
    } catch (std::exception e) {
        cerr << endl << "exception fixing results: " << e.what();
    }
    try {
        cout << endl << "handleSituationRequest( " << __LINE__ << "): fixing column names";
        fixColumnNames(columnNames);
    } catch (std::exception e) {
        cerr << endl << "exception fixing column names: " << e.what();
    }
    cout << endl << "handleSituationRequest( " << __LINE__ << "): retType=" << retType;
    if(retType == "json") {
        resp = makeJSONresponse(columnNames, result, args.limit);
        mimeType = MIME_JSON;
    }
    else if(retType == "html") {
        resp = renderHTMLTable(columnNames, result, args.retopts, args.limit);
        mimeType = MIME_HTML;
    } else {
        resp = "invalid ret '" + retType + "'";
        mimeType = MIME_TEXT;
        return 400;
    }

    return 0;                        
}
