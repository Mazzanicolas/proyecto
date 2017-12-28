# Aplicación Proyecto 2017

Aplicación para el cálculo de la zona de disponiblidad para mutualistas en Montevideo, Uruguay.


## Dependencias

1. Descargar e instalar [PostgresSQL 9.6](https://www.openscg.com/bigsql/postgresql/installers.jsp/).
2. Descargar e instalar [Python 3.5+](https://www.python.org). 
3. Descargar e instalar [Redis 2.4.6](http://ruilopes.com/redis-setup/).
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
En caso de tener problema con alguna libreria descargar los [.whl](https://www.lfd.uci.edu/~gohlke/pythonlibs/)
## Build

1. Crear en PostgresSQL una base de datos con el nombre `proyectodb` con contraseña `1234`(Esto va a cambiar).

Para los siguientes pasos Python debe estar en las variables de entorno. En caso de no tenerlo remplazar `python` o `py` por el directorio donde se ecuentra `python.exe`. 

2. Clonar el repositorio y moverse en un terminal al directorio de trabajo.

```
python manage.py makemigrations
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
2. Cargar `Matriz de transporte privado`
3. Cargar `Matriz de transporte caminando`
4. Cargar `Centros`
5. Cargar `Personas`
