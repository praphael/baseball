import React from 'react'
import { useState, useEffect } from 'react'

const Check = ({fieldName, val, onChange, 
                checkClasses, isGroup=true }) => {
  const onNewVal = (v) => {
    console.log("Check onNewVal", fieldName, " v=", v);
    onChange(fieldName, v, isGroup);
  }
  //console.log("Check ", fieldName, " initValue=", initValue)

  const id = `filter_${fieldName}` + isGroup? "_group":"";
  return (
    <div className={checkClasses.divClass}>
        
        <label className={checkClasses.labelClass} htmlFor={id}>
        <input className={checkClasses.checkClass} type="checkbox" id={id} checked={val} onChange={
            (e)=>(onNewVal(e.target.checked))} />
        
            {checkClasses.label}
        </label>
    </div>
  )
}

export default Check