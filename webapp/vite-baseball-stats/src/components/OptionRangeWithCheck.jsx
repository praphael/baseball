import React from 'react'
import { useState } from 'react'

import Check from './Check';

const OptionRangeWithCheck = ({fieldName, label, options, valLow, valHigh,
                       checkVal, onChange, optionClasses,
                       checkClasses}) => {
    const onNewVal = (v, lowHigh) => {
        const fName = fieldName + lowHigh;
        onChange(fName, v);
    }
    //console.log("OptionWithCheck val=", val, " checkVal=", checkVal)
    const idLow = `"filter_${fieldName}_low"`;
    const idHigh = `"filter_${fieldName}_low"`;
    return (
        <div className={optionClasses.divClass}>
            <h5 className={optionClasses.labelClass} htmlFor={idLow}>{label}:</h5>
            <div className="container">
                <div className="row">
                    <div className="col-auto">
                        
                        <select className={optionClasses.selectClass} id={idLow} value={valLow} 
                            onChange={ (e)=> (onNewVal(e.target.value, "low"))}>
                            <option value="">(all)</option>
                            { options.map((opt)=> (<option key={opt[1]} value={opt[1]}>{opt[0]}</option>)) }
                        </select>
                    </div>
                    <span className="col-auto"><label>to</label></span>
                    <div className="col-auto">
                        <select className={optionClasses.selectClass} id={idHigh} value={valHigh} 
                            onChange={ (e)=> (onNewVal(e.target.value, "high"))}>
                            <option value="">(all)</option>
                            { options.map((opt)=> (<option key={opt[1]} value={opt[1]}>{opt[0]}</option>)) }
                        </select>
                    </div>
                </div>
            </div>
            <Check fieldName={fieldName} val={checkVal} onChange={onChange}
                              checkClasses={checkClasses}/>
        </div>
    )
}

export default OptionRangeWithCheck