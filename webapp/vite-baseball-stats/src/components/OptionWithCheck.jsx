import React from 'react'
import { useState } from 'react'

import Check from './Check';

const OptionWithCheck = ({fieldName, label, options, initValue, 
                       initCheckVal, onChange, optionClasses,
                       checkClasses}) => {
    const [val, setVal] = useState(initValue);

    const onNewVal = (v) => {
        onChange(fieldName, v);
        setVal(v);
    }
    // console.log("OptionWithCheck initValue=", initValue)
    const id = `"filter_${fieldName}"`;
    return (
        <div className={optionClasses.divClass}>
            <h5 className={optionClasses.labelClass} htmlFor={id}>{label}:
            <select className={optionClasses.selectClass} id={id} value={val} onChange={ (e)=> (onNewVal(e.target.value))}>
                <option value="">(all)</option>
                { options.map((opt)=> (<option key={opt[1]} value={opt[1]}>{opt[0]}</option>)) }
            </select>
            </h5>
            <Check fieldName={fieldName} initValue={initCheckVal} onChange={onChange}
                              checkClasses={checkClasses}/>
        </div>
    )
}

export default OptionWithCheck