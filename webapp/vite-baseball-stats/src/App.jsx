import { useState } from 'react'

import BoxScoreFilters from './components/BoxScoreFilters.jsx'
import Results from './components/Results.jsx'

import { doRequest } from './js/requests.js'

function makeBoxScoreQueryString(filter) {
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
  qy += ("grp=" + grp.slice(1));
  qy += ("&agg=" + filter.agg)
  return qy;
}

const resultsClass="container";
const updateButtonClass="btn btn-primary col-4";

function App() {
  const [results, setResults] = useState("");
  const [filter, setFilter] = useState({});
  
  const updateData = async () => {
    console.log("updateData");
    const qy = makeBoxScoreQueryString(filter);
    console.log("qy=", qy);
    const url = "/box?" + qy + "&ret=html-bs";
    const r = await doRequest(url, 'GET', null, "", null, "html", (errMsg) => {
        alert("Update error:  ", errMsg);
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
      { /* <form className="form"> */ }
          <div className="container"><h3 className="col-2">Filters:</h3>
          <span className="col-2"></span>
          <button className={updateButtonClass} onClick={()=>(updateData())}>Get Data</button>
          </div>
          <BoxScoreFilters filter={filter} setFilter={setFilter} />
      { /* </form> */ }
        </div>
        <div className="col-8 mt-3">
        <Results resultsTable={results} divClassName={resultsClass}/>
        </div>
        </div>
      </div>
    </>
  )
}

export default App
