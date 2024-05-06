import { doRequest } from "./requests.js";

const filterFields=[["Year", "year"], ["Month", "month"],
                    ["Team", "team"], ["Home/Away", "homeaway"],
                    ["Day", "dow"], ["League", "league"],
                    ["Park", "park"], ["Date", "date"],
                    ["Games played", "gp"], ["Won", "won"],
                    ["Lost", "lost"], ["Record", "rec"],
                    ["Season", "season"], ["Playoff round", "postseries"],
                    ["Day/Night", "daynight"], ["Field condition", "fieldcond"],
                    ["Precipitation", "precip"], ["Sky", "sky"],
                    ["Wind direction", "winddir"], ["Temperature", "temp"],
                    ["Windspeed", "windspeed"]];
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

const season = [["Regular", "Reg"], ["Post", "Post"]]
const postseries = [["Wildcard","Wildcard"], ["Division","Division"], ["League","League"],
                    ["World Series","World Series"], ["Playoff tiebreak","Playoff tiebreak"]]

const daynight = [["Day", "Day"], ["Night", "Night"]]
const fieldcond = [["Dry", "Dry"], ["Damp", "Damp"], ["Wet","Wet"], ["Soaked", "Soaked"]]
const precip = [["None","None"], ["Drizzle","Drizzle"], ["Rain","Rain"], ["Showers","Showers"], ["Snow", "Snow"]]
const sky = [["Sunny","Sunny"], ["Cloudy","Cloudy"], ["Overcast","Overcast"], ["Dome","Dome"], ["Night", "Night"]]
const winddir = [["From CF","From CF"], ["From LF","From LF"],["From RF","From RF"],
                 ["RF to LF","RF to LF"], ["To CF","To CF"], ["To LF","To LF"], ["To RF","To RF"]  ]
const temp = []
for (let t=40; t<=100; t++) temp.push([t.toString(), t.toString()]);
const windspeed = []
for (let ws=0; ws<=30; ws++) windspeed.push([ws.toString(), ws.toString()]);

const firstYear = 1901;
const lastYear = 2023;
const years = [];
for (let yr=firstYear; yr<=lastYear; yr++) years.push([yr.toString(), yr.toString()]);

/* "batter", "pitcher", "batter_team", "pitcher_team",
"fielder", "sit_inn", "sit_innhalf", "sit_outs",
"sit_bat_tm_sco", "sit_pit_tm_sco", "sit_sco_diff", 
"sit_bases", "sit_base_1", "sit_base_2", "sit_base_3", 
"sit_bat_cnt", "sit_play_res", "sit_play_base",
"sit_play_res2", "sit_play_base2", "sit_play_res3",
"sit_play_base3", "sit_hit_loc", "sit_hit_type",
"sit_outs_made", "sit_runs_sco" */

const innings = [];
for (let inn=1; inn<=25; inn++) innings.push([inn.toString(), inn.toString()]);
const inning_halves = [["Top", "T"], ["Bottom", "B"]];
const outs = []; 
for (let o=0; o<=2; o++) outs.push([o.toString(), o.toString()]);
const sco_diff = [];
for (let d=-4; d<=4; d++) sco_diff.push([d.toString(), d.toString()]);
const sit_bases = [["Empty", "empty"], ["First", "first"], ["First+Second", "firstsecond"], ["Scoring position", "risp"], ["Loaded", "loaded"] ];
const bat_cnt = [["0-0", "00"], ["0-1", "01"], ["0-2", "02"],
                     ["1-0", "10"], ["1-1", "11"], ["1-2", "12"], 
                     ["2-0", "20"], ["2-1", "21"], ["2-2", "22"],
                     ["3-0", "30"], ["3-1", "31"], ["3-2", "32"]] 
const play_res = [["Walk", "BB"], ["Intentional walk", "IBB"],
                  ["Single", "S"], ["Double", "D"],
                  ["Ground rule double", "DGR"], ["Triple", "T"],
                  ["Home run", "HR"], ["Out", "O"], ["Force out", "FO"],
                  ["Fielders choice", "FC"], ["Hit by pitch", "HBP"],
                  ["Strikeout", "K"], ["Error", "E"], ["Balk", "BK"],
                  ["Wild pitch", "WP"], ["Pick off", "PO"],
                  ["Stolen base", "SB"], ["Caught stealing", "CS"],
                  ["Passed ball", "PB"], ["Error on foul ball", "FLE"],
                  ["Pick off/caught stealing", "POCS"], ["Other advance", "OA"],
                  ["Defensive indifference", "DI"], ["Catcher interference", "CI"]];
const hit_loc = [];
const hit_type = [["Pop up", "P"], ["Ground ball", "G"],
                  ["Fly ball", "F"], ["Line drive", "L"] ];
const outs_made = [];
for (let o=0; o<=3; o++) outs_made.push([o.toString(), o.toString()]);
const runs_sco = [];
for (let r=0; r<=4; r++) runs_sco.push([r.toString(), r.toString()]);

// get park info
async function getParksTeams() {
    const parks = [];
    const teams = [];
    const r = await doRequest(`/parks?since=${firstYear}`, "GET", null, null, "json", "", (err)=>{
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
    const r2 = await doRequest(`/teams?since=${firstYear}`, "GET", null, null, "json", "", (err)=>{
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
const boxScoreFiltOptsDefaults = { teams, years, months, daysOfWeek, homeAway, league, parks,
    season, postseries, daynight, fieldcond, precip, sky, winddir, windspeed, temp,
    innings, inning_halves, outs, sco_diff, sit_bases, bat_cnt,
    play_res, hit_loc, hit_type, outs_made, runs_sco }

//const boxScoreIdxMaps = { teamIdxMap, monthIdxMap, dayOfWeekIdxMap }

const boxScoreFiltDefaults = {
    values: new Map(),
    group: new Set(),
    agg: "sum"  // aggregation ("sum", "avg", "no")
}
boxScoreFiltDefaults.values.set("team", "");
boxScoreFiltDefaults.values.set("_team", "");
boxScoreFiltDefaults.values.set("year_low", "2022");
boxScoreFiltDefaults.values.set("year_high", "2022");
boxScoreFiltDefaults.values.set("month", "");
boxScoreFiltDefaults.values.set("park_id", "");
boxScoreFiltDefaults.values.set("dow", "");
boxScoreFiltDefaults.values.set("homeaway", "");
boxScoreFiltDefaults.values.set("game_low", "");
boxScoreFiltDefaults.values.set("game_high", "");
boxScoreFiltDefaults.values.set("league", "");
boxScoreFiltDefaults.values.set("_league", "");
boxScoreFiltDefaults.values.set("season", "");
boxScoreFiltDefaults.values.set("round", "");
boxScoreFiltDefaults.values.set("daynight", "");
boxScoreFiltDefaults.values.set("fieldcond", "");
boxScoreFiltDefaults.values.set("precip", "");
boxScoreFiltDefaults.values.set("sky", "");
boxScoreFiltDefaults.values.set("temp_low", "");
boxScoreFiltDefaults.values.set("temp_high", "");
boxScoreFiltDefaults.values.set("winddir", "");
boxScoreFiltDefaults.values.set("windspeed_low", "");
boxScoreFiltDefaults.values.set("windspeed_high", "");
boxScoreFiltDefaults.values.set("batter", "");
boxScoreFiltDefaults.values.set("pitcher", "");
boxScoreFiltDefaults.values.set("sit_inn_low", "");
boxScoreFiltDefaults.values.set("sit_inn_high", "");
boxScoreFiltDefaults.values.set("sit_innhalf", "");
boxScoreFiltDefaults.values.set("sit_outs_low", "");
boxScoreFiltDefaults.values.set("sit_outs_high", "");
boxScoreFiltDefaults.values.set("sit_sco_diff_low", "");
boxScoreFiltDefaults.values.set("sit_sco_diff_high", "");
boxScoreFiltDefaults.values.set("sit_bases ", "");
boxScoreFiltDefaults.values.set("sit_bat_cnt", "");
boxScoreFiltDefaults.values.set("sit_play_res", "");
boxScoreFiltDefaults.values.set("sit_hit_loc", "");
boxScoreFiltDefaults.values.set("sit_hit_type", "");
boxScoreFiltDefaults.values.set("sit_outs_made", "");
boxScoreFiltDefaults.values.set("sit_runs_sco", "");
boxScoreFiltDefaults.group.add("team");

const orderDefaults = [["team", false], ["year", true], ["date", false]]

export {boxScoreFiltOptsDefaults, boxScoreFiltDefaults, filterFields, orderDefaults, getParksTeams}; //}, boxScoreIdxMaps};