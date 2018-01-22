# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time
from app.models import Individuo, Settings,IndividuoCentro, TipoTransporte,Sector, Prestador, AnclaTemporal, SectorTiempo,Centro,Pediatra,IndividuoTiempoCentro,MedidasDeResumen
import app.utils as utils


@shared_task
def calculateIndividual(individuos,simParam):
    #individuos = Individuo.objects.filter(id__in = individuos)
    listCentros = Centro.objects.all()
    result = []
    daysList = {0:'Lunes',1:'Martes',2:'Miercoles',3:'Jueves',4:'Viernes',5:'Sabado'}
    for individuo in individuos:
        print("Individuo: "+str(individuo.id))
        tiempoIni = time.time()
        if(simParam):
            tipoTrans = TipoTransporte.objects.get(id = int(simParam.get('tipoTransporte',1))) if(simParam.get('tipoTransporte',1) != '-1') else individuo.tipo_transporte
            tieneTrabajo = individuo.tieneTrabajo and (simParam.get('trabaja',0) == '1')
            tieneJardin =  individuo.tieneJardin and (simParam.get('jardin',0) == '1')
            prestador = int(simParam.get('mutualista','-1'))
            if(prestador != -2):
                prestador = Prestador.objects.get(id=prestador) if(prestador!= -1) else individuo.prestador.id
        else:
            tipoTrans = individuo.tipo_transporte
            tieneTrabajo = individuo.tieneTrabajo
            tieneJardin = individuo.tieneJardin
            prestador = individuo.prestador.id
        for centro in listCentros:
            tiempos = IndividuoTiempoCentro.objects.filter(individuo = individuo, centro = centro)
            tiemposViaje = utils.getTiempos(individuo = individuo,centro = centro,tipoTrans = tipoTrans.id)
            if(prestador == -2):
                prestador = centro.prestador.id
            samePrest = prestador == centro.prestador.id
            #individuo.prestador = prestador
            #individuo.tipoTransporte = tipoTrans
            centroId = centro.id_centro
            aux =[]
            for tiempo in tiempos:
                tiempoViaje, llegaG,llega = calcTiempoAndLlega(individuo = individuo,centro = centroId,dia = tiempo.dia,hora = tiempo.hora, pediatras = tiempo.cantidad_pediatras,tiempos = tiemposViaje,samePrest = samePrest, tieneTrabajo = tieneTrabajo, tieneJardin = tieneJardin)
                result.append([individuo.id,prestador,centroId,centro.prestador.id,tipoTrans.nombre,daysList[tiempo.dia],tiempo.hora,tiempoViaje,llegaG,tiempo.cantidad_pediatras,llega])
        print("Tiempo en el individuo: "+str(time.time()-tiempoIni))
    return result
@shared_task
def suzuki(individuos,simParam):
    resultList = []
    individuos = Individuo.objects.filter(id__in = individuos)
    listCentros = Centro.objects.all()
    for individuo in individuos:
        print("Individuo: "+str(individuo.id))
        tiempoIni = time.time()
        if(simParam):
            tipoTrans = simParam.get('tipoTrans',1) if(simParam.get('tipoTrans',1) != -1) else individuo.tipo_transporte.id
            tieneTrabajo = individuo.tieneTrabajo and (simParam.get('trabaja',1) == 1)
            tieneJardin =  individuo.tieneJardin and (simParam.get('jardin',1) == 1)
            prestadorId = simParam.get('mutualista',1) if(simParam.get('mutualista',1) != -1) else individuo.prestador.id
        else:
            tipoTrans = individuo.tipo_transporte.id
            tieneTrabajo = individuo.tieneTrabajo
            tieneJardin = individuo.tieneJardin
            prestadorId = individuo.prestador.id
        #, centro__prestador__id = individuo.prestador.id)
        dictConsultasPorDia = {0:0,1:0,2:0,3:0,4:0,5:0}
        dictHorasPorDia = {0:set(),1:set(),2:set(),3:set(),4:set(),5:set()}
        dictCentrosPorDia = {0:set(),1:set(),2:set(),3:set(),4:set(),5:set()}
        centros = dict()
        for centro in listCentros:
            tiempos = IndividuoTiempoCentro.objects.filter(individuo = individuo, centro = centro)
            tiemposViaje = utils.getTiempos(individuo = individuo,centro = centro,tipoTrans = tipoTrans)
            samePrest = prestadorId == centro.prestador.id if (prestadorId != -2) else True
            centroId = centro.id_centro
            for tiempo in tiempos:
                tiempoViaje, llega = calcTiempoDeViaje(individuo = individuo,centro = centroId,dia = tiempo.dia,hora = tiempo.hora, pediatras = tiempo.cantidad_pediatras,tiempos = tiemposViaje,samePrest = samePrest, tieneTrabajo = tieneTrabajo, tieneJardin = tieneJardin)
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
        centroOptimo = Centro.objects.get(id_centro = centroOptimo) if(centroOptimo) else centroOptimo
        leResumen = MedidasDeResumen(persona = individuo, cantidadTotalHoras = totalHoras,cantidadHorasLunes = len(dictHorasPorDia[0]),
                    cantidadHorasMartes = len(dictHorasPorDia[1]),cantidadHorasMiercoles = len(dictHorasPorDia[2]), cantidadHorasJueves = len(dictHorasPorDia[3]),
                    cantidadHorasViernes = len(dictHorasPorDia[4]),cantidadHorasSabado = len(dictHorasPorDia[5]), cantidadMaximaHoras = utils.getMaximoDict(dictHorasPorDia),
                    cantidadConsultasLunes = dictConsultasPorDia[0], cantidadConsultasMartes = dictConsultasPorDia[1],cantidadConsultasMiercoles = dictConsultasPorDia[2],
                    cantidadConsultasJueves = dictConsultasPorDia[3], cantidadConsultasViernes = dictConsultasPorDia[4],cantidadConsultasSabado = dictConsultasPorDia[5],
                    cantidadTotalConsultas = totalConsultas, cantidadCentrosLunes = len(dictCentrosPorDia[0]), cantidadCentrosMartes = len(dictCentrosPorDia[1]),
                    cantidadCentrosMiercoles = len(dictCentrosPorDia[2]),cantidadCentrosJueves = len(dictCentrosPorDia[3]), cantidadCentrosViernes = len(dictCentrosPorDia[4]),
                    cantidadCentrosSabado = len(dictCentrosPorDia[5]), cantidadTotalCentros = totalCentros, centroOptimo = centroOptimo)
        resultList.append(leResumen)
        print("Tiempo en el individuo: "+str(time.time()-tiempoIni))
    return resultList
def calcTiempoDeViaje(individuo,centro,dia,hora,pediatras,tiempos, samePrest,tieneTrabajo,tieneJardin):
    tiempoMaximo = int(Settings.objects.get(setting = "tiempoMaximo").value)  # Cambiar(Tomar de bd)
    tiempoConsulta = int(Settings.objects.get(setting = "tiempoConsulta").value) #Cambiar(Tomar de bd)
    hogar = individuo.hogar
    trabajo = individuo.trabajo
    jardin = individuo.jardin
    hasPed = pediatras>=0
    if(tieneTrabajo and hora in range(trabajo.hora_inicio,trabajo.hora_fin) or tieneJardin and hora in range(jardin.hora_inicio,jardin.hora_fin) or pediatras < 1 or not samePrest):
        return -1,"No"
    if(tieneTrabajo and dia in utils.getListOfDays(trabajo.dias)):
        if(hora < trabajo.hora_inicio):
            if(tieneJardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    resultTimpo = tiempos['tHogarCentro']
                    resultLlega = "Si" if (resultTimpo<=tiempoMaximo and tiempoConsulta + tiempos['tCentroJardin'] <= jardin.hora_inicio and tiempoConsulta + tiempos['tCentroJardin'] + tiempos['tJardinTrabajo']<= trabajo.hora_inicio and hasPed ) else "No"
                    return resultTimpo,resultLlega
                else:
                    resultTimpo = tiempos['tHogarJardin'] + tiempos['tJardinCentro']
                    horaViajeMasConsulta = hora + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo']
                    resultLlega = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta <= trabajo.hora_inicio and jardin.hora_fin + tiempos['tJardinCentro'] <= hora and hasPed ) else "No"
                    return resultTimpo,resultLlega
            else:
                resultTimpo = tiempos['tHogarCentro']
                horaViajeMasConsulta = hora + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo']
                resultLlega = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta <= trabajo.hora_inicio and hasPed ) else "No"
                return resultTimpo,resultLlega
        else:
            if(tieneJardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    resultTimpo = tiempos['tTrabajoHogar'] + tiempos['tHogarCentro']
                    horaViajeMasConsulta = hora + tiempoConsulta + tiempos['tCentroJardin']
                    resultLlega = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta<= jardin.hora_inicio and trabajo.hora_fin + resultTimpo <= hora and hasPed ) else "No"
                    return resultTimpo,resultLlega

                else:
                    resultTimpo = tiempos['tTrabajoJardin'] + tiempos['tJardinCentro']
                    horaLlegadaJardin = trabajo.hora_fin + tiempos['tTrabajoJardin']
                    horaSalidaJardin = jardin.hora_fin if (horaLlegadaJardin <= jardin.hora_fin) else horaLlegadaJardin
                    resultLlega = "Si" if (resultTimpo<=tiempoMaximo and  horaSalidaJardin + tiempos['tJardinCentro'] <= hora and hasPed  ) else "No"
                    return resultTimpo,resultLlega
            else:
                resultTimpo = tiempos['tTrabajoHogar'] + tiempos['tHogarCentro']
                resultLlega = "Si" if (resultTimpo<=tiempoMaximo and trabajo.hora_fin + resultTimpo <= hora and hasPed ) else "No"
                return resultTimpo,resultLlega
    else:
        if(jardin and dia in utils.getListOfDays(jardin.dias)):
            if(hora < jardin.hora_inicio):
                resultTimpo = tiempos['tHogarCentro']
                resultLlega = "Si" if (resultTimpo<=tiempoMaximo and hora + tiempoConsulta + tiempos['tCentroJardin'] <= jardin.hora_inicio and hasPed ) else "No"
                return resultTimpo,resultLlega
            else:
                resultTimpo = tiempos['tHogarJardin']+ tiempos['tJardinCentro']
                resultLlega = "Si" if (resultTimpo<=tiempoMaximo and jardin.hora_fin + tiempos['tJardinCentro'] <= hora and hasPed ) else "No"
                return resultTimpo,resultLlega
        else:
            resultTimpo = tiempos['tHogarCentro']
            resultLlega = "Si" if (resultTimpo<=tiempoMaximo and hasPed ) else "No"
            return resultTimpo,resultLlega
def calcTiempoAndLlega(individuo,centro,dia,hora,pediatras,tiempos, samePrest,tieneTrabajo,tieneJardin):
    tiempoMaximo = int(Settings.objects.get(setting = "tiempoMaximo").value)  # Cambiar(Tomar de bd)
    tiempoConsulta = int(Settings.objects.get(setting = "tiempoConsulta").value) #Cambiar(Tomar de bd)
    hogar = individuo.hogar
    trabajo = individuo.trabajo
    jardin = individuo.jardin
    hasPed = pediatras>=0
    if(tieneTrabajo and hora in range(trabajo.hora_inicio,trabajo.hora_fin) or tieneJardin and hora in range(jardin.hora_inicio,jardin.hora_fin)):
        return -1,"No","No"
    if(tieneTrabajo and dia in utils.getListOfDays(trabajo.dias)):
        if(hora < trabajo.hora_inicio):
            if(tieneJardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    resultTimpo = tiempos['tHogarCentro']
                    resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and tiempoConsulta + tiempos['tCentroJardin'] <= jardin.hora_inicio and tiempoConsulta + tiempos['tCentroJardin'] + tiempos['tJardinTrabajo']<= trabajo.hora_inicio) else "No"
                    BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                    resultLlega = "Si" if (BoolLlega) else "No"
                    return resultTimpo,resultLlegaG,resultLlega
                else:
                    resultTimpo = tiempos['tHogarJardin'] + tiempos['tJardinCentro']
                    horaViajeMasConsulta = hora + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo']
                    resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta <= trabajo.hora_inicio and jardin.hora_fin + tiempos['tJardinCentro'] <= hora) else "No"
                    BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                    resultLlega = "Si" if (BoolLlega) else "No"
                    return resultTimpo,resultLlegaG,resultLlega
            else:
                resultTimpo = tiempos['tHogarCentro']
                horaViajeMasConsulta = hora + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo']
                resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta <= trabajo.hora_inicio) else "No"
                BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                resultLlega = "Si" if (BoolLlega) else "No"
                return resultTimpo,resultLlegaG,resultLlega
        else:
            if(tieneJardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    resultTimpo = tiempos['tTrabajoHogar'] + tiempos['tHogarCentro']
                    horaViajeMasConsulta = hora + tiempoConsulta + tiempos['tCentroJardin']
                    resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and horaViajeMasConsulta<= jardin.hora_inicio and trabajo.hora_fin + resultTimpo <= hora) else "No"
                    BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                    resultLlega = "Si" if (BoolLlega) else "No"
                    return resultTimpo,resultLlegaG,resultLlega

                else:
                    resultTimpo = tiempos['tTrabajoJardin'] + tiempos['tJardinCentro']
                    horaLlegadaJardin = trabajo.hora_fin + tiempos['tTrabajoJardin']
                    horaSalidaJardin = jardin.hora_fin if (horaLlegadaJardin <= jardin.hora_fin) else horaLlegadaJardin
                    resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and  horaSalidaJardin + tiempos['tJardinCentro'] <= hora) else "No"
                    BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                    resultLlega = "Si" if (BoolLlega) else "No"
                    return resultTimpo,resultLlegaG,resultLlega
            else:
                resultTimpo = tiempos['tTrabajoHogar'] + tiempos['tHogarCentro']
                resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and trabajo.hora_fin + resultTimpo <= hora) else "No"
                BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                resultLlega = "Si" if (BoolLlega) else "No"
                return resultTimpo,resultLlegaG,resultLlega
    else:
        if(jardin and dia in utils.getListOfDays(jardin.dias)):
            if(hora < jardin.hora_inicio):
                resultTimpo = tiempos['tHogarCentro']
                resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and hora + tiempoConsulta + tiempos['tCentroJardin'] <= jardin.hora_inicio) else "No"
                BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                resultLlega = "Si" if (BoolLlega) else "No"
                return resultTimpo,resultLlegaG,resultLlega
            else:
                resultTimpo = tiempos['tHogarJardin']+ tiempos['tJardinCentro']
                resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo and jardin.hora_fin + tiempos['tJardinCentro'] <= hora) else "No"
                BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
                resultLlega = "Si" if (BoolLlega) else "No"
                return resultTimpo,resultLlegaG,resultLlega
        else:
            resultTimpo = tiempos['tHogarCentro']
            resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo) else "No"
            BoolLlega = resultLlegaG == "Si" and samePrest and hasPed
            resultLlega = "Si" if (BoolLlega) else "No"
            return resultTimpo,resultLlegaG,resultLlega
