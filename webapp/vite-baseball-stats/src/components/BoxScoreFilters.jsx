import React from 'react'
import { useEffect, useState } from 'react'

import { boxScoreFiltOpts, boxScoreFiltDefaults } from '../js/filters.js'

import FilterNumberInput from './FilterNumberInput.jsx'
import FilterOption from './FilterOption.jsx'

const boxScoreFilt = { ...boxScoreFiltDefaults };

const filtOptDivClass = "border border-secondary row mb-1 mt-1";
const filtInputDivClass = "border border-secondary row mb-1 mt-1";
const selectClass = "col-4 form-select";
const inputClass = "col-8 form-input";
const filtOptLabelClass = "form-label"
const filtInputLabelClass = "form-label"
const groupDivClass = "col-1 form-check mb-2";
const checkClass = "col-2 ms-1 form-check-input";
const groupLabelClass= "form-check-label"

const BoxScoreFilters = ({filter, setFilter}) => {
  const onFiltChange = (field, value, isGroup) => {
    console.log("onFiltChange field=", field, "value=", value);
    if(isGroup) {
        if(value)
           filter.group.add(field);
        else
           filter.group.delete(field);
    }
    else if (field === "agg") filter.agg = value;
    else filter.values.set(field, value);
    setFilter(filter);
  }

  useEffect(() => {
    // initial value for filter
    setFilter(boxScoreFilt)
  }, [])

  const [aggVal, setAggVal] = useState(boxScoreFilt.agg)

  const onNewAggVal=(v) => {
    onFiltChange("agg", v);
    setAggVal(v);
  } 

  console.log("boxScoreFilt.values= ", boxScoreFilt.values);
  console.log("boxScoreFilt.group= ", boxScoreFilt.group);

  return (
    <div className="container">
        <FilterOption fieldName="team" label="Team" options={boxScoreFiltOpts.teams} 
            initValue={boxScoreFilt.values.get("team")} 
            initGroup={boxScoreFilt.group.has("team")}  
            onChange={onFiltChange} 
            divClass={filtOptDivClass} selectClass={selectClass}
            labelClass={filtOptLabelClass} checkClass={checkClass}
            groupDivClass={groupDivClass}
            groupLabelClass={groupLabelClass}/>
        <FilterNumberInput fieldName="year" label="Year" 
            initValue={boxScoreFilt.values.get("year")}
            initGroup={boxScoreFilt.group.has("year")}   
            onChange={onFiltChange}
            divClass={filtInputDivClass} inputClass={inputClass}
            labelClass={filtInputLabelClass} 
            checkClass={checkClass} groupDivClass={groupDivClass} 
            groupLabelClass={groupLabelClass} />
        <FilterOption fieldName="month" label="Month" options={boxScoreFiltOpts.months} 
            initValue={boxScoreFilt.values.get("month")}
            initGroup={boxScoreFilt.group.has("month")}
            onChange={onFiltChange} 
            divClass={filtOptDivClass} selectClass={selectClass}
            labelClass={filtOptLabelClass}  
            checkClass={checkClass} groupDivClass={groupDivClass}
            groupLabelClass={groupLabelClass} />
       { /* aggregation */ }
        <div className={filtOptDivClass}>
            <label className={filtOptLabelClass} htmlFor="filter_agg">Sum/Avg:</label>
            <select className={selectClass} id="filter_agg" value={aggVal} onChange={(e)=> (
                onNewAggVal(e.target.value))}>
                <option value="no">(no)</option>
                <option value="sum">sum</option>
                <option value="average">avg</option>
            </select>
        </div>
        { /* day of week */ }
        <FilterOption fieldName="dow" label="DOW" options={boxScoreFiltOpts.daysOfWeek} 
            initValue={boxScoreFilt.values.get("dow")} 
            initGroup={boxScoreFilt.group.has("dow")}
            onChange={onFiltChange} 
            divClass={filtOptDivClass} selectClass={selectClass}
            labelClass={filtOptLabelClass}  
            checkClass={checkClass} groupDivClass={groupDivClass}
            groupLabelClass={groupLabelClass} />
    </div>
  )
}

export default BoxScoreFilters
