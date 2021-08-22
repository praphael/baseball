#!/usr/bin/python3

import csv
import os
import re

fileInfoMap = dict()
fileInfoMap["AllstarFull.csv"] = { "idx_str" : [0, 3, 4, 5], "idx_date" : []}
fileInfoMap["Appearances.csv"] = { "idx_str" : [1, 2, 3], "idx_date" : [] }
fileInfoMap["AwardsManagers.csv"] = { "idx_str" : [0, 1, 3, 4, 5], "idx_date" : [] }
fileInfoMap["AwardsPlayers.csv"] = { "idx_str" : [0, 1, 3, 4, 5], "idx_date" : [] }
fileInfoMap["AwardsShareManagers.csv"] = { "idx_str" : [0, 2, 3], "idx_date" : [] }
fileInfoMap["AwardsSharePlayers.csv"] = { "idx_str" : [0, 2, 3], "idx_date" : [] }

fileInfoMap["Batting.csv"] = { "idx_str" : [0, 3, 4], "idx_date" : [] }
fileInfoMap["BattingPost.csv"] = { "idx_str" : [1, 2, 3, 4], "idx_date" : [] }
fileInfoMap["CollegePlaying.csv"] = { "idx_str" : [0, 1], "idx_date" : [] }

fileInfoMap["Fielding.csv"] = { "idx_str" : [0, 3, 4, 5], "idx_date" : [] }
fileInfoMap["FieldingOF.csv"] = { "idx_str" : [0], "idx_date" : [] }
fileInfoMap["FieldingOFsplit.csv"] = { "idx_str" : [0, 3, 4, 5], "idx_date" : [] }
fileInfoMap["FieldingPost.csv"] = { "idx_str" : [0, 2, 3, 4, 5], "idx_date" : [] }

fileInfoMap["HallOfFame.csv"] = { "idx_str" : [0, 2, 7], "idx_date" : [] }
fileInfoMap["HomeGames.csv"] = { "idx_str" : [1, 2, 3], "idx_date" : [4, 5] }
fileInfoMap["Managers.csv"] = { "idx_str" : [0, 2, 3, 10], "idx_date" : [] } 
fileInfoMap["ManagersHalf.csv"] =  { "idx_str" : [0, 2, 3], "idx_date" : [] }

fileInfoMap["Parks.csv"] = { "idx_str" : [0, 1, 2, 3, 4, 5], "idx_date" : [] }
#playerID,birthYear,birthMonth,birthDay,birthCountry,birthState,birthCity,deathYear,deathMonth,deathDay,deathCountry,deathState,deathCity,nameFirst,nameLast,nameGiven,weight,height,bats,throws,debut,finalGame,retroID,bbrefID
fileInfoMap["People.csv"] = { "idx_str" : [0, 4, 5, 6, 10, 11, 12, 13, 14, 15, 18, 19, 22, 23], "idx_date" : [20, 21]}
fileInfoMap["Pitching.csv"] = { "idx_str" : [0, 3, 4], "idx_date" : [] }
fileInfoMap["PitchingPost.csv"] = { "idx_str" : [0, 2, 3, 4], "idx_date" : [] }

fileInfoMap["Salaries.csv"] = { "idx_str" : [0, 1, 2, 3], "idx_date" : [] }
fileInfoMap["Schools.csv"] = { "idx_str" : [0, 1, 2, 3, 4, 5], "idx_date" : [] }
fileInfoMap["SeriesPost.csv"] = { "idx_str" : [1, 2, 3, 4, 5], "idx_date" : [] }
fileInfoMap["Teams.csv"] = { "idx_str" : [1, 2, 3, 4, 40, 41, 45, 46, 47], "idx_date" : [] }
fileInfoMap["TeamsFranchises.csv"] = { "idx_str" : [0, 1, 2, 3], "idx_date" : [] }
fileInfoMap["TeamsHalf.csv"] = { "idx_str" : [1, 2, 4, 5], "idx_date" : [] }


coreDir = "baseballdatabank-master/core"

for fName, info in fileInfoMap.items():
    # don't know how to parse this file yet
    if info is None:
        continue
    fPath = os.path.join(coreDir, fName)
    r = re.split("\.", fName)
    tbl_name = r[0] 
    outpath = f"{tbl_name}.sql"
    fout = open(outpath, "wt")
    if fout is None:
        print(f"could not open file '{outpath}'")
        continue

    with open(fPath, "r") as fin:
        rdr = csv.reader(fin, delimiter=',', quotechar='"')
        hdr = None
        for row in rdr:
            if hdr is None:
                hdr = row
            else:
                fout.write(f"INSERT INTO {tbl_name} VALUES(")
                i = 0
                for v in row:
                    # if a string value, surround with quotes
                    if len(v) == 0:
                        fout.write("NULL")
                    elif i in info["idx_str"]:
                        fout.write(f'"{v}"')
                    else:
                        fout.write(f'{v}')
                    i += 1
                    if i < len(row):
                        fout.write(", ")
                    
                fout.write(")\n")
            
            
        
    
