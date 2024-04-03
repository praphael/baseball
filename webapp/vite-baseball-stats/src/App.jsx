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

function App() {
  const [results, setResults] = useState("");
  const [filter, setFilter] = useState({});
  
  const updateData = async () => {
    console.log("updateData");
    const qy = makeBoxScoreQueryString(filter);
    console.log("qy=", qy);
    const url = "/box?" + qy + "&ret=html";
    const r = await doRequest(url, 'GET', null, "", null, "html", (errMsg) => {
        alert("Update error:  ", errMsg);
    });
    console.log("r=", r);
    if(r != null)
      setResults(r);
  }
  
  return (
    <>
      <BoxScoreFilters filter={filter} setFilter={setFilter} />
      <button onClick={()=>(updateData())}>Update</button>
      <Results resultsTable={results}/>
    </>
  )
}

export default App
