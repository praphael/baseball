import { useState } from 'react'

import BoxScoreFilters from './components/BoxScoreFilters.jsx'
import Results from './components/Results.jsx'

import { doRequest } from './js/requests.js'
import StatTypes from './components/StatTypes.jsx';

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
  statTypes.forEach((st) => { stqy += "," + st})
  qy += stqy.slice(1)
  return qy;
}

const resultsClass="row";
const statTypesClassName="row";
const updateButtonClass="btn btn-primary col-4";

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
    console.log("r=", r);
    if(r != null)
      setResults(r);
  }
  
  return (
    <>
      <div className="container">
        <div className="row">
          <div className="col-4">
            <div className="container"><h3 className="col-2">Filters:</h3>
              <span className="col-2"></span>
              <button className={updateButtonClass} onClick={()=>(updateData())}>Get Data</button>
            </div>
            <BoxScoreFilters filter={filter} setFilter={setFilter} />
          </div>
          <div className="col-8 mt-3">
            <div className="container">
               { /*  */ }
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
