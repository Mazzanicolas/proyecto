/*Consultas XML*/
window.onload = askMatrizAutoStatusCheck();

function getMatrizAutoStatus(progressLoop) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
        var obj = JSON.parse(this.responseText);
        var crrnt = (obj['progressStatus']).toFixed(1);
        document.getElementById("progressBarMatrizAuto").style.width = crrnt.toString()+"%";
        document.getElementById("progressBarMatrizAutoPercentage").innerHTML = crrnt.toString()+"%";
        progressLoop = setTimeout(function() { getMatrizAutoStatus(progressLoop); }, 15000);
        if(crrnt>99){
            document.getElementById('progressBarMatrizAutoContainer').style.visibility = 'hidden';
            document.getElementById('descargar').style.visibility = 'visible';                  
            clearTimeout(progressLoop);
        }
        if(crrnt<0){
            document.getElementById('progressBarMatrizAutoContainer').style.visibility = 'hidden';
            clearTimeout(progressLoop);
        }
        }
    };
    xhttp.open("GET", "progressMatrizAuto/", true);
    xhttp.send();
    }

function askMatrizAutoStatusCheck(){
    var progressLoop = setTimeout(function() { getMatrizAutoStatus(progressLoop); }, 100);
}


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