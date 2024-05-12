import React from 'react'

import OptionWithCheck from './OptionWithCheck.jsx'
import OptionRangeWithCheck from './OptionRangeWithCheck.jsx'

const ConditionFilters = ({filter, boxScoreFiltOpts, onFiltChange, optionClasses, checkClasses}) => {
  return (
    <div class="container">  
      <div class="row">
        <div class="col-auto">
          <OptionWithCheck fieldName="daynight" label="Day/Night" 
            options={boxScoreFiltOpts.daynight} 
            val={filter.values.get("daynight")} 
            checkVal={filter.group.has("daynight")}
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
          <OptionWithCheck fieldName="precip" label="Preciptation" 
            options={boxScoreFiltOpts.precip} 
            val={filter.values.get("precip")} 
            checkVal={filter.group.has("precip")}
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
          <OptionWithCheck fieldName="sky" label="Sky" 
            options={boxScoreFiltOpts.sky} 
            val={filter.values.get("sky")} 
            checkVal={filter.group.has("sky")}
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
          <OptionWithCheck fieldName="fieldcond" label="Field Condition" 
            options={boxScoreFiltOpts.fieldcond} 
            val={filter.values.get("fieldcond")} 
            checkVal={filter.group.has("fieldcond")}
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
        </div>
        <div class="col-auto">
          <OptionRangeWithCheck fieldName="temp" label="Temperature" 
            options={boxScoreFiltOpts.temp} 
            valLow={filter.values.get("temp_low")}
            valHigh={filter.values.get("temp_high")}
            checkVal={filter.group.has("temp")}
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
          <OptionRangeWithCheck fieldName="windspeed" label="Wind speed" 
            options={boxScoreFiltOpts.windspeed} 
            valLow={filter.values.get("windspeed_low")}
            valHigh={filter.values.get("windspeed_high")}
            checkVal={filter.group.has("windspeed")}
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
          <OptionWithCheck fieldName="winddir" label="Wind Dir" 
            options={boxScoreFiltOpts.winddir} 
            val={filter.values.get("winddir")} 
            checkVal={filter.group.has("winddir")}
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
          </div>
        </div>
    </div>
  )
}

export default ConditionFilters