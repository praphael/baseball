import { statSortOrder } from "./stats";

function makeQueryJSONBase(filter, agg, statTypes, order, minGP, limit) {
    let qy = {};
    let skip = false;
    filter.values.forEach((v, k) => {
        console.log("makeQueryJSON", k, v);
        if(typeof(v) == typeof(""))
            v = v.trim();
        skip = false;
        if(filter.query == "gamelog" || filter.query == "playergame") {
            if (k.startsWith("sit_"))
                skip = true;
            else if (filter.query == "gamelog" && (k == "batter" || k == "pitcher")) 
                skip = true;
        }

        if (!skip) {
            // extract id (number between parentheses)
            if (k == "batter" || k == "pitcher") {
                const idx1 = v.indexOf("(");
                const idx2 = v.indexOf(")");
                if(idx1 >= 0 && idx2 >= 0) {
                    v = parseInt(v.substr(idx1+1, idx2-idx1-1));
                    // for playergame fielding queries, interpret batter as fielder
                    if(k == "batter" && filter.subType == "fld")
                        qy["fielder"] = v;  
                    else
                        qy[k] = v;
                }
            }
            // range 
            else if (k.endsWith("_low") || k.endsWith("_high")) {
                if (v != "(all)" && v != "") {
                    //console.log("makeQueryJSONBase k=", k, " v=", v);
                    v = parseInt(v);
                    //console.log("makeQueryJSONBase (after parse) v=", v);
                    if (v >= 0) {
                        if (k.endsWith("_low")) {
                            const b = k.substr(0, k.length-4);
                            const q = qy[b];
                            qy[b] = {...q, "low" : v};
                        }
                        else if (k.endsWith("_high")) {
                            const b = k.substr(0, k.length-5);
                            const q = qy[b];
                            qy[b] = {...q, "high" : v};
                        }
                        else {
                            qy[k] = v;
                        }
                    }
                }
            }
            else if(v.length > 0) {            
                qy[k] = v;
            }
        }
    });
    
    qy["group"] = [];
    filter.group.forEach((k) => {
        qy["group"].push(k);
    });
    
    qy["aggregation"] = agg;
    
    let stArr = [];
    statTypes.forEach((st) => { 
        stArr.push(st); 
    });
    if (filter.query == "gamelog") {
        stArr.sort((a, b) => { 
            const isAgA = (a[0] == "_");
            const isAgB = (b[0] == "_");

            if ( isAgA && !isAgB) return 1;
            else if (!isAgA && isAgB) return -1;
            else if (isAgA && isAgB) 
            return statSortOrder[a.slice(1)] - statSortOrder[b.slice(1)]
            return statSortOrder[a] - statSortOrder[b]
        });
    }

    qy["stats"] = []
    stArr.forEach((st) => { qy["stats"].push(st) });
    qy["order"] = []
    order.forEach((ord) => { 
      let ordStr = ord[0];
      console.log("ord= ", ord)
      ordStr += (ord[1]? ">" : "<");
      qy["order"].push(ordStr);
    });   
    qy["minGP"] = minGP;
    qy["ret"] = "html";
    qy["retopt"] = "bs"; // bootstrap
    qy["limit"] = limit;
    console.log("makeQueryJSONBase: qy=", qy);
    return qy;
}

function makeGamelogQueryJSON(filter, agg, statTypes, order, minGP, limit) {
    filter.query = "gamelog";
    filter.subType = "";
    const qy = makeQueryJSONBase(filter, agg, statTypes, order, minGP, limit);
    return JSON.stringify(qy);
}

function makePlayerGameQueryJSON(playerGameQueryType, filter, agg, statTypes, order, minGP, limit) {
    filter.query = "playergame";
    if (playerGameQueryType == "bat") {
        statTypes = ["AB", "H", "2B", "3B", "HR", "BB", "K", "RBI", "R", "SB", "CS"];
    } else if (playerGameQueryType == "pit") {
        statTypes = ["IP3", "H", "n2B", "n3B", "HR", "BB", "K", "R", "WP", "BK"];
    } else if (playerGameQueryType == "fld") {
        statTypes = ["IF3", "PO", "A", "E", "PB", "DP", "TP"];
    }
    filter.subType = playerGameQueryType;
    const qy = makeQueryJSONBase(filter, agg, statTypes, order, minGP, limit);
    qy["pgqy_t"] = playerGameQueryType;
    return JSON.stringify(qy);
}

function makeSituationQueryJSON(filter, agg, statTypes, order, minGP, limit) {
    filter.query = "situation";
    filter.subType = "";
    const qy = makeQueryJSONBase(filter, agg, statTypes, order, minGP, limit);
    return JSON.stringify(qy);
}

export { makeGamelogQueryJSON, makePlayerGameQueryJSON, makeSituationQueryJSON }