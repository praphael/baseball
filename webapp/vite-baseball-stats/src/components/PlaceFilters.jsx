import React from 'react'

import OptionWithCheck from './OptionWithCheck'

const PlaceFilters = ({filter, boxScoreFiltOpts, onFiltChange, optionClasses, checkClasses}) => {
  return (
    <div>
        <OptionWithCheck fieldName="homeaway" label="Home/Away"
          options={boxScoreFiltOpts.homeAway}
          val={filter.values.get("homeaway")}
          checkVal={filter.group.has("homeaway")}
          onChange={onFiltChange}
          optionClasses={optionClasses}
          checkClasses={checkClasses} />
        { /* park */ }
        <OptionWithCheck fieldName="park_id" label="Park" options={boxScoreFiltOpts.parks} 
            val={filter.values.get("park_id")} 
            checkVal={filter.group.has("park_id")}
            onChange={onFiltChange} 
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
    </div>

  )
}


export default PlaceFilters