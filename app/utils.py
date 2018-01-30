from app.models import *
from shapely.geometry import Polygon, Point

def generateParamDict(getReq):
    res = dict()
    if(getReq.get('checkB',0) == '-1'):
        res['mutualista'] ='-1'
    else:
        res['mutualista'] = getReq.get('prestador','-1')
    if(getReq.get('checkM','0') == '-1'):
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
        return lugar.sector_auto
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

def getSectorForPoint(ancal,tipo,shapeAuto, shapeCaminando):
    if(tipo == "Auto" or tipo == 1 ):
        shapes = shapeAuto
        tipo = "Auto"
    else:
        tipo = "Caminando"
        shapes = shapeCaminando
    point = Point(ancal.x_coord,ancal.y_coord)
    for i in range(len(shapes)):
        polygon = Polygon(shapes[i].points)
        if(point.within(polygon)):
            return Sector.objects.get(shape = i,tipo_sector = tipo)#len(shapeAuto)+i)#, tipo_sector = tipo)
def calcularTiempoViaje(anclas,transporte):
    tiempoViaje = 0
    hora = 0
    if not (transporte == "bus" or transporte == 2 or transporte == 3):
        for i in range(0,len(anclas)-1):
            if(anclas[i] is None or anclas[i+1] is None):
                return -7000#-1/60
            if(transporte == 0):
                if(anclas[i].id <= anclas[i+1].id):
                    sector1 = anclas[i]
                    sector2 = anclas[i+1]
                else:
                    sector1 = anclas[i+1]
                    sector2 = anclas[i]
            else:
                sector1 = anclas[i]
                sector2 = anclas[i+1]
            tiempoViaje += (SectorTiempo.objects.get(sector_1 = sector1, sector_2 = sector2).tiempo)
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
