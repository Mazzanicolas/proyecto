/* Init alertas */


/*Checkeo de errores, validacion*/

$(document).ready(function(){
    $(document.getElementById("tiempoTransporteValidation")).change(function(){
        if(isNaN(document.getElementById("tiempoTransporteValidation").value))
            document.getElementById("tiempoTransporteValidation").className = "form-control is-invalid";
        else
            document.getElementById("tiempoTransporteValidation").className = "form-control is-valid";
    });
});

$(document).ready(function(){
    $(document.getElementById("tiempoConsultaValidation")).change(function(){
        if(isNaN(document.getElementById("tiempoConsultaValidation").value))
            document.getElementById("tiempoConsultaValidation").className = "form-control is-invalid";
        else
            document.getElementById("tiempoConsultaValidation").className = "form-control is-valid";
    });
});

$(document).ready(function(){
    $(document.getElementById("tiempoLlegaValidation")).change(function(){
        if(isNaN(document.getElementById("tiempoLlegaValidation").value))
            document.getElementById("tiempoLlegaValidation").className = "form-control is-invalid";
        else
            document.getElementById("tiempoLlegaValidation").className = "form-control is-valid";
    });
});

/* Hidden checbox */
$(document).ready(function(){
    $('#checkTransporte').change(function(){
        if(this.checked)
            $('#transporteDiv').hide();
        else
            $('#transporteDiv').show();
    });
});

$(document).ready(function(){
    $('#checkPrestador').change(function(){
        if(this.checked)
            $('#prestadorDiv').hide();
        else
            $('#prestadorDiv').show();
    });
});

$(document).ready(function(){
    $('#checkDiasEjecutar').change(function(){
        if(this.checked)
            $('#diasDivEjecutar').hide();
        else
            $('#diasDivEjecutar').show();
    });
});

$(document).ready(function(){
    $('#checkDiasSimular').change(function(){
        if(this.checked)
            $('#diasDivSimular').hide();
        else
            $('#diasDivSimular').show();
    });
});

/* Bloqueo de descarga*/
$(document).ready(function(){
    $(document.getElementById("cbCSV0")).change(function(){
        if(this.checked){
          document.getElementById("cbCSV").disabled = true;
          document.getElementById("cbCSV").checked = true;
        }
        else
          document.getElementById("cbCSV").disabled = false;
        });
    });

$(document).ready(function(){
    $(document.getElementById("cbCSV2")).change(function(){
        if(this.checked){
            document.getElementById("cbCSV1").disabled = true;
            document.getElementById("cbCSV1").checked = true;
        }
        else
            document.getElementById("cbCSV1").disabled = false;
    });
});
//Loading Bar
/*var loadingBar = new ProgressBar.Circle(loadingbar, {
    color: '#d6d7d8',
    // This has to be the same size as the maximum width to
    // prevent clipping
    strokeWidth: 7,
    trailWidth: 1,
    easing: 'easeInOut',
    duration: 2500,
    text: {
      autoStyleContainer: false
    },
    from: { color: '#4158d0', width: 2 },
    to: { color: '#c850c0', width: 5 },
    // Set default step function for all animate calls
    step: function(state, circle) {
      circle.path.setAttribute('stroke', state.color);
      circle.path.setAttribute('stroke-width', state.width);
  
      var value = Math.round(circle.value() * 100);
      if (value === 0) {
        circle.setText('¡Listo!');
      } else {
        circle.setText(String(value)+' %');
      }
  
    }
  });
  loadingBar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
  loadingBar.text.style.fontStyle = "italic"
  loadingBar.text.style.fontSize = '3rem';
*/
var bar = new ProgressBar.Circle(container, {
    color: '#d6d7d8',
    // This has to be the same size as the maximum width to
    // prevent clipping
    strokeWidth: 7,
    trailWidth: 1,
    easing: 'easeInOut',
    duration: 2500,
    text: {
      autoStyleContainer: false
    },
    from: { color: '#4158d0', width: 2 },
    to: { color: '#c850c0', width: 5 },
    // Set default step function for all animate calls
    step: function(state, circle) {
      circle.path.setAttribute('stroke', state.color);
      circle.path.setAttribute('stroke-width', state.width);
  
      var value = Math.round(circle.value() * 100);
      if (value === 0) {
        circle.setText('¡Listo!');
      } else {
        circle.setText(String(value)+' %');
      }
  
    }
  });
  bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
  bar.text.style.fontStyle = "italic"
  bar.text.style.fontSize = '3rem';

/*Consultas XML*/
/*
window.onload = askMatrizAutoStatusCheck();

function getMatrizAutoStatus(progressLoopMatrizAuto) {
    //console.log("XML CARGADO AUTO")
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var obj = JSON.parse(this.responseText);
            var saveStatus = ((obj['progressStatus']).toFixed(2));
            progressLoopMatrizAuto = setTimeout(function() { getMatrizAutoStatus(progressLoopMatrizAuto); }, 15000);
            //console.log(saveStatus);  
            saveStatus = parseFloat(saveStatus)      
            if(saveStatus>0){
                document.getElementById('container').style.visibility = 'visible';
                bar.animate(saveStatus)                
                document.getElementById('alertCargandoAutos').style.visibility = 'visible';
            }
            if(saveStatus>0.999){
                bar.animate(0)
                document.getElementById('container').style.visibility = 'visible';
                document.getElementById('alertCargandoAutos').style.visibility = 'hidden';
                clearTimeout(progressLoopMatrizAuto);
            }
            if(saveStatus<0){ 
                document.getElementById('container').style.visibility = 'hidden';
                document.getElementById('alertCargandoAutos').style.visibility = 'hidden';
                clearTimeout(progressLoopMatrizAuto);
            }
        }
    };
    xhttp.open("GET", "progressMatrizAuto/", true);
    xhttp.send();
    }

function askMatrizAutoStatusCheck(){
    var progressLoopMatrizAuto = setTimeout(function() { getMatrizAutoStatus(progressLoopMatrizAuto); }, 100);
}*/
/*sys*/
window.onload = systemStatus();

function systemStatus(){
    console.log("XML Checking System...");
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log("XML response 200 OK")
            var systemStatusResponse = JSON.parse(this.responseText);            
            workingProcessId = systemStatusResponse['loadingDataId'] //100 Si nada esta cargando //103 Si tiene algo cargado //0-8 Id del proceso cargando
            processStatus    = systemStatusResponse['status'] //Si se esta haciendo algo siempre >= 0.01
            console.log(workingProcessId);
            console.log(processStatus);
            eventHandler(workingProcessId,processStatus);
        }
    };
    xhttp.open("GET", "systemStatus/", true);
    xhttp.send();
}

function progressStatus(url){
    console.log("XML Checking Progress...");
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log("XMLP response 200 OK")
            var systemStatusResponse = JSON.parse(this.responseText);            
            processStatus = systemStatusResponse['status'] //Si se esta haciendo algo siempre >= 0.01
            return processStatus
        }
    };
    xhttp.open("GET", url, true);
    xhttp.send();
}

function eventHandler(workingProcessId, processStatus){
    switch(workingProcessId) {
        case 0:
            isEjecutnadoInit(processStatus);
            break;
        case 1:
            isSimulandoInit(processStatus);
            break;
        case 100:
            noFilesFoundInit(processStatus);
            break;
        case 103:
            filesFoundInit(processStatus);
            break;        
        case 2:
            isRecalculandoInit(processStatus);
            break;
        case 3:
            isCargandoPersonasInit(processStatus);
            break;
        case 4:
            isCargandoCentrosInit(processStatus);
            break;
        case 5:
            isCargandoPrestadoresInit(processStatus);
            break;
        case 6:
            isCargandoCaminandoInit(processStatus);
            break;
        case 7:
            isCargandoOmnibusInit(processStatus);
            break;
        case 8:
            isCargandoAutoInit(processStatus);
            break;
        default:
            console.log("Error no process id found");
    }
}

function isEjecutnadoInit(processStatus){
    console.log(typeof processStatus);
    bar.animate(processStatus);
    showAlert('alertEjecutando');
    showLoadingBar();
    daemonRequest(updateGUIejecutar);
}
function updateGUIejecutar(progressLoop){
    currentStatus = progressStatus('ejecutarProgress/')
    if(currentStatus>0.999){
        bar.animate(0);
        hdieAlert('alertEjecutando');
        clearTimeout(progressLoop);
        showDownloadButton();
    } else {
        bar.animate(currentStatus);
        progressLoop = setTimeout(function() { updateGUIejecutar(progressLoop); }, 10000);
    }
}
function isSimulandoInit(processStatus){}
function noFilesFoundInit(processStatus){
    hideLoadingBar();
    hiddeDownloadButton();    
}
function filesFoundInit(processStatus){
    showDownloadButton()
    bar.animate(0);
    showLoadingBar()
}
function isRecalculandoInit(processStatus){}
function isCargandoPersonasInit(processStatus){}
function isCargandoCentrosInit(processStatus){}
function isCargandoPrestadores(processStatus){}
function isCargandoCaminandoInit(processStatus){}
function isCargandoOmnibusInit(processStatus){}
function isCargandoAutoInit(processStatus){}

function daemonRequest(currentProcess){
    var progressLoop = setTimeout(function() { currentProcess(progressLoop); }, 100);
}

function showLoadingBar(){
    document.getElementById('container').style.visibility = 'visible';
}
function hideLoadingBar(){
    document.getElementById('container').style.visibility = 'hidden';
}
function showDownloadButton(){
    document.getElementById('descargar').style.visibility = 'visible';
    document.getElementById('alertCalculos').style.display = 'block';
}
function hiddeDownloadButton(){
    document.getElementById('descargar').style.visibility = 'hidden';
    document.getElementById('alertCalculos').style.display = 'none';
}
function showAlert(id){
    document.getElementById(id).style.display = 'block';
}
function hideAlert(id){
    document.getElementById(id).style.display = 'none';
}
/*sys*/
/*window.onload = calculate();

function ask2(progressLoop) {
    //console.log("XML CARGADO")
    var xhttp = new XMLHttpRequest();
    clearTimeout(progressLoop);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var obj = JSON.parse(this.responseText);
            var fileStatus = ((parseFloat(obj['Done'])/parseFloat(obj['Total']))).toFixed(2);
            //console.log(typeof fileStatus);        
            fileStatus = parseFloat(fileStatus);
            bar.animate(fileStatus); 
            progressLoop = setTimeout(function() { ask2(progressLoop); }, 10000);
            if(fileStatus>0){
                document.getElementById('container').style.visibility = 'visible';
            }
            if(fileStatus>0.999){
                bar.animate(0)
                downloadRedy();
                clearTimeout(progressLoop);
            }
            if(fileStatus<0){
                noFileInCache();
                clearTimeout(progressLoop);
            }
        }
    };
    xhttp.open("GET", "progress/", true);
    xhttp.send();
}

function calculate(){
    var progressLoop = setTimeout(function() { ask2(progressLoop); }, 100);
}

function downloadRedy(){
    document.getElementById('descargar').style.visibility = 'visible';
    document.getElementById('container').style.visibility = 'visible';
    document.getElementById('alertCalculos').style.display = 'block';
}
function noFileInCache(){
    document.getElementById('container').style.visibility = 'hidden';
    document.getElementById('alertCalculos').style.display= 'none';
}*/
/*Alerts*/
