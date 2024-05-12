import { useState, useEffect } from 'react'

import BoxScoreFilters from './components/BoxScoreFilters.jsx'
import Results from './components/Results.jsx'
import StatTypes from './components/StatTypes.jsx';
import Check from './components/Check.jsx';
import OptionRangeWithCheck from './components/OptionRangeWithCheck.jsx'

import { doRequest } from './js/requests.js'
import { makeGamelogQueryJSON, makePlayerGameQueryJSON, makeSituationQueryJSON } from './js/queries.js'
import { boxScoreFiltOptsDefaults, boxScoreFiltDefaults, filterFields, getParksTeams, orderDefaults } from './js/filters.js'

import { statTypesArr, statSortOrder, statSetsDefault } from './js/stats.js'
import NumberInputWithCheck from './components/NumberInputWithCheck.jsx';
import RadioButtonGroup from './components/RadioButtonGroup.jsx';
import ButtonGroup from './components/ButtonGroup.jsx';
import PlayerInput from './components/PlayerInput.jsx';
import OptionWithCheck from './components/OptionWithCheck.jsx';
import CommonFilters from './components/CommonFilters.jsx';

const statSets = statSetsDefault;

const resultsClass = "overflow-x-scroll flex-no-wrap";
const statTypesClassName="col-auto";
const aggregateDivClass = "col-2" ; // border border-secondary
const aggregateSelectClass = "col-auto form-select";
const updateButtonClass = "btn btn-success text-no-wrap";
const optionInputDivClass = "row mb-1 mt-1"; // border border-secondary
const selectClass = "col-4 form-select";
const inputClass = "ml-2 col-8 form-input";
const optionInputLabelClass = "form-label"
const optionClasses = { divClass:optionInputDivClass, selectClass, labelClass:optionInputLabelClass } 
const checkDivClass = "form-check form-check-inline mb-2";
const checkClass = " ms-1 me-1 form-check-input";
const checkLabelClass= "form-check-label"
const checkClasses = { divClass:checkDivClass, checkClass, labelClass:checkLabelClass, label:"Group" }

const queryTypes = [["Team", "gamelog"], ["Player","playergame"], ["Situation","situation"]];


const RANGE_FIELDS = new Set();
RANGE_FIELDS.add("year");
RANGE_FIELDS.add("temp");
RANGE_FIELDS.add("windspeed");
RANGE_FIELDS.add("sit_outs");
RANGE_FIELDS.add("sit_sco_diff");
RANGE_FIELDS.add("sit_inn");

function App() {
  const [results, setResults] = useState("");
  const [filter, setFilter] = useState(boxScoreFiltDefaults);
  //const [statTypes, setStatTypes] = useState({});
  const [statSet, setStatSet] = useState("off1");
  const [order, setOrder] = useState(orderDefaults);
  const [aggregate, setAggregate] = useState("sum");
  const [boxScoreFiltOpts, setBoxScoreFiltOpts] = useState(boxScoreFiltOptsDefaults);
  const [minGP, setMinGP] = useState(1);
  const [limit, setLimit] = useState(30);

  

  console.log("boxScoreFiltOptsDefaults=", boxScoreFiltOptsDefaults);
  useEffect(() => {
      const doFetch = async () => {
        console.log("useEffect boxScoreFiltOpts=", boxScoreFiltOpts);
        const boxScoreFiltOptsNew = {...boxScoreFiltOpts};
        const r = await getParksTeams();
        boxScoreFiltOptsNew.parks = r.parks;
        boxScoreFiltOptsNew.teams = r.teams;
        setBoxScoreFiltOpts(boxScoreFiltOptsNew);
        // do initial fetch with default params
        await getData("gamelog");
      };
      doFetch();
  }, []);
  
  const getData = async (queryType, playerGameQueryType) => {
    console.log("getData");
    const statTypes = statSets.get(statSet);

    if (queryType == "gamelog") {
      const qy = makeGamelogQueryJSON(filter, aggregate, statTypes, order, minGP, limit);
      console.log("qy=", qy);
      const url = encodeURI("/gamelog?" + qy);
      const r = await doRequest(url, 'GET', null, "", null, "html", (e) => {
          alert(`Get Data:  status ${e.status} error: ${e.error}`);
      });
      // console.log("updateData r=", r);
      if(r != null)
        setResults(r);
    }
    if (queryType == "playergame") {
      const qy = makePlayerGameQueryJSON(playerGameQueryType, filter, aggregate, statTypes, order, minGP, limit);
      console.log("qy=", qy);
      const url = encodeURI("/playergame?" + qy);
      const r = await doRequest(url, 'GET', null, "", null, "html", (e) => {
          alert(`Get Data:  status ${e.status} error: ${e.error}`);
      });
      // console.log("updateData r=", r);
      if(r != null)
        setResults(r);
    }
    if (queryType == "situation") {
      const qy = makeSituationQueryJSON(filter, aggregate, statTypes, order, minGP, limit);
      console.log("qy=", qy);
      const url = encodeURI("/situation?" + qy);
      const r = await doRequest(url, 'GET', null, "", null, "html", (e) => {
          alert(`Get Data:  status ${e.status} error: ${e.error}`);
      });
      // console.log("updateData r=", r);
      if(r != null)
        setResults(r);
    }
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
    console.log("onFiltChange field=", field, "value=", value, "isGroup=", isGroup);
    //console.log("onFiltChange filter=", filter);
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
            if(RANGE_FIELDS.has(field)) {
               if(filter.values.get(field + "_low") == filter.values.get(field + "_high")) {
                 newFilt.values.set(field + "_low", "");
                 newFilt.values.set(field + "_high", "");
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
    console.log("onOrderChange field=", field, " value=", value);
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

  const onStatSetChange = (stSet) => {
    console.log("onStatSetChange=", stSet)
    setStatSet(stSet);
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
             </p>
             <p>
                Source available on Github here <a href="https://github.com/praphael/baseball">here</a>. 
                Feel free to leave comments/suggestions there as well. 
                Keep in this is a side/learning project, using a combo of ReactJS, C++ for backend and sqlite3 in-memory database for speed.
                Some combinations of parameters may not make sense.
             </p>
        </div>
            

        <div className="row overflow-x-scroll flex-no-wrap">
          
          <div className="col-auto border">
            <h4>Options</h4>
            <CommonFilters boxScoreFiltOpts={boxScoreFiltOpts} filter={filter}
                            onFiltChange={onFiltChange} optionClasses={optionClasses} 
                            checkClasses={checkClasses} />
          </div>

          <div className="col-auto border">
            <h4>Filters/Order</h4>
            <BoxScoreFilters boxScoreFiltOpts={boxScoreFiltOpts} filter={filter}
                             onFiltChange={onFiltChange} order={order} 
                             onOrderChange={onOrderChange}/>
          </div>
        </div>
        <div className="row">
          <StatTypes statSet={statSet} onStatSetChange={onStatSetChange} 
                      updateData={getData}
                      divClassName={statTypesClassName} />
        </div>
        
        <div className="row mt-4">
              <div className={aggregateDivClass}>
              
                  <label>Aggregate:</label>
                  <select className={aggregateSelectClass} id="filter_agg" value={aggregate}
                      onInput={(e)=> (onNewAggVal(e.target.value))}>
                      <option value="no">(no)</option>
                      <option value="sum">Total</option>
                      <option value="avg">Average</option>
                      <option value="max">Max</option>
                      <option value="min">Min</option>
                  </select>
              </div>

              <div className="col-1">
                <label className="form-label" htmlFor="filter_minGP">Min Games/ Plays:</label><br/>
                <input className="input form-input" size="5"
                  type="text" id="filter_minGP" value={minGP}
                  onChange={(e)=>(onNewMinGPVal(e.target.value))} />
              </div>
              <div className="col-1">
                <label className="form-label" htmlFor="filter_minGP">Limit:</label><br/>
                <input className="input form-input" size="5"
                  type="text" id="filter_limit" value={limit}
                  onChange={(e)=>(onNewLimit(e.target.value))} />
              </div>
              <div className="col-2">
              <div className="container">
                  <div className="row">
                    <Check fieldName="showCond" val={filter.values.get("showCond")} 
                            onChange={onFiltChange} checkClasses={{ divClass:checkDivClass, checkClass, 
                            labelClass:checkLabelClass, label:"Show Conditions" }}  isGroup={false}/>
                  </div>
                  <div className="row">
                    <Check fieldName="showPark" val={filter.values.get("showPark")} 
                            onChange={onFiltChange} checkClasses={{ divClass:checkDivClass, checkClass, 
                            labelClass:checkLabelClass, label:"Show Park Info" }} isGroup={false}/>
                  </div>
                </div>
              </div>
              <div className="col-2">
                <Check fieldName="showWLS" val={filter.values.get("showWLS")} 
                        onChange={onFiltChange} checkClasses={{ divClass:checkDivClass, checkClass, 
                        labelClass:checkLabelClass, label:"Show Win/Loss/Save" }} isGroup={false}/>
              </div>
   
   
            <div className="row mt-3 flex-no-wrap">
              <div className="hstack gap-3">
                <button className={updateButtonClass} onClick={()=>(getData("gamelog"))}>Get Team Stats</button>
                <button className={updateButtonClass} onClick={()=>(getData("playergame", "bat"))}>Get Player Batting</button>
                <button className={updateButtonClass} onClick={()=>(getData("playergame", "pit"))}>Get Player Pitching</button>
                <button className={updateButtonClass} onClick={()=>(getData("playergame", "fld"))}>Get Player Fielding</button>
                <button className={updateButtonClass} onClick={()=>(getData("situation"))}>Get Situation Stats</button>
              </div>
            </div>
            <div className="row overflow-x-scroll flex-no-wrap">
                <Results resultsTable={results} divClassName={resultsClass}/>
            </div>
        </div>                         
      </div>
    </>
  )
}

export default App
