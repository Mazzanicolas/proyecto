import app.utils as utils
from app.models import *
from app.checkeo_errores import *
import app.utils
import csv
from django.http import HttpResponse, StreamingHttpResponse

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

def cargarCentroPediatras(request,shapeAuto, shapeCaminando):
    p = list(Prestador.objects.all()) # Traigo todos los prestadores
    dict_prestadores = {p[x].nombre:p[x].id for x in range(len(p))} # armo un diccionario que relaciona el nombre con la id
    res, lineas = checkCentroPediatras(request,dict_prestadores)
    if not res:
        return lineas
    Pediatra.objects.all().delete()
    Centro.objects.all().delete()
    horas = [str(float(x)) for x in range(6,22)] # ["6.0".."21.0"]
    for caso in lineas:
        ## Centro
        #Id, Coordenada X, Coordenada Y, SectorAuto, SectorCaminando, Prestador
        id_centro = int(caso[0])
        prestador = dict_prestadores.get(caso[1],1000)
        centro = Centro(id_centro,float(caso[3]),float(caso[4]),None,None,prestador)
        centro.sector_auto = utils.getSectorForPoint(centro,"Auto",shapeAuto, shapeCaminando)
        centro.sector_caminando = utils.getSectorForPoint(centro,"Caminando",shapeAuto, shapeCaminando)
        centro.save()
        ## Pediatra
        #Centro, Dia, Hora, Cantidad de pediatras
        contador_dias = 5
        pediatras = list()
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
                pediatras.append(Pediatra(centro_id = id_centro, dia = i, hora = parsear_hora(j), cantidad_pediatras = cantPediatras))
                contador_dias +=1
        Pediatra.objects.bulk_create(pediatras)
    print("Se cargo correctamente el archivo")

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

def cargarSectores(shapeAuto, shapeCaminando):
    for i in range(len(shapeAuto)):
        centroide = utils.centroid(shapeAuto[i])
        sector = Sector(i,centroide.x,centroide.y,"Auto",i)
        sector.save()
    for i in range(len(shapeCaminando)):
        centroide = utils.centroid(shapeCaminando[i])
        sector = Sector(i+len(shapeAuto),centroide.x,centroide.y,"Caminando",i)
        sector.save()

def cargarIndividuoAnclas(requestf,shapeAuto, shapeCaminando):
    prestadores = [x.id for x in Prestador.objects.all()]
    tipos_transporte = [x.nombre for x in TipoTransporte.objects.all()]
    dicc_transporte = {x.nombre:x for x in TipoTransporte.objects.all()}
    res, lineas = checkIndividuoAnclas(requestf,prestadores,tipos_transporte)
    if not res:
        return lineas
    Individuo.objects.all().delete()
    AnclaTemporal.objects.all().delete()
    idAncla = 0
    for caso in lineas:
        print("Individuo "+caso[0])
        ## Ancla
        #Coordenada X, Coordenada Y, Tipo, Hora inicio, Hora fin, Dias, Sector auto, Sector caminando
        #Duda Tecnica -Contemplar casos donde no hay jardin y/o trabajo
        if(caso[5] == "1"):
            anclaJardin  = AnclaTemporal(idAncla,float(caso[10]),float(caso[11]),"jardin" ,utils.parsear_hora(caso[7]) ,utils.parsear_hora(caso[8]) ,caso[6] ,None,None)
            anclaJardin.sector_auto = utils.getSectorForPoint(anclaJardin,"Auto",shapeAuto, shapeCaminando)
            anclaJardin.sector_caminando = utils.getSectorForPoint(anclaJardin,"Caminando",shapeAuto, shapeCaminando)
            anclaJardin.save()
            idAncla +=1
            tieneJardin = True
        else:
            tieneJardin = False
            anclaJardin = None
        if(caso[12] == "1"):
            anclaTrabajo = AnclaTemporal(idAncla,float(caso[14]),float(caso[15]),"trabajo",utils.parsear_hora(caso[17]),utils.parsear_hora(caso[18]),caso[16],None,None)
            anclaTrabajo.sector_auto = utils.getSectorForPoint(anclaTrabajo,"Auto",shapeAuto, shapeCaminando)
            anclaTrabajo.sector_caminando = utils.getSectorForPoint(anclaTrabajo,"Caminando",shapeAuto, shapeCaminando)
            anclaTrabajo.save()
            idAncla +=1
            tieneTrabajo = True
        else:
            tieneTrabajo = False
            anclaTrabajo = None
        anclaHogar   = AnclaTemporal(idAncla,float(caso[22]),float(caso[23]),"hogar",None,None,"L-D",None,None)
        anclaHogar.sector_auto = utils.getSectorForPoint(anclaHogar,"Auto",shapeAuto, shapeCaminando)
        anclaHogar.sector_caminando = utils.getSectorForPoint(anclaHogar,"Caminando",shapeAuto, shapeCaminando)
        anclaHogar.save()
        idAncla +=1
        ## Individuo
        #Id, Tipo transporte, Prestador, Hogar, Trabajo, Jardin
        individuo  = Individuo(id = int(caso[0]),tipo_transporte = dicc_transporte.get(caso[19]),prestador = Prestador.objects.get(id =int(caso[1])),
                    hogar = anclaHogar,trabajo = anclaTrabajo, jardin = anclaJardin, tieneJardin = tieneJardin,tieneTrabajo = tieneTrabajo)
        individuo.save()
    print("Se cargo correctamente el archivo")
    print("Generando matriz cartesiana Individuo-Centro-Dia-Hora")
    init()
    print("Matriz Carteasiana generada")

def cargarTiempos(tipo,request,shapeAuto, shapeCaminando):
    res, lineas = checkTiempos(tipo,request)
    if not res:
        return lineas
    if(tipo == 0):
        SectorTiempo.objects.filter(sector_1_id__id__lt = len(shapeAuto)).delete()
        id = 0
    else:
        SectorTiempo.objects.filter(sector_1_id__id__gte = len(shapeAuto)).delete()
        id = SectorTiempo.objects.latest('id').id + 1
    tiempos = []
    for caso in lineas:
        if(tipo == 0):
            sector1 = int(caso[0])
            sector2 = int(caso[1])
        else:
            sector1 = int(caso[0]) + len(shapeAuto)
            sector2 = int(caso[1]) + len(shapeAuto)
        t = float(caso[2])
        dist = float(caso[3])
        tiempo = SectorTiempo(id = id , sector_1_id = sector1, sector_2_id = sector2,tiempo = float(caso[2]), distancia = float(caso[3]))
        tiempos.append(tiempo)
        id +=1
        if(id % 10000 == 0):
            print(id)
            guardar = SectorTiempo.objects.bulk_create(tiempos)
            tiempos = []
    if(tiempos):
        guardar = SectorTiempo.objects.bulk_create(tiempos)
    print("Se cargo correctamente el archivo")

def cargarTiemposBus(request):
    res, lineas = checkTiemposBus(request)
    if not res:
        return lineas
    SectorTiempoOmnibus.objects.all().delete()
    id = 0
    tiempos = []
    for i in range(len(lineas)):
        for j in range(len(lineas[i])):
            if i == j:
                t = SectorTiempo.objects.get(sector_1 = i, sector_2 = j).tiempo
            else:
                #t = float(lineas[i][j])
                l = list(map(lambda x: float(x),lineas[i][j].split(';')))
                t = l[0]*TIEMPO_ESPERA + l[1]*TIEMPO_VIAJE + l[2]*TIEMPO_CAMBIO_PARADA
                if t < 0:
                    t = TIEMPO_ARBITRARIAMENTE_ALTO
            tiempo = SectorTiempoOmnibus(id = id, sectorO_1_id = i, sectorO_2_id = j, tiempo = t)
            tiempos.append(tiempo)
            id +=1
            if(id % 100000 == 0):
                guardar = SectorTiempoOmnibus.objects.bulk_create(tiempos)
                tiempos = []
    if(tiempos != list()):
        guardar = SectorTiempoOmnibus.objects.bulk_create(tiempos)
    print("Se cargo correctamente el archivo")

def init():
    if(IndividuoTiempoCentro.objects.count() == 0 and Centro.objects.count() > 0 and Individuo.objects.count() > 0):
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
