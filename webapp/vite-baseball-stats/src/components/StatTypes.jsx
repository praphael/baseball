import React from 'react'
import { useEffect, useState } from 'react'

import StatTypeCheck from './StatTypeCheck'

import { statTypesArr, statSetDefault } from '../js/stats.js'

const groupDivClass = "mb-2 mr-sm-2"; // form-check 
const checkClass = "btn btn-check" // "form-check-input";
const groupLabelClass= "btn btn-outline-info" // "form-check-label"
// sr-only" for="inlineFormInputName">Name</label>
// <input type="text" class="form-control mb-2 mr-sm-2

const statSet = statSetDefault;

const StatTypes = ({statTypes, setStatTypes, divClassName}) => {
    useEffect(() => {
      // initial value for filter
      setStatTypes(statSet)
    }, [])

    const onStatTypeChange = (stat, value) => {
        console.log("onStatTypeChange stat=", stat, "value=", value);
        if(value) statTypes.add(stat);
        else statTypes.delete(stat);
        setStatTypes(statTypes);
    }

    // console.log("statSet=", statSet);
    return (
      <>
        <h4>Stats:</h4>
        <div className={divClassName}>
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
            
            {/* Against */ }
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
        </div>
      </>
    )
}

export default StatTypes