import app.utils as utils
from app.models import *
from app.checkeo_errores import *
import app.utils
import csv
from app.task import *
from django.http import HttpResponse, StreamingHttpResponse
import time
import shapefile
from app.cancelar import *
from django.db import connection
import redis
import zipfile
from django.conf import settings

#Habria que sacar todos estos tiempos a settings, pero no es urgente
global TIEMPO_ARBITRARIAMENTE_ALTO
TIEMPO_ARBITRARIAMENTE_ALTO = 70 * 60
global newVELOCIDAD_CAMINANDO
newVELOCIDAD_CAMINANDO = 5000/60 # 5000 metros en 60 minutos
global TIEMPO_ESPERA
TIEMPO_ESPERA = 5*60 # 5 minutos en segundos
global TIEMPO_VIAJE
TIEMPO_VIAJE = 45 # 45 segundos entre paradas
global RADIO_CERCANO
RADIO_CERCANO = 500 # distancia maxima en metros para que dos paradas se consideren cercanas
global TIEMPO_CAMBIO_PARADA
TIEMPO_CAMBIO_PARADA = 60 * (RADIO_CERCANO / 2) * (1 / newVELOCIDAD_CAMINANDO) # Regla de 3 para sacar el tiempo caminando promedio entre dos paradas cercanas
                                                                          # con los valores por defecto es 3 minutos.

def cargarCentroPediatras(request):
    timeInit = time.time()
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if(not (Settings.objects.get(setting = 'statusPrestador').value == '1'and Settings.objects.get(setting = 'statusMatrizAuto').value == '1' and Settings.objects.get(setting = 'statusMatrizBus').value == '1'and Settings.objects.get(setting = 'statusMatrizCaminando').value == '1')):
                return [["Faltan cargar matrices o se estan cargando"]]
            status  = Settings.objects.get(setting='statusMatrizIndividuoTiempoCentro')
            status.value  = -1
            status.save()
            p = list(Prestador.objects.all()) # Traigo todos los prestadores
            dict_prestadores = {p[x].nombre:p[x].id for x in range(len(p))} # armo un diccionario que relaciona el nombre con la id
            res, lineas = checkCentroPediatras(request,dict_prestadores)
            if not res:
                return lineas
            status  = Settings.objects.get(setting='statusMatrizCentro')
            status.value  = 0
            status.save()
            progressDone  = Settings.objects.get(setting='currentMatrizCentro')
            progressTotal = Settings.objects.get(setting='totalMatrizCentro')
            progressDone.value  = 0.1
            progressTotal.value = len(lineas) 
            progressDone.save()
            progressTotal.save()
            asyncTask = saveCentrosToDB.apply_async(args=[lineas,dict_prestadores],queue = 'delegate')
            asyncKey = asyncTask.id
            utils.getOrCreateSettigs('asyncKeyCentro',asyncKey)
        else:
            return [["Faltan cargar matrices o se estan cargando"]]
    except:
        utils.getOrCreateSettigs("statusMatrizCentro", -1);    
        return [["Faltan cargar matrices o se estan cargando"]]

    finally:
        print("Se preparo el cargado de centros en "+str(time.time() - timeInit)+"s")        
        if have_lock:
            my_lock.release()    



def cargarMutualistas(request):
    timeInit = time.time()
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if(not utils.nothingLoading()):
                return [["Faltan cargar matrices o se estan cargando"]]
            utils.getOrCreateSettigs("statusPrestador", 0);
            status  = Settings.objects.get(setting='statusMatrizIndividuoTiempoCentro')
            status.value  = -1
            status.save()
            status  = Settings.objects.get(setting='statusMatrizCentro')
            status.value  = -1
            status.save()
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}" CASCADE'.format(IndividuoTiempoCentro._meta.db_table))
            cursor.execute('TRUNCATE TABLE "{0}" CASCADE'.format(IndividuoCentro._meta.db_table))
            cursor.execute('TRUNCATE TABLE "{0}" CASCADE'.format(Centro._meta.db_table))
            res, lineas = checkMutualistas(request)
            if not res:
                return lineas
            Prestador.objects.all().delete()
            prestadores = list()
            for linea in lineas:
                p = Prestador(int(linea[0]),linea[1])
                prestadores.append(p)
            Prestador.objects.bulk_create(prestadores)
            utils.getOrCreateSettigs("statusPrestador", 1);
            print("Se cargo correctamente el archivo")
        else:
            return [["Faltan cargar matrices o se estan cargando"]]
            print("Did not acquire lock.")
    except:
        utils.getOrCreateSettigs("statusPrestador", -1);    
        return [["Faltan cargar matrices o se estan cargando"]]
    finally:
        print("Se cargaron los prestadores en "+str(time.time() - timeInit)+"s")
        if have_lock:
            my_lock.release()    

    

def cargarTiposTransporte(request):
    timeInit = time.time()
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if( not utils.nothingLoading()):
                return [["Faltan cargar matrices o se estan cargando"]]
            utils.getOrCreateSettigs("statusTipoTransporte", 0);    
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}" CASCADE'.format(IndividuoTiempoCentro._meta.db_table))
            cursor.execute('TRUNCATE TABLE "{0}" CASCADE'.format(IndividuoCentro._meta.db_table))
            cursor.execute('TRUNCATE TABLE "{0}" CASCADE'.format(AnclaTemporal._meta.db_table))
            cursor.execute('TRUNCATE TABLE "{0}" CASCADE'.format(Individuo._meta.db_table))
            status  = Settings.objects.get(setting='statusMatrizIndividuo')
            status.value  = -1
            status.save()
            res, lineas = checkTiposTransporte(request)
            if not res:
                return lineas
            TipoTransporte.objects.all().delete()
            tipos = list()
            for linea in lineas:
                t = TipoTransporte(int(linea[0]),linea[1])
                tipos.append(t)
            TipoTransporte.objects.bulk_create(tipos)
            print("Se cargo correctamente el archivo")
            utils.getOrCreateSettigs("statusTipoTransporte", 1);    
        else:
            print("Did not acquire lock.")
            return [["Faltan cargar matrices o se estan cargando"]]
    except:
        utils.getOrCreateSettigs("statusTipoTransporte", -1);    
        return [["Faltan cargar matrices o se estan cargando"]]
    finally:
        print("Se cargo tipos de transporte en "+str(time.time() - timeInit)+"s")
        if have_lock:
            my_lock.release()    
    

def cargarIndividuoAnclas(requestf):
    timeInit = time.time()
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if(not (Settings.objects.get(setting = 'statusTipoTransporte').value == '1'and Settings.objects.get(setting = 'statusMatrizAuto').value == '1' and Settings.objects.get(setting = 'statusMatrizBus').value == '1'and Settings.objects.get(setting = 'statusMatrizCaminando').value == '1') or not utils.nothingLoading()):
                return [["Faltan cargar matrices o se estan cargando"]]
            status  = Settings.objects.get(setting='statusMatrizIndividuoTiempoCentro')
            status.value  = -1
            status.save()
            prestadores = [x.id for x in Prestador.objects.all()]
            tipos_transporte = [x.nombre for x in TipoTransporte.objects.all()]
            dicc_transporte = {x.nombre:x for x in TipoTransporte.objects.all()}
            res, lineas = checkIndividuoAnclas(requestf,prestadores,tipos_transporte)
            if not res:
                return lineas
            status  = Settings.objects.get(setting='statusMatrizIndividuo')
            status.value  = 0
            status.save()
            progressDone  = Settings.objects.get(setting='currentMatrizIndividuo')
            progressTotal = Settings.objects.get(setting='totalMatrizIndividuo')
            progressDone.value  = 0.1
            progressTotal.value = len(lineas) 
            progressDone.save()
            progressTotal.save()
            asyncTask = saveIndividuosToDB.apply_async(args=[lineas],queue = 'delegate')
            asyncKey = asyncTask.id
            utils.getOrCreateSettigs('asyncKeyIndividuo',asyncKey)
        else:
            print("Did not acquire lock.")
            return [["Faltan cargar matrices o se estan cargando"]]
    except:
        utils.getOrCreateSettigs("statusMatrizIndividuo", -1);    
        return [["Faltan cargar matrices o se estan cargando"]]
    finally:
        print("Se preparo el cargado de individuos "+str(time.time() - timeInit)+"s")
        if have_lock:
            my_lock.release()    


def cargarTiempos(tipo,request):
    timeInit = time.time()
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if(not (Settings.objects.get(setting = 'shapeAutoStatus').value == '1' and Settings.objects.get(setting = 'shapeCaminandoStatus').value == '1') or not utils.nothingLoading()):
                return [["Faltan cargar matrices o se estan cargando"]]
            status  = Settings.objects.get(setting='statusMatrizIndividuoTiempoCentro')
            status.value  = -1
            status.save()
            #res, lineas = checkTiempos(tipo,request)
            #if not res:
            #    return lineas
            if(tipo == 0):
                tipoId = "Caminando"
            else:
                tipoId = "Auto"
            csvfile = request.FILES['inputFile']
            baseDirectory  = settings.BASE_DIR + "/app/data/RawCsv/"
            utils.createFolder(baseDirectory)
            newCsv = open(baseDirectory + "tiempos"+tipoId+".csv", 'wb')
            for chunk in csvfile.chunks():
                newCsv.write(chunk)
            newCsv.close()
            #lineas=[]
            #lineas.extend(l)
            #lineas = lineas[1:]
            status  = Settings.objects.get(setting='statusMatriz'+tipoId)
            status.value  = 0
            status.save()
            progressDone  = Settings.objects.get(setting='currentMatriz'+tipoId)
            progressDone.value  = 0.1
            progressDone.save()
            asyncTask = saveTiemposToDB.apply_async(args=[tipo],queue = 'delegate')
            asyncKey = asyncTask.id
            utils.getOrCreateSettigs('asyncKey'+tipoId,asyncKey)
        else:
            print("Did not acquire lock.")
            return [["Faltan cargar matrices o se estan cargando"]]
    except Exception as e:
        if(tipo == 0):
            tipoId = "Caminando"
        else:
            tipoId = "Auto"
        status  = Settings.objects.get(setting='statusMatriz'+tipoId)
        status.value  = -1
        status.save()
        return [["Faltan cargar matrices o se estan cargando"]]
    finally:
        print("Se preparo el cargado la Matriz en "+str(time.time() - timeInit)+"s")
        if have_lock:
            my_lock.release()    
    

def cargarTiemposBus(request):
    timeInit = time.time()
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if(not (Settings.objects.get(setting = 'shapeBusStatus').value == '1') or not utils.nothingLoading()):
                return [["Faltan cargar matrices o se estan cargando"]]
            status  = Settings.objects.get(setting='statusMatrizIndividuoTiempoCentro')
            status.value  = -1
            status.save()
        #    res, lineas = checkTiemposBus(request)
        #    if not res:
        #        return lineas
            csvfile = request.FILES['inputFile']
            baseDirectory  = settings.BASE_DIR + "/app/data/RawCsv/"
            utils.createFolder(baseDirectory)
            newCsv = open(baseDirectory + "tiemposBus.csv", 'wb')
            for chunk in csvfile.chunks():
                newCsv.write(chunk)
            newCsv.close()
            status  = Settings.objects.get(setting='statusMatrizBus')
            status.value  = 0
            status.save()
            progressDone  = Settings.objects.get(setting='currentMatrizBus')
            progressDone.value  = 0.1
            progressDone.save()
            asyncTask = saveTiemposBusToDB.apply_async(queue = 'delegate')
            asyncKey = asyncTask.id
            utils.getOrCreateSettigs('asyncKeyBus',asyncKey)
        else:
            print("Did not acquire lock.")
            return [["Faltan cargar matrices o se estan cargando"]]
    except:
        status  = Settings.objects.get(setting='statusMatrizBus')
        status.value  = -1
        status.save()
        return [["Faltan cargar matrices o se estan cargando"]]
    finally:
        print("Se preparo el cargado la Matriz en"+str(time.time() - timeInit)+"s")
        if have_lock:
            my_lock.release()   

def loadShapes(request,tipo):
    timeInit = time.time()
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if(not utils.nothingLoading()):
                return [["Faltan cargar matrices o se estan cargando"]]
            if(tipo == 0):
                tipoNombre = "shapeCaminando"
                utils.getOrCreateSettigs('shapeCaminandoStatus',0)
            if(tipo == 1):
                    utils.getOrCreateSettigs('shapeAutoStatus',0)
                    tipoNombre = "shapeAuto"
            if(tipo == 2):
                utils.getOrCreateSettigs('shapeBusStatus',0)
                tipoNombre = "shapeBus"
            status  = Settings.objects.get(setting='statusMatrizIndividuoTiempoCentro')
            status.value  = -1
            status.save()
            status  = Settings.objects.get(setting='statusMatrizCentro')
            status.value  = -1
            status.save()
            status  = Settings.objects.get(setting='statusMatrizIndividuo')
            status.value  = -1
            status.save()
            content = request.FILES['inputFile']
            unzipped = zipfile.ZipFile(content)
            baseDirectory = settings.BASE_DIR+"/app/data/shapes/"
            utils.createFolder(baseDirectory)
            for libitem in unzipped.namelist():
                filename = libitem.split('.')
                file = open(baseDirectory+tipoNombre+"."+filename[1],'wb')
                file.write(unzipped.read(libitem))
                file.close()
            asyncTask = cargarSectores.apply_async(args = [tipo], queue = 'delegate')
            asyncTask.get()
        else:
            return [["Error 500"]]
    except:
        if(tipo == 0):
            tipoNombre = "shapeCaminando"
            utils.getOrCreateSettigs('shapeCaminandoStatus',-1)
        if(tipo == 1):
            utils.getOrCreateSettigs('shapeAutoStatus',-1)
            tipoNombre = "shapeAuto"
        if(tipo == 2):
            utils.getOrCreateSettigs('shapeBusStatus',-1)
        return [["Error 500"]]
    finally:
        print("Shapes cargados en " +str(time.time() - timeInit))
        if have_lock:
            my_lock.release()