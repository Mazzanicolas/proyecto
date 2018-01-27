from __future__ import absolute_import, unicode_literals
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from app.models import Individuo, Settings, TipoTransporte,Sector, Prestador, AnclaTemporal, SectorTiempo,Centro,Pediatra,IndividuoTiempoCentro,MedidasDeResumen,SectorTiempoOmnibus,IndividuoCentro, IndividuoCentroOptimo
from django.db.models import F
import math
from django_tables2.export.export import TableExport
from app.tables import PersonTable,ResumenTable,TestPersonTable, SimPersonTable,PagedFilteredTableView
from django_tables2 import RequestConfig
import shapefile
import time
import csv
from django.shortcuts import redirect
from celery import group, result
from proyecto.celery import app
from app.checkeo_errores import *
from app.task import suzuki, calculateIndividual
import app.utils as utils
import app.load as load
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.http import JsonResponse
import redis
import os
import zipfile
from io import BytesIO
from app.shpModule import *

global shapeAuto
global shapeCaminando

sf = shapefile.Reader('app/files/shapeAuto.shp')
shapeAuto = sf.shapes()
sf = shapefile.Reader('app/files/shapeCaminando.shp')
shapeCaminando = sf.shapes()

def genShape(request):
    values    = request.GET
    filenames = generarShape(values,request.session.session_key)
    #'app/files/shpOut/centrosDefecto'      +sfkey+'.shp', 'app/files/shpOut/centrosDefecto'+sfkey+'.shx', 'app/files/shpOut/centrosDefecto'+sfkey+'.dbf',
    #'app/files/shpOut/hogarCentro'         +sfkey+'.shp', 'app/files/shpOut/hogarCentro'   +sfkey+'.shx', 'app/files/shpOut/hogarCentro'   +sfkey+'.dbf']
    zip_subdir   = "Shapefiles"
    zip_filename = "%s.zip" % zip_subdir
    s  = BytesIO()
    zf = zipfile.ZipFile(s, "w")
    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path    = os.path.join(zip_subdir, fname)
        zf.write(fpath, zip_path)
    zf.close()
    resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp


def test(request):
    if(IndividuoCentro.objects.count() <Individuo.objects.count()*Centro.objects.count() and Individuo.objects.count() > 0 and Centro.objects.count()>0):
        print("******************************************************************************************************************")
        newCalcTimes()
    getReq = request.GET
    if(getReq.get('checkRango','0') == '-1'):
        return consultaToCSV(request)
    response = redirect('consultaConFiltro')
    return response

def progress(request):
    print("PROGRESS")
    groupId = request.session.get('groupId', None)
    if(groupId):
        #resultado = app.GroupResult.restore(groupId)
        #done = resultado.completed_count()
        done = request.session.get('current',-1)
    else:
        done = -1
    total = request.session.get('total', 100)
    data = {"Done":done,"Total":total}
    return JsonResponse(data)

def redirectSim(request):
    if(IndividuoCentro.objects.count() <Individuo.objects.count()*Centro.objects.count() and Individuo.objects.count() > 0 and Centro.objects.count()>0):
        print("******************************************************************************************************************")
        newCalcTimes()
    getReq = request.GET
    if(getReq.get('checkRes','0') == '1'):
        return resumenConFiltroOSinFiltroPeroNingunoDeLosDos(request)
    if(getReq.get('checkRango','0') == '-1'):
        return consultaToCSV(request)
    response = redirect('Simulacion')
    if(getReq.get('checkB',0) == '-1'):
        response.set_cookie(key='mutualista',value='-1')
    else:
        response.set_cookie(key='mutualista',value=int(getReq.get('prestador','-1')))
    if(getReq.get('checkM','0') == '-1'):
        response.set_cookie(key='tipoTransporte',value='-1')
    else:
        response.set_cookie(key='tipoTransporte',value=int(getReq.get('tipoTransporte','-1')))
    response.set_cookie(key='trabaja', value=int(getReq.get('anclaTra','0')))
    response.set_cookie(key='jardin', value=int(getReq.get('anclaJar','0')))
    return response

def index(request):
    init()
    if(not Sector.objects.all()):
        load.cargarSectores(shapeAuto,shapeCaminando)
    post = request.POST
    if(not Settings.objects.filter(setting = "tiempoMaximo")):
        s = Settings(setting = "tiempoMaximo",value = "60")
        s.save()
    if(not Settings.objects.filter(setting = "tiempoConsulta")):
        s = Settings(setting = "tiempoConsulta",value = "30")
        s.save()
    if(post):
        tiempoMax = post.get("tiempoTransporte")
        tiempoCons = post.get("tiempoConsulta")
        radioCargado = post.get("optionsRadios")
        radioMatrix =  radioCargado
        if(radioCargado):
            if(radioCargado == "option1"):
                lineas = load.cargarMutualistas(request)
            elif(radioCargado == "option2"):
                lineas = load.cargarIndividuoAnclas(request,shapeAuto, shapeCaminando)
            elif(radioMatrix == "option3"):
                lineas = load.cargarTiempos(0,request,shapeAuto, shapeCaminando)
            elif(radioMatrix == "option4"):
                lineas = load.cargarTiempos(1,request,shapeAuto, shapeCaminando)
            elif(radioMatrix == "option5"):
                lineas = load.cargarCentroPediatras(request,shapeAuto, shapeCaminando)
            elif(radioMatrix == "option6"): # omnibus
                lineas = load.cargarTiemposBus(request)
            elif(radioMatrix == "option7"):
                lineas = load.cargarTiposTransporte(request)
            if lineas is not None:
                pseudo_buffer = utils.Echo()
                writer = csv.writer(pseudo_buffer)
                response = StreamingHttpResponse((writer.writerow(row) for row in lineas),
                                                 content_type="text/csv")
                response['Content-Disposition'] = 'attachment; filename="errores.csv"'
                return response
        if(tiempoMax):
            maxT = Settings.objects.get(setting = "tiempoMaximo")
            maxT.value = tiempoMax
            maxT.save()
        if(tiempoCons):
            consT = Settings.objects.get(setting = "tiempoConsulta")
            consT.value = tiempoCons
            consT.save()
    maxT = Settings.objects.get(setting = "tiempoMaximo").value
    consT = Settings.objects.get(setting = "tiempoConsulta").value
    context = {'tiempoMaximo': maxT, 'tiempoConsulta': consT}
    return render(request, 'app/index2.html',context)

def guardarArchivo(nombre, archivo):
    with default_storage.open('tmp/'+nombre, 'wb+') as destination:
        for chunk in archivo.chunks():
            destination.write(chunk)
        csv = os.path.join(settings.MEDIA_ROOT, destination)
        return csv

def resumenConFiltroOSinFiltroPeroNingunoDeLosDos(request):
    tiempoInicio = time.time()
    sessionKey = request.session.session_key
    if(MedidasDeResumen.objects.all()):
        individuos = []
    else:
        getData = request.GET
        fromRange = int(getData.get('fromRange')) if(getData.get('fromRange',"") != "" ) else 0
        toRange = int(getData.get('toRange')) if(getData.get('toRange',"") != "" ) else Individuo.objects.last().id
        if(getData.get("simular",'0') == '1' ):
            indQuery = Individuo.objects.filter(id__gte = fromRange,id__lte = toRange)
            #indQuery = IndividuoTiempoCentro.objects.filter(individuo__in = individuos).values_list('id', flat=True):
            dictParam = utils.generateParamDict(getData)
            print(dictParam)
        else:
            transportList = []
            if(getData.get('autoResumenes', None)):
                transportList.append(1)
            if(getData.get('caminandoResumenes', None)):
                transportList.append(0)
            if(getData.get('omnibusResumenes', None)):
                transportList.append(2)
            trabajaReq = getData.get('trabajaResumenes', None)
            jardinReq =  getData.get('jardinResumenes', None)
            trabaja = [True] if trabajaReq else [False]
            jardin = [True] if jardinReq else [False]
            if(jardinReq == '0'):
                jardin.append(False)
            if(trabajaReq == '0'):
                trabaja.append(False)
            indQuery = Individuo.objects.filter(id__gte = fromRange,id__lte = toRange, tipo_transporte__id__in = transportList, tieneTrabajo__in = trabaja,tieneJardin__in = jardin)
            dictParam = None
    numberPerGroup = math.ceil(len(indQuery)/8)
    numberPerGroup = min(3,numberPerGroup)
    numberPerGroup = 2
    individuos = [[[x.id for x in indQuery[i:i + numberPerGroup]],dictParam,sessionKey] for i in range(0, len(indQuery), numberPerGroup)]
    request.session['total'] = len(individuos)
    print("Individuos a calcular: "+str(len(indQuery)))
    resultList = []
    job = suzuki.chunks(individuos,1).group()
    result = job.apply_async()
    result.save()
    request.session['lock'] = '1'
    request.session['current'] = 0
    request.session['groupId'] = result.id
    request.session['resultType'] = 'resumen'
    response = redirect('index')
    return response

def consultaToCSV(request):
    tiempoInicio = time.time()
    sessionKey = request.session.session_key
    getData = request.GET
    fromRange = int(getData.get('fromRange')) if(getData.get('fromRange',"") != "" ) else 0
    toRange = int(getData.get('toRange')) if(getData.get('toRange',"") != "" ) else Individuo.objects.last().id
    if(getData.get("simular",'0') == '1' ):
        indQuery = Individuo.objects.filter(id__gte = fromRange,id__lte = toRange)
        dictParam = utils.generateParamDict(getData)
    else:
        transportList = [int(x) for x in getData.getlist('tipoTransporte', [])]
        trabajaReq = getData.get('trabajaResumenes', None)
        jardinReq =  getData.get('jardinResumenes', None)
        trabaja = [True] if trabajaReq else [False]
        jardin = [True] if jardinReq else [False]
        if(jardinReq == '0'):
            jardin.append(False)
        if(trabajaReq == '0'):
            trabaja.append(False)
        indQuery = Individuo.objects.filter(id__gte = fromRange,id__lte = toRange, tipo_transporte__id__in = transportList, tieneTrabajo__in = trabaja,tieneJardin__in = jardin)
        print("Individuos a calcular: "+str(len(indQuery)))
        dictParam = None
    numberPerGroup = math.ceil(len(indQuery)/8)
    numberPerGroup = min(3,numberPerGroup)
    individuos = [[indQuery[i:i + numberPerGroup],dictParam,sessionKey] for i in range(0, len(indQuery), numberPerGroup)]
    request.session['total'] = len(individuos)
    resultList = []
    job = calculateIndividual.chunks(individuos,1).group()
    result = job.apply_async()
    result.save()
    request.session['current'] = 0
    request.session['lock'] = '1'
    request.session['groupId'] = result.id
    request.session['resultType'] = 'individual'
    response = redirect('index')
    return response

def downloadFile(request):
    groupId = request.session.get('groupId', None)
    resultType = request.session.get('resultType', None)
    if(groupId and resultType):
        resultado = app.GroupResult.restore(groupId)
        if(resultType == 'individual'):
            resumenObjectList = resultado.join()
            resumenObjectList = sum(sum(resumenObjectList,[]), [])
            pseudo_buffer = utils.Echo()
            writer = csv.writer(pseudo_buffer)
            response = StreamingHttpResponse((writer.writerow(row) for row in resumenObjectList),
                                             content_type="text/csv")
            response['Content-Disposition'] = 'attachment; filename="resultado.csv"'
            return response
        else:
            resumenObjectList = resultado.join()
            resumenObjectList = sum(sum(resumenObjectList,[]), [])
            table  = ResumenTable(resumenObjectList)
            RequestConfig(request).configure(table)
            exporter = TableExport('csv', table)
            return exporter.response('table.{}'.format('csv'))
    response = redirect('index')
    return response

def plot(request):
    return render(request,'app/plot.html')

def newCalcTimes():
    tiempoMaximo   = int(Settings.objects.get(setting = "tiempoMaximo").value)  # Cambiar(Tomar de bd)
    tiempoConsulta = int(Settings.objects.get(setting = "tiempoConsulta").value) #Cambiar(Tomar de bd)
    individuos     = Individuo.objects.select_related().all()
    prestadores    = Prestador.objects.select_related().all()
    centros        = Centro.objects.select_related().all()
    pedi           = Pediatra.objects.select_related()
    for individuo in individuos:
        print(individuo.id)
        prest      = prestadores#[individuo.prestador]#arreglar
        transporte = individuo.tipo_transporte.id
        trabajo    = individuo.trabajo
        jardin     = individuo.jardin
        secHogarAuto   = utils.newGetSector(individuo.hogar,1)
        secTrabajoAuto = utils.newGetSector(trabajo,1)
        secJardinAuto  = utils.newGetSector(jardin,1)
        ######
        secHogarCaminando   = utils.newGetSector(individuo.hogar,0)
        secTrabajoCaminando = utils.newGetSector(trabajo,0)
        secJardinCaminando  = utils.newGetSector(jardin,0)
        #####
        secHogarBus   = utils.newGetSector(individuo.hogar,1)
        secTrabajoBus = utils.newGetSector(trabajo,1)
        secJardinBus  = utils.newGetSector(jardin,1)
        ####
        tHogarTrabajoAuto  = utils.calcularTiempoViaje([secHogarAuto, secTrabajoAuto],1)
        tHogarJardinAuto   =  utils.calcularTiempoViaje([secHogarAuto, secJardinAuto],1)
        tJardinTrabajoAuto = utils.calcularTiempoViaje([secJardinAuto, secTrabajoAuto],1)
        tTrabajoJardinAuto = utils.calcularTiempoViaje([secJardinAuto, secHogarAuto],1)
        tTrabajoHogarAuto  = utils.calcularTiempoViaje([secTrabajoAuto, secHogarAuto],1)
#######################
        tHogarTrabajoCaminando  = utils.calcularTiempoViaje([secHogarCaminando, secTrabajoCaminando],0)
        tHogarJardinCaminando   =  utils.calcularTiempoViaje([secHogarCaminando, secJardinCaminando],0)
        tJardinTrabajoCaminando = utils.calcularTiempoViaje([secJardinCaminando, secTrabajoCaminando],0)
        tTrabajoJardinCaminando = utils.calcularTiempoViaje([secJardinCaminando, secHogarCaminando],0)
        tTrabajoHogarCaminando  = utils.calcularTiempoViaje([secTrabajoCaminando, secHogarCaminando],0)
#######################
        tHogarTrabajoBus  = utils.calcularTiempoViaje([secHogarBus, secTrabajoBus],2)
        tHogarJardinBus   =  utils.calcularTiempoViaje([secHogarBus, secJardinBus],2)
        tJardinTrabajoBus = utils.calcularTiempoViaje([secJardinBus, secTrabajoBus],2)
        tTrabajoJardinBus = utils.calcularTiempoViaje([secJardinBus, secHogarBus],2)
        tTrabajoHogarBus  = utils.calcularTiempoViaje([secTrabajoBus, secHogarBus],2)
        tiemposCentros = []
        auxOptimo = IndividuoCentroOptimo(individuo = individuo)
        for centro in centros:
            aux = time.time()
            secCentroAuto      = utils.newGetSector(centro,1)
            secCentroCaminando = utils.newGetSector(centro,0)
            secCentroBus       = utils.newGetSector(centro,1)
            horas              = Pediatra.objects.filter(centro = centro)
            tHogarCentroAuto   = utils.calcularTiempoViaje([secHogarAuto, secCentroAuto],1)
            tJardinCentroAuto  = utils.calcularTiempoViaje([secJardinAuto, secCentroAuto],1)
            tCentroHogarAuto   = utils.calcularTiempoViaje([secCentroAuto, secHogarAuto],1)
            tCentroJardinAuto  = utils.calcularTiempoViaje([secCentroAuto, secJardinAuto],1)
####################
            tHogarCentroCaminando  = utils.calcularTiempoViaje([secHogarCaminando, secCentroCaminando],0)
            tJardinCentroCaminando = utils.calcularTiempoViaje([secJardinCaminando, secCentroCaminando],0)
            tCentroHogarCaminando  = utils.calcularTiempoViaje([secCentroCaminando, secHogarCaminando],0)
            tCentroJardinCaminando = utils.calcularTiempoViaje([secCentroCaminando, secJardinCaminando],0)
#########################
            tHogarCentroBus  = utils.calcularTiempoViaje([secHogarBus, secCentroBus],2)
            tJardinCentroBus = utils.calcularTiempoViaje([secJardinBus, secCentroBus],2)
            tCentroHogarBus  = utils.calcularTiempoViaje([secCentroBus, secHogarBus],2)
            tCentroJardinBus = utils.calcularTiempoViaje([secCentroBus, secJardinBus],2)

            listaHoras = []
            ini = time.time()
            q = IndividuoCentro(individuo          = individuo , centro = centro, tHogarTrabajoAuto = tHogarTrabajoAuto/60,
                                tHogarJardinAuto   = tHogarJardinAuto/60,tJardinTrabajoAuto  = tJardinTrabajoAuto/60,
                                tTrabajoJardinAuto = tTrabajoJardinAuto/60,tTrabajoHogarAuto = tTrabajoHogarAuto/60,
                                tHogarCentroAuto   = tHogarCentroAuto/60,tJardinCentroAuto   = tJardinCentroAuto/60,
                                tCentroHogarAuto   = tCentroHogarAuto/60,tCentroJardinAuto   = tCentroJardinAuto/60,
            tHogarTrabajoCaminando = tHogarTrabajoCaminando/60,
                                tHogarJardinCaminando   = tHogarJardinCaminando/60,tJardinTrabajoCaminando  = tJardinTrabajoCaminando/60,
                                tTrabajoJardinCaminando = tTrabajoJardinCaminando/60,tTrabajoHogarCaminando = tTrabajoHogarCaminando/60,
                                tHogarCentroCaminando   = tHogarCentroCaminando/60,tJardinCentroCaminando   = tJardinCentroCaminando/60,
                                tCentroHogarCaminando   = tCentroHogarCaminando/60,tCentroJardinCaminando   = tCentroJardinCaminando/60,
            tHogarTrabajoBus = tHogarTrabajoBus/60,
                                tHogarJardinBus   = tHogarJardinBus/60,tJardinTrabajoBus  = tJardinTrabajoBus/60,
                                tTrabajoJardinBus = tTrabajoJardinBus/60,tTrabajoHogarBus = tTrabajoHogarBus/60,
                                tHogarCentroBus   = tHogarCentroBus/60,tJardinCentroBus   = tJardinCentroBus/60,
                                tCentroHogarBus   = tCentroHogarBus/60,tCentroJardinBus   = tCentroJardinBus/60)
            tiemposCentros.append(q)
            auxOptimo = setOptimo(auxOptimo, centro, tHogarCentroAuto, tHogarCentroBus, tHogarCentroCaminando)
        IndividuoCentro.objects.bulk_create(tiemposCentros)
        auxOptimo.save()
        print("Termino el individuo: "+str(individuo.id))

def setOptimo(auxOptimo, centro, tHogarCentroAuto, tHogarCentroOmnibus, tHogarCentroCaminando):
    if(auxOptimo.centroOptimoAuto is None):
        auxOptimo.centroOptimoAuto      = centro
        auxOptimo.centroOptimoOmnibus   = centro
        auxOptimo.centroOptimoCaminando = centro
        auxOptimo.tHogarCentroAuto      = tHogarCentroAuto
        auxOptimo.tHogarCentroOmnibus   = tHogarCentroOmnibus
        auxOptimo.tHogarCentroCaminando = tHogarCentroCaminando
        return auxOptimo

    if(auxOptimo.tHogarCentroAuto  > tHogarCentroAuto):
        auxOptimo.centroOptimoAuto = centro
        auxOptimo.tHogarCentroAuto = tHogarCentroAuto

    if(auxOptimo.tHogarCentroOmnibus  > tHogarCentroOmnibus):
        auxOptimo.centroOptimoOmnibus = centro
        auxOptimo.tHogarCentroOmnibus = tHogarCentroOmnibus

    if(auxOptimo.tHogarCentroCaminando  > tHogarCentroCaminando):
        auxOptimo.centroOptimoCaminando = centro
        auxOptimo.tHogarCentroCaminando = tHogarCentroCaminando
    return auxOptimo

def init():
    if(IndividuoTiempoCentro.objects.count() < Individuo.objects.count() * Pediatra.objects.count() and Centro.objects.count() > 0 and Individuo.objects.count() > 0):
        individuos = Individuo.objects.all()
        centros = Centro.objects.all()
        for individuo in individuos:
            print("IndividuoCentro: "+str(individuo.id))
            for centro in centros:
                consultas = Pediatra.objects.filter(centro = centro)
                listaHoras = []
                for consulta in consultas:
                    q = IndividuoTiempoCentro(individuo = individuo,centro=centro,dia = consulta.dia,hora = consulta.hora,cantidad_pediatras = consulta.cantidad_pediatras)
                    listaHoras.append(q)
                IndividuoTiempoCentro.objects.bulk_create(listaHoras)
