import React from 'react'

import { statSetsDefault } from '../js/stats.js'
import RadioButtonGroup from './RadioButtonGroup.jsx';

const groupDivClass = "mb-2 mr-sm-2"; // form-check 
const checkClass = "btn btn-check" // "form-check-input";
const groupLabelClass= "btn btn-outline-info" // "form-check-label"
// sr-only" for="inlineFormInputName">Name</label>
// <input type="text" class="form-control mb-2 mr-sm-2

const statSetsCur = statSetsDefault;
// const statSet = statSetDefault;

const statSetOptions=[["Game Box", "box"], ["Offense 1", "off1"],
  ["Offense 2", "off2"], ["Pitching 1", "pit1"], ["Pitching 2", "pit2"],
  ["Fielding", "fld"]];

const StatTypes = ({statSet, onStatSetChange, updateData, divClassName}) => {

    // console.log("statSet=", statSet);
    return (
      <>
        <h4>Stats:</h4>
        <div className={divClassName}>
          <RadioButtonGroup fieldName="statSet" label=""
              options={statSetOptions} val={statSet}
              onRadioChange={onStatSetChange}
              radioClasses={{divClass:"", labelClass:""}} />
          { /* <StatTypesRadio fieldName="statType" label=""
             options={statSetOptions}
             val={valArr} onStatRadioChange={onStatSetChange}
             radioClasses={{divClass:"", labelClass:""}} />
          */ }
          {/* Against 
          <div className="container">
            <div className="row">
              <h5 className="text-justify-right">For:</h5>
              <div className="overflow-scroll hstack text-nowrap">
              { 
                statTypesArr.map((st)=> ( <StatTypeCheck key={st[1]+"_k"} fieldName={st[1]}
                fieldLabel={st[0]} initValue={statSet.has(st[1])} isAgainst={true} onChange={onStatTypeChange}
                checkClass={checkClass} divClass={groupDivClass} labelClass={groupLabelClass} />)) 
              }
              </div>
            </div>
            
            
            <div className="row">
              <h5 className="text-justify-right">Opp:</h5>
              <div className="overflow-scroll hstack text-nowrap">
              { 
                statTypesArr.map((st)=> ( <StatTypeCheck key={st[1]+"_k"} fieldName={"_"+st[1]}
                fieldLabel={st[0]} initValue={statSet.has(st[1])} isAgainst={true} onChange={onStatTypeChange}
                checkClass={checkClass} divClass={groupDivClass} labelClass={groupLabelClass} />)) 
              }  
              </div>
            </div>
          </div>
          */ }
        </div>
      </>
    )
}

export default StatTypes