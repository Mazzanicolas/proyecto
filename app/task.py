# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task, group, result
from celery.result import allow_join_result
import time
from math import ceil
from datetime import timedelta
from app.models import *
import app.utils as utils
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
import redis
import csv
import math
import shapefile

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

@shared_task()
def delegator(get,sessionKey,cookies):
    session = SessionStore(session_key=sessionKey)
    tiempoInicio = time.time()
    getData      = get
    isResumen = False
    isIndividual = False
    indQuery,dictParam,dictTiemposSettings = utils.getIndivList_ParamDict_SettingsDict(get,cookies)
    numberPerGroup = math.ceil(len(indQuery)/8)
    numberPerGroup = min(3,numberPerGroup)
    individuos = [[indQuery[i:i + numberPerGroup],dictParam,sessionKey,dictTiemposSettings] for i in range(0, len(indQuery), numberPerGroup)]
    session['current'] = 0.01
    session['calculationStatus'] = 0
    if(getData.get('generarIndividual',0)== '1'):
        print("Soy un Individual")
        session['isIndividual'] = 1
        isIndividual = True
    if(getData.get('generarResumen',0) == '1'):
        print("Soy un resumen")
        session['isResumen'] = 1
        isResumen = True
    session['total'] = len(individuos)*2 + 10 if (isIndividual and isResumen) else len(individuos) + 5
    session.save()
    if(isIndividual):
        header = [['individuo', 'prestadorIndividuo', 'centro','prestadorCentro','tipoTransporte','dia','hora','tiempoViaje','llegaGeografico','cantidadPediatras','llega']]
        with open('./app/files/consultOut/IndividualResult'+sessionKey+'.csv', 'w',newline="") as csvFile:
            writer = csv.writer(csvFile)
            for i in range(0,len(individuos),6):
                nIndividuos = individuos[i:i+6]
                job = calculateIndividual.chunks(nIndividuos,1).group()
                resultado = job.apply_async(queue = "CalculationQueue")
                with allow_join_result():
                    resultList = resultado.join()
                    resultList = sum(sum(resultList,[]), [])
                    for row in resultList:
                        writer.writerow(row)
                #saveCSVfromString(resultList,sessionKey)
        addProgress(sessionKey,5)
        print("ENDOSINDIVIDUALCSV")
    if(isResumen):
        job = suzuki.chunks(individuos,1).group()
        result = job.apply_async(queue = "CalculationQueue")
        with allow_join_result():
            resultList = result.join()
            resultList = sum(sum(resultList,[]), [])
            saveResumenToCsv(resultList,sessionKey)
    session['calculationStatus'] = 1
    session.save()
    #raise SystemExit()

def saveResumenToCsv(result,sessionKey):
    fieldNames = ['persona', 'cantidadTotalHoras','cantidadHorasLunes','cantidadHorasMartes','cantidadHorasMiercoles', 'cantidadHorasJueves',
                'cantidadHorasViernes','cantidadHorasSabado', 'cantidadMaximaHoras','cantidadConsultasLunes', 'cantidadConsultasMartes','cantidadConsultasMiercoles',
                'cantidadConsultasJueves', 'cantidadConsultasViernes','cantidadConsultasSabado','cantidadTotalConsultas', 'cantidadCentrosLunes',
                'cantidadCentrosMartes','cantidadCentrosMiercoles','cantidadCentrosJueves', 'cantidadCentrosViernes','cantidadCentrosSabado', 'cantidadTotalCentros',
                'centroOptimo']
    with open('./app/files/consultOut/ResumenResult'+sessionKey+'.csv', 'w',newline="") as csvFile:
        writer = csv.DictWriter(csvFile,delimiter = ',',fieldnames = fieldNames)
        writer.writeheader()
        for row in result:
            writer.writerow(row)
    addProgress(sessionKey,5)
    print("EndOFRESUMENCSV")

def saveCSVfromString(csvAsString,sessionKey):
    with open('./app/files/consultOut/IndividualResult'+sessionKey+'.csv', 'w',newline="") as csvFile:
        writer = csv.writer(csvFile)
        for row in csvAsString:
            writer.writerow(row)
    addProgress(sessionKey,5)
    print("ENDOSINDIVIDUALCSV")
def addProgress(sessionKey,amount):
    session = SessionStore(session_key=sessionKey)
    have_lock = False
    my_lock = redis.Redis().lock(sessionKey)
    try:
        have_lock = my_lock.acquire(blocking=True)
        if have_lock:
            print("Got lock.")
            session['current'] = session['current'] + amount if(session.get('current',None)) else amount
            session.save()
        else:
            print("Did not acquire lock.")
    finally:
        if have_lock:
            my_lock.release()
@shared_task
def calculateIndividual(individuos,simParam,sessionKey,dictTiemposSettings):
    dictTiemposSettings['tiempoMaximo'] = timedelta(minutes = int(dictTiemposSettings.get('tiempoMaximo')))
    dictTiemposSettings['tiempoConsulta'] = timedelta(minutes = int(dictTiemposSettings.get('tiempoConsulta')))
    dictTiemposSettings['tiempoLlega'] = timedelta(minutes = int(dictTiemposSettings.get('tiempoLlega')))
    #individuos = Individuo.objects.filter(id__in = individuos)
    diasFilter = [int(x) for x in dictTiemposSettings.get('dias','0.1.2.3.4.5').split('.')]
    horaInicio = int(dictTiemposSettings.get('horaInicio',0))*100
    horaFin = int(dictTiemposSettings.get('horaFin',23))*100
    result = []
    daysList = {0:'Lunes',1:'Martes',2:'Miercoles',3:'Jueves',4:'Viernes',5:'Sabado',6:'Domingo'}
    if(simParam):
        listaCentros = Centro.objects.all()
    else:
        p = dictTiemposSettings['centroPrest']
        if(p == '-1'):
            listaCentros = Centro.objects.all()
        else:
            prestadorIdList = [int(x) for x in dictTiemposSettings['centroPrest']]
            listaCentros = Centro.objects.filter(prestador__id__in = prestadorIdList)
    for individuo in individuos:
        print("Individuo: "+str(individuo.id))
        tiempoIni = time.time()
        if(simParam):
            tipoTrans = TipoTransporte.objects.get(id = int(simParam.get('tipoTransporte',1))) if(simParam.get('tipoTransporte',1) != '-1') else individuo.tipo_transporte
            tieneTrabajo = individuo.tieneTrabajo and (simParam.get('trabaja',0) == '1')
            tieneJardin =  individuo.tieneJardin and (simParam.get('jardin',0) == '1')
            prestador = int(simParam.get('mutualista','-1'))
            if(prestador != -2):
                prestadorObject = Prestador.objects.get(id=prestador) if(prestador!= -1) else individuo.prestador
                prestador = prestadorObject.id if(prestador!= -1) else individuo.prestador.id

        else:
            tipoTrans = individuo.tipo_transporte
            tieneTrabajo = individuo.tieneTrabajo
            tieneJardin = individuo.tieneJardin
            prestadorObject = individuo.prestador
            prestador = prestadorObject.id
        if(individuo.jardin):
            inicioJar = utils.horaMilToDateTime(individuo.jardin.hora_inicio)
            finJar = utils.horaMilToDateTime(individuo.jardin.hora_fin)
        else:
            inicioJar = None
            finJar = None
        if(individuo.trabajo):
            inicioTra = utils.horaMilToDateTime(individuo.trabajo.hora_inicio)
            finTra = utils.horaMilToDateTime(individuo.trabajo.hora_fin)
        else:
            inicioTra = None
            finTra = None

        for centro in listaCentros:
            tiempos = IndividuoTiempoCentro.objects.filter(individuo = individuo, centro = centro,dia__in = diasFilter,hora__gte = horaInicio,hora__lte = horaFin)
            tiemposViaje = utils.getDeltaTiempos(individuo = individuo,centro = centro,tipoTrans = tipoTrans.id)
            if(prestador == -2):
                prestador = centro.prestador.id
                prestadorObject = centro.prestador
            samePrest = prestador == centro.prestador.id
            #individuo.prestador = prestador
            #individuo.tipoTransporte = tipoTrans
            centroId = centro.id_centro
            aux =[]
            for tiempo in tiempos:
                tiempoViaje, llegaG,llega = calcTiempoAndLlega(individuo = individuo,centro = centroId,dia = tiempo.dia,hora = tiempo.hora,
                            pediatras = tiempo.cantidad_pediatras,tiempos = tiemposViaje,samePrest = samePrest, tieneTrabajo = tieneTrabajo,
                            tieneJardin = tieneJardin,dictTiemposSettings=dictTiemposSettings,inicioJar = inicioJar,finJar = finJar ,inicioTra = inicioTra ,finTra = finTra)
                result.append([individuo.id,prestadorObject.nombre,centroId,centro.prestador.nombre,tipoTrans.nombre,daysList[tiempo.dia],tiempo.hora,tiempoViaje,llegaG,tiempo.cantidad_pediatras,llega])
        print("Tiempo en el individuo: "+str(time.time()-tiempoIni))
    have_lock = False
    my_lock = redis.Redis().lock(sessionKey)
    try:
        have_lock = my_lock.acquire(blocking=True)
        if have_lock:
            s = SessionStore(session_key=sessionKey)
            print("Got lock.")
            s['current'] = s['current'] + 1 if(s.get('current',None)) else 1
            s.save()
        else:
            print("Did not acquire lock.")
    finally:
        if have_lock:
            my_lock.release()
    return result
@shared_task
def suzuki(individuos,simParam,sessionKey,dictTiemposSettings):
    dictTiemposSettings['tiempoMaximo'] = timedelta(minutes = int(dictTiemposSettings.get('tiempoMaximo')))
    dictTiemposSettings['tiempoConsulta'] = timedelta(minutes = int(dictTiemposSettings.get('tiempoConsulta')))
    dictTiemposSettings['tiempoLlega'] = timedelta(minutes = int(dictTiemposSettings.get('tiempoLlega')))
    resultList = []
    diasFilter = [int(x) for x in dictTiemposSettings.get('dias','0.1.2.3.4.5').split('.')]
    horaInicio = int(dictTiemposSettings.get('horaInicio',0))*100
    horaFin = int(dictTiemposSettings.get('horaFin',23))*100
    if(simParam):
        listaCentros = Centro.objects.all()
    else:
        p = dictTiemposSettings['centroPrest']
        if(p == '-1'):
            listaCentros = Centro.objects.all()
        else:
            prestadorIdList = [int(x) for x in dictTiemposSettings['centroPrest']]
            listaCentros = Centro.objects.filter(prestador__id__in = prestadorIdList)
    for individuo in individuos:
        print("Individuo: "+str(individuo.id))
        tiempoIni = time.time()
        if(simParam):
            tipoTrans = simParam.get('tipoTrans',"1") if(simParam.get('tipoTrans',"1") != "-1") else individuo.tipo_transporte.id
            tieneTrabajo = individuo.tieneTrabajo and (simParam.get('trabaja',"0") == "1")
            tieneJardin =  individuo.tieneJardin and (simParam.get('jardin',"0") == "1")
            prestadorId = simParam.get('mutualista',"1") if(simParam.get('mutualista',"1") != "-1") else individuo.prestador.id
        else:
            tipoTrans = individuo.tipo_transporte.id
            tieneTrabajo = individuo.tieneTrabajo
            tieneJardin = individuo.tieneJardin
            prestadorId = individuo.prestador.id
        if(individuo.jardin):
            inicioJar = utils.horaMilToDateTime(individuo.jardin.hora_inicio)
            finJar = utils.horaMilToDateTime(individuo.jardin.hora_fin)
        else:
            inicioJar = None
            finJar = None
        if(individuo.trabajo):
            inicioTra = utils.horaMilToDateTime(individuo.trabajo.hora_inicio)
            finTra = utils.horaMilToDateTime(individuo.trabajo.hora_fin)
        else:
            inicioTra = None
            finTra = None
        #, centro__prestador__id = individuo.prestador.id)
        #print("***********************************************")
        #print(tipoTrans,tieneTrabajo,tieneJardin,prestadorId)
        dictConsultasPorDia = {0:0,1:0,2:0,3:0,4:0,5:0}
        dictHorasPorDia = {0:set(),1:set(),2:set(),3:set(),4:set(),5:set()}
        dictCentrosPorDia = {0:set(),1:set(),2:set(),3:set(),4:set(),5:set()}
        centros = dict()
        for centro in listaCentros:
            tiempos = IndividuoTiempoCentro.objects.filter(individuo = individuo, centro = centro,dia__in = diasFilter,hora__gte = horaInicio,hora__lte = horaFin)
            tiemposViaje = utils.getDeltaTiempos(individuo = individuo,centro = centro,tipoTrans = tipoTrans)
            samePrest = prestadorId == centro.prestador.id if (prestadorId != -2) else True
            centroId = centro.id_centro
            for tiempo in tiempos:
                tiempoViaje, llega = calcTiempoDeViaje(individuo = individuo,centro = centroId,dia = tiempo.dia,hora = tiempo.hora, pediatras = tiempo.cantidad_pediatras,tiempos = tiemposViaje,
                        samePrest = samePrest, tieneTrabajo = tieneTrabajo, tieneJardin = tieneJardin,dictTiemposSettings=dictTiemposSettings,inicioJar = inicioJar,finJar = finJar ,inicioTra = inicioTra ,finTra = finTra)
                if(llega == "Si"):
                    dia = tiempo.dia
                    dictConsultasPorDia[dia] = dictConsultasPorDia[dia] + 1
                    dictHorasPorDia[dia].add(tiempo.hora)
                    dictCentrosPorDia[dia].add(centroId)
                    if(centroId in centros):
                        if(tiempoViaje < centros[centroId]):
                            centros[centroId] = tiempoViaje
                    else:
                        centros[centroId] = tiempoViaje
        totalHoras = utils.getTotalFromDict(dictHorasPorDia)
        totalConsultas = utils.getTotalFromDict(dictConsultasPorDia)
        totalCentros = len(centros)
        centroOptimo = getCentroOptimo(individuo).id_centro
       # centroOptimo = Centro.objects.get(id_centro = centroOptimo) if(centroOptimo) else centroOptimo
        leResumen = {'persona':individuo.id, 'cantidadTotalHoras':totalHoras,'cantidadHorasLunes':len(dictHorasPorDia[0]),
                    'cantidadHorasMartes':len(dictHorasPorDia[1]),'cantidadHorasMiercoles':len(dictHorasPorDia[2]), 'cantidadHorasJueves':len(dictHorasPorDia[3]),
                    'cantidadHorasViernes':len(dictHorasPorDia[4]),'cantidadHorasSabado':len(dictHorasPorDia[5]), 'cantidadMaximaHoras':utils.getMaximoDict(dictHorasPorDia),
                    'cantidadConsultasLunes':dictConsultasPorDia[0], 'cantidadConsultasMartes':dictConsultasPorDia[1],'cantidadConsultasMiercoles':dictConsultasPorDia[2],
                    'cantidadConsultasJueves':dictConsultasPorDia[3], 'cantidadConsultasViernes':dictConsultasPorDia[4],'cantidadConsultasSabado':dictConsultasPorDia[5],
                    'cantidadTotalConsultas':totalConsultas, 'cantidadCentrosLunes':len(dictCentrosPorDia[0]), 'cantidadCentrosMartes':len(dictCentrosPorDia[1]),
                    'cantidadCentrosMiercoles':len(dictCentrosPorDia[2]),'cantidadCentrosJueves':len(dictCentrosPorDia[3]), 'cantidadCentrosViernes':len(dictCentrosPorDia[4]),
                    'cantidadCentrosSabado':len(dictCentrosPorDia[5]), 'cantidadTotalCentros':totalCentros, 'centroOptimo':centroOptimo}
        resultList.append(leResumen)
        print("Tiempo en el individuo: "+str(time.time()-tiempoIni))
    have_lock = False
    my_lock = redis.Redis().lock(sessionKey)
    try:
        have_lock = my_lock.acquire(blocking=True)
        if have_lock:
            s = SessionStore(session_key=sessionKey)
            print("Got lock.")
            s['current'] = s['current'] + 1 if(s.get('current',None)) else 1
            s.save()
        else:
            print("Did not acquire lock.")
    finally:
        if have_lock:
            my_lock.release()
    return resultList
def getCentroOptimo(individuo):
    if(individuo.tipo_transporte.id == 0):
        return IndividuoCentroOptimo.objects.get(individuo = individuo).centroOptimoCaminando
    elif(individuo.tipo_transporte.id == 2):
        return IndividuoCentroOptimo.objects.get(individuo = individuo).centroOptimoOmnibus
    else:
        return IndividuoCentroOptimo.objects.get(individuo = individuo).centroOptimoAuto
def calcTiempoDeViaje(individuo,centro,dia,hora,pediatras,tiempos, samePrest,tieneTrabajo,tieneJardin,dictTiemposSettings,inicioJar ,finJar ,inicioTra ,finTra ):
    tiempoMaximo   = dictTiemposSettings.get('tiempoMaximo')
    tiempoConsulta = dictTiemposSettings.get('tiempoConsulta')
    tiReLle        = dictTiemposSettings.get('tiempoLlega')
    horaSalida = 0
    hogar = individuo.hogar
    trabajo = individuo.trabajo
    jardin = individuo.jardin
    hasPed = pediatras >0
    horaDate = utils.horaMilToDateTime(hora)
    if(tieneTrabajo and horaDate > inicioTra and horaDate < finTra and trabajo.dias in utils.getListOfDays(trabajo.dias)
            or tieneJardin and horaDate > inicioJar and horaDate < finJar and jardin.dias in utils.getListOfDays(jardin.dias)):
        return -1,"No"
    if(tieneTrabajo and dia in utils.getListOfDays(trabajo.dias)):
        if(horaDate < inicioTra):
            if(tieneJardin and dia in utils.getListOfDays(jardin.dias)):
                if(horaDate < inicioJar):
                    resultTimpo = tiempos['tHogarCentro']
                    resultLlega = "Si" if (resultTimpo<=tiempoMaximo and horaDate + tiempoConsulta + tiempos['tCentroJardin'] <= inicioJar and horaDate + tiempoConsulta + tiempos['tCentroJardin'] + tiempos['tJardinTrabajo'] <= inicioTra and hasPed  and samePrest) else "No"
                    return resultTimpo.total_seconds() / 60,resultLlega
                else:
                    resultTimpo = tiempos['tHogarJardin'] + tiempos['tJardinCentro']
                    horaTerCons1 = horaDate + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo']
                    horaTerCons2  = finJar + tiempos['tJardinCentro'] + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo']
                    horaViajeMasConsulta = max(horaTerCons1, horaTerCons2)
                    if(horaViajeMasConsulta <= inicioTra and finJar + tiempos['tJardinCentro'] <= horaDate + tiReLle):
                        llegaG, resultTimpo = utils.vuelveHogar(finJar,tiempos['tJardinHogar'],tiempos['tHogarCentro'],resultTimpo,horaDate,tiReLle,tiempoMaximo)
                    else:
                        llegaG = "No"
                    resultLlega = "Si" if (llegaG == "Si" and hasPed  and samePrest) else "No"
                    return resultTimpo.total_seconds() / 60,resultLlega
            else:
                resultTimpo =tiempos['tHogarCentro']
                horaViajeMasConsulta =horaDate + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo']
                resultLlega = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta <= inicioTra and hasPed and samePrest ) else "No"
                return resultTimpo.total_seconds() / 60,resultLlega
        else:
            if(tieneJardin and dia in utils.getListOfDays(jardin.dias)):
                if(horaDate < inicioJar):
                    resultTimpo = tiempos['tTrabajoHogar'] + tiempos['tHogarCentro']
                    horaTerCons1 = horaDate + tiempoConsulta + tiempos['tCentroJardin']
                    horaTerCons2 =finTra + tiempos['tTrabajoHogar'] + tiempos['tHogarCentro'] + tiempoConsulta + tiempos['tCentroJardin']
                    horaViajeMasConsulta = max(horaTerCons1, horaTerCons2)
                    if(horaViajeMasConsulta <= inicioJar and finTra + resultTimpo <= horaDate + tiReLle):
                        llegaG, resultTimpo = utils.vuelveHogar(finTra,tiempos['tTrabajoHogar'],tiempos['tHogarCentro'],resultTimpo,horaDate,tiReLle,tiempoMaximo)
                    else:
                        llegaG = "No"
                    resultLlega = "Si" if (llegaG == "Si" and hasPed  and samePrest) else "No"
                    return resultTimpo.total_seconds() / 60,resultLlega

                else:
                    resultTimpo =tiempos['tTrabajoJardin'] + tiempos['tJardinCentro']
                    horaLlegadaJardin =finTra + tiempos['tTrabajoJardin']
                    horaSalidaJardin = finJar if (horaLlegadaJardin <= finJar) else horaLlegadaJardin
                    if(horaSalidaJardin + tiempos['tJardinCentro'] <= horaDate + tiReLle ):
                        llegaG,resultTimpo = utils.vuelveHogar(horaSalidaJardin,tiempos['tJardinHogar'],tiempos['tHogarCentro'],resultTimpo,horaDate,tiReLle,tiempoMaximo)
                    else:
                        llegaG = "No"
                    resultLlega = "Si" if (llegaG == "Si" and hasPed   and samePrest) else "No"
                    return resultTimpo.total_seconds() / 60,resultLlega
            else:
                resultTimpo = tiempos['tTrabajoHogar'] + tiempos['tHogarCentro']
                if(finTra + resultTimpo <= horaDate +tiReLle):
                        llegaG,resultTimpo = utils.vuelveHogar(finTra,tiempos['tTrabajoHogar'],tiempos['tHogarCentro'],resultTimpo,horaDate,tiReLle,tiempoMaximo)
                else:
                    llegaG = "No"
                resultLlega = "Si" if (llegaG == "Si" and hasPed  and samePrest) else "No"
                return resultTimpo.total_seconds() / 60,resultLlega
    else:
        if(jardin and dia in utils.getListOfDays(jardin.dias)):
            if(horaDate < inicioJar):
                resultTimpo = tiempos['tHogarCentro']
                resultLlega = "Si" if (resultTimpo<=tiempoMaximo and horaDate + tiempoConsulta + tiempos['tCentroJardin'] <= inicioJar and hasPed  and samePrest) else "No"
                return resultTimpo.total_seconds() / 60,resultLlega
            else:
                resultTimpo =tiempos['tHogarJardin']+ tiempos['tJardinCentro']
                if(finJar + tiempos['tJardinCentro'] <= horaDate + tiReLle):
                    llegaG,resultTimpo = utils.vuelveHogar(finJar,tiempos['tJardinHogar'],tiempos['tHogarCentro'],resultTimpo,horaDate,tiReLle,tiempoMaximo)
                else:
                    llegaG = "No"
                resultLlega = "Si" if (llegaG and hasPed and samePrest) else "No"
                return resultTimpo.total_seconds() / 60,resultLlega
        else:
            resultTimpo =tiempos['tHogarCentro']
            resultLlega = "Si" if (resultTimpo<=tiempoMaximo and hasPed  and samePrest) else "No"
            return resultTimpo.total_seconds() / 60,resultLlega
def calcTiempoAndLlega(individuo,centro,dia,hora,pediatras,tiempos, samePrest,tieneTrabajo,tieneJardin,dictTiemposSettings,inicioJar,finJar,inicioTra,finTra):
    tiempoMaximo = dictTiemposSettings.get('tiempoMaximo')
    tiempoConsulta = dictTiemposSettings.get('tiempoConsulta')
    tiReLle = dictTiemposSettings.get('tiempoLlega')
    hogar = individuo.hogar
    trabajo = individuo.trabajo
    jardin = individuo.jardin
    hasPed = pediatras>0
    horaDate = utils.horaMilToDateTime(hora)

    if(tieneTrabajo and horaDate >= inicioTra and horaDate < finTra and dia in utils.getListOfDays(trabajo.dias) or
            tieneJardin and horaDate >= inicioJar and horaDate < finJar and dia in utils.getListOfDays(jardin.dias)):
        return -1,"No","No"
    if(tieneTrabajo and dia in utils.getListOfDays(trabajo.dias)):
        if(horaDate < inicioTra):
            if(tieneJardin and dia in utils.getListOfDays(jardin.dias)):
                if(horaDate < inicioJar):
                    resultTimpo = tiempos['tHogarCentro']
                    resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and horaDate + tiempoConsulta + tiempos['tCentroJardin'] <= inicioJar and horaDate + tiempoConsulta + tiempos['tCentroJardin'] + tiempos['tJardinTrabajo'] <= inicioTra) else "No"
                    BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                    resultLlega = "Si" if (BoolLlega) else "No"
                    return resultTimpo.total_seconds() / 60,resultLlegaG,resultLlega
                else:
                    #TODO: VER AFTER LUNES
                    resultTimpo = tiempos['tHogarJardin'] + tiempos['tJardinCentro']
                    horaTerCons1 = horaDate + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo']
                    horaTerCons2  = finJar + tiempos['tJardinCentro'] + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo']
                    horaViajeMasConsulta = max(horaTerCons1, horaTerCons2)
                    resultLlegaG = "Si" if (horaViajeMasConsulta <= inicioTra and finJar + tiempos['tJardinCentro'] <= horaDate + tiReLle) else "No"
                    if(resultLlegaG == "Si"):
                        resultLlegaG,resultTimpo = utils.vuelveHogar(finJar,tiempos['tJardinHogar'],tiempos['tHogarCentro'],resultTimpo,horaDate,tiReLle,tiempoMaximo)                        
                    BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                    resultLlega = "Si" if (BoolLlega) else "No"
                    return resultTimpo.total_seconds() / 60,resultLlegaG,resultLlega
            else:
                resultTimpo = tiempos['tHogarCentro']
                horaViajeMasConsulta = horaDate + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo']
                resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta <= inicioTra) else "No"
                BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                resultLlega = "Si" if (BoolLlega) else "No"
                return resultTimpo.total_seconds() / 60,resultLlegaG,resultLlega
        else:
            if(tieneJardin and dia in utils.getListOfDays(jardin.dias)):
                if(horaDate < inicioJar):
                    resultTimpo = tiempos['tTrabajoHogar'] + tiempos['tHogarCentro']
                    horaTerCons1 = horaDate + tiempoConsulta + tiempos['tCentroJardin']
                    horaTerCons2 = finTra + tiempos['tTrabajoHogar'] + tiempos['tHogarCentro'] + tiempoConsulta + tiempos['tCentroJardin']
                    horaViajeMasConsulta = max(horaTerCons1, horaTerCons2)
                    resultLlegaG = "Si" if (horaViajeMasConsulta<= inicioJar and finTra + resultTimpo <= horaDate + tiReLle) else "No"
                    if(resultLlegaG == "Si"):
                        resultLlegaG,resultTimpo = utils.vuelveHogar(finTra,tiempos['tTrabajoHogar'],tiempos['tHogarCentro'],resultTimpo,horaDate,tiReLle,tiempoMaximo)                        
                    BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                    resultLlega = "Si" if (BoolLlega) else "No"
                    return resultTimpo.total_seconds() / 60,resultLlegaG,resultLlega

                else:
                    resultTimpo = tiempos['tTrabajoJardin'] + tiempos['tJardinCentro']
                    horaLlegadaJardin = finTra + tiempos['tTrabajoJardin']
                    horaSalidaJardin = finJar if (horaLlegadaJardin <= finJar) else horaLlegadaJardin
                    resultLlegaG = "Si" if (horaSalidaJardin + tiempos['tJardinCentro'] <= horaDate, tiReLle) else "No"
                    if(resultLlegaG == "Si"):
                        resultLlegaG,resultTimpo = utils.vuelveHogar(horaSalidaJardin,tiempos['tJardinHogar'],tiempos['tHogarCentro'],resultTimpo,horaDate,tiReLle,tiempoMaximo)                        
                    BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                    resultLlega = "Si" if (BoolLlega) else "No"
                    return resultTimpo.total_seconds() / 60,resultLlegaG,resultLlega
            else:
                resultTimpo = tiempos['tTrabajoHogar'] + tiempos['tHogarCentro']
                resultLlegaG = "Si" if (finTra + resultTimpo <= horaDate + tiReLle) else "No"
                if(resultLlegaG == "Si"):
                        resultLlegaG,resultTimpo = utils.vuelveHogar(finTra,tiempos['tTrabajoHogar'],tiempos['tHogarCentro'],resultTimpo,horaDate,tiReLle,tiempoMaximo)      
                BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                resultLlega = "Si" if (BoolLlega) else "No"
                return resultTimpo.total_seconds() / 60,resultLlegaG,resultLlega
    else:
        if(jardin and dia in utils.getListOfDays(jardin.dias)):
            if(horaDate < inicioJar):
                resultTimpo = tiempos['tHogarCentro']
                resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and horaDate + tiempoConsulta + tiempos['tCentroJardin'] <= inicioJar) else "No"
                BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                resultLlega = "Si" if (BoolLlega) else "No"
                return resultTimpo.total_seconds() / 60,resultLlegaG,resultLlega
            else:
                resultTimpo = tiempos['tHogarJardin']+ tiempos['tJardinCentro']
                resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and finJar + tiempos['tJardinCentro'] <= horaDate + tiReLle) else "No"
                if(resultLlegaG == "Si"):
                        resultLlegaG,resultTimpo = utils.vuelveHogar(finJar,tiempos['tJardinHogar'],tiempos['tHogarCentro'],resultTimpo,horaDate,tiReLle,tiempoMaximo) 
                BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                resultLlega = "Si" if (BoolLlega) else "No"
                return resultTimpo.total_seconds() / 60,resultLlegaG,resultLlega
        else:
            resultTimpo = tiempos['tHogarCentro']
            resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo) else "No"
            BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
            resultLlega = "Si" if (BoolLlega) else "No"
            return resultTimpo.total_seconds() / 60,resultLlegaG,resultLlega
@shared_task
def saveTiemposToDB(tipo):
    if(tipo == 0):
        tipoId = 'Caminando'
        sep = ';'
        print("soyCaminando")
        SectorTiempoCaminando.objects.all().delete()
    else:
        tipoId = 'Auto'
        print("soyAuto")
        sep = ','
        print(tipo)
        SectorTiempoAuto.objects.all().delete()
    id = -1
    tiempos = []
    init = time.time()
    bulkAmount = 10000
    csvFile = open("./app/files/RawCsv/tiempos"+tipoId+".csv", 'r')
    lineas = csv.reader(csvFile)
    progressTotal = Settings.objects.get(setting='totalMatriz'+tipoId)
    progressTotal.value = sum(1 for row in lineas) - 1 #len(lineas)
    csvFile.seek(0)
    progressTotal.save()
    for caso in lineas:
        if(id == -1):
            id +=1
            continue
        if(sep==';'):
            caso = caso[0].split(sep)
        sector1 = caso[0]
        sector2 = caso[1]
        t = float(caso[2])
        dist = float(caso[3])
        if(tipo == 0):
            tiempo = SectorTiempoCaminando(id = id , sector_1_id = sector1, sector_2_id = sector2, tiempo = float(caso[2]), distancia = float(caso[3]))
        else:
            tiempo = SectorTiempoAuto(id = id , sector_1_id = sector1, sector_2_id = sector2, tiempo = float(caso[2]), distancia = float(caso[3]))
        id +=1
        tiempos.append(tiempo)
        if(id % bulkAmount == 0):
            progressDone  = Settings.objects.get(setting='currentMatriz'+tipoId)
            progressDone.value  = int(progressDone.value) + bulkAmount
            progressDone.save()
            print(id)
            print(time.time() - init)
            init = time.time()
            print("Wea "+str(progressDone.value))
            if(tipo == 1):
                guardar = SectorTiempoAuto.objects.bulk_create(tiempos)
            else:
                guardar = SectorTiempoCaminando.objects.bulk_create(tiempos)
            tiempos = []
    if(tiempos):
        if(tipo == 1):
            guardar = SectorTiempoAuto.objects.bulk_create(tiempos)
        else:
            guardar = SectorTiempoCaminando.objects.bulk_create(tiempos)
    progressDone  = Settings.objects.get(setting='currentMatriz'+tipoId)
    progressDone.value  = float(progressDone.value) + bulkAmount
    progressDone.save()
    status  = Settings.objects.get(setting='statusMatriz'+tipoId)
    status.value  = 1
    status.save()
    print("Se cargo correctamente el archivo")
@shared_task
def saveTiemposBusToDB(lineas):
    SectorTiempoOmnibus.objects.all().delete()
    id = 0
    tiempos = []
    bulkAmount = 10000
    lineas,diagonales = lineas[:-1], lineas[-1]
    for i in range(len(lineas)):
        for j in range(len(lineas[i])):
            if i == j:
                t = float(diagonales[j])
            else:
                l = list(map(lambda x: float(x),lineas[i][j].split(';')))
                t = l[0]*TIEMPO_ESPERA + l[1]*TIEMPO_VIAJE + l[2]*TIEMPO_CAMBIO_PARADA
                if t < 0:
                    t = TIEMPO_ARBITRARIAMENTE_ALTO
            tiempo = SectorTiempoOmnibus(id = id, sectorO_1_id = i, sectorO_2_id = j, tiempo = t)
            tiempos.append(tiempo)
            id +=1
            if(id % bulkAmount == 0):
                print(id)
                guardar = SectorTiempoOmnibus.objects.bulk_create(tiempos)
                tiempos = []
                progressDone  = Settings.objects.get(setting='currentMatrizBus')
                progressDone.value  = float(progressDone.value) + bulkAmount
                progressDone.save()
                print(id)
    if(tiempos != list()):
        guardar = SectorTiempoOmnibus.objects.bulk_create(tiempos)
        progressDone  = Settings.objects.get(setting='currentMatrizBus')
        progressDone.value  = float(progressDone.value) + bulkAmount
        progressDone.save()
        status  = Settings.objects.get(setting='statusMatrizBus')
        status.value  = 1
        status.save()
    print("Se cargo correctamente el archivo")
@shared_task
def saveCentrosToDB(lineas,dict_prestadores):
    sf = shapefile.Reader('app/files/shapeAuto.shp')
    shapeAuto = sf.shapes()
    recordsAuto = sf.records()
    sf = shapefile.Reader('app/files/shapeCaminando.shp')
    shapeCaminando = sf.shapes()
    recordsCaminando = sf.records()
    sf = shapefile.Reader('app/files/shapeBus.shp')
    shapeBus = sf.shapes()
    recordsBus = sf.records()
    Pediatra.objects.all().delete()
    Centro.objects.all().delete()
    horas = [str(float(x)) for x in range(6,22)] # ["6.0".."21.0"]
    for caso in lineas:
        ## Centro
        #Id, Coordenada X, Coordenada Y, SectorAuto, SectorCaminando, Prestador
        id_centro = int(caso[0])
        prestador = dict_prestadores.get(caso[1],1000)
        centro = Centro(id_centro,float(caso[3]),float(caso[4]),None,None,None,prestador)
        centro.sector_auto      = utils.getSectorForPoint(centro, shapeAuto,recordsAuto, SectorAuto)
        centro.sector_caminando = utils.getSectorForPoint(centro, shapeCaminando,recordsCaminando, SectorCaminando)
        centro.sector_bus       = utils.getSectorForPoint(centro, shapeBus, recordsBus, SectorOmnibus)
        centro.save()
        ## Pediatra
        #Centro, Dia, Hora, Cantidad de pediatras
        contador_dias = 5
        pediatras = list()
        print("Se completo el centro: "+str(id_centro))
        for i in range(6):
            for j in horas:
                if(contador_dias > len(caso)): # Nunca deberia pasar, pero supongo?
                    break
                try:
                    if ((caso[contador_dias]) == '0' or caso[contador_dias] == ''):
                        cantPediatras = 0
                    else:
                        cantPediatras = int(caso[contador_dias].rstrip('0').replace('.','')) # "10.0" -> "10." -> "10" -> 10
                except:
                    print(caso[contador_dias])
                    print(caso)
                pediatras.append(Pediatra(centro_id = id_centro, dia = i, hora = utils.parsear_hora(j), cantidad_pediatras = cantPediatras))
                contador_dias +=1
        Pediatra.objects.bulk_create(pediatras)
        progressDone  = Settings.objects.get(setting='currentMatrizCentro')
        progressDone.value  = float(progressDone.value) + 1
        progressDone.save()
    status  = Settings.objects.get(setting='statusMatrizCentro')
    status.value  = 1
    status.save()
    print("Se cargo correctamente el archivo")
@shared_task
def saveIndividuosToDB(lineas):
    sf = shapefile.Reader('app/files/shapeAuto.shp')
    shapeAuto = sf.shapes()
    recordsAuto = sf.records()
    sf = shapefile.Reader('app/files/shapeCaminando.shp')
    shapeCaminando = sf.shapes()
    recordsCaminando = sf.records()
    sf = shapefile.Reader('app/files/shapeBus.shp')
    shapeBus = sf.shapes()
    recordsBus = sf.records()
    AnclaTemporal.objects.all().delete()
    Individuo.objects.all().delete()
    tipos_transporte = [x.nombre for x in TipoTransporte.objects.all()]
    dicc_transporte = {x.nombre:x for x in TipoTransporte.objects.all()}
    idAncla = 0
    for caso in lineas:
        print("Individuo "+caso[0])
        ## Ancla
        #Coordenada X, Coordenada Y, Tipo, Hora inicio, Hora fin, Dias, Sector auto, Sector caminando
        #Duda Tecnica -Contemplar casos donde no hay jardin y/o trabajo
        if(caso[5] == "1"):
            anclaJardin  = AnclaTemporal(idAncla,float(caso[10]),float(caso[11]),"jardin" ,utils.parsear_hora(caso[7]) ,utils.parsear_hora(caso[8]) ,caso[6] ,None,None)
            anclaJardin.sector_auto      = utils.getSectorForPoint(anclaJardin, shapeAuto,recordsAuto, SectorAuto)
            anclaJardin.sector_caminando = utils.getSectorForPoint(anclaJardin,shapeCaminando,recordsCaminando, SectorCaminando)
            anclaJardin.sector_bus       = utils.getSectorForPoint(anclaJardin, shapeBus, recordsBus, SectorOmnibus)
            anclaJardin.save()
            idAncla +=1
            tieneJardin = True
        else:
            tieneJardin = False
            anclaJardin = None
        if(caso[12] == "1"):
            anclaTrabajo = AnclaTemporal(idAncla,float(caso[14]),float(caso[15]),"trabajo",utils.parsear_hora(caso[17]),utils.parsear_hora(caso[18]),caso[16],None,None)
            anclaTrabajo.sector_auto      = utils.getSectorForPoint(anclaTrabajo, shapeAuto,recordsAuto, SectorAuto)
            anclaTrabajo.sector_caminando = utils.getSectorForPoint(anclaTrabajo,shapeCaminando,recordsCaminando, SectorCaminando)
            anclaTrabajo.sector_bus       = utils.getSectorForPoint(anclaTrabajo, shapeBus, recordsBus, SectorOmnibus)
            anclaTrabajo.save()
            idAncla +=1
            tieneTrabajo = True
        else:
            tieneTrabajo = False
            anclaTrabajo = None
        anclaHogar   = AnclaTemporal(idAncla,float(caso[22]),float(caso[23]),"hogar",None,None,"L-D",None,None)
        anclaHogar.sector_auto      = utils.getSectorForPoint(anclaHogar, shapeAuto,recordsAuto, SectorAuto)
        anclaHogar.sector_caminando = utils.getSectorForPoint(anclaHogar,shapeCaminando,recordsCaminando, SectorCaminando)
        anclaHogar.sector_bus       = utils.getSectorForPoint(anclaHogar, shapeBus, recordsBus, SectorOmnibus)
        anclaHogar.save()
        idAncla +=1
        ## Individuo
        #Id, Tipo transporte, Prestador, Hogar, Trabajo, Jardin
        individuo  = Individuo(id = int(caso[0]),tipo_transporte = dicc_transporte.get(caso[19]),prestador = Prestador.objects.get(id =int(caso[1])),
                    hogar = anclaHogar,trabajo = anclaTrabajo, jardin = anclaJardin, tieneJardin = tieneJardin,tieneTrabajo = tieneTrabajo)
        individuo.save()
        progressDone  = Settings.objects.get(setting='currentMatrizIndividuo')
        progressDone.value  = float(progressDone.value) + 1
        progressDone.save()
    print("Se cargo correctamente el archivo")
    status  = Settings.objects.get(setting='statusMatrizIndividuo')
    status.value  = 1
    status.save()

@shared_task
def calcularTiemposMatrix():
    individuos = Individuo.objects.all()
    centros = Centro.objects.all()
    id = 0
    for individuo in individuos:
        print("IndividuoCentro: "+str(individuo.id))
        listaHoras = []
        for centro in centros:
            consultas = Pediatra.objects.filter(centro = centro)
            for consulta in consultas:
                q = IndividuoTiempoCentro(id = id,individuo = individuo,centro=centro,dia = consulta.dia,hora = consulta.hora,cantidad_pediatras = consulta.cantidad_pediatras)
                listaHoras.append(q)
                id = id+1
        IndividuoTiempoCentro.objects.bulk_create(listaHoras)
        progressDone  = Settings.objects.get(setting='currentMatrizIndividuoTiempoCentro')
        progressDone.value  = float(progressDone.value) + 1
        progressDone.save()
    newCalcTimes()

def newCalcTimes():
    individuos     = Individuo.objects.select_related().all()
    centros        = Centro.objects.select_related().all()
    #individuos = Individuo.objects.all()
    #centros = Centro.objects.all()
    for individuo in individuos:
        print(individuo.id)
        transporte     = individuo.tipo_transporte.id
        trabajo        = individuo.trabajo
        jardin         = individuo.jardin
        secHogarAuto   = utils.newGetSector(individuo.hogar, 1)
        secTrabajoAuto = utils.newGetSector(trabajo,         1)
        secJardinAuto  = utils.newGetSector(jardin,          1)
        ######
        secHogarCaminando   = utils.newGetSector(individuo.hogar, 0)
        secTrabajoCaminando = utils.newGetSector(trabajo,         0)
        secJardinCaminando  = utils.newGetSector(jardin,          0)
        #####
        secHogarBus   = utils.newGetSector(individuo.hogar, 2)
        secTrabajoBus = utils.newGetSector(trabajo,         2)
        secJardinBus  = utils.newGetSector(jardin,          2)
        ####
        tHogarTrabajoAuto  = ceil(utils.calcularTiempoViaje([secHogarAuto,   secTrabajoAuto],  1)/60)
        tHogarJardinAuto   = ceil(utils.calcularTiempoViaje([secHogarAuto,   secJardinAuto],   1)/60)
        tJardinTrabajoAuto = ceil(utils.calcularTiempoViaje([secJardinAuto,  secTrabajoAuto],  1)/60)
        tJardinHogarAuto   = ceil(utils.calcularTiempoViaje([secJardinAuto,  secHogarAuto],    1)/60)
        tTrabajoJardinAuto = ceil(utils.calcularTiempoViaje([secTrabajoAuto, secJardinAuto],   1)/60)
        tTrabajoHogarAuto  = ceil(utils.calcularTiempoViaje([secTrabajoAuto, secHogarAuto],    1)/60)
#######################
        tHogarTrabajoCaminando  = ceil(utils.calcularTiempoViaje([secHogarCaminando,   secTrabajoCaminando],  0)/60)
        tHogarJardinCaminando   = ceil(utils.calcularTiempoViaje([secHogarCaminando,   secJardinCaminando],   0)/60)
        tJardinTrabajoCaminando = ceil(utils.calcularTiempoViaje([secJardinCaminando,  secTrabajoCaminando],  0)/60)
        tJardinHogarCaminando   = ceil(utils.calcularTiempoViaje([secJardinCaminando,  secHogarCaminando],    0)/60)
        tTrabajoJardinCaminando = ceil(utils.calcularTiempoViaje([secTrabajoCaminando, secJardinCaminando],   0)/60)
        tTrabajoHogarCaminando  = ceil(utils.calcularTiempoViaje([secTrabajoCaminando, secHogarCaminando],    0)/60)
#######################
        tHogarTrabajoBus  = ceil(utils.calcularTiempoViaje([secHogarBus,   secTrabajoBus], 2)/60)
        tHogarJardinBus   = ceil(utils.calcularTiempoViaje([secHogarBus,   secJardinBus],  2)/60)
        tJardinTrabajoBus = ceil(utils.calcularTiempoViaje([secJardinBus,  secTrabajoBus], 2)/60)
        tJardinHogarBus   = ceil(utils.calcularTiempoViaje([secJardinBus,  secHogarBus],   2)/60)
        tTrabajoJardinBus = ceil(utils.calcularTiempoViaje([secTrabajoBus, secJardinBus],  2)/60)
        tTrabajoHogarBus  = ceil(utils.calcularTiempoViaje([secTrabajoBus, secHogarBus],   2)/60)
        tiemposCentros = []
        auxOptimo = IndividuoCentroOptimo(individuo = individuo)
        for centro in centros:
            aux = time.time()
            secCentroAuto      = utils.newGetSector(centro, 1)
            secCentroCaminando = utils.newGetSector(centro, 0)
            secCentroBus       = utils.newGetSector(centro, 2)

            tHogarCentroAuto   = ceil(utils.calcularTiempoViaje([secHogarAuto,  secCentroAuto], 1)/60)
            tJardinCentroAuto  = ceil(utils.calcularTiempoViaje([secJardinAuto, secCentroAuto], 1)/60)
            tCentroHogarAuto   = ceil(utils.calcularTiempoViaje([secCentroAuto, secHogarAuto],  1)/60)
            tCentroJardinAuto  = ceil(utils.calcularTiempoViaje([secCentroAuto, secJardinAuto], 1)/60)
####################
            tHogarCentroCaminando  = ceil(utils.calcularTiempoViaje([secHogarCaminando,  secCentroCaminando], 0)/60)
            tJardinCentroCaminando = ceil(utils.calcularTiempoViaje([secJardinCaminando, secCentroCaminando], 0)/60)
            tCentroHogarCaminando  = ceil(utils.calcularTiempoViaje([secCentroCaminando, secHogarCaminando],  0)/60)
            tCentroJardinCaminando = ceil(utils.calcularTiempoViaje([secCentroCaminando, secJardinCaminando], 0)/60)
#########################
            tHogarCentroBus  = ceil(utils.calcularTiempoViaje([secHogarBus,  secCentroBus], 2)/60)
            tJardinCentroBus = ceil(utils.calcularTiempoViaje([secJardinBus, secCentroBus], 2)/60)
            tCentroHogarBus  = ceil(utils.calcularTiempoViaje([secCentroBus, secHogarBus],  2)/60)
            tCentroJardinBus = ceil(utils.calcularTiempoViaje([secCentroBus, secJardinBus], 2)/60)
            ini = time.time()
            q = IndividuoCentro(individuo = individuo, centro = centro, 
                                
                                tHogarTrabajoAuto  = tHogarTrabajoAuto,    tHogarJardinAuto  = tHogarJardinAuto,   
                                tJardinTrabajoAuto = tJardinTrabajoAuto,   tJardinHogarAuto  = tJardinHogarAuto,
                                tTrabajoJardinAuto = tTrabajoJardinAuto,   tTrabajoHogarAuto = tTrabajoHogarAuto,
                                tHogarCentroAuto   = tHogarCentroAuto,     tJardinCentroAuto = tJardinCentroAuto,
                                tCentroHogarAuto   = tCentroHogarAuto,     tCentroJardinAuto = tCentroJardinAuto,
                
                                tHogarTrabajoCaminando  = tHogarTrabajoCaminando,  tHogarJardinCaminando  = tHogarJardinCaminando,
                                tJardinTrabajoCaminando = tJardinTrabajoCaminando, tJardinHogarCaminando  = tJardinHogarCaminando,
                                tTrabajoJardinCaminando = tTrabajoJardinCaminando, tTrabajoHogarCaminando = tTrabajoHogarCaminando,
                                tHogarCentroCaminando   = tHogarCentroCaminando,   tJardinCentroCaminando = tJardinCentroCaminando,
                                tCentroHogarCaminando   = tCentroHogarCaminando,   tCentroJardinCaminando = tCentroJardinCaminando,
                
                                tHogarTrabajoBus  = tHogarTrabajoBus,  tHogarJardinBus  = tHogarJardinBus,
                                tJardinTrabajoBus = tJardinTrabajoBus, tJardinHogarBus  = tJardinHogarBus,
                                tTrabajoJardinBus = tTrabajoJardinBus, tTrabajoHogarBus = tTrabajoHogarBus,
                                tHogarCentroBus   = tHogarCentroBus,   tJardinCentroBus = tJardinCentroBus,
                                tCentroHogarBus   = tCentroHogarBus,   tCentroJardinBus = tCentroJardinBus
            )
            tiemposCentros.append(q)
            auxOptimo = setOptimo(auxOptimo, centro, tHogarCentroAuto, tHogarCentroBus, tHogarCentroCaminando)
        progressDone  = Settings.objects.get(setting='currentMatrizIndividuoTiempoCentro')
        progressDone.value  = float(progressDone.value) + 1
        progressDone.save()
        IndividuoCentro.objects.bulk_create(tiemposCentros)
        auxOptimo.save()
        print("Termino el individuo: "+str(individuo.id))
    status  = Settings.objects.get(setting='statusMatrizIndividuoTiempoCentro')
    status.value  = 1
    status.save()

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
