function btnClk(){
  document.getElementById("result").innerHTML += "test"+"</br>";
}

function addTable(res?:string[]){
  var range= 1;
  for(var i=0;i<range;i++){
    document.getElementById("result-table").innerHTML +="<li class='list-group-item'>"+"RESULT"+"</li>";
  }
}

function clearTable(res?:string[]){
  var range= 1;
  for(var i=0;i<range;i++){
    document.getElementById("result-table").innerHTML ="";
  }
}
