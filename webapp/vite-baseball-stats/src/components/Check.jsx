import React from 'react'
import { useState, useEffect } from 'react'

const Check = ({fieldName, val, onChange, 
                checkClasses, isGroup=true }) => {
  const onNewVal = (v) => {
    console.log("Check onNewVal", fieldName, " v=", v);
    onChange(fieldName, v, isGroup);
  }
  //console.log("Check ", fieldName, " initValue=", initValue)

  const id = `filter_${fieldName}` + isGroup? "_group" : "";
  const lblID = id + '_lbl';
  const divID = id + '_div';

  return (
    <div className={checkClasses.divClass} id={divID} name={divID}>
        
        <input className={checkClasses.checkClass} type="checkbox" id={id} name={id} checked={val} onChange={
            (e)=>(onNewVal(e.target.checked))} />
        <label className={checkClasses.labelClass} id={lblID}  name={lblID} htmlFor={id}>
        {checkClasses.label}
        </label>

    </div>
  )
}

export default Check