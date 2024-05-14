import React from 'react'

/* "batter", "pitcher", "batter_team", "pitcher_team",
"fielder", "sit_inn", "sit_innhalf", "sit_outs",
"sit_bat_tm_sco", "sit_pit_tm_sco", "sit_sco_diff", 
"sit_bases", "sit_base_1", "sit_base_2", "sit_base_3", 
"sit_bat_cnt", "sit_play_res", "sit_play_base",
"sit_play_res2", "sit_play_base2", "sit_play_res3",
"sit_play_base3", "sit_hit_loc", "sit_hit_type",
"sit_outs_made", "sit_runs_sco" */

import OptionWithCheck from './OptionWithCheck.jsx'
import OptionRangeWithCheck from './OptionRangeWithCheck.jsx'
import PlayerInput from './PlayerInput.jsx'
import TriStateButtonGroup from './TriStateButtonGroup.jsx'

// const sit_bases = [["sit_base_1", 0], ["sit_base_2", 0], ["tsit_base_3", 0]];

const SituationFilters = ({divClass="container mt-1", filter, boxScoreFiltOpts, onFiltChange, optionClasses, checkClasses}) => {
  const onBasesChange = (v, st) =>  {
    //const msg= "onBasesChange v=" + v + " st=" + st;
    //alert(msg);
    onFiltChange(v, st, false);    
  }

  const sit_bases = [];
  for (let b=1; b<4; b++) {
    const k = "sit_base_" + b;
    let v = filter.values.get(k);
    if( v == undefined || v == NaN) 
      v = "?";
    sit_bases.push([k, v, b]);
  }
   
  return (
    <div classNane={divClass}>  
      <div className="row">
        <div className="col-auto">
        <OptionWithCheck fieldName="sit_innhalf" label="Inning Half" 
          options={boxScoreFiltOpts.inning_halves} 
          val={filter.values.get("sit_innhalf")} 
          checkVal={filter.group.has("sit_innhalf")}
          onChange={onFiltChange}
          optionClasses={optionClasses}
          checkClasses={checkClasses} />
        <OptionRangeWithCheck fieldName="sit_inn" label="Inning" 
          options={boxScoreFiltOpts.innings} 
          valLow={filter.values.get("sit_inn_low")}
          valHigh={filter.values.get("sit_inn_high")}
          checkVal={filter.group.has("sit_inn")}
          onChange={onFiltChange}
          optionClasses={optionClasses}
          checkClasses={checkClasses} />    
        <OptionRangeWithCheck fieldName="sit_sco_diff" label="Score Differential" 
          options={boxScoreFiltOpts.sco_diff} 
          valLow={filter.values.get("sit_sco_diff_low")}
          valHigh={filter.values.get("sit_sco_diff_high")}
          checkVal={filter.group.has("sit_sco_diff")}
          onChange={onFiltChange}
          optionClasses={optionClasses}
          checkClasses={checkClasses} />  
        </div>
        <div class="col-auto">
          <TriStateButtonGroup fieldName="sit_bases" label="Bases:" 
            val={sit_bases} 
            onButtonChange={onBasesChange}
            buttonClasses={{divClass:"", labelClass:"me-2"}}/>
          <OptionRangeWithCheck fieldName="sit_outs" label="Outs" 
            options={boxScoreFiltOpts.outs} 
            valLow={filter.values.get("sit_outs_low")}
            valHigh={filter.values.get("sit_outs_high")}
            checkVal={filter.group.has("sit_outs")}
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses} />  
          <OptionWithCheck fieldName="sit_bat_cnt" label="Batter count" 
            options={boxScoreFiltOpts.bat_cnt} 
            val={filter.values.get("sit_bat_cnt")} 
            checkVal={filter.group.has("sit_bat_cnt")}
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
        </div>
      </div>  
    </div>

  )
}

export default SituationFilters