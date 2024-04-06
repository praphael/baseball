import { statSortOrder } from "./stats";

function makeBoxScoreQueryString(filter, agg, statTypes, order) {
    let qy = "";
    filter.values.forEach((v, k) => {
        if(v.length > 0) {
            qy += `${k}=${v}&`;
        }
    });
    let grp = "";
    filter.group.forEach((k) => {
        grp += `,${k}`
    });
    if (grp.length > 0)
        qy += ("grp=" + grp.slice(1));
    qy += ("&agg=" + agg);
    qy += "&stats=";
    let stqy = ""
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
    stArr.forEach((st) => { stqy += "," + st });
    qy += stqy.slice(1)
    let ordStr = ""
    order.forEach((ord) => { 
      ordStr += "," + ord[0];
      console.log("ord= ", ord)
      ordStr += (ord[1]? "<" : ">");
    });
    qy += "&order=" + ordStr.slice(1)
    return qy;
}

export { makeBoxScoreQueryString }