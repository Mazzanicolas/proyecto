from app.models import *
from shapely.geometry import Polygon, Point
import os
import glob
import shapefile
import redis
from datetime import datetime, timedelta

def numbersToDays(numberList):
    daysDict = {0:'Lunes',1:'Martes',2:'Miercoles',3:'Jueves',4:'Viernes',5:'Sabado',6:'Domingo'}
    return [daysDict[x] for x in numberList]
def cleanAllFolderFiles(path):
    files = glob.glob(path+'*')
    for aFile in files:
        os.remove(aFile)
def getPrestadoresNombres():
    puto = [(x.id,x.nombre) for x in Prestador.objects.all()]
    return puto
def getPrestaresNombresFiltrosSimular():
    return [(-1,"Por defecto"),(-2,"Ignorar")]+ [(x.id,x.nombre) for x in Prestador.objects.all()]
def createFolder(directory):
    #directory = './app/data/'+directory
    if not os.path.exists(directory):
        os.makedirs(directory)

def getOrCreateSettigs(id,value,isOnlyGet = False):
    currentSettingsQuery = Settings.objects.filter(setting=id)[:]
    if(currentSettingsQuery):
        setting = currentSettingsQuery[0]
        if(not isOnlyGet):
            setting.value = value
            setting.save()
        return setting
    currentSettings = Settings(setting=id,value=value)
    currentSettings.save()

def generateParamDict(getReq):
    res = dict()
    res['mutualista'] = getReq.get('prestadorFiltro','-1')
    if(getReq.get('checkT','0') == '-1'):
        res['tipoTransporte'] ='-1'
    else:
        res['tipoTransporte'] = getReq.get('tipoTransporte','-1')
    res['trabaja']= getReq.get('anclaTra','0')
    res['jardin']= getReq.get('anclaJar','0')
    return res
class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value
        
def newGetSector(lugar, transporte):
    if(lugar is None):
        return None
    if(transporte == 'AUTO' or transporte == 1):
        return lugar.sector_auto
    elif(transporte == 'CAMINANDO' or transporte == 0):
        return lugar.sector_caminando
    else:
        return lugar.sector_bus

def printCentroids(shapeAuto):
    for shape in shapeAuto:
        p = Polygon(shape.points)
        if(p.is_valid):
            return p.representative_point()
        else:
            return p.centroid

def centroid(shape):
    poligono = Polygon(shape.points)
    if poligono.is_valid:
        return poligono.representative_point()
    else:
        return poligono.centroid

def parsear_hora(hora):
    if(not '.' in hora):
        if(len(hora)>1):
            hora = '{:<04d}'.format(int(hora))
        else:
            hora = '{:<03d}'.format(int(hora))
        return int(hora)
    h,m = hora.split('.')
    if(len(h)>1):
        h = '{:<02d}'.format(int(h))
    m = '{:<02d}'.format(int(m))
    return int(h + m)

def getSectorForPoint(ancal,shapes,records,SectorClass):
    point = Point(ancal.x_coord,ancal.y_coord)
    for i in range(len(shapes)):
        polygon = Polygon(shapes[i].points)
        if(point.within(polygon)):
            return SectorClass.objects.get(shapeid =records[i][0])

def calcularTiempoViaje(anclas,transporte):
    tiempoViaje = 0
    hora = 0
    if not (transporte == "bus" or transporte == 2 or transporte == 3):
        for i in range(0,len(anclas)-1):
            if(anclas[i] is None or anclas[i+1] is None):
                return -7000#-1/60
            sector1 = anclas[i]
            sector2 = anclas[i+1]
            if(transporte == 0):
                aux = SectorTiempoCaminando.objects.filter(sector_1 = sector1, sector_2 = sector2)
                if(len(aux)>0):
                    tiempoViaje += aux[0].tiempo
                else:
                    tiempoViaje += SectorTiempoCaminando.objects.get(sector_1 = sector2, sector_2 = sector1).tiempo
                return tiempoViaje
            tiempoViaje += SectorTiempoAuto.objects.get(sector_1 = sector1, sector_2 = sector2).tiempo
            return tiempoViaje
    else:
        for i in range(len(anclas)-1):
            if(anclas[i] is None or anclas[i+1] is None):
                return -7000
            tiempoViaje += (SectorTiempoOmnibus.objects.get(sectorO_1 = anclas[i], sectorO_2 = anclas[i+1])).tiempo
            return tiempoViaje
def getPrestadores():
    try:
        pres = {str(x.id):x.nombre for x in Prestador.objects.all()}
        return pres
    except:
        return None

def getListOfDays(stringDays):
    daysList = {'L':0,'M':1,'Mi':2,'J':3,'V':4,'S':5,'D':6}
    daysByComma = stringDays.split('.')
    resDays = []
    for day in daysByComma:
        if('-' in day):
            frm, to = day.split('-')
            frm = daysList[frm]
            to = daysList[to]
            resDays = resDays + list(range(frm,to+1))
        else:
            resDays.append(daysList.get(day))
    return resDays
def setParams(self,cookies):
    if(not cookies.get('trabaja','1') == '1'):
        self.trabaja = False
    if(not cookies.get('jardin','1') == '1'):
        self.jardin = False
    self.tipoTrans = cookies.get('tipoTransporte','1')
    self.mutualista = cookies.get('mutualista','-1')
def getTiempos(individuo,centro,tipoTrans):
    tiempos = IndividuoCentro.objects.get(individuo = individuo,centro = centro)
    if(tipoTrans == '-1'):
        tipoTrans = individuo.tipo_transporte.id
    tiemposDict = dict()
    tipoTrans = int(tipoTrans)
    tiemposDict['tHogarCentro'] = getTHogarCentro(tipoTrans,tiempos)
    tiemposDict['tHogarTrabajo'] = getTHogarTrabajo(tipoTrans,tiempos)
    tiemposDict['tHogarJardin'] = getTHogarJardin(tipoTrans,tiempos)
    tiemposDict['tCentroHogar'] = getTCentroHogar(tipoTrans,tiempos)
    tiemposDict['tCentroJardin'] = getTCentroJardin(tipoTrans,tiempos)
    tiemposDict['tTrabajoJardin']= getTTrabajoJardin(tipoTrans,tiempos)
    tiemposDict['tTrabajoHogar']= getTTrabajoHogar(tipoTrans,tiempos)
    tiemposDict['tJardinTrabajo']= getTJardinTrabajo(tipoTrans,tiempos)
    tiemposDict['tJardinCentro']= getTJardinCentro(tipoTrans,tiempos)
    return tiemposDict
def getDeltaTiempos(individuo,centro,tipoTrans):
    tiempos = IndividuoCentro.objects.get(individuo = individuo,centro = centro)
    if(tipoTrans == '-1'):
        tipoTrans = individuo.tipo_transporte.id
    tiemposDict = dict()
    tipoTrans = int(tipoTrans)
    tiemposDict['tHogarCentro'  ] = timedelta(minutes = getTHogarCentro(tipoTrans,   tiempos))
    tiemposDict['tHogarTrabajo' ] = timedelta(minutes = getTHogarTrabajo(tipoTrans,  tiempos))
    tiemposDict['tHogarJardin'  ] = timedelta(minutes = getTHogarJardin(tipoTrans,   tiempos))
    tiemposDict['tCentroHogar'  ] = timedelta(minutes = getTCentroHogar(tipoTrans,   tiempos))
    tiemposDict['tCentroJardin' ] = timedelta(minutes = getTCentroJardin(tipoTrans,  tiempos))
    tiemposDict['tTrabajoJardin'] = timedelta(minutes = getTTrabajoJardin(tipoTrans, tiempos))
    tiemposDict['tTrabajoHogar' ] = timedelta(minutes = getTTrabajoHogar(tipoTrans,  tiempos))
    tiemposDict['tJardinHogar'  ] = timedelta(minutes = getTJardinHogar(tipoTrans,   tiempos))
    tiemposDict['tJardinTrabajo'] = timedelta(minutes = getTJardinTrabajo(tipoTrans, tiempos))
    tiemposDict['tJardinCentro' ] = timedelta(minutes = getTJardinCentro(tipoTrans,  tiempos))
    return tiemposDict
def getTHogarCentro(tipoTrans,tiempos):
    if(tipoTrans == 2):
        return tiempos.tHogarCentroBus
    elif (tipoTrans == 0):
        return tiempos.tHogarCentroCaminando
    else:
        return tiempos.tHogarCentroAuto

def getTHogarTrabajo(tipoTrans,tiempos):
    if(tipoTrans == 2):
        return tiempos.tHogarTrabajoBus
    elif (tipoTrans == 0):
        return tiempos.tHogarTrabajoCaminando
    else:
        return tiempos.tHogarTrabajoAuto

def getTHogarJardin(tipoTrans,tiempos):
    if(tipoTrans == 2):
        return tiempos.tHogarJardinBus
    elif (tipoTrans == 0):
        return tiempos.tHogarJardinCaminando
    else:
        return tiempos.tHogarJardinAuto

def getTCentroHogar(tipoTrans,tiempos):
    if(tipoTrans == 2):
        return tiempos.tCentroHogarBus
    elif (tipoTrans == 0):
        return tiempos.tCentroHogarCaminando
    else:
        return tiempos.tCentroHogarAuto

def getTCentroJardin(tipoTrans,tiempos):
    if(tipoTrans == 2):
        return tiempos.tCentroJardinBus
    elif (tipoTrans == 0):
        return tiempos.tCentroJardinCaminando
    else:
        return tiempos.tCentroJardinAuto

def getTTrabajoJardin(tipoTrans,tiempos):
    if(tipoTrans == 2):
        return tiempos.tTrabajoJardinBus
    elif (tipoTrans == 0):
        return tiempos.tTrabajoJardinCaminando
    else:
        return tiempos.tTrabajoJardinAuto

def getTTrabajoHogar(tipoTrans,tiempos):
    if(tipoTrans == 2):
        return tiempos.tTrabajoHogarBus
    elif (tipoTrans == 0):
        return tiempos.tTrabajoHogarCaminando
    else:
        return tiempos.tTrabajoHogarAuto

def getTJardinTrabajo(tipoTrans,tiempos):
    if(tipoTrans == 2):
        return tiempos.tJardinTrabajoBus
    elif (tipoTrans == 0):
        return tiempos.tJardinTrabajoCaminando
    else:
        return tiempos.tJardinTrabajoAuto

def getTJardinHogar(tipoTrans,tiempos):
    if(tipoTrans == 2):
        return tiempos.tJardinHogarBus
    elif (tipoTrans == 0):
        return tiempos.tJardinHogarCaminando
    else:
        return tiempos.tJardinHogarAuto

def getTJardinCentro(tipoTrans,tiempos):
    if(tipoTrans == 2):
        return tiempos.tJardinCentroBus
    elif (tipoTrans == 0):
        return tiempos.tJardinCentroCaminando
    else:
        return tiempos.tJardinCentroAuto
def getTotalFromDict(mapa):
    res = 0
    for value in mapa.values():
        res += value if type(value) == int else len(value)
    return res
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
    #        print("Individuos a calcular: "+str(len(indQuery)))
def genSettingsDict(GET,COOKIES):
    settingsDict = dict()
    settingsDict['tiempoMaximo'] = COOKIES.get('tiempoMaximo')
    settingsDict['tiempoConsulta'] = COOKIES.get('tiempoConsulta')
    settingsDict['tiempoLlega'] = COOKIES.get('tiempoLlega')
    if(GET.get('checkPrestador',None)):
        settingsDict['centroPrest'] = '-1'
    else:
        #printprint(GET.getlist("prestadorFiltro",[]))
        settingsDict['centroPrest'] = GET.getlist("prestadorFiltro",[])
    settingsDict['horaInicio'] = GET.get("horaInicio")
    settingsDict['horaFin'] = GET.get("horaFin")
    if(GET.get('checkDias',None)):
        settingsDict['dias'] = '0.1.2.3.4.5.6'
    else:
        settingsDict['dias'] = '.'.join(GET.getlist('dias'))
    return settingsDict

def getIndivList_ParamDict_SettingsDict(get,cookies):
    getData = get
    dictSettings = genSettingsDict(get,cookies)
    if(getData.get("idList",None)):
        idStringList = getData.get("idList",None).split(",")
        try:
            idList = [int(x) for x in idStringList]
            dictSettings['idList'] = idList
            indvList = Individuo.objects.filter(id__in = idList)
        except:
            dictSettings['idList'] = ['Todos']
            indvList = Individuo.objects.all()
    else:
        indvList = Individuo.objects.all()
    if(getData.get("simular",'0') == '1' ):
        dictParam = generateParamDict(get)
    else:
        if(getData.get('checkT')):
            transportList = TipoTransporte.objects.all().values_list('id', flat=True)            
            dictSettings['transportList'] = transportList
        else:
            transportList = [int(x) for x in getData.getlist('tipoTransporte', [])]
            dictSettings['transportList'] = transportList
        trabajaReq    = getData.get('trabaja', None)
        jardinReq     =  getData.get('asisteJardin', None)
        dictSettings['trabaja'] = trabajaReq
        dictSettings['jardin'] = jardinReq
        trabaja       = [True] if trabajaReq else [False]
        jardin        = [True] if jardinReq else [False]
        if(jardinReq == '0'):
            jardin.append(False)
        if(trabajaReq == '0'):
            trabaja.append(False)
        indQuery = indvList.filter(tipo_transporte__id__in = transportList, tieneTrabajo__in = trabaja,tieneJardin__in = jardin)
        dictParam = None
    return indvList,dictParam,dictSettings
def minsToMil(time):
    hours = time/60
    mins  = time%60
    return int(hours)*100+mins
def writeSettings(userId,dictSettings,simParams):
    baseDirectory = "./app/data/users/user"+userId+"/consultOut/"
    createFolder(baseDirectory)
    with open(baseDirectory + "Parametros.txt", "w") as text_file:
        if(simParams):
            text_file.write("Parametros de Simulacion \n")
            if(simParams['tipoTransporte'] == '-1'):
                text_file.write("Tipo de Transporte: Por Defecto \n")
            else:
                text_file.write("Tipo de Transporte: {} \n".format(TipoTransporte.objects.get(id = int(simParams['tipoTransporte'])).nombre))
            p = int(simParams['mutualista'])
            if(p == -1):
                text_file.write("Prestador a Simular: Por Defecto \n")
            elif(p == -2):
                text_file.write("Prestador a Simular: Ignorar \n")
            else:
                prestador = Prestador.objects.get(id = p)
                text_file.write("Prestador a Simular: {} \n".format(prestador))
            if(simParams.get('trabaja',0) == '1'):
                text_file.write("Se utiliza el ancla temporal Trabajo \n")
            else:
                text_file.write("No Se utiliza el ancla temporal Trabajo \n")
            if(simParams.get('jardin',0) == '1'):
                text_file.write("Se utiliza el ancla temporal Jardin \n")
            else:
                text_file.write("No Se utiliza el ancla temporal Jardin \n")
            text_file.write("Filtros utilizados \n")
        else:
            text_file.write("Filtros utilizados \n")
            transportList = [x.nombre for x in TipoTransporte.objects.filter(id__in = dictSettings['transportList'])]
            text_file.write("Tipo de Transporte utilizados: {}\n".format(", ".join(transportList)))
            if(dictSettings['trabaja']):
                text_file.write('Trabaja: Si\n')
            else:
                text_file.write('Trabaja: No\n')
            if(dictSettings['jardin']):
                text_file.write('Tiene Jardin: Si\n')
            else:
                text_file.write('Tiene Jardin: No\n')
            p = dictSettings['centroPrest']
            if(p == '-1'):
                text_file.write("Prestador: Por Defecto \n")
            else:
                prestadores = Prestador.objects.filter(id__in = [int(x) for x in p])
                prestadores = ', '.join([x.nombre for x in prestadores])
                text_file.write("Prestador: {} \n".format(prestadores))
        dias = numbersToDays([int(x) for x in dictSettings['dias'].split('.')])
        text_file.write("Dias: {} \n".format(', '.join(dias)))
        text_file.write("Desde Las: {} \n".format(dictSettings['horaInicio']))
        text_file.write("Hasta Las: {} \n".format(dictSettings['horaFin']))
       
        if(dictSettings.get('idList',None)):
            idList = [str(x) for x in dictSettings.get('idList',None)]
            text_file.write("Individuos: {} \n".format(', '.join(idList)))
        else:
          text_file.write("Individuos: Todos")
def getLock(key):
    return redis.Redis().lock(key)
def releaseLock(haveLock,lock):
    if(haveLock):
        lock.release()
def releaseAllLocks(locksTupleList):
    for tuple in locksTupleList:
        releaseLock(tuple[0],tuple[1])
def getSimpleLock(key):
    have_lock = False
    my_lock = redis.Redis().lock(key)
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            return True
        else:
            return False
    finally:    
        if have_lock:
            my_lock.release()

def horaMilToDateTime(hora):
    if hora is None:
        return hora
    if(hora == 2400):
        return datetime(2013,3,11,hour = 0,minute = 0)
    hora = str(hora)
    if(len(hora)==3):
        return datetime(2013,3,10,hour = int(hora[:1]),minute = int(hora[-2:]))
    elif(len(hora) == 4):
        return datetime(2013,3,10,hour = int(hora[:2]),minute = int(hora[-2:]))
    else:
        return datetime(2013,3,10, minute = int(hora))


def proTime(hora,minutes):
    return horaMilToDateTime(hora) + timedelta(minutes)

def vuelveHogar(salidaDelAncla,tAnclaHogar,tHogarCentro,tAnclaCentro,hora,tiReLle,tiempoMaximo):
    horaLlegadaDesdeHogar = salidaDelAncla + tAnclaHogar + timedelta(minutes = 30) + tHogarCentro
    if (horaLlegadaDesdeHogar <= hora + tiReLle):
        if(tHogarCentro <= tiempoMaximo):
            return "Si",tHogarCentro
        else:
            if(tAnclaCentro <= tiempoMaximo):
                return "Si", tAnclaCentro
            else:
                return "No", tHogarCentro
    else:
        if(tAnclaCentro < tiempoMaximo):
            return "Si",tAnclaCentro
        else:
            return "No",tAnclaCentro
def nothingLoading():
    stastusKeys = ["statusMatrizAuto",
                    "statusMatrizBus",
                    "statusMatrizCaminando",
                    "statusMatrizCentro",
                    "statusMatrizIndividuo",
                    "statusMatrizIndividuoCentro",
                    "statusMatrizIndividuoTiempoCentro",
                    "statusPrestador",
                    "shapeAutoStatus"
                    "shapeBusStatus",
                    "shapeCaminandoStatus"]
    acumulator = True
    for statusKey in stastusKeys:
        acumulator = acumulator and Settings.objects.get(statusKey).value in ['-1','0']
        if(not acumulator):
            return False
    return acumulator

def allLoaded():
    stastusKeys = ["statusMatrizAuto",
                    "statusMatrizBus",
                    "statusMatrizCaminando",
                    "statusMatrizCentro",
                    "statusMatrizIndividuo",
                    "statusMatrizIndividuoCentro",
                    "statusMatrizIndividuoTiempoCentro",
                    "statusPrestador",
                    "shapeAutoStatus"
                    "shapeBusStatus",
                    "shapeCaminandoStatus"]
    acumulator = True
    for statusKey in stastusKeys:
        acumulator = acumulator and Settings.objects.get(statusKey).value == '1'
        if(not acumulator):
            return False
    return acumulator