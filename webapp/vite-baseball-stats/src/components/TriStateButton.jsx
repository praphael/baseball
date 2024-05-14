import React from 'react'

const TriStateButton = ({btnname, lbl, btnTxt, onButtonChange}) => {

  const onBtnChange = (v) => {
    const msg = "btnname=" + btnname + " v=" + v + " lbl= " + lbl;
    // alert(msg);
    // console.log("btnname=", btnname, " v=", v)
    let nxt = "o";
    if (btnTxt == "o") nxt="x";
    else if (btnTxt == "x") nxt="?";
    onButtonChange(btnname, nxt); 
  }

  let cls = "btn";
  console.log("TriStateButton label=", lbl);
  if(btnTxt == "?")
    cls += " btn-outline-secondary";
  else if(btnTxt == "o")
    cls += " btn-outline-danger";
  else if(btnTxt == "x")
    cls += " btn-success";
  return (
    <div>
        <label className="me-2 ms-2"><h5>{lbl}</h5></label>
        <input type="button" className={cls} value={btnTxt}
          onClick={(e) => (onBtnChange(e.target.value))}/>
    </div>
  )
}

export default TriStateButton