import React from 'react'
import { useState } from 'react'
import { seasons } from '../js/filters'

import ButtonGroup from './ButtonGroup'
import OptionWithCheck from './OptionWithCheck'
import OptionRangeWithCheck from './OptionRangeWithCheck'
import PlayerInput from './PlayerInput'

const seasonValMapDefault = new Map();
seasonValMapDefault.set("Reg", true)
seasonValMapDefault.set("Post", false)

const CommonFilters = ({filter, boxScoreFiltOpts, onFiltChange, optionClasses, checkClasses}) => {
  const [seasonValMap, setSeasonValMap] = useState(seasonValMapDefault);

  const onSeasonChange = (v, st) =>  {
    const newMap = new Map(seasonValMap);
    console.log("onSeasonChange v=", v, " st=", st);
    newMap.set(v, st);
    
    // construct array of set values
    const seasArr = [];
    if (newMap.get("Reg")) seasArr.push("Reg");
    if (newMap.get("Post")) seasArr.push("Post");
    onFiltChange("season", seasArr);

    // filter.values.get("season")
    setSeasonValMap(newMap);
  }

  return (
    <div>
        <ButtonGroup fieldName="season" label="Season: "
            options={seasons} 
            valMap={seasonValMap}
            onButtonChange={onSeasonChange}
            buttonClasses={{divClass:"", labelClass:"me-2"}}/>
        <OptionWithCheck fieldName="team" label="Team/Batting"
            options={boxScoreFiltOpts.teams} 
            val={filter.values.get("team")}
            checkVal={filter.group.has("team")} 
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses}/>
        <PlayerInput fieldName="batter" label="Batter" 
                     checkVal={filter.group.has("batter")} 
                     onFiltChange={onFiltChange}
                     checkClasses={checkClasses}/>
        <PlayerInput fieldName="pitcher" label="Pitcher" 
                     checkVal={filter.group.has("pitcher")} 
                     onFiltChange={onFiltChange}
                     checkClasses={checkClasses}/>

        <OptionRangeWithCheck fieldName="year" label="Years" 
            options={boxScoreFiltOpts.years} 
            valLow={filter.values.get("year_low")}
            valHigh={filter.values.get("year_high")}
            checkVal={filter.group.has("year")} 
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses}/>
    </div>
  )
}

export default CommonFilters