import React from 'react'

import { filterFields } from '../js/filters.js'
import { statTypesArr } from '../js/stats.js'
import NumberInputWithCheck from './NumberInputWithCheck.jsx'
import OptionWithCheck from './OptionWithCheck.jsx'
import OptionRangeWithCheck from './OptionRangeWithCheck.jsx'
import AccordionHeader from './AccordionHeader.jsx'

const optionInputDivClass = "row mb-1 mt-1"; // border border-secondary
const selectClass = "col-4 form-select";
const inputClass = "ml-2 col-8 form-input";
const optionInputLabelClass = "form-label"
const optionClasses = { divClass:optionInputDivClass, selectClass, labelClass:optionInputLabelClass } 
const numberInputClasses = { divClass:optionInputDivClass, inputClass, labelClass:optionInputLabelClass }
const checkDivClass = "col-1 form-check mb-2";
const checkClass = "col-2 ms-1 form-check-input";
const checkLabelClass= "form-check-label"
const checkClasses = { divClass:checkDivClass, checkClass, labelClass:checkLabelClass, label:"Group" }
const checkClassesOrder = { divClass:checkDivClass, checkClass, labelClass:checkLabelClass, label:"Highest first" }

const BoxScoreFilters = ({boxScoreFiltOpts, filter, onFiltChange, order, onOrderChange, updateData}) => {

  const orderFields = new Array()
  orderFields.push(...filterFields)
  orderFields.push(...statTypesArr)
  

  console.log("BoxScoreFilters filter=", filter);
  console.log("BoxScoreFilters filter.group=", filter.group);


//  console.log("boxScoreFilt.values= ", boxScoreFilt.values);
//  console.log("boxScoreFilt.group= ", boxScoreFilt.group);
  console.log("order= ", order);
  return (
    <div className="container">
        <div className="accordion" id="filtersAccordion">
          <div className="accordion-item">
            <AccordionHeader dataBsTarget="#collapseOne"
              ariaControls="collapseOne" label="Basic Filters"/>
            
            <div id="collapseOne" className="accordion-collapse collapse show" 
              aria-labelledby="headingOne" data-bs-parent="#filtersAccordion">
              <div className="accordion-body">
        <OptionWithCheck fieldName="team" label="Team" options={boxScoreFiltOpts.teams} 
            val={filter.values.get("team")}
            checkVal={filter.group.has("team")} 
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses}/>
        <OptionRangeWithCheck fieldName="year" label="Years" options={boxScoreFiltOpts.years} 
            valLow={filter.values.get("yearlow")}
            valHigh={filter.values.get("yearhigh")}
            checkVal={filter.group.has("year")} 
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses}/>
        <OptionWithCheck fieldName="month" label="Month" options={boxScoreFiltOpts.months}
            val={filter.values.get("month")}
            checkVal={filter.group.has("month")}
            onChange={onFiltChange}
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
        { /* home/away */ }
        <OptionWithCheck fieldName="homeaway" label="Home/Away"
          options={boxScoreFiltOpts.homeAway}
          val={filter.values.get("homeaway")}
          checkVal={filter.group.has("homeaway")}
          onChange={onFiltChange}
          optionClasses={optionClasses}
          checkClasses={checkClasses} />
            </div>
          </div>
        </div>
        <div className="accordion-item">
          <AccordionHeader dataBsTarget="#collapseTwo"
              ariaControls="collapseTwo" label="Other Filters"/>
          <div id="collapseTwo" className="accordion-collapse collapse" 
            aria-labelledby="headingOne" data-bs-parent="#filtersAccordion">
            <div className="accordion-body">
        { /* AL/NL */ }
        <OptionWithCheck fieldName="league" label="League" 
          options={boxScoreFiltOpts.league} 
          val={filter.values.get("league")}
          checkVal={filter.group.has("league")}
          onChange={onFiltChange}
          optionClasses={optionClasses}
          checkClasses={checkClasses} />
        { /* day of week */ }
        <OptionWithCheck fieldName="dow" label="Day" options={boxScoreFiltOpts.daysOfWeek} 
            val={filter.values.get("dow")} 
            checkVal={filter.group.has("dow")}
            onChange={onFiltChange} 
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
        { /* park */ }
        <OptionWithCheck fieldName="park" label="Park" options={boxScoreFiltOpts.parks} 
            val={filter.values.get("park")} 
            checkVal={filter.group.has("park")}
            onChange={onFiltChange} 
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
          </div>
          </div>
        </div>
        <div className="accordion-item">
          <AccordionHeader dataBsTarget="#collapseThree"
              ariaControls="collapseThree" label="Ordering"/>
          <div id="collapseThree" className="accordion-collapse collapse" 
            aria-labelledby="headingOne" data-bs-parent="#filtersAccordion">
            <div className="accordion-body">
            { /* First Order  */ }
        <OptionWithCheck fieldName="order0" label="First" 
          options={orderFields} 
          val={order[0][0]}
          checkVal={order[0][1]}
          onChange={onOrderChange}
          optionClasses={optionClasses}
          checkClasses={checkClassesOrder} />
        { /* Second order */ }
        <OptionWithCheck fieldName="order1" label="Second" 
            options={orderFields} 
            val={order[1][0]} 
            checkVal={order[1][1]}
            onChange={onOrderChange} 
            optionClasses={optionClasses}
            checkClasses={checkClassesOrder} />
        { /* Third order */ }
        <OptionWithCheck fieldName="order2" label="Third" 
            options={orderFields} 
            val={order[2][0]} 
            checkVal={order[2][1]}
            onChange={onOrderChange} 
            optionClasses={optionClasses}
            checkClasses={checkClassesOrder} />

            </div>
          </div>
        </div>
      </div>
    </div>

  )
}

export default BoxScoreFilters
