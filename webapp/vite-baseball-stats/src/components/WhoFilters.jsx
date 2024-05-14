import React from 'react'

import OptionWithCheck from './OptionWithCheck'

const WhoFilters = ({divClass="mt-1", filter, boxScoreFiltOpts, onFiltChange, optionClasses, checkClasses}) => {
  return (
    <div classNane={divClass}>
        <OptionWithCheck fieldName="_team" 
            label="Opposing/Pitching Team" 
            options={boxScoreFiltOpts.teams} 
            val={filter.values.get("_team")}
            checkVal={filter.group.has("_team")} 
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses}/>       
            
        { /* AL/NL */ }
        <OptionWithCheck fieldName="league" label="League" 
          options={boxScoreFiltOpts.league} 
          val={filter.values.get("league")}
          checkVal={filter.group.has("league")}
          onChange={onFiltChange}
          optionClasses={optionClasses}
          checkClasses={checkClasses} />
        <OptionWithCheck fieldName="_league" label="Opp League" 
          options={boxScoreFiltOpts.league} 
          val={filter.values.get("_league")}
          checkVal={filter.group.has("_league")}
          onChange={onFiltChange}
          optionClasses={optionClasses}
          checkClasses={checkClasses} />
    </div>
  )
}

export default WhoFilters