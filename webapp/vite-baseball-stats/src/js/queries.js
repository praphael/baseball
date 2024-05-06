import { statSortOrder } from "./stats";

function makeQueryJSONBase(filter, agg, statTypes, order, minGP, limit) {
    let qy = {};
    filter.values.forEach((v, k) => {
        v = v.trim();
        // range 
        if (k.endsWith("_low") || k.endsWith("_high")) {
            if (v != "(all)" && v != "") {
                console.log("makeQueryJSONBase k=", k, " v=", v);
                v = parseInt(v);
                console.log("makeQueryJSONBase (after parse) v=", v);
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
    stArr.sort((a, b) => { 
        const isAgA = (a[0] == "_");
        const isAgB = (b[0] == "_");

        if ( isAgA && !isAgB) return 1;
        else if (!isAgA && isAgB) return -1;
        else if (isAgA && isAgB) 
          return statSortOrder[a.slice(1)] - statSortOrder[b.slice(1)]
        return statSortOrder[a] - statSortOrder[b]
    });

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
    return JSON.stringify(qy);
}

function makeGamelogQueryJSON(filter, agg, statTypes, order, minGP, limit) {
    return makeQueryJSONBase(filter, agg, statTypes, order, minGP, limit);
}

function makePlayerGameQueryJSON(filter, agg, statTypes, order, minGP, limit) {
    return makeQueryJSONBase(filter, agg, statTypes, order, minGP, limit);
}

function makeSituationQueryJSON(filter, agg, statTypes, order, minGP, limit) {
    return makeQueryJSONBase(filter, agg, statTypes, order, minGP, limit);
}

export { makeGamelogQueryJSON, makePlayerGameQueryJSON, makeSituationQueryJSON }