import React from 'react'

const Results = ({resultsTable, divClassName}) => {
  const renderHTML = (r) => {
    if (r == "")
      r = "(no data)"
    return {__html: r};
  };

  return (
    <div className={divClassName} dangerouslySetInnerHTML={renderHTML(resultsTable)}>
    </div>
  )
}

export default Results