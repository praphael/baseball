import React from 'react'
import { useState } from 'react'

import FilterGroupCheck from './FilterGroupCheck';

const FilterOption = ({fieldName, label, options, initValue, 
                       initGroup, onChange, selectClass, divClass,
                       labelClass, checkClass, groupDivClass, groupLabelClass}) => {
    const [val, setVal] = useState(initValue);

    const onNewVal = (v) => {
        onChange(fieldName, v);
        setVal(v);
    }
    const id = `"filter_${fieldName}"`;
    return (
        <div className={divClass}>
            <label className={labelClass} htmlFor={id}>{label}:
            <select className={selectClass} id={id} value={val} onChange={ (e)=> (onNewVal(e.target.value))}>
                <option value="">(all)</option>
                { options.map((opt)=> (<option key={opt[0]} value={opt[0]}>{opt[1]}</option>)) }
            </select>
            </label>
            <FilterGroupCheck fieldName={fieldName} initValue={initGroup} onChange={onChange}
                              checkClass={checkClass} divClass={groupDivClass} labelClass={groupLabelClass}/>
        </div>
    )
}

export default FilterOption