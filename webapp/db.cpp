#include <iostream>
#include <cstring>
#include <sstream>

#include "db.h"
#include "baseball_tables.h"


using std::string;
using std::vector;
using std::cout;
using std::endl;
using std::unordered_map;
using std::to_string;

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
        std::cout << std::endl << "could not prepare insert statement " << err;
        exit(1);
    }                             

    //std::cout << std::endl << "sqlite3_prepare_v2 err=" << err;
    err = sqlite3_step(pstmt);
    if (err != SQLITE_ROW) {
        std::cout << std::endl << "sqlite3_step() err=" << err;
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
                            std::cout << std::endl << "sqlite3_bind_null failed err=" << err << " c=" << c;
                            exit(1);
                        }
                    }
                    else {
                        auto n = sqlite3_column_int(pstmt, c);
                        ins_s += std::to_string(n);
                        err = sqlite3_bind_int(instmt, c+1, n);
                        if (err != SQLITE_OK) {
                            std::cout << std::endl << "sqlite3_bind_int failed err=" << err << " c=" << c;
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
                            std::cout << std::endl << "sqlite3_bind_null failed err=" << err << " c=" << c;
                            exit(1);
                        }
                    }
                    else {
                        auto txt = reinterpret_cast<const char*>(r);
                        auto s = std::string(txt);
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
                            std::cout << std::endl << "sqlite3_bind_text failed err=" << err << " c=" << c;
                            std::cout << std::endl << " s=" << s;
                            std::cout << std::endl << " ins_s=" << ins_s;
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
                std::cout << std::endl << "could not prepare err=" << err << " row=" << row;
                exit(1);
            }
            err = sqlite3_step(ins_stmt);
            if (err != SQLITE_DONE) {
                std::cout << std::endl << "could not insert err=" << err << " row=" << row;
                std::cout << std::endl << " ins_s=" << ins_s;
                exit(1);
            }
            sqlite3_finalize(ins_stmt);

            err = sqlite3_reset(instmt);
            // if (row > 220000) std::cout << std::endl << "fetched row=" << row;
            row++;
        } else {
            std::cout << "could not get row i=" << i << " row=" << row;
            std::cout << " err=" << err;
        }      

        //std::cout << std::endl << "calling sqlite3_step";
        err = sqlite3_step(pstmt);
        i++;
    }
    std::cout << std::endl << "done fetched " << row << " rows" << std::endl;
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
        errMsg = "could not prepare query statement ";
        std::cout << std::endl << errMsg << err;
        return(1);
    }                             

    /* bind parametes */
    int c = 1;
    for (auto p : prms) {
        if (p.valType() == field_val_t::INT) {
            err = sqlite3_bind_int(pstmt, c, p.asInt());
            if (err != SQLITE_OK) {
                errMsg = "sqlite3_bind_int failed err=" + to_string(err)+ " c=" + to_string(c);
                cout << endl << errMsg;
                return 1;
            }
        }
        else if (p.valType() == field_val_t::STR) {
            auto s = p.asCharPtr();
            // TODO: investigate potential memory leak here
            err = sqlite3_bind_text(pstmt, c+1, s, strlen(s), SQLITE_TRANSIENT);
            if (err != SQLITE_OK) {
                cout << endl << "sqlite3_bind_text() failed err=" << err << " c=" << c;
                return 2;
            }
        } else {
            return 3;  // unknown type
        }
        c++; 
    }
    //std::cout << std::endl << "sqlite3_prepare_v2 err=" << err;
    err = sqlite3_step(pstmt);
    if (err != SQLITE_ROW) {
        std::cout << std::endl << "sqlite3_step() err=" << err;
        return(4);
    }

    result.clear();
    columnNames.clear();
    int row = 0;
    int i = 0;
    while (err != SQLITE_DONE) {
        vector<string> r;
        //std::cout << std::endl;
        // err = sqlite3_prepare_v2(pdb_mem, qy.c_str(), qy.size(), &pstmt, &pzTail); 
        if (err == SQLITE_ROW) {
            auto numCols = sqlite3_column_count(pstmt);
            for(int c=0; c<numCols; c++) {
                if(row == 1)
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
                    cout << endl << errMsg;
                    return 5;
                }
            }
            result.push_back(r);
            row++;
        }
        err = sqlite3_step(pstmt);
        if(err != SQLITE_ROW || err != SQLITE_DONE) {
            std::cout << endl << "could not get row i=" << i << " row=" << row << " err=" << err;
        }      
        i++;
    }
    cout << endl << "done fetched " << row << " rows" << std::endl;
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
        std::cout << std::endl << "Could not open 'baseball.db', exiting";
        exit(1);
    }
    err = sqlite3_open(":memory:", &pdb_mem);
    if(err != SQLITE_OK) {
        std::cout << std::endl << "Could not open memory db, exiting";
        exit(1);
    }
    char *errMsg = new char[256];
    err = sqlite3_exec(pdb_mem, CREATE_PARKS, nullptr, nullptr, &errMsg);
    if(err != SQLITE_OK) {
        std::cout << std::endl << "Could not create table 'parks";
        exit(1);
    }
    err = sqlite3_exec(pdb_mem, CREATE_TEAMS, nullptr, nullptr, &errMsg);
    if(err != SQLITE_OK) {
        std::cout << std::endl << "Could not create table 'teams";
        exit(1);
    }
    err = sqlite3_exec(pdb_mem, CREATE_BOXSCORE, nullptr, nullptr, &errMsg);
    if(err != SQLITE_OK) {
        std::cout << std::endl << "Could not create table 'boxscore";
        exit(1);
    }
    copyTable(pdb, qyTeams, teamsCol, "teams", pdb_mem, 600);
    copyTable(pdb, qyParks, parksCol, "parks", pdb_mem, 1000);
    auto startYear = 1950;
    auto endYear = 1960;
    for (auto yr=startYear; yr<=endYear; yr++) {
        auto qyBox = std::string("SELECT * from boxscore WHERE CAST(substr(game_date,0,5) AS INTEGER) == ") + std::to_string(yr);
        std::cout << std::endl << "getting year" << yr;
        copyTable(pdb, qyBox, boxCol, "boxscore", pdb_mem, 100000);
    }

    std::cout << std::endl << "closing db";
    sqlite3_close(pdb);
    std::cout << std::endl << "done";

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

int handleParksRequest(sqlite3 *pdb, const string &qy, string& resp) {
    string qry = "SELECT * FROM parks";
    query_result_t result;
    vector<field_val_t> prms;
    vector<string> columnNames;
    int err = doQuery(pdb, qry, prms, result, columnNames, resp);
    if (err) return err;
    resp.clear();
    for(auto c : columnNames)
        resp.insert(resp.end(), c.begin(), c.end());
    for(auto row : result) {
        resp.push_back('\n');
        for (auto c : row) {
            resp.insert(resp.end(), c.begin(), c.end());
        }
    }
    return 0;
}

int handleTeamsRequest(sqlite3 *pdb, const string &qy, string& resp) {
    string qry = "SELECT * FROM teams";
    query_result_t result;
    vector<field_val_t> prms;
    vector<string> columnNames;
    int err = doQuery(pdb, qry, prms, result, columnNames, resp);
    if (err) return err;
    resp.clear();
    for(auto c : columnNames)
        resp.insert(resp.end(), c.begin(), c.end());
    for(auto row : result) {
        resp.push_back('\n');
        for (auto c : row) {
            resp.insert(resp.end(), c.begin(), c.end());
        }
    }
    return 0;
}

int handleBoxRequest(sqlite3 *pdb, const string &qy, string& resp, string &mimeType) {
    unordered_map<string, string> args;
    auto err = makeArgMap(qy, args);
    if(err) {
        resp = "error parsing arguments";
        cout << endl << resp;
        return 400;
    }

    string box_qry;
    vector<field_val_t> prms;
    err = buildSQLQuery(args, box_qry, prms, resp);
    if(err) return 400;
    query_result_t result;
    vector<string> columnNames;
    err = doQuery(pdb, box_qry, prms, result, columnNames, resp);
    if (err) return 500;
    auto retType = string("html-bs");
    if(args.count("ret") > 0) {
        retType = args.at("ret");
    }
    auto retTvec = splitStr(retType, '-');
    if(retTvec[0] == "json") {

    }
    else if(retTvec[0] == "html") {
        auto opts = string("");
        if(retTvec.size() > 1) opts = retTvec[1];
        resp = renderHTMLTable(columnNames, result, opts);
    }
    
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