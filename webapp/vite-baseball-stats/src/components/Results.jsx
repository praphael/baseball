import React from 'react'

const Results = ({resultsTable}) => {
  const renderHTML = (r) => {
    return {__html: r};
  };

  return (
    <div dangerouslySetInnerHTML={renderHTML(resultsTable)}>
    </div>
  )
}

export default Results