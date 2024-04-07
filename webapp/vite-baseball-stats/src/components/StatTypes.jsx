import React from 'react'
import { useState } from 'react';

import { statSetsDefault } from '../js/stats.js'
import StatTypesRadio from './StatTypesRadio.jsx';

const groupDivClass = "mb-2 mr-sm-2"; // form-check 
const checkClass = "btn btn-check" // "form-check-input";
const groupLabelClass= "btn btn-outline-info" // "form-check-label"
// sr-only" for="inlineFormInputName">Name</label>
// <input type="text" class="form-control mb-2 mr-sm-2

const statSetsCur = statSetsDefault;
// const statSet = statSetDefault;

const statSetOptions=["Game Box", "Offense 1", "Offense 2", "Pitching 1", "Pitching 2", "Fielding"];
const initValArr = ['off', 'on', false, false, false, false]

const StatTypes = ({statSet, setStatSet, updateData, divClassName}) => {
    // const [statSet, setStatSet] = useState({})
    const [valArr, setValArr] = useState(initValArr);
    /*
    const onStatTypeChange = (stat, value) => {
        console.log("onStatTypeChange stat=", stat, "value=", value);
        if(value) statTypes.add(stat);
        else statTypes.delete(stat);
        setStatTypes(statTypes);
    } */

    const onStatSetChange= (statSet_str) => {
        setStatSet(statSet_str);
        const newArr = [...valArr];
        for(let i=0; i<newArr.length; i++) {
            newArr[i] = (statSet_str === statSetOptions[i]) ? 'off' : 'on';
        }
        setValArr(newArr);
        console.log("onStatSetChange statSet_str= ", statSet_str);
    }

    // console.log("statSet=", statSet);
    return (
      <>
        <h4>Stats:</h4>
        <div className={divClassName}>
          <StatTypesRadio fieldName="statType" label=""
             options={statSetOptions}
             val={valArr} onStatRadioChange={onStatSetChange}
             radioClasses={{divClass:"", labelClass:""}} />
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