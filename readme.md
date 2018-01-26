# Aplicación Proyecto 2017

Aplicación para el cálculo de la zona de disponiblidad para mutualistas en Montevideo, Uruguay.


## Dependencias

1. Descargar e instalar [PostgresSQL 9.6](https://www.openscg.com/bigsql/postgresql/installers.jsp/).
2. Descargar e instalar [Python 3.5+](https://www.python.org). 
3. Descargar e instalar [Redis 3](https://github.com/ServiceStack/redis-windows/raw/master/downloads/redis-latest.zip).
4. Instalar las librerias de Python usando `pip install` o `pip3 install`
* `Django 2.0`
```
pip install django
```
* `Django Bootstrap 3 9.1.0`
```
pip install django-bootstrap3
```
* `Django Tables 2 1.16`
```
pip install django-tables2
```
* `Django Filter 1.1.0`
```
pip install django-filter
```
* `Django Crispy Forms 1.7.0`
```
pip install django-crispy-forms
```
* `Psycopg 2 2.7.3.2`
```
pip install psycopg2
```
* `Shapely 1.6.2`
```
pip install shapely
```
* `Pyshp 1.2.12`
```
pip install pyshp
```
* `Geopy 1.11.0`
```
pip install geopy
```
* `Celery 4.1.0`
```
pip install celery
```
* `Tablib 0.12.1`
```
pip install tablib
```
* `Redis 2.10.6`
```
pip install redis
```
* `Django Celery Results 1.0.1`
```
pip install django_celery_results
```
* `Django CRequest 2016.3.16`
```
pip install django-crequest
```
* `Math Plot Lib`
```
pip install matplotlib
```
* `mpld3`
```
pip install mpld3
```

* `Jinja2 2.10`
```
pip install jinja2
```
En caso de tener problema con alguna libreria descargar los [.whl](https://www.lfd.uci.edu/~gohlke/pythonlibs/)
## Build

1. Crear en PostgresSQL una base de datos con el nombre `proyectodb` con contraseña `1234`(Esto va a cambiar).

Para los siguientes pasos Python debe estar en las variables de entorno. En caso de no tenerlo remplazar `python` o `py` por el directorio donde se ecuentra `python.exe`. 

2. Clonar el repositorio y moverse en un terminal al directorio de trabajo.

```
python manage.py makemigrations app
```
* Esto crea las instruciones para crear la base de datos

```
python manage.py migrate
```
* Esto crea la estructura de la base de datos

3. Abrir `redis-server.exe` como administrador

4. En el repositorio clonado ejecutar `redis.bat` y esperar que cargue

5. Volver al cmd donde se creo la estructura de la base de datos
```
python manage.py runserver
```
* Esto levanta el servidor en `127.0.0.1:8000/app/`

## Preparacion para la utilización

1. Entrar desde el navegador a `127.0.0.1:8000/app/`
2. Cargar `Tipos de transporte`
3. Cargar `Matriz de transporte privado`
4. Cargar `Matriz de transporte caminando`
5. Cargar `Matriz omnibus`
6. Cargar `Prestadores`
7. Cargar `Centros`
8. Cargar `Personas`

# Generar matrices usando OSRM

## Levantar el Server OSRM (Forma 1)

1. Clonar el repositorio de [OSRM](https://github.com/Project-OSRM/osrm-backend)
2. Seguir las instrucciones de OSRM

## Levantar el Server OSRM (Forma 2)

1. Descargar el modulo de [OSRM SV](https://drive.google.com/open?id=0B9_PBnYXKWkBVzBjdExNQnQ3Nm8)
2. Entrar a [Geofabrik](http://download.geofabrik.de/), [BBBIKE](http://download.bbbike.org/osm/) o [Open Street Map](https://www.openstreetmap.org/export) y descargar el mapa a utilizar. Nota: debe ser en formato `.osm.bpf`
3. Si no existe un directorio `temp` en `C:\` crearlo.
4. Moverse en la consola de comandos hasta donde se descargo el `OSRM SV` y ejecutar los siguientes comandos:
```
osrm-extract NOMBRE.osm.pbf -p TIPO.lua
```
* En `NOMBRE.osm.pbf` usar el nombre del archivo descargado y especificar el directorio de ser necesario.
* En `TIPO.lua` el tipo de grafo a generar, estos valores pueden ser `foot`, `car` o `bike`.
```
osrm-contract NOMBRE.osrm
```
```
osrm-routed NOMBRE.osrm
```
5. El servidor quedara esuchando en 127.0.0.1 puerto 5000 

## Levantar el Server OSRM (Forma 3)

1. Descargar el modulo de [OSRM SV](https://drive.google.com/open?id=0B9_PBnYXKWkBVzBjdExNQnQ3Nm8)
2. Entrar a [Geofabrik](http://download.geofabrik.de/), [BBBIKE](http://download.bbbike.org/osm/) o [Open Street Map](https://www.openstreetmap.org/export) y descargar el mapa a utilizar. Nota: debe ser en formato `.osm.bpf`
3. Ejecutar `RUNSERVER.bat`
4. El servidor quedara esuchando en 127.0.0.1 puerto 5000

Para mas información sobre OSRM consultar la [documentación](https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md)
