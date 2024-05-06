import React from 'react'
import { useState, useEffect } from 'react'

const Check = ({fieldName, val, onChange, 
                checkClasses}) => {
  const onNewVal = (v) => {
    console.log("Check onNewVal", fieldName, " v=", v);
    onChange(fieldName, v, true);
  }
  //console.log("Check ", fieldName, " initValue=", initValue)
  const id = `"filter_${fieldName}_group"`;
  return (
    <div className={checkClasses.divClass}>
        
        <input className={checkClasses.checkClass} type="checkbox" id={id} checked={val} onChange={
            (e)=>(onNewVal(e.target.checked))} />
        <label className={checkClasses.labelClass} htmlFor={id}>
            {checkClasses.label}
        </label>
    </div>
  )
}

export default Check