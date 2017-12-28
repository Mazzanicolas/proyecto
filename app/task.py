# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time
from app.models import Individuo, Settings,IndividuoCentro, TipoTransporte,Sector, Prestador, AnclaTemporal, SectorTiempo,Centro,Pediatra,IndividuoTiempoCentro,MedidasDeResumen

@shared_task
def suzuki(individuos):
    resultList = []
    individuos = Individuo.objects.filter(id = individuos)
    listCentros = Centro.objects.all()
    for individuo in individuos:
        print("Individuo: "+str(individuo.id))
        tiempoIni = time.time()
        #, centro__prestador__id = individuo.prestador.id)
        dictConsultasPorDia = {0:0,1:0,2:0,3:0,4:0,5:0}
        dictHorasPorDia = {0:set(),1:set(),2:set(),3:set(),4:set(),5:set()}
        dictCentrosPorDia = {0:set(),1:set(),2:set(),3:set(),4:set(),5:set()}
        centros = dict()
        tiempoInViaje = 0
        tiempoInCheck = 0
        count = 0
        for centro in listCentros:
            tiempos = IndividuoTiempoCentro.objects.filter(individuo = individuo, centro = centro)
            tiemposViaje = IndividuoCentro.objects.get(individuo = individuo,centro = centro)
            samePrest = individuo.prestador.id == centro.prestador.id
            centroId = centro.id_centro
            print("ddddddd")
            print(centro)
            for tiempo in tiempos:
                count += 1
                tiempoCero =time.time()
                tiempoViaje, llega = calcTiempoDeViaje(individuo,centroId,tiempo.dia,tiempo.hora,tiempo.cantidad_pediatras,tiemposViaje,samePrest)
                tiempoInCheck += time.time() - tiempoCero
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
        print("In calcTiempoDeViaje = "+str(tiempoInCheck))
        print("Mean of time in calcTiempoDeViaje = "+str(tiempoInCheck/count) + " En: "+str(count))
        totalHoras = getTotalFromDict(dictHorasPorDia)
        totalConsultas = getTotalFromDict(dictConsultasPorDia)
        totalCentros = len(centros)
        centroOptimo = getCentroOptimo(centros)
        leResumen = MedidasDeResumen(persona = individuo, cantidadTotalHoras = totalHoras,cantidadHorasLunes = len(dictHorasPorDia[0]),
                    cantidadHorasMartes = len(dictHorasPorDia[1]),cantidadHorasMiercoles = len(dictHorasPorDia[2]), cantidadHorasJueves = len(dictHorasPorDia[3]),
                    cantidadHorasViernes = len(dictHorasPorDia[4]),cantidadHorasSabado = len(dictHorasPorDia[5]), cantidadMaximaHoras = getMaximoDict(dictHorasPorDia),
                    cantidadConsultasLunes = dictConsultasPorDia[0], cantidadConsultasMartes = dictConsultasPorDia[1],cantidadConsultasMiercoles = dictConsultasPorDia[2],
                    cantidadConsultasJueves = dictConsultasPorDia[3], cantidadConsultasViernes = dictConsultasPorDia[4],cantidadConsultasSabado = dictConsultasPorDia[5],
                    cantidadTotalConsultas = totalConsultas, cantidadCentrosLunes = len(dictCentrosPorDia[0]), cantidadCentrosMartes = len(dictCentrosPorDia[1]),
                    cantidadCentrosMiercoles = len(dictCentrosPorDia[2]),cantidadCentrosJueves = len(dictCentrosPorDia[3]), cantidadCentrosViernes = len(dictCentrosPorDia[4]),
                    cantidadCentrosSabado = len(dictCentrosPorDia[5]), cantidadTotalCentros = totalCentros, centroOptimo = Centro.objects.get(id_centro = centroOptimo))
        resultList.append(leResumen)
        print("Tiempo en el individuo: "+str(time.time()-tiempoIni))
    return resultList
def calcTiempoDeViaje(individuo,centro,dia,hora,pediatras,tiempos, samePrest ):
    tiempoMaximo = int(Settings.objects.get(setting = "tiempoMaximo").value)  # Cambiar(Tomar de bd)
    tiempoConsulta = int(Settings.objects.get(setting = "tiempoConsulta").value) #Cambiar(Tomar de bd)
    tieneTrabajo = individuo.tieneTrabajo
    tieneJardin = individuo.tieneJardin
    hogar = individuo.hogar
    trabajo = individuo.trabajo
    jardin = individuo.jardin
    hasPed = pediatras>=0
    if(tieneTrabajo and hora in range(trabajo.hora_inicio,trabajo.hora_fin) or tieneJardin and hora in range(jardin.hora_inicio,jardin.hora_fin) or pediatras < 1 or not samePrest):
        return -1,"No"
    if(tieneTrabajo and dia in getListOfDays(trabajo.dias)):
        if(hora < trabajo.hora_inicio):
            if(tieneJardin and dia in getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    resultTimpo = tiempos.tHogarCentro
                    resultLlega = "Si" if (resultTimpo<=tiempoMaximo and tiempoConsulta + tiempos.tCentroJardin <= jardin.hora_inicio and tiempoConsulta + tiempos.tCentroJardin + tiempos.tJardinTrabajo<= trabajo.hora_inicio and hasPed ) else "No"
                    return resultTimpo,resultLlega
                else:
                    resultTimpo = tiempos.tHogarJardin + tiempos.tJardinCentro
                    horaViajeMasConsulta = hora + tiempoConsulta + tiempos.tCentroHogar + tiempos.tHogarTrabajo
                    resultLlega = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta <= trabajo.hora_inicio and jardin.hora_fin + tiempos.tJardinCentro <= hora and hasPed ) else "No"
                    return resultTimpo,resultLlega
            else:
                resultTimpo = tiempos.tHogarCentro
                horaViajeMasConsulta = hora + tiempoConsulta + tiempos.tCentroHogar + tiempos.tHogarTrabajo
                resultLlega = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta <= trabajo.hora_inicio and hasPed ) else "No"
                return resultTimpo,resultLlega
        else:
            if(tieneJardin and dia in getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    resultTimpo = tiempos.tTrabajoHogar + tiempos.tHogarCentro
                    horaViajeMasConsulta = hora + tiempoConsulta + tiempos.tCentroJardin
                    resultLlega = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta<= jardin.hora_inicio and trabajo.hora_fin + resultTimpo <= hora and hasPed ) else "No"
                    return resultTimpo,resultLlega

                else:
                    resultTimpo = tiempos.tTrabajoJardin + tiempos.tJardinCentro
                    horaLlegadaJardin = trabajo.hora_fin + tiempos.tTrabajoJardin
                    horaSalidaJardin = jardin.hora_fin if (horaLlegadaJardin <= jardin.hora_fin) else horaLlegadaJardin
                    resultLlega = "Si" if (resultTimpo<=tiempoMaximo and  horaSalidaJardin + tiempos.tJardinCentro <= hora and hasPed  ) else "No"
                    return resultTimpo,resultLlega
            else:
                resultTimpo = tiempos.tTrabajoHogar + tiempos.tHogarCentro
                resultLlega = "Si" if (resultTimpo<=tiempoMaximo and trabajo.hora_fin + resultTimpo <= hora and hasPed ) else "No"
                return resultTimpo,resultLlega
    else:
        if(jardin and dia in getListOfDays(jardin.dias)):
            if(hora < jardin.hora_inicio):
                resultTimpo = tiempos.tHogarCentro
                resultLlega = "Si" if (resultTimpo<=tiempoMaximo and hora + tiempoConsulta + tiempos.tCentroJardin <= jardin.hora_inicio and hasPed ) else "No"
                return resultTimpo,resultLlega
            else:
                resultTimpo = tiempos.tHogarJardin + tiempos.tJardinCentro
                resultLlega = "Si" if (resultTimpo<=tiempoMaximo and jardin.hora_fin + tiempos.tJardinCentro <= hora and hasPed ) else "No"
                return resultTimpo,resultLlega
        else:
            resultTimpo = tiempos.tHogarCentro
            resultLlega = "Si" if (resultTimpo<=tiempoMaximo and hasPed ) else "No"
            return resultTimpo,resultLlega
def getCentroOptimo(centros):
    centroOptimo = None
    for key, value in centros.items():
        if(centroOptimo and value < centros[centroOptimo]):
            centroOptimo = key
        else:
            centroOptimo = key
    return centroOptimo
def getMaximoDict(mapa):
    maximo = 0
    for value in mapa.values():
        aux = value if type(value) == int else len(value)
        if( aux > maximo):
            maximo = aux
    return maximo
def getTotalFromDict(mapa):
    res = 0
    for value in mapa.values():
        res += value if type(value) == int else len(value)
    return res
def getListOfDays(stringDays):
    daysList = {'L':0,'M':1,'Mi':2,'J':3,'V':4,'S':5}
    daysByComma = stringDays.split(';')
    resDays = []
    for day in daysByComma:
        if('-' in day):
            frm, to = day.split('-')
            frm = daysList[frm]
            to = daysList[to]
            resDays = resDays + list(range(frm,to+1))
        else:
            resDays.append(day)
    return resDays
