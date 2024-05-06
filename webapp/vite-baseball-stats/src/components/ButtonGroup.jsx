import React from 'react'

const GroupBtn = ({btnname, id, lbl, opt, onButtonChange, isChecked}) => {
    console.log("GroupBtn opt=", opt, " isChecked=", isChecked);
    if (isChecked)
        return <>
            <input type="checkbox" className="btn-check" name={btnname} id={id} value={opt} checked
                            onChange={(e)=>(onButtonChange(opt, e.target.checked))} autoComplete="off"
                            />
            <label className="btn btn-outline-primary" htmlFor={id}>{lbl}</label>
        </>
    else
        return <>
            <input type="checkbox" className="btn-check" name={btnname} id={id} value={opt}
                            onChange={(e)=>(onButtonChange(opt, e.target.checked))} autoComplete="off"
                            />
            <label className="btn btn-outline-primary" htmlFor={id}>{lbl}</label>
        </>
}

const ButtonGroup = ({fieldName, label, options, valMap, 
    onButtonChange, buttonClasses}) => {

    console.log("valMap=", valMap);
    const id = "group_"+{fieldName}
    const btnname= "btngroup" + fieldName;
    return (
        <div className={buttonClasses.divClass} id={id}>
            <span><label className={buttonClasses.labelClass}><h5>{label}</h5></label></span>
            <div className="btn-group" role="group" aria-label={`"${fieldName} button group"`}
                    id={id+"_group"}>
                { options.map((o)=>(<GroupBtn key={o[1]} btnname={btnname} 
                        id={o[1]+"_id"} lbl={o[0]} opt={o[1]} onButtonChange={onButtonChange} 
                        isChecked={valMap.get(o[1])}/>)) }
            </div>            
        </div>
    )
}

export default ButtonGroup