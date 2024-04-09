import { doRequest } from "./requests.js";

const filterFields=[["Year", "year"], ["Month", "month"],
                    ["Team", "team"], ["Home/Away", "homeaway"],
                    ["Day", "dow"], ["League", "league"],
                    ["Park", "park"], ["Date", "date"],
                    ["Games played", "gp"]]
//const teamIdxMap = new Map();
//for(let i=0; i<teams.length; i++) teamIdxMap[teams[i][0]] = i;

const months = [["March", 3], ["April", 4], ["May", 5], 
                ["June", 6], ["July", 7], ["August", 8], 
                ["September", 9], ["October", 10]];
//const monthIdxMap = new Map();
//for(let i=0; i<months.length; i++) monthIdxMap[teams[i][0]] = i;

const daysOfWeek = [["Sun", "Sun"], ["Mon", "Mon"], ["Tue", "Tue"], ["Wed", "Wed"],
                    ["Thu", "Thu"], ["Fri", "Fri"], ["Sat", "Sat"]];
//const dayOfWeekIdxMap = new Map();
//for(let i=0; i<daysOfWeek.length; i++) dayOfWeekIdxMap[daysOfWeek[i][0]] = i;
const league = [["American", "AL"], ["National", "NL"]]
const homeAway = [["Home", "home"], ["Away", "away"]]

// get park info
const lastYear = 1903

async function getParksTeams() {
    const parks = [];
    const teams = [];
    const r = await doRequest(`/parks?since=${lastYear}`, "GET", null, null, "json", "", (err)=>{
        console.log("could not fetch park data status=", err.status, " error=", err.error);
    });

    if(r != null) {
        console.log("r.result (0..5)=", r.result.slice(0, 5));
        r.result.map((v) => { 
            const parkId = v[0]; 
            const openYear = v[5].slice(6);
            let closeYear=""
            if (v[6] != null)
                closeYear = v[6].slice(6);
            const parkName = `${v[1]} (${v[3]}, ${v[4]} ${openYear}-${closeYear})`;
            parks.push([parkName, parkId]);
        })
        parks.sort();
    }

    // get team info
    const r2 = await doRequest(`/teams?since=${lastYear}`, "GET", null, null, "json", "", (err)=>{
        console.log("could not fetch park data status=", err.status, " error=", err.error);
    });

    if(r2 != null) {
        console.log("r2.result (0..5)=", r2.result.slice(0, 5));
        r2.result.map((v) => { 
            const tmId = v[0];
            const tmName= `${v[2]} ${v[3]} (${v[1]} ${v[4]}-${v[5]})`
            //console.log(tmId, " ", tmName);
            teams.push([tmName, tmId]);
        })
        teams.sort();
    }

    return {parks, teams};
}

// default to empty until we fetch
const parks = [];
const teams = [];
const boxScoreFiltOptsDefaults = { teams, months, daysOfWeek, homeAway, league, parks };
//const boxScoreIdxMaps = { teamIdxMap, monthIdxMap, dayOfWeekIdxMap }

const boxScoreFiltDefaults = {
    values: new Map(),
    group: new Set(),
    agg: "sum"  // aggregation ("sum", "avg", "no")
}
boxScoreFiltDefaults.values.set("team", "BAL");
boxScoreFiltDefaults.values.set("year", "2019");
boxScoreFiltDefaults.values.set("month", "");
boxScoreFiltDefaults.values.set("park", "");
boxScoreFiltDefaults.values.set("dow", "");
boxScoreFiltDefaults.values.set("homeaway", "");
boxScoreFiltDefaults.values.set("league", "");
boxScoreFiltDefaults.group.add("month");

const orderDefaults = [["team", true], ["year", false], ["date", false]]

export {boxScoreFiltOptsDefaults, boxScoreFiltDefaults, filterFields, orderDefaults, getParksTeams}; //}, boxScoreIdxMaps};