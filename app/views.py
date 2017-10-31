from django.http import HttpResponse
from django.shortcuts import render
from app.models import Individuo, Settings, TipoTransporte,Sector, Prestador, AnclaTemporal, SectorTiempo,Centro,Pediatra,IndividuoTiempoCentro,MedidasDeResumen
from app.filters import IndividuoTiempoCentroFilter
from app.tables import PersonTable,ResumenTable
from django_tables2 import RequestConfig
from shapely.geometry import Polygon, Point
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from app.forms import FooFilterFormHelper
import shapefile
from io import StringIO
from app.bus.omnibus import get_horarios, load, busqueda
import csv
global shapeAuto
global shapeCaminando
global horarios
global nodos
horarios = get_horarios('app/bus/horarios.csv')
nodos = load('app/bus/nodos.csv')
sf = shapefile.Reader('app/files/shapeAuto.shp')
shapeAuto = sf.shapes()
sf = shapefile.Reader('app/files/shapeCaminando.shp')
shapeCaminando = sf.shapes()

class FilteredPersonListView(SingleTableMixin, FilterView):
    table_class = PersonTable
    model = IndividuoTiempoCentro
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filterset_class = IndividuoTiempoCentroFilter
def index(request):
    if(not Sector.objects.all()):
        cargarSectores()
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
                cargarMutualistas(request)
            elif(radioCargado == "option2"):
                cargarIndividuoAnclas(request)
            elif(radioMatrix == "option3"):
                cargarTiempos(0,request)
            elif(radioMatrix == "option4"):
                cargarTiempos(1,request)
            elif(radioMatrix == "option5"):
                cargarCentroPediatras(request)
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
def res(request):
    print("*********")
    isJardin = request.POST.get("anclaJar")
    isTrabajo = request.POST.get("anclaTra")
    if request.POST.get("checkB") == 'default':
        pr = request.POST.get("checkB")
    else:
        pr = request.POST.get("mutualistasRadio")
    tiempoMaximo = int(Settings.objects.get(setting = "tiempoMaximo").value)  # Cambiar(Tomar de bd)
    tiempoConsulta = int(Settings.objects.get(setting = "tiempoConsulta").value) #Cambiar(Tomar de bd)
    transporte = request.POST.get("checkM") if request.POST.get("checkM") else request.POST.get("transporteRadio")
    individuos = Individuo.objects.all()
    prestadores = Prestador.objects.all()
    IndividuoTiempoCentro.objects.all().delete()
    for individuo in individuos:
        prest = getPrestador(request,prestadores,individuo,pr)
        transporte = getTransporte(request,individuo) if transporte == "default" else transporte
        trabajo = individuo.trabajo
        jardin = individuo.jardin
        secHogar = getSector(individuo.hogar,transporte)
        secTrabajo = getSector(trabajo,transporte)
        secJardin = getSector(jardin,transporte)
        for prestador in prest:
            centros = Centro.objects.filter(prestador = prestador)
            for centro in centros:
                secCentro = getSector(centro,transporte)
                horas = Pediatra.objects.filter(centro__id_centro = centro.id_centro)
                for hora in horas:
                    if(trabajo and isTrabajo):
                        if(hora.hora < trabajo.hora_inicio):
                            if(isJardin and jardin):
                                tiempoViaje = calcularTiempos([secCentro, secJardin, secTrabajo],transporte,hora.hora)
                            else:
                                tiempoViaje = calcularTiempos([secCentro,secHogar, secTrabajo],transporte,hora.hora)
                            horaFinConsulta = hora.hora + tiempoConsulta/60
                            if(trabajo.hora_inicio >= tiempoViaje + horaFinConsulta and tiempoViaje < tiempoMaximo/60 and hora.cantidad_pediatras >0):
                                llega = "Si"
                            else:
                                llega = "No"
                            q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia =hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje*60, cantidad_pediatras=hora.cantidad_pediatras, llega =  llega)
                            q.save()
                        else:
                            if(jardin and isJardin):
                                tiempoViaje = calcularTiempos([secTrabajo, secJardin, secCentro],transporte,hora.hora)
                            else:
                                tiempoViaje = calcularTiempos([secTrabajo, secHogar, secCentro],transporte,hora.hora)
                            if(hora.hora >=  trabajo.hora_fin + tiempoViaje and tiempoViaje < tiempoMaximo/60 and hora.cantidad_pediatras>0):
                                llega = "Si"
                            else:
                                llega = "No"
                            q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia = hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje*60, cantidad_pediatras=hora.cantidad_pediatras,llega =  llega)
                            q.save()
                    else:
                        if(isJardin and jardin):
                            if(centro.hora < hora_inicio):
                                tiempoViaje = calcularTiempos([secCentro, secJardin],transporte,hora.hora)
                                horaFinConsulta = hora.hora + tiempoConsulta/60
                                if(jardin.hora_inicio >= horaFinConsulta + tiempoViaje and tiempoViaje < tiempoMaximo/60 and hora.cantidad_pediatras>0):
                                    llega = "Si"
                                else:
                                    llega = "No"
                                q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia = hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje*60, cantidad_pediatras=hora.cantidad_pediatras,llega =  llega)
                                q.save()
                            else:
                                tiempoViaje = calcularTiempos([secJardin, secCentro],transporte,hora.hora)
                                if(hora.hora >=  jardin.hora_fin + tiempoViaje and tiempoViaje < tiempoMaximo/60):
                                    llega = "Si"
                                else:
                                    llega = "No"
                                q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia = hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje*60, cantidad_pediatras=hora.cantidad_pediatras,llega =  llega)
                                q.save()
                        else:
                            tiempoViaje = calcularTiempos([secHogar, secCentro],transporte,hora.hora)
                            if(tiempoViaje < tiempoMaximo/60):
                                llega = "Si"
                            else:
                                llega = "No"
                            q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia = hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje*60, cantidad_pediatras=hora.cantidad_pediatras,llega =  llega)
                            q.save()
    dias = ["Lunes","Martes","Miercoles", "Jueves","Viernes","Sabado","Domingo"]
    table = PersonTable(IndividuoTiempoCentro.objects.all())
    RequestConfig(request, paginate={'per_page': 100000000000000000}).configure(table)
    context = {'result': table, 'dias':dias}
    return render(request, 'app/calcAll2.html', context)
    #return render(request, 'app/res.html')
def cargarMutualistas(archivo):
        Prestador.objects.all().delete()
        p = Prestador(11,"MEDICA URUGUAYA")
        p.save()
        p = Prestador(2,"ASOCIACION ESPANOLA")
        p.save()
        t =TipoTransporte(1,"Auto")
        t.save()
        t = TipoTransporte(0,"Caminando")
        t.save()
        t = TipoTransporte(2,"bus")
        t.save()
        t = TipoTransporte(3,"bus")
        t.save()
        p = Prestador(1,"ASSE")
        p.save()
        p = Prestador(3,"CASA DE GALICIA")
        p.save()
        p = Prestador(4,"CASMU")
        p.save()
        p = Prestador(5,"CIRCULO CATOLICO")
        p.save()
        p = Prestador(6,"COSEM")
        p.save()
        p = Prestador(7,"CUDAM")
        p.save()
        p = Prestador(8,"GREMCA")
        p.save()
        p = Prestador(9,"HOSPITAL BRITANICO")
        p.save()
        p = Prestador(10,"HOSPITAL EVANGELICO")
        p.save()
        p = Prestador(12,"MP")
        p.save()
        p = Prestador(13,"SMI")
        p.save()
        p = Prestador(14,"UNIVERSAL")
        p.save()
        p = Prestador(15,"NOEXISTE")
        p.save()

def getPrestador(request,prestadores,individuo,pr):
    if (pr == 'default'):
        prest = [individuo.prestador]
    elif (pr == 'ignorar'):
        prest = prestadores
    else:
        prest = prestadores.filter(nombre = pr)
    return prest
def getTransporte(request,individuo):
    if(request.POST.get("checkM") == "default"):
        transporte = individuo.tipo_transporte.id
    else:
        transporte = request.POST.get("transporteRadio")
    return transporte
def calcularTiempos(anclas,transporte,hora):
    tiempoViaje = 0
    if(not (transporte == "bus" or transporte == 2 or transporte == 3)):
        for i in range(0,len(anclas)-1):
            tiempoViaje += (SectorTiempo.objects.get(sector_1 = anclas[i], sector_2 = anclas[i+1])).tiempo/60
    else:
        for i in range(0,len(anclas)-1):
            coords_origen = (anclas[i].x_coord,anclas[i].y_coord)
            coords_destino = (anclas[i+1].x_coord,anclas[i+1].y_coord)
            #print("*******************Coords origen: "+str(coords_origen)+" Coords destino: "+str(coords_destino))
            tiempoViaje += busqueda(coords_origen,coords_destino,nodos,horarios,hora)
    return tiempoViaje/60
def getSector(lugar, transporte):
    #print(transporte):
    if(transporte == 'Auto' or transporte == 1):
        return lugar.sector_auto
    elif(transporte == 'Caminando' or transporte == 0):
        return lugar.sector_caminando
    else:
        return lugar
def guardarArchivo(nombre, archivo):
    with default_storage.open('tmp/'+nombre, 'wb+') as destination:
        for chunk in archivo.chunks():
            destination.write(chunk)
        csv = os.path.join(settings.MEDIA_ROOT, destination)
        return csv


def cargarSectores():
    for i in range(len(shapeAuto)):
        centroide = centroid(shapeAuto[i])
        sector = Sector(i,centroide.x,centroide.y,"Auto",i)
        sector.save()
    for i in range(len(shapeCaminando)):
        centroide = centroid(shapeCaminando[i])
        sector = Sector(i+len(shapeAuto),centroide.x,centroide.y,"Caminando",i)
        sector.save()
def centroid(shape):
    poligono = Polygon(shape.points)
    if poligono.is_valid:
        return poligono.representative_point()
    else:
        return poligono.centroid
def parsear_hora(hora):
    if(not "." in hora):
        str(float(hora))
    h,m = hora.split('.')
    return int(h.zfill(2) + m.zfill(2))

def cargarIndividuoAnclas(requestf):
    Individuo.objects.all().delete()
    csvfile = requestf.FILES['inputFile']
    csvf = StringIO(csvfile.read().decode())
    l = csv.reader(csvf, delimiter=',', quotechar='"')
    lineas=[]
    lineas.extend(l)
    lineas = lineas[1:]
    idAncla = 0
    for caso in lineas:
        ## Ancla
        #Coordenada X, Coordenada Y, Tipo, Hora inicio, Hora fin, Dias, Sector auto, Sector caminando
        #Duda Tecnica -Contemplar casos donde no hay jardin y/o trabajo
        anclaJardin  = AnclaTemporal(idAncla,float(caso[10]),float(caso[11]),"jardin" ,parsear_hora(caso[7]) ,parsear_hora(caso[8]) ,caso[6] ,None,None)
        anclaJardin.sector_auto = getSectorForPoint(anclaJardin,"Auto")
        anclaJardin.sector_caminando = getSectorForPoint(anclaJardin,"Caminando")
        anclaJardin.save()
        idAncla +=1
        anclaTrabajo = AnclaTemporal(idAncla,float(caso[14]),float(caso[15]),"trabajo",parsear_hora(caso[17]),parsear_hora(caso[18]),caso[16],None,None)
        anclaTrabajo.sector_auto = getSectorForPoint(anclaTrabajo,"Auto")
        anclaTrabajo.sector_caminando = getSectorForPoint(anclaTrabajo,"Caminando")
        anclaTrabajo.save()
        idAncla +=1
        anclaHogar   = AnclaTemporal(idAncla,float(caso[22]),float(caso[23]),"hogar",None,None,"L-D",None,None)
        anclaHogar.sector_auto = getSectorForPoint(anclaHogar,"Auto")
        anclaHogar.sector_caminando = getSectorForPoint(anclaHogar,"Caminando")
        anclaHogar.save()
        idAncla +=1
        ## Individuo
        #Id, Tipo transporte, Prestador, Hogar, Trabajo, Jardin
        individuo  = Individuo(int(caso[0]),int(caso[19]),int(caso[1]),anclaHogar.id,anclaTrabajo.id,anclaJardin.id)
        individuo.save()

def getSectorForPoint(ancal,tipo):
    if(tipo == "Auto" or tipo == 1 ):
        shapes = shapeAuto
    else:
        shapes = shapeCaminando
    point = Point(ancal.x_coord,ancal.y_coord)
    for i in range(len(shapes)):
        polygon = Polygon(shapes[i].points)
        if(polygon.contains(point)):
            return Sector.objects.get(shape = i, tipo_sector = tipo)

def cargarTiempos(tipo,request):
    print(request.FILES)
    if(tipo == 0):
        SectorTiempo.objects.filter(id__lt = len(shapeAuto)).delete()
    else:
        SectorTiempo.objects.filter(id__gte = len(shapeAuto)).delete()
    csvfile = request.FILES['inputFile']
    csvf = StringIO(csvfile.read().decode())
    l = csv.reader(csvf, delimiter=',')
    lineas=[]
    lineas.extend(l)
    lineas = lineas[1:]
    id = 0
    tiempos = []
    #sectores = Sector.objects.all()
    for caso in lineas:
        tiempo = SectorTiempo(id = id , sector_1_id = int(caso[0]), sector_2_id = int(caso[1]),tiempo = float(caso[2]), distancia = float(caso[3]))
        tiempos.append(tiempo)
        id +=1
        if(id % 100000 == 0):
            guardar = SectorTiempo.objects.bulk_create(tiempos)
            tiempos = []
    if(tiempos):
        guardar = SectorTiempo.objects.bulk_create(tiempos)

def cargarCentroPediatras(request):
    Pediatra.objects.all().delete()
    csvfile = request.FILES['inputFile']
    csvf = StringIO(csvfile.read().decode())
    l = csv.reader(csvf, delimiter=',')
    lineas=[]
    lineas.extend(l)
    lineas = lineas[1:]
    inti = 0
    horas = ["6.0","7.0","8.0","9.0","10.0","11.0","12.0","13.0","14.0","15.0","16.0","17.0","18.0","19.0","20.0","21.0"]
    id = 0
    for caso in lineas:
    ## Centro
    #Id, Coordenada X, Coordenada Y, Sector, Direccion, Prestador
        if(caso[2]!=""):
            #int(caso[3] id para cuando sean unicas
            centro = Centro(inti,float(caso[9]),float(caso[10]),None,None,caso[7],int(caso[2]))
            centro.sector_auto = getSectorForPoint(centro,"Auto")
            centro.sector_caminando = getSectorForPoint(centro,"Caminando")
            centro.save()
        ## Pediatra
        #Centro, Dia, Hora, Cantidad de pediatras
        #dias = ["LUNES","MARTES","MIERCOLES","JUEVES","VIERNES","SABADO"]
            contador_dias = 11
            for i in range(6):
                for j in horas:
                    if(contador_dias > 106): ##Arreglar
                        break
                    if ((caso[contador_dias]) == ''):
                        caso[contador_dias]=0
                        pediatra = Pediatra (centro_id = inti,dia = i, hora = parsear_hora(j), cantidad_pediatras = int(caso[contador_dias]))
                        pediatra.save()
                        contador_dias +=1
                    else:
                        pediatra = Pediatra (centro_id = inti,dia = i, hora = parsear_hora(j), cantidad_pediatras = int(caso[contador_dias]))
                        contador_dias +=1
                        pediatra.save()
            inti +=1
def consultaConFiltro(request):
    if(not IndividuoTiempoCentro.objects.all()):
        calcAndSaveDefault()
    #prestadorFiltro  = getFilters(request,'prestadorFiltro')
    #transporteFiltro = getFilters(request,'transporteFiltro')
    #diaFiltro        = getFilters(request,'diasFiltro')
    #horaFiltro       = getFilters(request,'horasFiltro')
    consulta = IndividuoTiempoCentro.objects.select_related().all()#.filter(centro__prestador__nombre__in = prestadorFiltro, individuo__tipo_transporte__nombre__in = transporteFiltro, dia__in=diaFiltro, hora__in=horaFiltro)
    dias     = ["Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo"]
    table    = PersonTable(consulta)
    RequestConfig(request).configure(table)
    context = {'result': table, 'dias':dias}
    return render(request, 'app/calcAll2.html', context)
def resumenConFiltroOSinFiltroPeroNingunoDeLosDos(request):
    if(MedidasDeResumen.objects.all()):
        individuos = []
    else:
        individuos = Individuo.objects.all()
    for individuo in individuos:
        tiempos = IndividuoTiempoCentro.objects.filter(individuo = individuo)
        dictConsultasPorDia = {0:0,1:0,2:0,3:0,4:0,5:0}
        dictHorasPorDia = {0:set(),1:set(),2:set(),3:set(),4:set(),5:set()}
        dictCentrosPorDia = {0:set(),1:set(),2:set(),3:set(),4:set(),5:set()}
        centros = dict()
        for tiempo in tiempos:
            if(tiempo.llega == "Si"):
                dia = tiempo.dia
                dictConsultasPorDia[dia] = dictConsultasPorDia[dia] + 1
                dictHorasPorDia[dia].add(tiempo.hora)
                dictCentrosPorDia[dia].add(tiempo.centro_id)
                if(tiempo.centro_id in centros):
                    if(tiempo.tiempoViaje < centros[tiempo.centro_id]):
                        centros[tiempo.centro_id] = tiempo.tiempoViaje
                else:
                    centros[tiempo.centro_id] = tiempo.tiempoViaje
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

        leResumen.save()
    consulta = MedidasDeResumen.objects.all()
    table  = ResumenTable(consulta)
    RequestConfig(request, paginate={'per_page': 10}).configure(table)
    context = {'result': table}
    return render(request, 'app/calcAll2.html', context)
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
def getFilters(request,filtro):
    filtros = []
    for key, value in request.POST.items():
        if(filtro.upper() in key.upper()):
            filtros.append(value)
    return filtros
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
def calcAndSaveDefault():
    tiempoMaximo = int(Settings.objects.get(setting = "tiempoMaximo").value)  # Cambiar(Tomar de bd)
    tiempoConsulta = int(Settings.objects.get(setting = "tiempoConsulta").value) #Cambiar(Tomar de bd)
    individuos = Individuo.objects.all()
    prestadores = Prestador.objects.all()
    for individuo in individuos:
        print("wew")
        prest      = [individuo.prestador]#arreglar
        transporte = individuo.tipo_transporte.id
        trabajo    = individuo.trabajo
        jardin     = individuo.jardin
        secHogar   = getSector(individuo.hogar,transporte)
        secTrabajo = getSector(trabajo,transporte)
        secJardin  = getSector(jardin,transporte)
        for prestador in prest:
            centros = Centro.objects.filter(prestador = prestador)
            for centro in centros:
                secCentro = getSector(centro,transporte)
                horas     = Pediatra.objects.filter(centro__id_centro = centro.id_centro)
                for hora in horas:
                    if(trabajo and hora.dia in getListOfDays(trabajo.dias)):
                        if(hora.hora < trabajo.hora_inicio):
                            if(jardin and hora.dia in getListOfDays(jardin.dias)):
                                tiempoViaje = calcularTiempos([secCentro, secJardin, secTrabajo],transporte,hora.hora)
                            else:
                                tiempoViaje = calcularTiempos([secCentro,secHogar, secTrabajo],transporte,hora.hora)
                            horaFinConsulta = hora.hora + tiempoConsulta/60
                            if(trabajo.hora_inicio >= tiempoViaje + horaFinConsulta and tiempoViaje < tiempoMaximo/60 and hora.cantidad_pediatras >0):
                                llega = "Si"
                            else:
                                llega = "No"
                            q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia =hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje*60, cantidad_pediatras=hora.cantidad_pediatras, llega =  llega)
                            q.save()
                        else:
                            if(jardin and hora.dia in getListOfDays(jardin.dias)):
                                tiempoViaje = calcularTiempos([secTrabajo, secJardin, secCentro],transporte,hora.hora)
                            else:
                                tiempoViaje = calcularTiempos([secTrabajo, secHogar, secCentro],transporte,hora.hora)
                            if(hora.hora >=  trabajo.hora_fin + tiempoViaje and tiempoViaje < tiempoMaximo/60 and hora.cantidad_pediatras>0):
                                llega = "Si"
                            else:
                                llega = "No"
                            q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia = hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje*60, cantidad_pediatras=hora.cantidad_pediatras,llega =  llega)
                            q.save()
                    else:
                        if(jardin and hora.dia in getListOfDays(jardin.dias)):
                            if(hora.hora < jardin.hora_inicio):
                                tiempoViaje     = calcularTiempos([secCentro, secJardin],transporte,hora.hora)
                                horaFinConsulta = hora.hora + tiempoConsulta/60
                                if(jardin.hora_inicio >= horaFinConsulta + tiempoViaje and tiempoViaje < tiempoMaximo/60 and hora.cantidad_pediatras>0):
                                    llega = "Si"
                                else:
                                    llega = "No"
                                q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia = hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje*60, cantidad_pediatras=hora.cantidad_pediatras,llega =  llega)
                                q.save()
                            else:
                                tiempoViaje = calcularTiempos([secJardin, secCentro],transporte,hora.hora)
                                if(hora.hora >=  jardin.hora_fin + tiempoViaje and tiempoViaje < tiempoMaximo/60):
                                    llega = "Si"
                                else:
                                    llega = "No"
                                q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia = hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje*60, cantidad_pediatras=hora.cantidad_pediatras,llega =  llega)
                                q.save()
                        else:
                            tiempoViaje = calcularTiempos([secHogar, secCentro],transporte,hora.hora)
                            if(tiempoViaje < tiempoMaximo/60):
                                llega = "Si"
                            else:
                                llega = "No"
                            q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia = hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje*60, cantidad_pediatras=hora.cantidad_pediatras,llega =  llega)
                            q.save()
