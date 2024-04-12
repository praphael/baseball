import { useState, useEffect } from 'react'

import BoxScoreFilters from './components/BoxScoreFilters.jsx'
import Results from './components/Results.jsx'
import StatTypes from './components/StatTypes.jsx';

import { doRequest } from './js/requests.js'
import { makeBoxScoreQueryString } from './js/queries.js'
import { boxScoreFiltOptsDefaults, boxScoreFiltDefaults, filterFields, getParksTeams, orderDefaults } from './js/filters.js'
import { statTypesArr, statSortOrder, statSetsDefault } from './js/stats.js'
import NumberInputWithCheck from './components/NumberInputWithCheck.jsx';

const statSets = statSetsDefault;

const resultsClass = "row";
const statTypesClassName="col-auto";
const aggregateDivClass = "col-auto" ; // border border-secondary
const aggregateSelectClass = "col-auto form-select";
const updateButtonClass = "btn btn-success text-no-wrap";

function App() {
  const [results, setResults] = useState("");
  const [filter, setFilter] = useState(boxScoreFiltDefaults);
  //const [statTypes, setStatTypes] = useState({});
  const [statSet, setStatSet] = useState("Offense 1");
  const [order, setOrder] = useState(orderDefaults);
  const [aggregate, setAggregate] = useState("sum");
  const [boxScoreFiltOpts, setBoxScoreFiltOpts] = useState(boxScoreFiltOptsDefaults);
  const [minGP, setMinGP] = useState(10);
  const [limit, setLimit] = useState(25);

  console.log("boxScoreFiltOptsDefaults=", boxScoreFiltOptsDefaults);
  useEffect(() => {
      const doFetch = async () => {
        console.log("useEffect boxScoreFiltOpts=", boxScoreFiltOpts);
        const boxScoreFiltOptsNew = {...boxScoreFiltOpts};
        const r = await getParksTeams();
        boxScoreFiltOptsNew.parks = r.parks;
        boxScoreFiltOptsNew.teams = r.teams;
        setBoxScoreFiltOpts(boxScoreFiltOptsNew);
        // do initla fetch with default params
        await updateData();
      };
      doFetch();
  }, []);
  
  const updateData = async () => {
    console.log("updateData");
    const statTypes = statSets.get(statSet);
    const qy = makeBoxScoreQueryString(filter, aggregate, statTypes, order, minGP, limit);
    console.log("qy=", qy);
    const url = encodeURI("/box?" + qy);
    const r = await doRequest(url, 'GET', null, "", null, "html", (e) => {
        alert(`Get Data:  status ${e.status} error: ${e.error}`);
    });
    // console.log("updateData r=", r);
    if(r != null)
      setResults(r);
  }

  const onNewAggVal=(v) => {
    setAggregate(v);
  }

  const onNewMinGPVal=(v) => {
    const n = parseInt(v);
    if (n != NaN && n >= 0) setMinGP(n);
  }

  const onNewLimit=(v) => {
    const n = parseInt(v);
    if (n != NaN && n >= 1) setLimit(n);
  }

  const onFiltChange = (field, value, isGroup) => {
    console.log("onFiltChange field=", field, "value=", value);
    console.log("onFiltChange filter=", filter);
    try {
      // we have to copy, or else React doens't detect state change
      const newFilt = {...filter}
      // true if called from group check, else undefined
      if(isGroup) {
          if(value) {
            newFilt.group.add(field);
            // clear the selected values 
            // because doesn't make sense to select for value while also grouping
            // except for ranges
            if(field == "team") {
              if(filter.values.get("teamlow") == filter.values.get("teamhigh")) {
                newFilt.values.set("teamlow", "");
                newFilt.values.set("teamhigh", "");
              }
            }
            else {
                newFilt.values.set(field, "");
            }
          }
          else {
            newFilt.group.delete(field);
          }
      }
      else filter.values.set(field, value);
      setFilter(newFilt);
      // updateData();
    } catch(e) { console.log("Could not set filter ", e)}
  }

  const onOrderChange = (field, value, isAsc) => {
    console.log("onOrderChange  field=", field, " value=", value);
    try {
      // we have to copy, or else React doens't detect state change
      const newOrd = [...order]
      const ord = parseInt(field[5])
      console.log("onOrderChange ord=", ord, " isAsc=", isAsc);
      // true if called from ascending check, else undefined
      if(isAsc) {
        console.log("setting ord[1] to", value);
        newOrd[ord][1] = value;
      } else {
        newOrd[ord][0] = value;
      }
      setOrder(newOrd);
      // updateData();
    } catch(e) { console.log("Could not set order ", e)}
  }

  console.log("App statSet=", statSet);
  console.log("filter=", filter);
  
  return (
    <>
      <div className="container-fluid mt-4 ml-3">
        <div className="row">
          <h2>Baseball stats</h2>
          <p>If questions like "what are the worst performances 
             for earned runs in a month by an MLB team", or "how many home runs were hit by each team over the last ten years"
             you may have come to the right place. This tool allows one to into various groupings and splits from different statics.
             MLB data derived from individual game going back to 1903. 
             All data was sourced from <a href="https://www.retrosheet.org/gamelogs/index.html#">Retrosheet</a>. 
             </p><p>
             Source available on Github here <a href="https://github.com/praphael/baseball">here</a>. 
             Feel free to leave comments/suggestions there as well. 
             Keep in this is a side/learning project, using a combo of ReactJS, C++ for backend and sqlite3 in-memory database for speed.
             Some combinations of parameters may not make sense.
             </p>
            </div>
        <div className="row">
          <div className="col-auto">
            <h4>Filters/Order:</h4>
            <BoxScoreFilters boxScoreFiltOpts={boxScoreFiltOpts} filter={filter} onFiltChange={onFiltChange}
                             order={order} onOrderChange={onOrderChange} updateData={updateData}/>
          </div>
          <div className="col-auto">
            <div className="container">
              <div className="row">
                <StatTypes statSet={statSet} setStatSet={setStatSet} 
                            updateData={updateData}
                            divClassName={statTypesClassName}/>
              </div>
              <div className="row mt-4">
              { /* aggregation */ }
                <div className={aggregateDivClass}>
                { /* <label className={filtOptLabelClass} htmlFor="filter_agg">Total/Avg:</label> */ }
                    <label>Aggregate:</label>
                    <select className={aggregateSelectClass} id="filter_agg" value={aggregate}
                        onInput={(e)=> (onNewAggVal(e.target.value))}>
                        <option value="no">(no)</option>
                        <option value="sum">Total</option>
                        <option value="avg">Average</option>
                    </select>
                </div>
                <div className="col-2">
                  <label className="form-label" htmlFor="filter_minGP">Min Games:</label><br/>
                  <input className="input form-input" size="5"
                    type="text" id="filter_minGP" value={minGP}
                    onChange={(e)=>(onNewMinGPVal(e.target.value))} />
                </div>
                <div className="col-2">
                  <label className="form-label" htmlFor="filter_minGP">Limit:</label><br/>
                  <input className="input form-input" size="5"
                    type="text" id="filter_limit" value={limit}
                    onChange={(e)=>(onNewLimit(e.target.value))} />
                </div>
                <div className="col-4 p-4 align-items-center">
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
