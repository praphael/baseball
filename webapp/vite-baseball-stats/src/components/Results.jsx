import React from 'react'

const Results = ({resultsTable, divClassName}) => {
  const renderHTML = (r) => {
    if (r == "")
      r = "(no data)"
    return {__html: r};
  };

  const divStyle = { transform: "rotateX(180deg)", overflowX: "auto" }
  const spanStyle = { transform: "rotateX(180deg)" }
  return (
    <div style={divStyle}>
    <div style={spanStyle}>
    <span className={divClassName} dangerouslySetInnerHTML={renderHTML(resultsTable)}>
    </span>
    </div>
    </div>
  )
}

export default Results