import React from 'react'
import { useEffect, useState } from 'react'

import { boxScoreFiltOpts, boxScoreFiltDefaults,
         filterFields, orderDefaults } from '../js/filters.js'
import { statTypesArr } from '../js/stats.js'
import NumberInputWithCheck from './NumberInputWithCheck.jsx'
import OptionWithCheck from './OptionWithCheck.jsx'
import AccordionHeader from './AccordionHeader.jsx'

const boxScoreFilt = { ...boxScoreFiltDefaults };

const optionInputDivClass = "row mb-1 mt-1"; // border border-secondary
const selectClass = "col-4 form-select";
const inputClass = "col-8 form-input";
const optionInputLabelClass = "form-label"
const optionClasses = { divClass:optionInputDivClass, selectClass, labelClass:optionInputLabelClass } 
const numberInputClasses = { divClass:optionInputDivClass, inputClass, labelClass:optionInputLabelClass }
const checkDivClass = "col-1 form-check mb-2";
const checkClass = "col-2 ms-1 form-check-input";
const checkLabelClass= "form-check-label"
const checkClasses = { divClass:checkDivClass, checkClass, labelClass:checkLabelClass, label:"Group" }
const checkClassesOrder = { divClass:checkDivClass, checkClass, labelClass:checkLabelClass, label:"Ascending" }

const BoxScoreFilters = ({filter, setFilter, order, setOrder, updateData}) => {
  useEffect(() => {
    // initial value for filter
    setFilter(boxScoreFilt);
    setOrder(orderDefaults);
  }, [])

  const onFiltChange = (field, value, isGroup) => {
    console.log("onFiltChange field=", field, "value=", value);
    console.log("onFiltChange filter=", filter);
    try {
      // true if called from group check, else undefined
      if(isGroup) {
          if(value)
            filter.group.add(field);
          else
            filter.group.delete(field);
      }
      else filter.values.set(field, value);
      setFilter(filter);
      // updateData();
    } catch(e) { console.log("Could not set filter ", e)}
  }

  const onOrderChange = (field, value, isAsc) => {
    console.log("onOrderChange  field=", field, " value=", value);
    try {
      const ord = parseInt(field[5])
      console.log("onOrderChange ord=", ord, " isAsc=", isAsc);
      // true if called from ascending check, else undefined
      if(isAsc) {
        console.log("setting ord[1] to", value);
        order[ord][1] = value;
      } else {
        order[ord][0] = value;
      }
      setOrder(order);
      // updateData();
    } catch(e) { console.log("Could not set order ", e)}
  }

  const orderFields = new Array()
  orderFields.push(...filterFields)
  orderFields.push(...statTypesArr)
  

//  console.log("boxScoreFilt.values= ", boxScoreFilt.values);
//  console.log("boxScoreFilt.group= ", boxScoreFilt.group);

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
            initValue={boxScoreFilt.values.get("team")} 
            initCheck={boxScoreFilt.group.has("team")}  
            onChange={onFiltChange} 
            optionClasses={optionClasses}
            checkClasses={checkClasses}/>
        <NumberInputWithCheck fieldName="year" label="Year" 
            initValue={boxScoreFilt.values.get("year")}
            initCheck={boxScoreFilt.group.has("year")}   
            onChange={onFiltChange}
            numberInputClasses={numberInputClasses}
            checkClasses={checkClasses} />
        <OptionWithCheck fieldName="month" label="Month" options={boxScoreFiltOpts.months} 
            initValue={boxScoreFilt.values.get("month")}
            initCheck={boxScoreFilt.group.has("month")}
            onChange={onFiltChange} 
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
        { /* home/away */ }
        <OptionWithCheck fieldName="homeaway" label="Home/Away" 
          options={boxScoreFiltOpts.homeAway} 
          initValue={boxScoreFilt.values.get("homeaway")}
          initCheck={boxScoreFilt.group.has("homeaway")}
          onChange={onFiltChange} 
          optionClasses={optionClasses}
          checkClasses={checkClasses} />
            </div>
          </div>
        </div>
        <div className="accordion-item">
          <AccordionHeader dataBsTarget="#collapseTwo"
              ariaControls="collapseTwo" label="Other Filters"/>
          <div id="collapseTwo" className="accordion-collapse collapse show" 
            aria-labelledby="headingOne" data-bs-parent="#filtersAccordion">
            <div className="accordion-body">
        { /* AL/NL */ }
        <OptionWithCheck fieldName="league" label="League" 
          options={boxScoreFiltOpts.league} 
          initValue={boxScoreFilt.values.get("league")}
          initCheck={boxScoreFilt.group.has("league")}
          onChange={onFiltChange}
          optionClasses={optionClasses}
          checkClasses={checkClasses} />
        { /* day of week */ }
        <OptionWithCheck fieldName="dow" label="Day" options={boxScoreFiltOpts.daysOfWeek} 
            initValue={boxScoreFilt.values.get("dow")} 
            initCheck={boxScoreFilt.group.has("dow")}
            onChange={onFiltChange} 
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
        { /* park */ }
        <OptionWithCheck fieldName="park" label="Park" options={boxScoreFiltOpts.parks} 
            initValue={boxScoreFilt.values.get("park")} 
            initCheck={boxScoreFilt.group.has("park")}
            onChange={onFiltChange} 
            optionClasses={optionClasses}
            checkClasses={checkClasses} />
          </div>
          </div>
        </div>
        <div className="accordion-item">
          <AccordionHeader dataBsTarget="#collapseThree"
              ariaControls="collapseThree" label="Ordering"/>
          <div id="collapseThree" className="accordion-collapse collapse show" 
            aria-labelledby="headingOne" data-bs-parent="#filtersAccordion">
            <div className="accordion-body">
            { /* First Order  */ }
        <OptionWithCheck fieldName="order0" label="First" 
          options={orderFields} 
          initValue={orderFields[0][1]}
          initCheck={false}
          onChange={onOrderChange}
          optionClasses={optionClasses}
          checkClasses={checkClassesOrder} />
        { /* Second order */ }
        <OptionWithCheck fieldName="order1" label="Second" 
            options={orderFields} 
            initValue={orderFields[1][1]} 
            initCheck={true}
            onChange={onOrderChange} 
            optionClasses={optionClasses}
            checkClasses={checkClassesOrder} />
        { /* Third order */ }
        <OptionWithCheck fieldName="order2" label="Third" 
            options={orderFields} 
            initValue={orderFields[2][1]} 
            initCheck={false}
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
