import React from 'react'

import OptionWithCheck from './OptionWithCheck'

const Ordering = ({orderFields, order, onOrderChange, optionClasses, checkClassesOrder}) => {
  return (
    <div>
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
  )
}

export default Ordering