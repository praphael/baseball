import React from 'react'

import { useState } from 'react'
import { filterFields } from '../js/filters.js'
import { statTypesArr } from '../js/stats.js'
import OptionWithCheck from './OptionWithCheck.jsx'
import OptionRangeWithCheck from './OptionRangeWithCheck.jsx'
import RadioButtonGroup from './RadioButtonGroup.jsx'
import ButtonGroup from './ButtonGroup.jsx'
import AccordionHeader from './AccordionHeader.jsx'
import ConditionFilters from './ConditionFilters.jsx'
import SituationFilters from './SituationFilters.jsx'
import OutcomeFilters from './OutcomeFilters.jsx'
import TimeFilters from './TimeFilters.jsx'
import PlaceFilters from './PlaceFilters.jsx'
import Ordering from './Ordering.jsx'
import WhoFilters from './WhoFilters.jsx'

const optionInputDivClass = "mb-1 mt-1"; // border border-secondary
const selectClass = "col-4 form-select";
const inputClass = "ml-2 col-8 form-input";
const optionInputLabelClass = "form-label"
const optionClasses = { divClass:optionInputDivClass, selectClass, labelClass:optionInputLabelClass } 
const checkDivClass = "form-check form-check-inline mb-2";
const checkClass = " ms-1 me-1 form-check-input";
const checkLabelClass= "form-check-label"
const checkClasses = { divClass:checkDivClass, checkClass, labelClass:checkLabelClass, label:"Group" }
const checkClassesOrder = { divClass:checkDivClass, checkClass, labelClass:checkLabelClass, label:"Highest first" }
const orderFields = new Array();
orderFields.push(...filterFields);
orderFields.push(...statTypesArr);

const filterSections = [["Time", "time"], ["Who", "who"], ["Place", "place"], 
                        ["Condition", "condition"], ["Situation", "situation"],
                        ["Outcome", "outcome"], ["Order", "order"]];
const BoxScoreFilters = ({boxScoreFiltOpts, filter, onFiltChange, order, onOrderChange}) => {
  const [filtSection, setFiltSection] = useState("basic");

  console.log("BoxScoreFilters filter=", filter);
  console.log("BoxScoreFilters filter.group=", filter.group);

  const onFiltSectChange = (opt) => {
    setFiltSection(opt);
  }
//  console.log("boxScoreFilt.values= ", boxScoreFilt.values);
//  console.log("boxScoreFilt.group= ", boxScoreFilt.group);
  console.log("order= ", order);
  return (
    <div className="container">
      <div className="row">
          <RadioButtonGroup fieldName="filter_section" label="" options={filterSections}
            val={filtSection} onRadioChange={onFiltSectChange} />
      </div>
      <div className="row">
          { filtSection == "time" ? <TimeFilters filter={filter} boxScoreFiltOpts={boxScoreFiltOpts}
              onFiltChange={onFiltChange} optionClasses={optionClasses} checkClasses={checkClasses} /> : "" }
          { filtSection == "who" ? <WhoFilters filter={filter} boxScoreFiltOpts={boxScoreFiltOpts}
              onFiltChange={onFiltChange} optionClasses={optionClasses} checkClasses={checkClasses} />  : ""  }
          { filtSection == "place" ? <PlaceFilters filter={filter} boxScoreFiltOpts={boxScoreFiltOpts}
              onFiltChange={onFiltChange} optionClasses={optionClasses} checkClasses={checkClasses} />  : ""  }
          { filtSection == "condition" ?  <ConditionFilters filter={filter} boxScoreFiltOpts={boxScoreFiltOpts}
              onFiltChange={onFiltChange} optionClasses={optionClasses} checkClasses={checkClasses} />  : ""  }
          { filtSection == "situation" ? <SituationFilters filter={filter} boxScoreFiltOpts={boxScoreFiltOpts}
              onFiltChange={onFiltChange} optionClasses={optionClasses} checkClasses={checkClasses} />  : ""  }
          { filtSection == "outcome" ? <OutcomeFilters filter={filter} boxScoreFiltOpts={boxScoreFiltOpts}
              onFiltChange={onFiltChange} optionClasses={optionClasses} checkClasses={checkClasses} />  : ""  }
          { filtSection == "order" ? <Ordering orderFields={orderFields} order={order} onOrderChange={onOrderChange}
              optionClasses={optionClasses} checkClassesOrder={checkClassesOrder} />  : ""  }
      </div>
    </div>

  )
}

export default BoxScoreFilters
