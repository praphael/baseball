import React from 'react'

import { useState } from 'react'

import { doRequest } from '../js/requests.js'

const inputClass = "ml-2 col-8 form-input";

// map name to numeric ID
// can just use one universal players map and update
// as we get data, since data
// does not change - don't need useState hook
const playersMap = new Map();

// 
const PlayerInput = ({fieldName, label, onFiltChange}) => {
  const [playersList, setPlayersList] = useState([[]]);
  const [timeoutID, setTimeoutID] = useState(0);

  const onInputChange = async (evt) => {
      const plyrName = evt.target.value;
      const inh = evt.target.innerHTML;
      console.log("PlayerInput: onInputChange() plyrName=", plyrName);
      onFiltChange(fieldName, plyrName, false);
      
      if(plyrName.indexOf(")") >= 0) 
        return;
    
      console.log("PlayerInput plyrName", plyrName, " inh=", inh);
      const url = encodeURI("/player?" + plyrName);
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
            r.players.map((p) => { playersMap.set(p[0], p[1]); });
        }
      }, 1000);
      setTimeoutID(tID);
  }

  const onOptionSelect = (e) => {
    console.log("onOptionSelect ", e);
  }

  const id = fieldName + "_players";
  const fn_id = fieldName + "_input";
  return (
    <div>
        <h5>{label}</h5><label htmlFor={fn_id}>&#x1F50D;</label>
        <input className={inputClass} type="text" list={id} id={fn_id} onChange={(e) => onInputChange(e)}/>
        <datalist id={id}>
        {playersList.map((p) => (
            <option onSelect={(e)=>(onOptionSelect(e))} 
                    value={p[0] + " (" + p[1] + ")"}>
            </option>)) }
        </datalist>
    </div>
  )
}

export default PlayerInput