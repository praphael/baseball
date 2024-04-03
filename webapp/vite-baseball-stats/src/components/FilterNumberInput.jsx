import React from 'react'
import { useState } from 'react'
import FilterGroupCheck from './FilterGroupCheck';

const FilterNumberInput = ({fieldName, label, initValue, initGroup, onChange}) => {
    const id = `"filter_${fieldName}"`;

    const [val, setVal] = useState(initValue);

    const onNewVal = (v) => {
        console.log("FilterNumberInput onNewVal() v=", v);
        onChange(fieldName, v);
        setVal(v);
    }

    return (
        <div>
            <label htmlFor={id}>{label}:</label>
            <input type="text" id={id} value={val}
                onChange={(e)=>(onNewVal(e.target.value))} />
            <FilterGroupCheck fieldName={fieldName} initValue={initGroup} 
                onChange={onChange} />
        </div>
    )
}

export default FilterNumberInput