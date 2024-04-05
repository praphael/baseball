import React from 'react'
import { useEffect, useState } from 'react'

import { boxScoreFiltOpts, boxScoreFiltDefaults } from '../js/filters.js'

import NumberInputWithCheck from './NumberInputWithCheck.jsx'
import OptionWithCheck from './OptionWithCheck.jsx'
import AccordionHeader from './AccordionHeader.jsx'

const boxScoreFilt = { ...boxScoreFiltDefaults };

const optionInputDivClass = "row mb-1 mt-1"; // border border-secondary
const selectClass = "col-4 form-select";
const inputClass = "col-8 form-input";
const optionInputLabelClass = "form-label"
const optionClasses = { divClass:optionInputDivClass, selectClass, labelClass:optionInputLabelClass } 
const numberInputClasses = { divClass:optionInputDivClass, inputClass, labelClass:optionInputLabelClass }
const checkDivClass = "col-1 form-check mb-2";
const checkClass = "col-2 ms-1 form-check-input";
const checkLabelClass= "form-check-label"
const checkClasses = { divClass:checkDivClass, checkClass, labelClass:checkLabelClass }

const BoxScoreFilters = ({filter, setFilter}) => {
  useEffect(() => {
    // initial value for filter
    setFilter(boxScoreFilt)
  }, [])

  const onFiltChange = (field, value, isGroup) => {
    console.log("onFiltChange field=", field, "value=", value);
    console.log("onFiltChange filter=", filter);
    try {
      if(isGroup) {
          if(value)
            filter.group.add(field);
          else
            filter.group.delete(field);
      }
      else if (field === "agg") filter.agg = value;
      else filter.values.set(field, value);
      setFilter(filter);
    } catch(e) { console.log("Could not set filter ", e)}
  }

  const [aggVal, setAggVal] = useState(boxScoreFilt.agg)

  const onNewAggVal=(v) => {
    onFiltChange("agg", v);
    setAggVal(v);
  } 

//  console.log("boxScoreFilt.values= ", boxScoreFilt.values);
//  console.log("boxScoreFilt.group= ", boxScoreFilt.group);

  return (
    <div className="container">
       { /* aggregation */ }
        <div className={optionClasses.divClass}>
        { /* <label className={filtOptLabelClass} htmlFor="filter_agg">Total/Avg:</label> */ }
            <h5>Total/Average</h5>
            <select className={selectClass} id="filter_agg" value={aggVal} onChange={(e)=> (
                onNewAggVal(e.target.value))}>
                <option value="no">(no)</option>
                <option value="sum">Total</option>
                <option value="average">Average</option>
            </select>
        </div>
        <div className="accordion" id="filtersAccordion">
          <div className="accordion-item">
            <AccordionHeader dataBsTarget="#collapseOne"
              ariaControls="collapseOne" label="Basic Filters"/>
            
            <div id="collapseOne" className="accordion-collapse collapse show" 
              aria-labelledby="headingOne" data-bs-parent="#filtersAccordion">
              <div className="accordion-body">
        <OptionWithCheck fieldName="team" label="Team" options={boxScoreFiltOpts.teams} 
            initValue={boxScoreFilt.values.get("team")} 
            initGroup={boxScoreFilt.group.has("team")}  
            onChange={onFiltChange} 
            optionClasses={optionClasses}
            checkClasses={checkClasses}/>
        <NumberInputWithCheck fieldName="year" label="Year" 
            initValue={boxScoreFilt.values.get("year")}
            initGroup={boxScoreFilt.group.has("year")}   
            onChange={onFiltChange}
            numberInputClasses={numberInputClasses}
            checkClasses={checkClasses} />
        <OptionWithCheck fieldName="month" label="Month" options={boxScoreFiltOpts.months} 
            initValue={boxScoreFilt.values.get("month")}
            initGroup={boxScoreFilt.group.has("month")}
            onChange={onFiltChange} 
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
        { /* home/away */ }
        <OptionWithCheck fieldName="homeaway" label="Home/Away" 
          options={boxScoreFiltOpts.homeAway} 
          initValue={boxScoreFilt.values.get("homeaway")}
          initGroup={boxScoreFilt.group.has("homeaway")}
          onChange={onFiltChange} 
          optionClasses={optionClasses}
          checkClasses={checkClasses} />
            </div>
          </div>
        </div>
        <div className="accordion-item">
          <AccordionHeader dataBsTarget="#collapseTwo"
              ariaControls="collapseTwo" label="Other Filters"/>
          <div id="collapseTwo" className="accordion-collapse collapse show" 
            aria-labelledby="headingOne" data-bs-parent="#filtersAccordion">
            <div className="accordion-body">
        { /* AL/NL */ }
        <OptionWithCheck fieldName="league" label="League" 
          options={boxScoreFiltOpts.league} 
          initValue={boxScoreFilt.values.get("league")}
          initGroup={boxScoreFilt.group.has("league")}
          onChange={onFiltChange}
          optionClasses={optionClasses}
          checkClasses={checkClasses} />
        { /* day of week */ }
        <OptionWithCheck fieldName="dow" label="Day" options={boxScoreFiltOpts.daysOfWeek} 
            initValue={boxScoreFilt.values.get("dow")} 
            initGroup={boxScoreFilt.group.has("dow")}
            onChange={onFiltChange} 
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
        { /* park */ }
        <OptionWithCheck fieldName="park" label="Park" options={boxScoreFiltOpts.parks} 
            initValue={boxScoreFilt.values.get("park")} 
            initGroup={boxScoreFilt.group.has("park")}
            onChange={onFiltChange} 
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
          </div>
          </div>
        </div>
      </div>
    </div>

  )
}

export default BoxScoreFilters
