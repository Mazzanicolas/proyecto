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
    $(document.getElementById("cbCSV1")).change(function(){
        if(this.checked){
            document.getElementById("cbCSV2").disabled = true;
            document.getElementById("cbCSV2").checked = true;
        }
        else
            document.getElementById("cbCSV2").disabled = false;
    });
});


/*
var bar = new ProgressBar.Circle(container, {
    strokeWidth: 3,
    color: '#FFEA82',
    trailColor: '#eee',
    trailWidth: 1,
    easing: 'easeInOut',
    duration: 1400,
    svgStyle: null,
    text: {
      value: '',
      alignToBottom: true
    },
    from: {color: '#e3e7f2'},
    to: {color: '#6c69db'},
    // Set default step function for all animate calls
    step: (state, bar) => {
      bar.path.setAttribute('stroke', state.color);
      var value = Math.round(bar.value() * 100);
      if (value === 0) {
        bar.setText('');
      } else {
        bar.setText(value);
      }  
      bar.text.style.color = state.color;
    }
  });
  bar.text.style.fontFamily = 'sans-serif';
  bar.text.style.fontSize = '10rem';
  bar.animate(1.0); */

  var bar = new ProgressBar.Path('#heart-path', {
    strokeWidth: 4,
    easing: 'easeInOut',
    duration: 1400,
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
/*
  var bar = new ProgressBar.Path('#heart-path', {
  strokeWidth: 4,
  easing: 'easeInOut',
  duration: 1400,
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
  to: {color: '#ED6A5A'},
  step: (state, bar) => {
    bar.setText(Math.round(bar.value() * 100) + ' %');
  }
});
*/
  
//bar.set(0);
bar.animate(0); 
/*Consultas XML*/
window.onload = askMatrizAutoStatusCheck();

function getMatrizAutoStatus(progressLoop) {
    console.log("Entro");
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log("Entro 200 ok");
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

//
window.onload = ask();

function ask2(progressLoop) {
    console.log("Entro 2")
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
            clearTimeout(progressLoop);
        }
        if(crrnt<0){
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