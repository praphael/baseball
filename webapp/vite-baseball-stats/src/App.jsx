import { useState } from 'react'

import BoxScoreFilters from './components/BoxScoreFilters.jsx'
import Results from './components/Results.jsx'

import { doRequest } from './js/requests.js'
import StatTypes from './components/StatTypes.jsx';
import { statSortOrder } from './js/stats.js';

function makeBoxScoreQueryString(filter, statTypes) {
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
  qy += ("&agg=" + filter.agg);
  qy += "&stats=";
  let stqy = ""
  let stArr = [];
  statTypes.forEach((st) => { stArr.push(st); });
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
  return qy;
}

const resultsClass="row";
const statTypesClassName="row";
const updateButtonClass="btn btn-primary text-no-wrap";

function App() {
  const [results, setResults] = useState("");
  const [filter, setFilter] = useState({});
  const [statTypes, setStatTypes] = useState(new Set());
  
  const updateData = async () => {
    console.log("updateData");
    const qy = makeBoxScoreQueryString(filter, statTypes);
    console.log("qy=", qy);
    const url = "/box?" + qy + "&ret=html-bs";
    const r = await doRequest(url, 'GET', null, "", null, "html", (e) => {
        alert(`Get Data:  status ${e.status} error: ${e.error}`);
    });
    // console.log("r=", r);
    if(r != null)
      setResults(r);
  }
  
  return (
    <>
      <div className="container-fluid mt-3">
        <div className="row">
          <div className="col-2">
            <h4>Filters:</h4>
            <button className={updateButtonClass} onClick={()=>(updateData())}>Get Data</button>
            <BoxScoreFilters filter={filter} setFilter={setFilter} />
          </div>
          <div className="col-auto">
            <div className="container">
              <StatTypes statTypes={statTypes} setStatTypes={setStatTypes} divClassName={statTypesClassName}/>
              <Results resultsTable={results} divClassName={resultsClass}/>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default App
