import app.utils as utils
from app.models import *
from app.checkeo_errores import *
import app.utils
import csv
from app.task import *
from django.http import HttpResponse, StreamingHttpResponse
import time
import shapefile

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

def cargarMutualistas(request):
    res, lineas = checkMutualistas(request)
    if not res:
        return lineas
    Prestador.objects.all().delete()
    prestadores = list()
    for linea in lineas:
        p = Prestador(int(linea[0]),linea[1])
        prestadores.append(p)
    Prestador.objects.bulk_create(prestadores)
    print("Se cargo correctamente el archivo")

def cargarTiposTransporte(request):
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

def cargarSectores():
    baseDirectory = "./app/data/shapes/"
    utils.createFolder(baseDirectory)
    sf = shapefile.Reader(baseDirectory + "shapeAuto.shp")
    shapeAuto = sf.shapes()
    recordsAuto = sf.records()
    sf = shapefile.Reader(baseDirectory + "shapeCaminando.shp")
    shapeCaminando = sf.shapes()
    recordsCaminando = sf.records()
    sf = shapefile.Reader(baseDirectory + "shapeBus.shp")
    shapeBus = sf.shapes()
    recordsBus = sf.records()
    for i in range(len(shapeAuto)):
        centroide = utils.centroid(shapeAuto[i])
        sector = SectorAuto(shapeid = recordsAuto[i][0],x_centroide = centroide.x,y_centroide = centroide.y,shapePosition=i)
        sector.save()
    for i in range(len(shapeCaminando)):
        centroide = utils.centroid(shapeCaminando[i])
        sector = SectorCaminando(shapeid = recordsCaminando[i][0],x_centroide = centroide.x,y_centroide = centroide.y,shapePosition=i)
        sector.save()
    for i in range(len(shapeBus)):
        centroide = utils.centroid(shapeBus[i])
        sector = SectorOmnibus(shapeid = recordsBus[i][0],x_centroide = centroide.x,y_centroide = centroide.y,shapePosition=i)
        sector.save()

def cargarIndividuoAnclas(requestf):
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
    asyncKey = saveIndividuosToDB.apply_async(args=[lineas],queue = 'CalculationQueue')
    utils.getOrCreateSettigs('asyncKeyIndividuo',asyncKey)
    print("Generando matriz cartesiana Individuo-Centro-Dia-Hora")
    print("Matriz Carteasiana generada")

def cargarTiempos(tipo,request):
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
    asyncKey = saveTiemposToDB.apply_async(args=[tipo],queue = 'CalculationQueue')
    utils.getOrCreateSettigs('asyncKey'+tipoId,asyncKey)

def cargarTiemposBus(request):
    res, lineas = checkTiemposBus(request)
    if not res:
        return lineas
    status  = Settings.objects.get(setting='statusMatrizBus')
    status.value  = 0
    status.save()
    progressDone  = Settings.objects.get(setting='currentMatrizBus')
    progressTotal = Settings.objects.get(setting='totalMatrizBus')
    progressDone.value  = 0.1
    progressTotal.value = len(lineas) 
    progressDone.save()
    progressTotal.save()
    asyncKey = saveTiemposBusToDB.apply_async(args=[lineas],queue = 'CalculationQueue')
    utils.getOrCreateSettigs('asyncKeyBus',asyncKey)

