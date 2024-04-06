import { useState, useEffect} from 'react'

import BoxScoreFilters from './components/BoxScoreFilters.jsx'
import Results from './components/Results.jsx'

import { doRequest } from './js/requests.js'
import { makeBoxScoreQueryString } from './js/queries.js'
import StatTypes from './components/StatTypes.jsx';
import { statSortOrder } from './js/stats.js';


const resultsClass="row";
const statTypesClassName="col-auto";
const aggregateDivClass = "col-auto" ; // border border-secondary
const aggregateSelectClass = "col-auto form-select";

const updateButtonClass="btn btn-primary text-no-wrap";


function App() {
  const [results, setResults] = useState("");
  const [filter, setFilter] = useState({});
  const [statTypes, setStatTypes] = useState({});
  const [order, setOrder] = useState([]);
  const [aggregate, setAggregate] = useState("");
  
  useEffect(() => {
    setAggregate("no");
  }, [])

  const updateData = async () => {
    console.log("updateData");
    const qy = makeBoxScoreQueryString(filter, aggregate, statTypes, order);
    console.log("qy=", qy);
    const url = "/box?" + qy + "&ret=html-bs";
    const r = await doRequest(url, 'GET', null, "", null, "html", (e) => {
        alert(`Get Data:  status ${e.status} error: ${e.error}`);
    });
    // console.log("updateData r=", r);
    if(r != null)
      setResults(r);
  }

  const onNewAggVal=(v) => {
    setAggregate(v);
    updateData();
  } 
  
  return (
    <>
      <div className="container-fluid mt-4 ml-3">
        <div className="row">
          <div className="col-2">
            <h4>Filters/Order:</h4>
            <BoxScoreFilters filter={filter} setFilter={setFilter}
                             order={order} setOrder={setOrder} updateData={updateData}/>
          </div>
          <div className="col-auto">
            <div className="container">
              <div className="row">
            <StatTypes statTypes={statTypes} setStatTypes={setStatTypes} 
                         updateData={updateData}
                         divClassName={statTypesClassName}/>
              </div>
              <div className="row mt-4">
              { /* aggregation */ }
                <div className={aggregateDivClass}>
                { /* <label className={filtOptLabelClass} htmlFor="filter_agg">Total/Avg:</label> */ }
                    <label>Total/Average</label>
                    <select className={aggregateSelectClass} id="filter_agg" value={aggregate} onChange={(e)=> (
                        onNewAggVal(e.target.value))}>
                        <option value="no">(no)</option>
                        <option value="sum">Total</option>
                        <option value="average">Average</option>
                    </select>
                </div>
                <div className="col-4 align-items-end">
                  <button className={updateButtonClass} onClick={()=>(updateData())}>Get Data</button>
                </div>
              </div>
              <div className="row">
                  <Results resultsTable={results} divClassName={resultsClass}/>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default App
