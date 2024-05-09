import React from 'react'

const RadioBtn = ({btnname, id, lbl, opt, onRadioChange, isChecked}) => {
    //console.log("RadioBtn opt=", opt, " isChecked=", isChecked);
    if (isChecked)
        return <>
            <input type="radio" className="btn-check" name={btnname} id={id} value={opt} checked
                            onChange={(e)=>(onRadioChange(opt))} autoComplete="off"
                            />
            <label className="btn btn-outline-primary" htmlFor={id}>{lbl}</label>
        </>
    else
        return <>
            <input type="radio" className="btn-check" name={btnname} id={id} value={opt}
                            onChange={(e)=>(onRadioChange(opt))} autoComplete="off"
                            />
            <label className="btn btn-outline-primary" htmlFor={id}>{lbl}</label>
        </>
}
const RadioButtonGroup = ({fieldName, label, options, val, 
    onRadioChange, radioClasses}) => {

    //console.log("RadioButtonGroup val=", val)
    const id = "radio_"+{fieldName}
    const btnname= "btnradio" + fieldName;
    return (
        <div className={radioClasses.divClass} id={id}>
            <label className={radioClasses.labelClass}>{label}</label>
            <div className="btn-group" role="group" aria-label={`"${fieldName} button group"`}
                  id={id+"_radio"} value={val}>
                { options.map((o)=>(<RadioBtn key={o[1]} btnname={btnname} 
                     id={o[1]+"_id"} lbl={o[0]} opt={o[1]} onRadioChange={onRadioChange} 
                     isChecked={val==o[1]}/>)) }
            </div>            
        </div>
    )

}

export default RadioButtonGroup