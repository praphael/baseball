import React from 'react'

import OptionWithCheck from './OptionWithCheck'

const TimeFilters = ({filter, boxScoreFiltOpts, onFiltChange, optionClasses, checkClasses}) => {
  return (
    <div>
        <OptionWithCheck fieldName="round" label="Playoff Round"
            options={boxScoreFiltOpts.postseries} 
            val={filter.values.get("round")}
            checkVal={filter.group.has("round")} 
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses}/>
        <OptionWithCheck fieldName="month" label="Month"
            options={boxScoreFiltOpts.months}
            val={filter.values.get("month")}
            checkVal={filter.group.has("month")}
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
        { /* day of week */ }
        <OptionWithCheck fieldName="dow" label="Day" options={boxScoreFiltOpts.daysOfWeek} 
            val={filter.values.get("dow")} 
            checkVal={filter.group.has("dow")}
            onChange={onFiltChange} 
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
    </div>
  )
}

export default TimeFilters