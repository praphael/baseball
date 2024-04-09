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
    sqlite3_stmt *pstmt;;
    const char *pzTail;

    errMsg.clear();

    auto err = sqlite3_prepare_v2(pdb, qy.c_str(), qy.size(), &pstmt, &pzTail); 
    if (err != SQLITE_OK) {
        errMsg = "doQuery(" + to_string(__LINE__) + "): could not prepare query statement "s;
        cerr << std::endl << errMsg << err;
        return(1);
    }                             

    /* bind parametes */
    int c = 1;
    for (auto p : prms) {
        if (p.valType() == valType::INT) {
            err = sqlite3_bind_int(pstmt, c, p.asInt());
            if (err != SQLITE_OK) {
                errMsg = "doQuery(" + to_string(__LINE__) + "): sqlite3_bind_int failed err="s;
                errMsg += to_string(err)+ " c=" + to_string(c);
                cerr << endl << errMsg;
                return 1;
            }
        }
        else if (p.valType() == valType::STR) {
            auto s = p.asCharPtr();
            // TODO: investigate potential memory leak here
            err = sqlite3_bind_text(pstmt, c, s, strlen(s), SQLITE_TRANSIENT);
            if (err != SQLITE_OK) {
                errMsg = "doQuery(" + to_string(__LINE__) + "): sqlite3_bind_text() failed err="s;
                errMsg += to_string(err) + " c=" + to_string(c);
                cerr << endl << errMsg;
                return 2;
            }
        } else {
            errMsg = "doQuery(" + to_string(__LINE__) + "): unknown type "s + to_string(p.valType());
            cerr << endl << errMsg;
            return 3;  // unknown type
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
        cerr << endl << "doQuery no data qy='" << qy << "'";
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

sqlite3* initDB() {
    initTableInfo();
    sqlite3 *pdb, *pdb_mem;
    
    const auto qyTeams = std::string("SELECT * from teams");
    const auto qyParks = std::string("SELECT * from parks");
    auto err = sqlite3_open("baseball.db", &pdb);
    if(err != SQLITE_OK) {
        cerr << endl << "initDB: Could not open 'baseball.db', exiting";
        exit(1);
    }
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
    auto startYear = 1950;
    auto endYear = 1960;
    for (auto yr=startYear; yr<=endYear; yr++) {
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

string makeJSONresponse(vector<string> columnNames, query_result_t result) {
    string r;
    r += "{ \"headers\": [";
    for(auto c : columnNames) {
        r += "\"" + c + "\",";
    }
    r.pop_back();
    r += "], \"result\": [";
    for(auto row : result) {
        r += "[";
        for(auto fld : row) {
            r += "\"" + fld + "\",";
        }
        r.pop_back();
        r += "],";
    }
    r.pop_back();
    r += "]}";
    return r;
}

string make_dt_ms_str(int dt_ms) {
    return to_string(dt_ms);
}

void fixColumnNames(vector<string>& colummNames) {
    for(auto& col : colummNames) {
        cout << endl << "col= " << col;
        if(col.size() > 1) {
            
            // statistics with '_' replace with 'opp'
            if(col[0] == '_') {
                col.replace(0, 1, "opp");
            }
            // stats prepened with 'n' so SQL works
            else if(isNumberChar(col[1])) {
                // delete first char
                col.erase(col.begin());
            }
            else if (col == "dow") {
                col = "Day of Week";
            }
            else if (col == "homeoraway") {
                col = "Home/Away";
            }
            else {
                col[0] = toUpper(col[0]);
            }
        }
        cout << "->" << col;
    }
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
            else if(col == "team") {
                if (teamsMap.count(oldVal) > 0)
                    row[c] = teamsMap.at(oldVal);
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
            " FROM parks p"
            " INNER JOIN boxscore b"
            " ON p.park_id=b.park"
            " WHERE CAST(substr(p.park_open, 7) AS INTEGER) > ?";
    
    auto yearSince = 1902;
    vector<field_val_t> prms;
    field_val_t fv;
    fv.setInt(yearSince);
    prms.push_back(fv);

    query_result_t result;
    vector<string> columnNames;
    int err = doQuery(pdb, qry, prms, result, columnNames, resp);
    if (err) return err;
    resp = makeJSONresponse(columnNames, result);
    mimeType = "application/json";
    return 0;
}

int handleTeamsRequest(sqlite3 *pdb, const string &qy, string& resp, string& mimeType, 
                       unordered_map<string, string>& teamsMap ) {
    string qry = "SELECT DISTINCT t.team_id, t.team_league, t.team_city," 
                 "team_nickname, team_first, team_last " 
                 " FROM teams t" 
                 " INNER JOIN boxscore b" 
                 " ON t.team_id=b.home_team WHERE team_last > ? ORDER BY team_last";
    
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
        teamsMap[row[0]] = row[2] + " " + row[3];
    }
    if (err) return err;
    resp = makeJSONresponse(columnNames, result);
    mimeType = "application/json";
    return 0;
}

int handleBoxRequest(sqlite3 *pdb, const string &qy, string& resp, string &mimeType,
                    const unordered_map<string, string>& teamsMap) {
    string box_qry;
    vector<field_val_t> prms;
    json args;
    cout << endl << "handleBoxRequest( " << __LINE__ << "): calling buildSQLQuery()" << args;
    auto err = buildSQLQuery(qy, box_qry, prms, resp, args);
    cout << endl << "handleBoxRequest( " << __LINE__ << "): box_qry=" << box_qry;
    if(err) { 
        resp = "handleBoxRequest() buildSQLQuery failed: err=" + to_string(err);
        cerr << endl << "handleBoxRequest( " << __LINE__ << "): buildSQLQuery failed err=";
        cerr << err;
        return 400;
    }
    query_result_t result;
    vector<string> columnNames;
    resp.clear();
    err = doQuery(pdb, box_qry, prms, result, columnNames, resp);
    cout << endl << "handleBoxRequest( " << __LINE__ << "): doQuery err=" << err;
    if (err) {
         cerr << endl << "handleBoxRequest( " << __LINE__ << "): doQuery failed err=";
         cerr << err;
         return 500;
    }
    auto retType = string("html");

    cout << endl << "handleBoxRequest( " << __LINE__ << "): doQuery returned " << result.size() << " rows";
    if(args.contains("ret")) {
        retType = args["ret"];
    }
    try { 
        cout << endl << "handleBoxRequest( " << __LINE__ << "): fixing results";
        fixResults(columnNames, result, teamsMap);
    } catch (std::exception e) {
        cerr << endl << "exception fixing results: " << e.what();
    }
    try {
        cout << endl << "handleBoxRequest( " << __LINE__ << "): fixing column names";
        fixColumnNames(columnNames);
    } catch (std::exception e) {
        cerr << endl << "exception fixing column names: " << e.what();
    }
    cout << endl << "handleBoxRequest( " << __LINE__ << "): retType=" << retType;
    if(retType == "json") {
        resp = makeJSONresponse(columnNames, result);
    }
    else if(retType == "html") {
        auto opts = string("");
        if(args.contains("retopt"))
            opts = args["retopt"].get<string>();
        resp = renderHTMLTable(columnNames, result, opts);
    } 
    mimeType = "application/json";

    return 0;
}

/*
# make header for table
        hdr = selectFieldsH
        for st in statList:
            hdr.append(st)

        # rename fields which started with '_' or number
        for i in range(len(hdr)):
            if hdr[i] == "homeoraway":
                hdr[i] = "Home/Away"
            elif hdr[i][0] == "n" and isNumberChar(hdr[i][1]):
                hdr[i] = hdr[i][1:]
            elif hdr[i][0] == "_":
                hdr[i] = "opp" + hdr[i][1:]
            else:
                h = hdr[i][1:]
                hdr[i] = toUpper(hdr[i][0]) + h

        # fix month from number to string value
        if "Month" in hdr or "Team" in hdr:
            monthIdx = -1
            teamIdx = -1
            if "Month" in hdr:
                monthIdx = hdr.index("Month")
            if "Team" in hdr:
                teamIdx = hdr.index("Team")
            if teamIdx >= 0 and not hasattr(app, 'team_name'):
                get_teams()
            i = 0
            for t in r:
                r2 = list(t)
                if monthIdx >= 0:
                    month = calendar.month_name[t[monthIdx]]
                    r2[monthIdx] = month
                if t[teamIdx] in app.team_names:
                    team = app.team_names[t[teamIdx]]
                    r2[teamIdx] = team

                r[i] = tuple(r2)
                i += 1
            #print("r(fixed month)=", r)

        ret = "json"
        if "ret" in args:
            ret = args.get("ret")
        print("ret=", ret)*/