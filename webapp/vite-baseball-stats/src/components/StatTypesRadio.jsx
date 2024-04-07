import React from 'react'

import { useState, useMemo } from 'react'

const StatTypesRadio = ({fieldName, label, options, val, 
    onStatRadioChange, radioClasses}) => {
    
    const onNewVal = (v, which) => {
        console.log("StatTypesRadio onNewVal: v=", v, " which=", which);
        onStatRadioChange(which);
    }

    console.log("val=", val)
    const id = "filter_"+{fieldName}
    const opt0_lbl = options[0];
    const opt1_lbl = options[1];
    const opt2_lbl = options[2];
    const opt3_lbl = options[3];
    const opt4_lbl = options[4];
    const opt5_lbl = options[5];
    const id0 = "btn" + options[0];
    const id1 = "btn" + options[1];
    const id2 = "btn" + options[2];
    const id3 = "btn" + options[3];
    const id4 = "btn" + options[4];
    const id5 = "btn" + options[5];
    const btnname= "btnradio" + fieldName;
    return (
        <div className={radioClasses.divClass} id={id}>
            <label className={radioClasses.labelClass}>{label}</label>
            <div className="btn-group" role="group" aria-label={`"${fieldName} button group"`}
                  id={id+"_radio"}>
                <input type="radio" className="btn-check" name={btnname} id={id0} value={val[0]}
                     onChange={(e)=>(onNewVal(e.target.value, options[0]))} autoComplete="off"
                     />
                <label className="btn btn-outline-primary" htmlFor={id0}>{opt0_lbl}</label>

                <input type="radio" className="btn-check" name={btnname} id={id1} value={val[1]}
                     onChange={(e)=>(onNewVal(e.target.value, options[1]))} autoComplete="off" 
                    />
                <label className="btn btn-outline-primary" htmlFor={id1}>{opt1_lbl}</label>

                <input type="radio" className="btn-check" name={btnname} id={id2} value={val[2]}
                    onChange={(e)=>(onNewVal(e.target.value, options[2]))} autoComplete="off"
                    />
                <label className="btn btn-outline-primary" htmlFor={id2}>{opt2_lbl}</label>

                <input type="radio" className="btn-check" name={btnname} id={id3} value={val[3]}
                     onChange={(e)=>(onNewVal(e.target.value, options[3]))} autoComplete="off" 
                    />
                <label className="btn btn-outline-primary" htmlFor={id3}>{opt3_lbl}</label>

                <input type="radio" className="btn-check" name={btnname} id={id4} value={val[4]}
                    onChange={(e)=>(onNewVal(e.target.value, options[4]))} autoComplete="off"
                    />
                <label className="btn btn-outline-primary" htmlFor={id4}>{opt4_lbl}</label>

                <input type="radio" className="btn-check" name={btnname} id={id5} value={val[5]}
                    onChange={(e)=>(onNewVal(e.target.value, options[5]))} autoComplete="off"
                    />
                <label className="btn btn-outline-primary" htmlFor={id5}>{opt5_lbl}</label>
                
            </div>
            {/* 
            <FilterGroupCheck fieldName={fieldName} initValue={initGroup} onChange={onChange}
            checkClass={checkClass} divClass={groupDivClass} labelClass={groupLabelClass}/>
            */ }
        </div>
    )

}

export default StatTypesRadio