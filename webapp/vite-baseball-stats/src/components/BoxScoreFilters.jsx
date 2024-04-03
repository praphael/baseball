import React from 'react'
import { useEffect } from 'react'

import { boxScoreFiltOpts, boxScoreFiltDefaults } from '../js/filters.js'

import FilterNumberInput from './FilterNumberInput.jsx'
import FilterOption from './FilterOption.jsx'

const boxScoreFilt = { ...boxScoreFiltDefaults };

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

  console.log("boxScoreFilt.values= ", boxScoreFilt.values);
  console.log("boxScoreFilt.group= ", boxScoreFilt.group);

  return (
    <div>
        <h3>Filters:</h3>
        <FilterOption fieldName="team" label="Team" options={boxScoreFiltOpts.teams} 
            initValue={boxScoreFilt.values.get("team")} 
            initGroup={boxScoreFilt.group.has("team")}  
            onChange={onFiltChange} />
        <FilterNumberInput fieldName="year" label="Year" 
            initValue={boxScoreFilt.values.get("year")}
            initGroup={boxScoreFilt.group.has("year")}   
            onChange={onFiltChange} />
        <FilterOption fieldName="month" label="Month" options={boxScoreFiltOpts.months} 
            initValue={boxScoreFilt.values.get("month")}
            initGroup={boxScoreFilt.group.has("month")}
            onChange={onFiltChange} />
        { /* day of week */ }
        <FilterOption fieldName="dow" label="DOW" options={boxScoreFiltOpts.daysOfWeek} 
            initValue={boxScoreFilt.values.get("dow")} 
            initGroup={boxScoreFilt.group.has("dow")}
            onChange={onFiltChange} />
        { /* aggregation */ }
        <div>
            <label htmlFor="filter_agg">Sum/Avg:</label>
            <select id="filter_agg" value={boxScoreFilt.agg} onChange={()=> (
                onFiltChange("agg", this.getSelectedIndex().value))}>
                <option value="no">(no)</option>
                <option value="sum">sum</option>
                <option value="avg">avg</option>
            </select>
        </div>
    </div>
  )
}

export default BoxScoreFilters
