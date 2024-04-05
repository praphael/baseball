import React from 'react'
import { useState } from 'react'

const Check = ({fieldName, initValue, onChange, 
                checkClasses}) => {
  const [val, setVal] = useState(initValue);

  const onNewVal = (v) => {
    onChange(fieldName, v, true);
    setVal(v);
  }
  // console.log("FilterGroupCheck ", fieldName, " initValue=", initValue)
  const id = `"filter_${fieldName}_group"`;
  return (
    <div className={checkClasses.divClass}>
        <input className={checkClasses.checkClass} type="checkbox" id={id} checked={val} onChange={
            (e)=>(onNewVal(e.target.checked))} />
        <label className={checkClasses.labelClass} htmlFor={id}>{checkClasses.label}</label>
    </div>
  )
}

export default Check