const statTypesArr = ["R", "H", "BB", "E", "HR", 
                      "_R", "_H", "_BB", "_E", "_HR"];

const statSetDefault = new Set();
statSetDefault.add("R")
statSetDefault.add("H")
statSetDefault.add("_R")
statSetDefault.add("_H")

export { statTypesArr, statSetDefault }