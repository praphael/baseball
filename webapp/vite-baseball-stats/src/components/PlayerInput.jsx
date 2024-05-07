import React from 'react'

import { useState } from 'react'

import { doRequest } from '../js/requests.js'

// 
const PlayerInput = ({fieldName, onChange}) => {
  const [playersList, setPlayersList] = useState([[]]);
  const [tLast, settLast] = useState(Date.now())
  const [timeoutID, setTimeoutID] = useState(0)

  const onInputChange = async (evt) => {
      const qy = evt.target.value;
      const inh = evt.target.innerHTML;
      console.log("PlayerInput qy", qy, " inh=", inh);
      const url = encodeURI("/player?" + qy);
      if (timeoutID != 0) {
        clearTimeout(timeoutID);
      }
      const tID = setTimeout(async () => {
        const r = await doRequest(url, 'GET', null, "", "json", null, (e) => {
            alert(`Get Data:  status ${e.status} error: ${e.error}`); 
        }); 
        // console.log("updateData r=", r);
        if(r != null) {
            console.log(r.players);
            setPlayersList(r.players);
        }
      }, 1000);
      setTimeoutID(tID);

  }

  const onOptionSelect = (e) => {
    console.log("onOptionSelect ", e);
  }

  const id = fieldName + "_players";
  return (
    <div>
        <label><h5>{fieldName}</h5> &#x1F50D;</label>
        <input type="text" list={id} onChange={(e) => onInputChange(e)}/>
        <datalist id={id}>
        {playersList.map((p) => (
            <option onSelect={(e)=>(onOptionSelect(e))} 
                    value={p[0]}>{p[1]}
            </option>)) }
        </datalist>
    </div>
  )
}

export default PlayerInput