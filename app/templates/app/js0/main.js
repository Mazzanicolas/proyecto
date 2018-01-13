			$(document).ready(function(){
			  $('.dropdown-submenu a.test').on("click", function(e){
			    $(this).next('ul').toggle();
			    e.stopPropagation();
			    e.preventDefault();
			  });
			});

			function selectOption(){//Eliminar, metodo discontinuado
				bootbox.prompt({
				    title: "¿Que desea hacer con los nuevos datos?",
				    inputType: 'select',
				    inputOptions: [
				        {
				            text: 'Seleccione una acción...',
				            value: '',
				        },
				        {
				            text: 'Remplazar matriz existente',
				            value: '1',
				        },
				        {
				            text: 'Agregar a matriz existente',
				            value: '2',
				        }
				    ],
				    callback: function (result) {
				        console.log(result);
				    }
				});
			}

			function selectOption2(){//Eliminar Discontinuado. Hacer generico con la de arriba, no me dan plas pelotas ahora
				bootbox.prompt({
				    title: "¿Que matriz desea calcular?",
				    inputType: 'select',
				    inputOptions: [
				        {
				            text: 'Seleccione una acción...',
				            value: '',
				        },
				        {
				            text: 'Recalcular matriz caminando',
				            value: '1',
				        },
				        {
				            text: 'Recalcular matriz autos',
				            value: '2',
				        }
				    ],
				    callback: function (result) {
				        console.log(result);
				    }
				});
			}
			function searchUser(){
				bootbox.prompt("Ingrese el nobmre del usuario a modificar", function(result){ console.log(result); });
			}
			function newUser(){//Eliminar Discontinuado
				var newU = [];
				bootbox.prompt({
				    title: "Complete los datos",
				    inputType: 'select',
				    inputOptions: [
				        {
				            text: 'Rol...',
				            value: '',
				        },
				        {
				            text: 'Usuario Comun',
				            value: '1',
				        },
				        {
				            text: 'Administrador',
				            value: '2',
				        },
				        {
				            text: 'Espectador',
				            value: '3',
				        }
				    ],

				    callback: function (result) {
				        console.log(result);
				        newU[2]=result;
				        //Aca se agrega a la bd
				    }

				});
				bootbox.prompt({
				    title: "Ingrese la contraseña del nuevo usuario",
				    inputType: 'password',
				    callback: function (result) {
				        console.log(result);
				        newU[1]=result;
				    }
				});				
				bootbox.prompt("Ingrese el nobmre del nuevo usuario", function(result){ console.log(result); 
					newU[0]=result;
				});
			}
			function showHideMap() {
			    var x = document.getElementById('mapContainer');
			    if (x.style.display === 'none') {
			        x.style.display = 'block';
			    } else {
			        x.style.display = 'none';
			    }
			}

			document.getElementById('tables').style.display = 'none';
			function showHideTables() {
			    var x = document.getElementById('tables');
			    if (x.style.display === 'none') {
			        x.style.display = 'block';
			    } else {
			        x.style.display = 'none';
			    }
			}
			function showTables() {
			    var x = document.getElementById('tables');
			    if (x.style.display === 'none') {
			        x.style.display = 'block';
			    }
			}