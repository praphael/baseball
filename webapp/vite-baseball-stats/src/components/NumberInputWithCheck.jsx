import React from 'react'
import { useState } from 'react'
import Check from './Check';

const NumberInputWithCheck = ({fieldName, label, initValue, initGroup, 
                            onChange, numberInputClasses, checkClasses}) => {
    const id = `"filter_${fieldName}"`;

    const [val, setVal] = useState(initValue);

    const onNewVal = (v) => {
        console.log("NumberInputWithCheck onNewVal() v=", v);
        onChange(fieldName, v);
        setVal(v);
    }

    return (
        <div className={numberInputClasses.divClass}>
            <h5 className={numberInputClasses.labelClass} 
                htmlFor={id}>{label}:
            <input className={numberInputClasses.inputClass} 
                   type="text" id={id} value={val}
                   onChange={(e)=>(onNewVal(e.target.value))} />
            </h5>                
            <Check fieldName={fieldName} initValue={initGroup} 
                onChange={onChange} checkClasses={checkClasses}/>
        </div>
    )
}

export default NumberInputWithCheck