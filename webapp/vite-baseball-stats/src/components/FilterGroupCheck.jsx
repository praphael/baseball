import React from 'react'
import { useState } from 'react'

const FilterGroupCheck = ({fieldName, initValue, onChange}) => {
  const [val, setVal] = useState(initValue);

  const onNewVal = (v) => {
    onChange(fieldName, v, true);
    setVal(v);
  }
  // console.log("FilterGroupCheck ", fieldName, " initValue=", initValue)
  const id = `"filter_${fieldName}_group"`;
  return (
    <div>
        <input type="checkbox" id={id} checked={val} onChange={
            (e)=>(onNewVal(e.target.checked))} />
        <label htmlFor={id}>Group</label>
    </div>
  )
}

export default FilterGroupCheck