/* Init alertas */
$('#alertCalculos').hide();


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

/*  var bar = new ProgressBar.Path('#heart-path', {
    strokeWidth: 4,
    easing: 'easeInOut',
    duration: 10000,
    text: {
        style: {
          // Text color.
          // Default: same as stroke color (options.color)
          color: '#999',
          position: 'absolute',
          right: '0',
          top: '30px',
          padding: 0,
          margin: 0,
          transform: null
        },
        autoStyleContainer: false
      },
      from: {color: '#FFEA82'},
      to: {color: '#ED6A5A'}
  });
*/
var bar = new ProgressBar.Circle(container, {
    color: '#d6d7d8',
    // This has to be the same size as the maximum width to
    // prevent clipping
    strokeWidth: 5,
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
        circle.setText('');
      } else {
        circle.setText(String(value)+'%');
      }
  
    }
  });
  bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
  bar.text.style.fontSize = '3rem';
//bar.set(0);
bar.animate(0); 
/*Consultas XML*/

window.onload = askMatrizAutoStatusCheck();

function getMatrizAutoStatus(progressLoopMatrizAuto) {
    console.log("Esto deberia salir solo una vez sino rip cargado auto")
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var obj = JSON.parse(this.responseText);
            var crrnt = ((obj['progressStatus']).toFixed(1)*100);
            console.log(crrnt)
            document.getElementById("progressBarMatrizAuto").style.width = (crrnt).toString()+"%";
            document.getElementById("progressBarMatrizAutoPercentage").innerHTML = (crrnt).toString()+"%";
            progressLoopMatrizAuto = setTimeout(function() { getMatrizAutoStatus(progressLoopMatrizAuto); }, 15000);
            if(crrnt>99){
                document.getElementById('matrizAutoStatus').style.visibility = 'hidden';
                clearTimeout(progressLoopMatrizAuto);
            }
            if(crrnt<0){
                bar.animate(0); 
                document.getElementById('progressBarMatrizAutoContainer').style.visibility = 'hidden';
                clearTimeout(progressLoopMatrizAuto);
            }
        }
    };
    xhttp.open("GET", "progressMatrizAuto/", true);
    xhttp.send();
    }

function askMatrizAutoStatusCheck(){
    var progressLoopMatrizAuto = setTimeout(function() { getMatrizAutoStatus(progressLoopMatrizAuto); }, 100);
}

//
window.onload = ask();

function ask2(progressLoop) {
    console.log("Esto deberia salir solo una vez sino rip barra de cargado")
    $('#alertCalculos').hide();
    var xhttp = new XMLHttpRequest();
    clearTimeout(progressLoop);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
        var obj = JSON.parse(this.responseText);
        var crrnt = ((parseFloat(obj['Done'])/parseFloat(obj['Total']))*100).toFixed(1);
        console.log(crrnt);
        bar.animate(crrnt/100); 
        progressLoop = setTimeout(function() { ask2(progressLoop); }, 15000);
        if(crrnt>99){
            document.getElementById('descargar').style.visibility = 'visible';
            $('#alertCalculos').show();
            clearTimeout(progressLoop);
        }
        if(crrnt<0){
            $('#alertCalculos').hide();
            clearTimeout(progressLoop);
        }
        }
    };
    xhttp.open("GET", "progress/", true);
    xhttp.send();
}

function ask(){
    var progressLoop = setTimeout(function() { ask2(progressLoop); }, 100);
}

/*Alerts*/