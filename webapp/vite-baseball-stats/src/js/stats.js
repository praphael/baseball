const statTypesArr = [["Runs", "R"], ["Hits", "H"], 
                      ["Walks", "BB"], ["Errors", "E"], 
                      ["Home Runs", "HR"], ["At Bats", "AB"],
                      ["Doubles", "2B"], ["Triples", "3B"], 
                      ["Runs Batted In", "RBI"], ["Sacrifice Hits", "SH"],
                      ["Sacrice Flies", "SF"], ["Hit By Pitch", "HBP"],
                      ["Intentional Walks", "IBB"], ["Strikeouts", "K"],
                      ["Stolen Bases", "SB"], ["Caught Stealing", "CS"], 
                      ["Ground Into Double Play","GIDP"], 
                      ["Catcher Interference", "CI"],
                      ["Left on Base", "LOB"], ["Indiv Earned Runs", "ERI"],
                      ["Team Earned Runs", "ERT"], ["Wild Pitches", "WP"],
                      ["Balks", "BLK"], ["Putouts", "PO"],
                      ["Assists", "A"], ["Passed Balls", "PB"],
                      ["Double Plays", "DP"], ["Triple Plays","TP"]]

// sorting order for display in tables
const statSortOrder = [];
statSortOrder["R"] = 0;
statSortOrder["H"] = 1;
statSortOrder["BB"] = 2;
statSortOrder["E"] = 3;
statSortOrder["AB"] = 4;
statSortOrder["K"] = 5;
statSortOrder["2B"] = 6;
statSortOrder["3B"] = 7;
statSortOrder["HR"] = 8;
statSortOrder["RBI"] = 9;
statSortOrder["SH"] = 10;
statSortOrder["SF"] = 11;
statSortOrder["IBB"] = 12;
statSortOrder["HBP"] = 13;
statSortOrder["LOB"] = 14;
statSortOrder["SB"] = 15;
statSortOrder["CS"] = 16;
statSortOrder["GIDP"] = 17;
statSortOrder["CI"] = 18;
statSortOrder["ERI"] = 19;
statSortOrder["ERT"] = 20;
statSortOrder["WP"] = 21;
statSortOrder["PB"] = 22;
statSortOrder["DP"] = 23;
statSortOrder["TP"] = 24;
statSortOrder["BLK"] = 25;
statSortOrder["PO"] = 26;
statSortOrder["A"] = 27;

const gamebox = ["R", "H", "BB", "E", 
                "_R", "_H", "_BB", "_E"]
const off1 = ["R", "H", "BB", "K", 
              "RBI", "2B", "3B", "HR"]
const off2 = ["AB", "SB", "CS", "SH", 
              "SF", "LOB", "IBB", "LOB"]
const pitch1 = ["_R", "ERI", "ERT", "_H", 
                "_BB", "_K"]
const pitch2 = ["_2B", "_3B", "_HR", "_AB",
                 "WP", "BLK", "_HBP"]
const def = [ "PB", "DP", "TP", "PO", 
              "A", "_SB", "_CS", "CI"]

const statSetsDefault = new Map()
statSetsDefault.set("Game Box", new Set(gamebox));
statSetsDefault.set("Offense 1", new Set(off1));
statSetsDefault.set("Offense 2", new Set(off2));
statSetsDefault.set("Pitching 1", new Set(pitch1));
statSetsDefault.set("Pitching 2", new Set(pitch2));
statSetsDefault.set("Fielding", new Set(def));

export { statTypesArr, statSetsDefault, statSortOrder }