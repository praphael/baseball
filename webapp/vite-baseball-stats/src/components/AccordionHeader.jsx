import React from 'react'

const AccordionHeader = ({ariaControls, dataBsTarget, label}) => {
  return (
    <h3 className="accordion-header" id="headingOne">
        <button className="accordion-button" type="button" 
        data-bs-toggle="collapse" data-bs-target={dataBsTarget}
        aria-expanded="true" aria-controls={ariaControls}>
        {label}
        </button>
    </h3>
  )
}

export default AccordionHeader