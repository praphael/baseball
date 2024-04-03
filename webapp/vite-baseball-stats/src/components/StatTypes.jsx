import React from 'react'
import { useEffect, useState } from 'react'

import StatTypeCheck from './StatTypeCheck'

import { statTypesArr, statSetDefault } from '../js/stats.js'

const groupDivClass = "col-1 form-check mb-2";
const checkClass = "col-2 form-check-input";
const groupLabelClass= "form-check-label"

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

    console.log("statSet=", statSet);
    return (
      <>
        <h4>Stats</h4>
        <div className={divClassName}>
          
        { 
        statTypesArr.map((st)=> ( <StatTypeCheck key={st+"_k"} fieldName={st}
        initValue={statSet.has(st)} onChange={onStatTypeChange} checkClass={checkClass} 
        divClass={groupDivClass} labelClass={groupLabelClass} />)) 
       }
        </div>
      </>
    )
}

export default StatTypes