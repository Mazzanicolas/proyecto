/* Init tooltips*/
$("[tt='tooltip']").tooltip({
    trigger : 'hover'
})  
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
/*Bloqueo de cargado*/
window.onload = blockLoadingChain();

function blockLoadingChain(){
    //if(isLoaded(SHPAuStatus) && isLoaded(SHPOmStatus) && isLoaded(SHPOmStatus)){
        if(isLoaded(TTrStatus)){
            unlockInput('customControlValidation1');
            if(isLoaded(MTAuStatus)){
                unlockInput('customControlValidation2');
                if(isLoaded(MTOmStatus)){
                    unlockInput('customControlValidation3');
                    if(isLoaded(MTCaStatus)){
                        unlockInput('customControlValidation4');
                        if(isLoaded(CDPrStatus)){
                            unlockInput('customControlValidation5');
                            if(isLoaded(CDCeStatus)){
                                unlockInput('customControlValidation6');
                                if(isLoaded(CDPeStatus)){
                                    document.getElementById('procesarButton').className = 'btn btn-primary';
                                }
                            }
                        }
                    }
                }
            }
        }
    //}
}
function unlockInput(id){
    document.getElementById(id).disabled = false;
}
function isLoaded(status){
    if(status==-1){
        return false;
    }
    return true;
}
//Loading Bar

var bar = new ProgressBar.Circle(container, {
    color: '#d6d7d8',
    strokeWidth: 7,
    trailWidth: 1,
    easing: 'easeInOut',
    duration: 2500,
    text: {
      autoStyleContainer: false
    },
    from: { color: '#4158d0', width: 2 },
    to: { color: '#c850c0', width: 5 },
    step: function(state, circle) {
      circle.path.setAttribute('stroke', state.color);
      circle.path.setAttribute('stroke-width', state.width);  
      var value = Math.round(circle.value() * 100);
      if (value < 0) {
        circle.setText('Iniciando');
      }
      else if (value === 0) {
        circle.setText('¡Listo!');
      } else {
        circle.setText(String(value)+' %');
      }
  
    }
  });
bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
bar.text.style.fontStyle = "italic"
bar.text.style.fontSize = '3rem';
bar.set(-0.01);

/*Consultas XML*/
window.onload = checkCalculating();

function checkCalculating(){
    if(isProcessing(currentProgress)){
        showProcessingGUI();
        showAlert('cancelarCalculos');
        updateStatus('progressCalculation/');
    } else if(filesInCache(currentProgress)){
        showDownloadButton();
        bar.animate(0);
        showLoadingBar();
        console.log('Files Found');
    }
    checkLoading();
}

function checkLoading(){
    if(isProcessing(TTrStatus)){
        //updateStatusLoading('/');
    } else if(isProcessing(MTAuStatus)) {        
        showAlertText('alertLoading','Matriz de tiempos Auto');
        showAlert('cancelarAuto');
        hiddeDownloadButton()
        updateStatusLoading('progressMatrizAuto/');
    } else if(isProcessing(MTOmStatus)) {
        showAlertText('alertLoading','Matriz de tiempos Omnibus');
        showAlert('cancelarOmnibus');
        hiddeDownloadButton()
        updateStatusLoading('progressMatrizBus/');
    } else if(isProcessing(MTCaStatus)) {
        showAlertText('alertLoading','Matriz de tiempos Caminando');
        showAlert('cancelarCaminando');
        hiddeDownloadButton()
        updateStatusLoading('progressMatrizCaminando/');
    } else if(isProcessing(CDPrStatus)) {
        //updateStatusLoading('/');
    } else if(isProcessing(CDCeStatus)) {
        showAlertText('alertLoading','Conjunto de datos para Centros');
        showAlert('cancelarCentro');
        hiddeDownloadButton()
        updateStatusLoading('progressCentro/');
    } else if(isProcessing(CDPeStatus)) {
        showAlertText('alertLoading','Conjunto de datos para Individuos');
        showAlert('cancelarIndividuo');
        hiddeDownloadButton()
        updateStatusLoading('progressIndividuo/');
    } else if(isProcessing(ReStatus)) {
        showAlertText('alertLoading','Datos nuevos en el sistema');
        showAlert('cancelarRecalculado');
        hiddeDownloadButton()
        updateStatusLoading('progressIndividuoTiempoCentro/');
    } else {
        console.log('Nothing Loading');
    }
}
function isProcessing(status){
    if(status == 0){
        return true;
    }
    return false;
}
function filesInCache(status){
    if(status >= 1){
        return true;
    }
    return false;
}
function updateStatus(url){
    var progressLoop = setTimeout(function() { progressStatus(url,progressLoop); }, 5000);
    showLoadingBar();
}
function updateStatusLoading(url){
    var progressLoop = setTimeout(function() { progressStatusLoading(url,progressLoop); }, 5000);
    showLoadingBar();
}

function progressStatus(url,progressLoop){
    console.log("XML Checking Progress...");
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var systemStatusResponse = JSON.parse(this.responseText);          
            processStatus = systemStatusResponse['progressStatus']
            if(processStatus>0){bar.animate(processStatus);}
            progressLoop = setTimeout(function() { progressStatus(url,progressLoop); }, 5000);
            console.log(processStatus);
            if(threadIsDone(processStatus)){
                clearTimeout(progressLoop);
                dissmisCancel();
                console.log("Thread closed")
                showDoneGUI();                
                document.location.href="/";
            }
        }
    };
    xhttp.open("GET", url, true);
    xhttp.send();
}

function progressStatusLoading(url,progressLoop){
    console.log("XML Checking Progress...");
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var systemStatusResponse = JSON.parse(this.responseText);          
            processStatus = systemStatusResponse['progressStatus']
            if(processStatus>0){bar.animate(processStatus);}
            progressLoop = setTimeout(function() { progressStatusLoading(url,progressLoop); }, 5000);
            console.log(processStatus);
            if(threadIsDone(processStatus)){
                clearTimeout(progressLoop);
                dissmisCancel();
                hideAlert('alertLoading');
                console.log("Thread closed");
                document.location.href="/";
            }
        }
    };
    xhttp.open("GET", url, true);
    xhttp.send();
}

function showDoneGUI(){
    bar.animate(0);
    showDownloadButton()
    hideAlert('alertCalculando');
}
function showProcessingGUI(){
    showAlert('alertCalculando');
}
function showLoadingGUI(url){
    showAlert('alertLoading');
}
function threadIsDone(threadStatus){
    if(threadStatus>0.999){
        return true;
    }
    return false;
}
function showLoadingBar(){
    document.getElementById('container').style.visibility = 'visible';
}
function hideLoadingBar(){
    document.getElementById('container').style.visibility = 'hidden';
}
function showDownloadButton(){
    document.getElementById('descargar').style.display = 'block';
    document.getElementById('alertCalculos').style.display = 'block';
}
function hiddeDownloadButton(){
    document.getElementById('descargar').style.display = 'block';
    document.getElementById('alertCalculos').style.display = 'none';
}
function showAlert(id){
    document.getElementById(id).style.display = 'block';
}
function showAlertText(id,text){
    document.getElementById(id).style.display = 'block';
    document.getElementById(id).innerHTML += text;
}
function hideAlert(id){
    document.getElementById(id).style.display = 'none';
}
function dissmisCancel(){
    hideAlert('cancelarCalculos');
    hideAlert('cancelarCaminando');
    hideAlert('cancelarOmnibus');
    hideAlert('cancelarIndividuo');
    hideAlert('cancelarCentro');
    hideAlert('cancelarRecalculado');
    hideAlert('cancelarAuto');

}
