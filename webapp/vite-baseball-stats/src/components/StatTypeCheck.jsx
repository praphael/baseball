import React from 'react'

import { useState } from 'react'

const StatTypeCheck = ({fieldName, fieldLabel, initValue, isAgainst,
    onChange, checkClass, divClass, labelClass}) => {
    const [val, setVal] = useState(initValue);

    const onNewVal = (v) => {
        onChange(fieldName, v);
        setVal(v);
    }

    // console.log("StatTypeCheck ", fieldName, " initValue=", initValue)
    const id = `"stat_${fieldName}"`;
    return (
      <div className={divClass}>
        <input className={checkClass} type="checkbox" id={id} checked={val} onChange={
            (e)=>(onNewVal(e.target.checked))} />
        <label className={labelClass} htmlFor={id}>{fieldLabel}</label>
      </div>
    )
}

export default StatTypeCheck