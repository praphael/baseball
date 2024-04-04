import React from 'react'

import { useState, useEffect } from 'react'
import FilterGroupCheck from './FilterGroupCheck';

const FilterRadio = ({fieldName, label, options, initValue, 
    initGroup, onChange, selectClass, divClass,
    labelClass, checkClass, groupDivClass, groupLabelClass}) => {
    
    const [val0, setVal0] = useState(false);
    const [val1, setVal1] = useState(false);
    const [val2, setVal2] = useState(false);
    
    const onNewVal = (v, which) => {
        console.log("FilterRadio onNewVal: v=", v, " which=", which);
        onChange(fieldName, which);
        if(which == options[0]) setVal0(true);
        else if(which == options[1]) setVal1(true);
        else if(which == options[2]) setVal2(true);
    }

    useEffect(() => {
        // initial value for filter
        onNewVal(true, initValue);
      }, [])

    const onRadioChange = (e) => {
        console.log("FilterRadio onGroupChange: e=", e);
        //onChange(fieldName, v);
        //setVal(v);
    }

    const id = "filter_"+{fieldName}
    const opt0_lbl = options[0];
    const opt1_lbl = options[1];
    const opt2_lbl = options[2];
    const id0 = "btn" + options[0];
    const id1 = "btn" + options[1];
    const id2 = "btn" + options[2];
    const btnname= "btnradio" + fieldName;
    return (
        <div className={divClass} id={id}>
            <label className={labelClass}>{label}</label>
            <div className="btn-group" role="group" aria-label={`"${fieldName} button group"`}
                 onChange={(e)=>(onRadioChange(e))} id={id+"_radio"}>
                    { /*  */ }
                <input type="radio" className="btn-check" name={btnname} id={id0} 
                     onChange={(e)=>(onNewVal(e.target.value, options[0]))} autoComplete="off"
                     checked={val0}/>
                <label className="btn btn-outline-primary" htmlFor={`"btn${options[0]}"`}>{opt0_lbl}</label>

                <input type="radio" className="btn-check" name={btnname} id={id1} 
                    onChange={(e)=>(onNewVal(e.target.value, options[1]))} autoComplete="off" 
                    checked={val1}/>
                <label className="btn btn-outline-primary" htmlFor={`"btn${options[1]}"`}>{opt1_lbl}</label>

                <input type="radio" className="btn-check" name={btnname} id={id2} 
                    onChange={(e)=>(onNewVal(e.target.value, options[2]))} autoComplete="off"
                    checked={val2}/>
                <label className="btn btn-outline-primary" htmlFor={`"btn${options[2]}"`}>{opt2_lbl}</label>
                
            </div>
            <FilterGroupCheck fieldName={fieldName} initValue={initGroup} onChange={onChange}
            checkClass={checkClass} divClass={groupDivClass} labelClass={groupLabelClass}/>
        </div>
    )

}

export default FilterRadio