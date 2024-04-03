import React from 'react'
import { useState } from 'react'
import FilterGroupCheck from './FilterGroupCheck';

const FilterNumberInput = ({fieldName, label, initValue, initGroup, 
                            onChange, divClass, inputClass, labelClass,
                            checkClass, groupDivClass, groupLabelClass}) => {
    const id = `"filter_${fieldName}"`;

    const [val, setVal] = useState(initValue);

    const onNewVal = (v) => {
        console.log("FilterNumberInput onNewVal() v=", v);
        onChange(fieldName, v);
        setVal(v);
    }

    return (
        <div className={divClass}>
            <label className={labelClass} htmlFor={id}>{label}:
            <input className={inputClass} type="text" id={id} value={val}
                onChange={(e)=>(onNewVal(e.target.value))} />
            </label>                
            <FilterGroupCheck fieldName={fieldName} initValue={initGroup} 
                onChange={onChange} checkClass={checkClass} 
                divClass={groupDivClass} labelClass={groupLabelClass}/>
        </div>
    )
}

export default FilterNumberInput