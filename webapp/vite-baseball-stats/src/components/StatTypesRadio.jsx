import React from 'react'

import { useState, useEffect } from 'react'

const StatTypesRadio = ({fieldName, label, options, initValue, 
    initGroup, onChange, selectClass, divClass,
    labelClass, checkClass, groupDivClass, groupLabelClass}) => {
    
    const [val0, setVal0] = useState(false);
    const [val1, setVal1] = useState(false);
    const [val2, setVal2] = useState(false);
    const [val3, setVal3] = useState(false);
    const [val4, setVal4] = useState(false);
    const [val5, setVal5] = useState(false);
    
    const onNewVal = (v, which) => {
        console.log("StatTypesRadio onNewVal: v=", v, " which=", which);
        onChange(fieldName, which);
        setVal0(false);
        setVal1(false);
        setVal2(false);
        setVal3(false);
        setVal4(false);
        setVal5(false);
        if(which == options[0]) setVal0(true);
        else if(which == options[1]) setVal1(true);
        else if(which == options[2]) setVal2(true);
        else if(which == options[3]) setVal3(true);
        else if(which == options[4]) setVal4(true);
        else if(which == options[5]) setVal4(true);
        onChange(which);
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

    console.log("options=", options)
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
        <div id={id}>
            <label className={labelClass}>{label}</label>
            <div className="btn-group" role="group" aria-label={`"${fieldName} button group"`}
                  id={id+"_radio"}>
                <input type="radio" className="btn-check" name={btnname} id={id0} 
                     onChange={(e)=>(onNewVal(e.target.value, options[0]))} autoComplete="off"
                     />
                <label className="btn btn-outline-primary" htmlFor={id0}>{opt0_lbl}</label>

                <input type="radio" className="btn-check" name={btnname} id={id1} 
                     onChange={(e)=>(onNewVal(e.target.value, options[1]))} autoComplete="off" 
                    />
                <label className="btn btn-outline-primary" htmlFor={id1}>{opt1_lbl}</label>

                <input type="radio" className="btn-check" name={btnname} id={id2} 
                    onChange={(e)=>(onNewVal(e.target.value, options[2]))} autoComplete="off"
                    />
                <label className="btn btn-outline-primary" htmlFor={id2}>{opt2_lbl}</label>

                <input type="radio" className="btn-check" name={btnname} id={id3} 
                     onChange={(e)=>(onNewVal(e.target.value, options[3]))} autoComplete="off" 
                    />
                <label className="btn btn-outline-primary" htmlFor={id3}>{opt3_lbl}</label>

                <input type="radio" className="btn-check" name={btnname} id={id4} 
                    onChange={(e)=>(onNewVal(e.target.value, options[4]))} autoComplete="off"
                    />
                <label className="btn btn-outline-primary" htmlFor={id4}>{opt4_lbl}</label>

                <input type="radio" className="btn-check" name={btnname} id={id5} 
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