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
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if(not (Settings.objects.get('statusPrestador').value == '1'and Settings.objects.get('statusMatrizAuto').value == '1' and Settings.objects.get('statusMatrizBus').value == '1'and Settings.objects.get('statusMatrizCaminando').value == '1')):
                return [["Faltan cargar matrizes o se estan cargando"]]
            status  = Settings.objects.get(setting='statusMatrizIndividuoTiempoCentro')
            status.value  = -1
            status.save()
            p = list(Prestador.objects.all()) # Traigo todos los prestadores
            dict_prestadores = {p[x].nombre:p[x].id for x in range(len(p))} # armo un diccionario que relaciona el nombre con la id
            res, lineas = checkCentroPediatras(request,dict_prestadores)
            if not res:
                return lineas
            print(dict_prestadores)
            status  = Settings.objects.get(setting='statusMatrizCentro')
            status.value  = 0
            status.save()
            progressDone  = Settings.objects.get(setting='currentMatrizCentro')
            progressTotal = Settings.objects.get(setting='totalMatrizCentro')
            progressDone.value  = 0.1
            progressTotal.value = len(lineas) 
            progressDone.save()
            progressTotal.save()
            asyncTask = saveCentrosToDB.apply_async(args=[lineas,dict_prestadores],queue = 'CalculationQueue')
            asyncKey = asyncTask.id
            utils.getOrCreateSettigs('asyncKeyCentro',asyncKey)
        else:
            print("Did not acquire lock.")
    except:
        utils.getOrCreateSettigs("statusMatrizCentro", -1);    
        return
    finally:
        if have_lock:
            my_lock.release()    



def cargarMutualistas(request):
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if(not utils.nothingLoading()):
                return [["Faltan cargar matrizes o se estan cargando"]]
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
            print("Did not acquire lock.")
    except:
        utils.getOrCreateSettigs("statusPrestador", -1);    
        return
    finally:
        if have_lock:
            my_lock.release()    

    

def cargarTiposTransporte(request):
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if( not utils.nothingLoading()):
                return [["Faltan cargar matrizes o se estan cargando"]]
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
            utils.getOrCreateSettigs("statusTipoTransporte", -1);    
        else:
            print("Did not acquire lock.")
    except:
        utils.getOrCreateSettigs("statusTipoTransporte", -1);    
        return
    finally:
        if have_lock:
            my_lock.release()    
    

def cargarIndividuoAnclas(requestf):
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if(not (Settings.objects.get('statusTipoTransporte').value == '1'and Settings.objects.get('statusMatrizAuto').value == '1' and Settings.objects.get('statusMatrizBus').value == '1'and Settings.objects.get('statusMatrizCaminando').value == '1') or not utils.nothingLoading()):
                return [["Faltan cargar matrizes o se estan cargando"]]
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
            asyncTask = saveIndividuosToDB.apply_async(args=[lineas],queue = 'CalculationQueue')
            asyncKey = asyncTask.id
            utils.getOrCreateSettigs('asyncKeyIndividuo',asyncKey)
            print("Generando matriz cartesiana Individuo-Centro-Dia-Hora")
            print("Matriz Carteasiana generada")
        else:
            print("Did not acquire lock.")
    except:
        utils.getOrCreateSettigs("statusMatrizIndividuo", -1);    
        return
    finally:
        if have_lock:
            my_lock.release()    


def cargarTiempos(tipo,request):
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if(not (Settings.objects.get('shapeAutoStatus').value == '1' and Settings.objects.get('shapeCaminandoStatus').value == '1') or not utils.nothingLoading()):
                return [["Faltan cargar matrizes o se estan cargando"]]
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
            baseDirectory  = "./app/data/RawCsv/"
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
            print("ENTRANDO")
            asyncTask = saveTiemposToDB.apply_async(args=[tipo],queue = 'CalculationQueue')
            asyncKey = asyncTask.id
            utils.getOrCreateSettigs('asyncKey'+tipoId,asyncKey)
        else:
            print("Did not acquire lock.")
    except:
        status  = Settings.objects.get(setting='statusMatriz'+tipoId)
        status.value  = -1
        status.save()
        return
    finally:
        if have_lock:
            my_lock.release()    
    

def cargarTiemposBus(request):
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if(not (Settings.objects.get('shapeBusStatus').value == '1') or not utils.nothingLoading()):
                return [["Faltan cargar matrizes o se estan cargando"]]
            status  = Settings.objects.get(setting='statusMatrizIndividuoTiempoCentro')
            status.value  = -1
            status.save()
        #    res, lineas = checkTiemposBus(request)
        #    if not res:
        #        return lineas
            csvfile = request.FILES['inputFile']
            baseDirectory  = "./app/data/RawCsv/"
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
            asyncTask = saveTiemposBusToDB.apply_async(queue = 'CalculationQueue')
            asyncKey = asyncTask.id
            utils.getOrCreateSettigs('asyncKeyBus',asyncKey)
        else:
            print("Did not acquire lock.")
    except:
        status  = Settings.objects.get(setting='statusMatrizBus')
        status.value  = -1
        status.save()
        return
    finally:
        if have_lock:
            my_lock.release()   

