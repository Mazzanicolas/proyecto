# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task, group, result
from celery.result import allow_join_result
import time
from app.models import *
import app.utils as utils
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
import redis
import csv
import math

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
    session['current'] = 0
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
        job = calculateIndividual.chunks(individuos,1).group()
        resultado = job.apply_async(queue = "CalculationQueue")
        header = [['individuo', 'prestadorIndividuo', 'centro','prestadorCentro','tipoTransporte','dia','hora','tiempoViaje','llegaGeografico','cantidadPediatras','llega']]
        with allow_join_result():
            resultList = resultado.join()
            resultList =  header + sum(sum(resultList,[]), [])
            saveCSVfromString(resultList,sessionKey)

    if(isResumen):
        job = suzuki.chunks(individuos,1).group()
        result = job.apply_async(queue = "CalculationQueue")
        with allow_join_result():
            resultList = result.join()
            resultList = sum(sum(resultList,[]), [])
            saveResumenToCsv(resultList,sessionKey)

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
        for centro in listaCentros:
            tiempos = IndividuoTiempoCentro.objects.filter(individuo = individuo, centro = centro,dia__in = diasFilter,hora__gte = horaInicio,hora__lte = horaFin)
            tiemposViaje = utils.getTiempos(individuo = individuo,centro = centro,tipoTrans = tipoTrans.id)
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
                            tieneJardin = tieneJardin,dictTiemposSettings=dictTiemposSettings)
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
        #, centro__prestador__id = individuo.prestador.id)
        #print("***********************************************")
        #print(tipoTrans,tieneTrabajo,tieneJardin,prestadorId)
        dictConsultasPorDia = {0:0,1:0,2:0,3:0,4:0,5:0}
        dictHorasPorDia = {0:set(),1:set(),2:set(),3:set(),4:set(),5:set()}
        dictCentrosPorDia = {0:set(),1:set(),2:set(),3:set(),4:set(),5:set()}
        centros = dict()
        for centro in listaCentros:
            tiempos = IndividuoTiempoCentro.objects.filter(individuo = individuo, centro = centro,dia__in = diasFilter,hora__gte = horaInicio,hora__lte = horaFin)
            tiemposViaje = utils.getTiempos(individuo = individuo,centro = centro,tipoTrans = tipoTrans)
            samePrest = prestadorId == centro.prestador.id if (prestadorId != -2) else True
            centroId = centro.id_centro
            for tiempo in tiempos:
                tiempoViaje, llega = calcTiempoDeViaje(individuo = individuo,centro = centroId,dia = tiempo.dia,hora = tiempo.hora, pediatras = tiempo.cantidad_pediatras,tiempos = tiemposViaje,
                        samePrest = samePrest, tieneTrabajo = tieneTrabajo, tieneJardin = tieneJardin,dictTiemposSettings=dictTiemposSettings)
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
        centroOptimo = utils.getCentroOptimo(centros)
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
def calcTiempoDeViaje(individuo,centro,dia,hora,pediatras,tiempos, samePrest,tieneTrabajo,tieneJardin,dictTiemposSettings):
    tiempoMaximo = int(dictTiemposSettings.get('tiempoMaximo'))
    tiempoConsulta = int(dictTiemposSettings.get('tiempoConsulta'))
    tiReLle = int(dictTiemposSettings.get('tiempoLlega'))
    hogar = individuo.hogar
    trabajo = individuo.trabajo
    jardin = individuo.jardin
    hasPed = pediatras >0
    if(tieneTrabajo and hora in range(trabajo.hora_inicio,trabajo.hora_fin) and trabajo.dias in utils.getListOfDays(trabajo.dias) 
            or tieneJardin and hora in range(jardin.hora_inicio,jardin.hora_fin) and jardin.dias in utils.getListOfDays(jardin.dias)):
        return -1,"No"
    if(tieneTrabajo and dia in utils.getListOfDays(trabajo.dias)):
        if(hora < trabajo.hora_inicio):
            if(tieneJardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    resultTimpo = utils.minsToMil(tiempos['tHogarCentro'])
                    resultLlega = "Si" if (resultTimpo<=tiempoMaximo and utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroJardin']) <= jardin.hora_inicio and utils.minsToMil(tiempoConsulta + tiempos['tCentroJardin'] + tiempos['tJardinTrabajo']) <= trabajo.hora_inicio and hasPed ) else "No"
                    return resultTimpo,resultLlega
                else:
                    resultTimpo = utils.minsToMil(tiempos['tHogarJardin'] + tiempos['tJardinCentro'])
                    horaTerCons1 = utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo'])
                    horaTerCons2  = utils.minsToMil(jardin.hora_fin + tiempos['tJardinCentro'] + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo'])
                    horaViajeMasConsulta = max(horaTerCons1, horaTerCons2)
                    resultLlega = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta <= trabajo.hora_inicio and utils.minsToMil(jardin.hora_fin + tiempos['tJardinCentro']) <= utils.minsToMil(hora + tiReLle) and hasPed  and samePrest) else "No"
                    return resultTimpo,resultLlega
            else:
                resultTimpo = utils.minsToMil(tiempos['tHogarCentro'])
                horaViajeMasConsulta = utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo'])
                resultLlega = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta <= trabajo.hora_inicio and hasPed ) else "No"
                return resultTimpo,resultLlega
        else:
            if(tieneJardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    resultTimpo = utils.minsToMil(tiempos['tTrabajoHogar'] + tiempos['tHogarCentro'])
                    horaTerCons1 = utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroJardin'])
                    horaTerCons2 = utils.minsToMil(trabajo.hora_fin + tiempos['tTrabajoHogar'] + tiempos['tHogarCentro'] + tiempoConsulta + tiempos['tCentroJardin'])
                    horaViajeMasConsulta = max(horaTerCons1, horaTerCons2)                    
                    resultLlega = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta<= jardin.hora_inicio and utils.minsToMil(trabajo.hora_fin + resultTimpo) <= utils.minsToMil(hora + tiReLle) and hasPed  and samePrest) else "No"
                    return resultTimpo,resultLlega

                else:
                    resultTimpo =utils.minsToMil(tiempos['tTrabajoJardin'] + tiempos['tJardinCentro'])
                    horaLlegadaJardin = utils.minsToMil(trabajo.hora_fin + tiempos['tTrabajoJardin'])
                    horaSalidaJardin = jardin.hora_fin if (horaLlegadaJardin <= jardin.hora_fin) else horaLlegadaJardin
                    resultLlega = "Si" if (resultTimpo<=tiempoMaximo and  utils.minsToMil(horaSalidaJardin + tiempos['tJardinCentro']) <= utils.minsToMil(hora + tiReLle) and hasPed   and samePrest) else "No"
                    return resultTimpo,resultLlega
            else:
                resultTimpo = utils.minsToMil(tiempos['tTrabajoHogar'] + tiempos['tHogarCentro'])
                resultLlega = "Si" if (resultTimpo<=tiempoMaximo and utils.minsToMil(trabajo.hora_fin + resultTimpo) <= utils.minsToMil(hora +tiReLle) and hasPed  and samePrest) else "No"
                return resultTimpo,resultLlega
    else:
        if(jardin and dia in utils.getListOfDays(jardin.dias)):
            if(hora < jardin.hora_inicio):
                resultTimpo = utils.minsToMil(tiempos['tHogarCentro'])
                resultLlega = "Si" if (resultTimpo<=tiempoMaximo and utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroJardin']) <= jardin.hora_inicio and hasPed  and samePrest) else "No"
                return resultTimpo,resultLlega
            else:
                resultTimpo = utils.minsToMil(tiempos['tHogarJardin']+ tiempos['tJardinCentro'])
                resultLlega = "Si" if (resultTimpo<=tiempoMaximo and utils.minsToMil(jardin.hora_fin + tiempos['tJardinCentro']) <= hora + tiReLle and hasPed and samePrest) else "No"
                return resultTimpo,resultLlega
        else:
            resultTimpo = utils.minsToMil(tiempos['tHogarCentro'])
            resultLlega = "Si" if (resultTimpo<=tiempoMaximo and hasPed  and samePrest) else "No"
            return resultTimpo,resultLlega
def calcTiempoAndLlega(individuo,centro,dia,hora,pediatras,tiempos, samePrest,tieneTrabajo,tieneJardin,dictTiemposSettings):
    tiempoMaximo = int(dictTiemposSettings.get('tiempoMaximo'))
    tiempoConsulta = int(dictTiemposSettings.get('tiempoConsulta'))
    tiReLle = int(dictTiemposSettings.get('tiempoLlega'))
    hogar = individuo.hogar
    trabajo = individuo.trabajo
    jardin = individuo.jardin
    hasPed = pediatras>0
    if(tieneTrabajo and hora in range(trabajo.hora_inicio,trabajo.hora_fin) and dia in utils.getListOfDays(trabajo.dias) or 
            tieneJardin and hora in range(jardin.hora_inicio,jardin.hora_fin) and dia in utils.getListOfDays(jardin.dias)):
        return -1,"No","No"
    if(tieneTrabajo and dia in utils.getListOfDays(trabajo.dias)):
        if(hora < trabajo.hora_inicio):
            if(tieneJardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    resultTimpo = utils.minsToMil(tiempos['tHogarCentro'])
                    resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroJardin']) <= jardin.hora_inicio and utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroJardin'] + tiempos['tJardinTrabajo'])<= trabajo.hora_inicio) else "No"
                    BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                    resultLlega = "Si" if (BoolLlega) else "No"
                    return resultTimpo,resultLlegaG,resultLlega
                else:
                    #TODO: VER AFTER LUNES
                    resultTimpo = utils.minsToMil(tiempos['tHogarJardin'] + tiempos['tJardinCentro'])
                    horaTerCons1 = utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo'])
                    horaTerCons2  = utils.minsToMil(jardin.hora_fin + tiempos['tJardinCentro'] + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo'])
                    horaViajeMasConsulta = max(horaTerCons1, horaTerCons2)
                    resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta <= trabajo.hora_inicio and utils.minsToMil(jardin.hora_fin + tiempos['tJardinCentro']) <= utils.minsToMil(hora + tiReLle)) else "No"
                    BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                    resultLlega = "Si" if (BoolLlega) else "No"
                    return resultTimpo,resultLlegaG,resultLlega
            else:
                resultTimpo = utils.minsToMil(tiempos['tHogarCentro'])
                horaViajeMasConsulta = utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo'])
                resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta <= trabajo.hora_inicio) else "No"
                BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                resultLlega = "Si" if (BoolLlega) else "No"
                return resultTimpo,resultLlegaG,resultLlega
        else:
            if(tieneJardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    resultTimpo = utils.minsToMil(tiempos['tTrabajoHogar'] + tiempos['tHogarCentro'])
                    horaTerCons1 = utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroJardin'])
                    horaTerCons2 = utils.minsToMil(trabajo.hora_fin + tiempos['tTrabajoHogar'] + tiempos['tHogarCentro'] + tiempoConsulta + tiempos['tCentroJardin'])
                    horaViajeMasConsulta = max(horaTerCons1, horaTerCons2) 
                    resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta<= jardin.hora_inicio and utils.minsToMil(trabajo.hora_fin + resultTimpo) <= utils.minsToMil(hora + tiReLle)) else "No"
                    BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                    resultLlega = "Si" if (BoolLlega) else "No"
                    return resultTimpo,resultLlegaG,resultLlega

                else:
                    resultTimpo = utils.minsToMil(tiempos['tTrabajoJardin'] + tiempos['tJardinCentro'])
                    horaLlegadaJardin = utils.minsToMil(trabajo.hora_fin + tiempos['tTrabajoJardin'])
                    horaSalidaJardin = jardin.hora_fin if (horaLlegadaJardin <= jardin.hora_fin) else horaLlegadaJardin
                    resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and  utils.minsToMil(horaSalidaJardin + tiempos['tJardinCentro']) <= utils.minsToMil(hora + tiReLle)) else "No"
                    BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                    resultLlega = "Si" if (BoolLlega) else "No"
                    return resultTimpo,resultLlegaG,resultLlega
            else:
                resultTimpo = utils.minsToMil(tiempos['tTrabajoHogar'] + tiempos['tHogarCentro'])
                resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and utils.minsToMil(trabajo.hora_fin + resultTimpo) <= utils.minsToMil(hora + tiReLle)) else "No"
                BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                resultLlega = "Si" if (BoolLlega) else "No"
                return resultTimpo,resultLlegaG,resultLlega
    else:
        if(jardin and dia in utils.getListOfDays(jardin.dias)):
            if(hora < jardin.hora_inicio):
                resultTimpo = utils.minsToMil(tiempos['tHogarCentro'])
                resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroJardin']) <= jardin.hora_inicio) else "No"
                BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                resultLlega = "Si" if (BoolLlega) else "No"
                return resultTimpo,resultLlegaG,resultLlega
            else:
                resultTimpo = utils.minsToMil(tiempos['tHogarJardin']+ tiempos['tJardinCentro'])
                resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and utils.minsToMil(jardin.hora_fin + tiempos['tJardinCentro']) <= utils.minsToMil(hora + tiReLle)) else "No"
                BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                resultLlega = "Si" if (BoolLlega) else "No"
                return resultTimpo,resultLlegaG,resultLlega
        else:
            resultTimpo = utils.minsToMil(tiempos['tHogarCentro'])
            resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo) else "No"
            BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
            resultLlega = "Si" if (BoolLlega) else "No"
            return resultTimpo,resultLlegaG,resultLlega
@shared_task
def saveTiemposToDB(lineas,tipo):
    print("AWDAWDAWDWADWA")
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
    id = 0
    tiempos = []
    init = time.time()
    bulkAmount = 10000
    for caso in lineas:
        caso = caso[0].split(sep)
        sector1 = caso[0]
        sector2 = caso[1]
        t = float(caso[2])
        dist = float(caso[3])
        if(tipo == 0):
            tiempo = SectorTiempoCaminando(id = id , sector_1_id = sector1, sector_2_id = sector2, tiempo = float(caso[2]), distancia = float(caso[3]))
        else:
            tiempo = SectorTiempoAuto(id = id , sector_1_id = sector1, sector_2_id = sector2, tiempo = float(caso[2]), distancia = float(caso[3]))
        tiempos.append(tiempo)
        id +=1
        if(id % bulkAmount == 0):
            progressDone  = Settings.objects.get(setting='currentMatriz'+tipoId)
            progressDone.value  = int(progressDone.value) + bulkAmount
            progressDone.save()
            print(id)
            print(time.time() - init)
            init = time.time()
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
    progressDone.value  = int(progressDone.value) + bulkAmount
    progressDone.save()
    status  = Settings.objects.get(setting='statusMatriz'+tipoId)
    status.value  = 1
    status.save()
    print("Se cargo correctamente el archivo")
