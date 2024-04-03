const teams = [["BAL", "Baltimore Orioles"], ["NYY", "New York Yankees"]];
//const teamIdxMap = new Map();
//for(let i=0; i<teams.length; i++) teamIdxMap[teams[i][0]] = i;

const months = [["March", 3], ["Apr", 4], ["May", 5], ["June", 6], ["July", 7], ["August", 8],
                ["September", 9], ["October", 10]];
//const monthIdxMap = new Map();
//for(let i=0; i<months.length; i++) monthIdxMap[teams[i][0]] = i;

const daysOfWeek = [["Sun", "Sun"], ["Mon", "Mon"], ["Tue", "Tue"], ["Wed", "Wed"],
                    ["Thu", "Thu"], ["Fri", "Fri"], ["Sat", "Sat"]];
//const dayOfWeekIdxMap = new Map();
//for(let i=0; i<daysOfWeek.length; i++) dayOfWeekIdxMap[daysOfWeek[i][0]] = i;

const boxScoreFiltOpts = { teams, months, daysOfWeek };
//const boxScoreIdxMaps = { teamIdxMap, monthIdxMap, dayOfWeekIdxMap }

const boxScoreFiltDefaults = {
    values: new Map(),
    group: new Set(),
    agg: "sum"  // aggregation ("sum", "avg", "no")
}
boxScoreFiltDefaults.values.set("team", "BAL");
boxScoreFiltDefaults.values.set("year", "2021");
boxScoreFiltDefaults.group.add("month");

export {boxScoreFiltOpts, boxScoreFiltDefaults}; //}, boxScoreIdxMaps};