import React from 'react'
import TriStateButton from './TriStateButton';

const TriStateButtonGroup = ({fieldName, label, val, onButtonChange, buttonClasses}) => {
  const id = "tristate_group_"+{fieldName}
  
  console.log("TriStateButtonGroup val=", val);
  return (
    <div>
        <span><label className={buttonClasses.labelClass}><h5>{label}</h5></label></span>
            <div className="btn-group" role="group" aria-label={`"${fieldName} tri-state button group"`}
                    id={id+"_group"}>
                { val.map((v)=>(<TriStateButton key={v[0]} btnname={v[0]} 
                        id={v[0]+"_id"} lbl={v[2]} btnTxt={v[1]} onButtonChange={onButtonChange}/>)) }
            </div>  
    </div>
  )
}

export default TriStateButtonGroup