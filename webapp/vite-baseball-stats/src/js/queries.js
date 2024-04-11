import { statSortOrder } from "./stats";

function makeBoxScoreQueryString(filter, agg, statTypes, order, minGP) {
    let qy = {};
    filter.values.forEach((v, k) => {
        v = v.trim();
        if (k == "yearlow" || k == "yearhigh" || k == "month") {
            if (v != "(all)" && v != "") {
                console.log("makeBoxScoreQueryString k=", k, " v=", v);
                v = parseInt(v);
                console.log("makeBoxScoreQueryString (after parse) v=", v);
                if (v >= 0) {
                    if (k == "yearlow") {
                        const q = qy["year"];
                        qy["year"] = {...q, "low" : v};
                        console.log("yearlow qy=", qy);
                    }
                    else if (k == "yearhigh") {
                        const q = qy["year"];
                        qy["year"] = {...q, "high" : v};
                        console.log("yearhigh qy=", qy);
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
    return JSON.stringify(qy);
}

export { makeBoxScoreQueryString }