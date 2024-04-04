import { doRequest } from "./requests.js";

const teams = [
    ["Arizona Diamondbacks", "ARI"],
    ["Atlanta Braves", "ATL"],
    ["Baltimore Orioles", "BAL"],
    ["Boston Red Sox", "BOS"],
    ["Chicago White Sox", "CWS"],
    ["Chicago Cubs", "CHC"],
    ["Cincinnati Reds", "CIN"],
    ["Cleveland Guardians", "CLE"],
    ["Colorado Rockies", "COL"],
    ["Detroit Tigers", "DET"],
    ["Houston Astros", "HOU"],
    ["Kansas City Royals", "KC"],
    ["Los Angeles Angels", "LAA"],
    ["Los Angeles Dodgers", "LAD"],
    ["Miami Marlins", "MIA"],
    ["Milwaukee Brewers", "MIL"],
    ["Minnesota Twins", "MIN"],
    ["New York Yankees", "NYY"],
    ["New York Mets", "NYM"],
    ["Oakland Athletics", "OAK"],
    ["Philadelphia Phillies", "PHI"],
    ["Pittsburgh Pirates", "PIT"],
    ["San Diego Padres", "SD"],
    ["San Francisco Giants", "SF"],
    ["Seattle Mariners", "SEA"],
    ["St. Louis Cardinals", "STL"],
    ["Tampa Bay Rays", "TB"],
    ["Texas Rangers", "TEX"],
    ["Toronto Blue Jays", "TOR"],
    ["Washington Nationals", "WSH"]
  ];
  
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
const r = await doRequest("/parks?since=1920", "GET", null, null, "json", "", (err)=>{
    console.log("could not fetch park data status=", err.status, " error=", err.error);
});
const parks=[]
if(r != null) {
    console.log("r=", r)
    r.result.map((v) => { 
        parks.push([v[1], v[0]])
    })
}

const boxScoreFiltOpts = { teams, months, daysOfWeek, homeAway, league, parks };
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