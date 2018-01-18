from __future__ import absolute_import, unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
from app.models import Individuo, Settings, TipoTransporte,Sector, Prestador, AnclaTemporal, SectorTiempo,Centro,Pediatra,IndividuoTiempoCentro,MedidasDeResumen,SectorTiempoOmnibus,IndividuoCentro
from django.db.models import F
import math
from django_tables2.export.export import TableExport
from app.filters import IndividuoTiempoCentroFilter
from app.tables import PersonTable,ResumenTable,TestPersonTable, SimPersonTable
from django_tables2 import RequestConfig
from shapely.geometry import Polygon, Point
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML,Field
from crispy_forms.bootstrap import Tab, TabHolder,InlineCheckboxes,InlineRadios
import shapefile
from django_tables2.export.views import ExportMixin
from io import StringIO
import time
from app.bus.omnibus import get_horarios, load, busqueda, parada_mas_cercana, get_parada
import csv
from django.shortcuts import redirect
from django_tables2 import SingleTableView
from celery import group
from app.checkeo_errores import *
from app.task import suzuki, calculateIndividual
from django.http import StreamingHttpResponse
global shapeAuto
global shapeCaminando
global horarios
global nodos

global TIEMPO_ARBITRARIAMENTE_ALTO
TIEMPO_ARBITRARIAMENTE_ALTO = 70

#horarios = get_horarios('app/bus/horarios.csv')
#nodos = load('app/bus/test_nodos_cercanos.csv')
sf = shapefile.Reader('app/files/shapeAuto.shp')
shapeAuto = sf.shapes()
sf = shapefile.Reader('app/files/shapeCaminando.shp')
shapeCaminando = sf.shapes()

def test(request):
    #print("Ke wea")
    if(len(IndividuoCentro.objects.all()) == 0):
        print("******************************************************************************************************************")
        newCalcTimes()
    getReq = request.GET
    if(getReq.get('checkRango','0') == '-1'):
        return consultaToCSV(request)
    response = redirect('consultaConFiltro')
    return response
def redirectSim(request):
    if(len(IndividuoCentro.objects.all()) == 0):
        print("******************************************************************************************************************")
        newCalcTimes()
    getReq = request.GET
    if(getReq.get('checkRes','0') == '1'):
        return resumenConFiltroOSinFiltroPeroNingunoDeLosDos(request)
    if(getReq.get('checkRango','0') == '-1'):
        return consultaToCSV(request)
    response = redirect('Simulacion')
    print(getReq.get('checkRango','0'))
    if(getReq.get('checkB',0) == '-1'):
        response.set_cookie(key='mutualista',value='-1')
    else:
        print("wow")
        response.set_cookie(key='mutualista',value=int(getReq.get('prestador','-1')))
    if(getReq.get('checkM','0') == '-1'):
        response.set_cookie(key='tipoTransporte',value='-1')
    else:
        response.set_cookie(key='tipoTransporte',value=int(getReq.get('tipoTransporte','-1')))
    response.set_cookie(key='trabaja', value=int(getReq.get('anclaTra','0')))
    response.set_cookie(key='jardin', value=int(getReq.get('anclaJar','0')))
    response['Location'] += '?individuo=87'
    return response

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
class PagedFilteredTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = IndividuoTiempoCentro.objects.all()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(PagedFilteredTableView, self).get_table()
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(PagedFilteredTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context
class FooFilterFormHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        TabHolder(
        Tab('Individuo-Centro',
        'individuo',
        Div('centro')
        ),
        Tab('Hora-Dia',
        'hora',InlineCheckboxes('dia')
        ),
        Tab('Prestadores', 'trabajo',InlineCheckboxes('prestador')),
        Tab('Transporte', 'tiempoViaje',InlineCheckboxes('transporte')),
        ),
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),
    )
class FilteredPersonListView(ExportMixin,PagedFilteredTableView):
    table_class = TestPersonTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = IndividuoTiempoCentroFilter
    formhelper_class = FooFilterFormHelper
class SimPersonView(ExportMixin,PagedFilteredTableView):
    table_class = SimPersonTable
    template_name = 'app/filterTable.html'
    paginate_by = 20
    filter_class = IndividuoTiempoCentroFilter
    formhelper_class = FooFilterFormHelper
def printCentroids():
    for shape in shapeAuto:
        p = Polygon(shape.points)
        if(p.is_valid):
            return p.representative_point()
        else:
            return p.centroid
def index(request):
    init()
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
            elif(radioMatrix == "option6"): # omnibus
                cargarTiemposBus(request)
            elif(radioMatrix == "option7"):
                cargarTiposTransporte(request)
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

def cargarMutualistas(request):
    lineas = checkMutualistas(request)
    if lineas is None: #Devuelve las lineas del archivo si la lista de errores esta vacia, None si no.
        return None
    Prestador.objects.all().delete()
    prestadores = list()
    for linea in lineas:
        p = Prestador(int(linea[0]),linea[1])
        prestadores.append(p)
    Prestador.objects.bulk_create(prestadores)
    print("Se cargo correctamente el archivo")

def cargarTiposTransporte(request):
    lineas = checkTiposTransporte(request)
    if lineas is None:
        return None
    TipoTransporte.objects.all().delete()
    tipos = list()
    for linea in lineas:
        t = TipoTransporte(int(linea[0]),linea[1])
        tipos.append(t)
    TipoTransporte.objects.bulk_create(tipos)
    print("Se cargo correctamente el archivo")

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
        return int(hora)
    h,m = hora.split('.')
    return int(h.zfill(2) + m.zfill(2))

def cargarIndividuoAnclas(requestf):
    prestadores = [x.id for x in Prestador.objects.all()]
    tipos_transporte = [x.id for x in TipoTransporte.objects.all()]
    lineas = checkIndividuoAnclas(requestf,prestadores,tipos_transporte)
    if lineas is None:
        return None
    Individuo.objects.all().delete()
    AnclaTemporal.objects.all().delete()
    idAncla = 0
    for caso in lineas:
        print("Individuo "+caso[0])
        ## Ancla
        #Coordenada X, Coordenada Y, Tipo, Hora inicio, Hora fin, Dias, Sector auto, Sector caminando
        #Duda Tecnica -Contemplar casos donde no hay jardin y/o trabajo
        if(caso[5] == "1"):
            anclaJardin  = AnclaTemporal(idAncla,float(caso[10]),float(caso[11]),"jardin" ,parsear_hora(caso[7]) ,parsear_hora(caso[8]) ,caso[6] ,None,None)
            anclaJardin.sector_auto = getSectorForPoint(anclaJardin,"Auto")
            anclaJardin.sector_caminando = getSectorForPoint(anclaJardin,"Caminando")
            anclaJardin.save()
            idAncla +=1
            tieneJardin = True
        else:
            tieneJardin = False
            anclaJardin = None
        if(caso[12] == "1"):
            anclaTrabajo = AnclaTemporal(idAncla,float(caso[14]),float(caso[15]),"trabajo",parsear_hora(caso[17]),parsear_hora(caso[18]),caso[16],None,None)
            anclaTrabajo.sector_auto = getSectorForPoint(anclaTrabajo,"Auto")
            anclaTrabajo.sector_caminando = getSectorForPoint(anclaTrabajo,"Caminando")
            anclaTrabajo.save()
            idAncla +=1
            tieneTrabajo = True
        else:
            tieneTrabajo = False
            anclaTrabajo = None
        anclaHogar   = AnclaTemporal(idAncla,float(caso[22]),float(caso[23]),"hogar",None,None,"L-D",None,None)
        anclaHogar.sector_auto = getSectorForPoint(anclaHogar,"Auto")
        anclaHogar.sector_caminando = getSectorForPoint(anclaHogar,"Caminando")
        anclaHogar.save()
        idAncla +=1
        ## Individuo
        #Id, Tipo transporte, Prestador, Hogar, Trabajo, Jardin
        individuo  = Individuo(id = int(caso[0]),tipo_transporte = TipoTransporte.objects.get(id =int(caso[19])),prestador = Prestador.objects.get(id =int(caso[1])),
                    hogar = anclaHogar,trabajo = anclaTrabajo, jardin = anclaJardin, tieneJardin = tieneJardin,tieneTrabajo = tieneTrabajo)
        individuo.save()
    print("Se cargo correctamente el archivo")
    init()

def getSectorForPoint(ancal,tipo):
    if(tipo == "Auto" or tipo == 1 ):
        shapes = shapeAuto
        tipo = "Auto"
    else:
        tipo = "Caminando"
        shapes = shapeCaminando
    point = Point(ancal.x_coord,ancal.y_coord)
    for i in range(len(shapes)):
        polygon = Polygon(shapes[i].points)
        if(ancal.x_coord == polygon.centroid.wkt):
            print("Same x")
        if(point.within(polygon)):
            return Sector.objects.get(shape = i,tipo_sector = tipo)#len(shapeAuto)+i)#, tipo_sector = tipo)
    if(tipo == "Auto"):
        print(point.wkt)

def cargarTiempos(tipo,request):
    lineas = checkTiempos(tipo,request)
    if (lineas is None): #Devuelve las lineas del archivo si la lista de errores esta vacia, None si no.
        return None
    if(tipo == 0):
        SectorTiempo.objects.filter(sector_1_id__id__lt = len(shapeAuto)).delete()
        id = 0
    else:
        SectorTiempo.objects.filter(sector_1_id__id__gte = len(shapeAuto)).delete()
        id = SectorTiempo.objects.latest('id').id + 1
        print(id)
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
        if(id % 100000 == 0):
            print(id)
            guardar = SectorTiempo.objects.bulk_create(tiempos)
            tiempos = []
    if(tiempos):
        guardar = SectorTiempo.objects.bulk_create(tiempos)
    print("Se cargo correctamente el archivo")

def cargarTiemposBus(request):
    lineas = checkTiemposBus(request)
    if (lineas is None): #Devuelve las lineas del archivo si la lista de errores esta vacia, None si no.
        return None
    SectorTiempoOmnibus.objects.all().delete()
    id = 0
    tiempos = []
    for i in range(len(lineas)):
        for j in range(len(lineas[i])):
            if i == j:
                t = SectorTiempo.objects.get(sector_1 = i, sector_2 = j).tiempo
            else:
                t = float(lineas[i][j])
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

def cargarCentroPediatras(request):
    p = list(Prestador.objects.all()) # Traigo todos los prestadores
    dict_prestadores = {p[x].nombre:p[x].id for x in range(len(p))} # armo un diccionario que relaciona el nombre con la id
    lineas = checkCentroPediatras(request,dict_prestadores)
    if lineas is None:
        return None
    Pediatra.objects.all().delete()
    Centro.objects.all().delete()
    horas = [str(float(x)) for x in range(6,22)] # ["6.0".."21.0"]
    for caso in lineas:
        ## Centro
        #Id, Coordenada X, Coordenada Y, SectorAuto, SectorCaminando, Prestador
        id_centro = int(caso[0])
        prestador = dict_prestadores.get(caso[1],1000)
        centro = Centro(id_centro,float(caso[3]),float(caso[4]),None,None,prestador)
        centro.sector_auto = getSectorForPoint(centro,"Auto")
        centro.sector_caminando = getSectorForPoint(centro,"Caminando")
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

def resumenConFiltroOSinFiltroPeroNingunoDeLosDos(request):
    tiempoInicio = time.time()
    if(MedidasDeResumen.objects.all()):
        individuos = []
    else:
        getData = request.GET
        fromRange = int(getData.get('fromRange')) if(getData.get('fromRange',"") != "" ) else 0
        toRange = int(getData.get('toRange')) if(getData.get('toRange',"") != "" ) else Individuo.objects.last().id
        if(getData.get("simular",'0') == '1' ):
            indQuery = Individuo.objects.filter(id__gte = fromRange,id__lte = toRange)
            #indQuery = IndividuoTiempoCentro.objects.filter(individuo__in = individuos).values_list('id', flat=True):
            dictParam = generateParamDict(getData)
        else:
            transportList = []
            if(getData.get('autoResumenes', None)):
                transportList.append(1)
            if(getData.get('caminandoResumenes', None)):
                transportList.append(2)
            if(getData.get('omnibusResumenes', None)):
                transportList.append(3)
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
        #size = math.ceil(len(indQuery)/8)
        individuos = [[[x.id for x in indQuery[i:i + 25]],None] for i in range(0, len(indQuery), 25)]
        #individuos = [[i.id,None] for i in indQuery]
        print(individuos)
        #print(len(individuos))
        #individuos = ([1],[2],[3]) #list(Individuo.objects.values_list('id')[0:3])
    resultList = []
    job = suzuki.chunks(individuos,1).group()
    result = job.apply_async()
    resumenObjectList = result.join()
    resumenObjectList = sum(sum(resumenObjectList,[]), [])
    table  = ResumenTable(resumenObjectList)
    print("Time in seconds = "+str(time.time() - tiempoInicio))
    RequestConfig(request).configure(table)
    exporter = TableExport('csv', table)
    return exporter.response('table.{}'.format('csv'))
    print(resumenObjectList)
    context = {"table":table}
    return render(request, 'app/calcAll2.html', context)
class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value
def consultaToCSV(request):
    tiempoInicio = time.time()
    getData = request.GET
    fromRange = int(getData.get('fromRange')) if(getData.get('fromRange',"") != "" ) else 0
    toRange = int(getData.get('toRange')) if(getData.get('toRange',"") != "" ) else Individuo.objects.last().id
    if(getData.get("simular",'0') == '1' ):
        indQuery = Individuo.objects.filter(id__gte = fromRange,id__lte = toRange)
        #indQuery = IndividuoTiempoCentro.objects.filter(individuo__in = individuos).values_list('id', flat=True):
        dictParam = generateParamDict(getData)
        print(dictParam)
        print(indQuery)
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
        print(trabaja,jardin,fromRange,toRange,transportList)
        indQuery = Individuo.objects.filter(id__gte = fromRange,id__lte = toRange, tipo_transporte__id__in = transportList, tieneTrabajo__in = trabaja,tieneJardin__in = jardin)
        print("Individuos a calcular: "+str(len(indQuery)))
        dictParam = None
    individuos = [[indQuery[i:i + 25],None] for i in range(0, len(indQuery), 25)]
    resultList = []
    job = calculateIndividual.chunks(individuos,1).group()
    result = job.apply_async()
    resumenObjectList = result.join()
    resumenObjectList = sum(sum(resumenObjectList,[]), [])
    #table  = PersonTable(resumenObjectList)
    print("Time in seconds = "+str(time.time() - tiempoInicio))
    timeinit = time.time()
    #RequestConfig(request).configure(table)
    #exporter = TableExport('csv', table)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in resumenObjectList),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="resultado.csv"'
    return response
    buffer = StringIO()
    wr = csv.writer(buffer, quoting=csv.QUOTE_ALL)
    wr.writerows(resumenObjectList)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=resultado.csv'
    print(time.time()-timeinit)
    return response
    return exporter.response('table.{}'.format('csv'))
def newCalcTimes():
    print("Lllegue")
    tiempoMaximo = int(Settings.objects.get(setting = "tiempoMaximo").value)  # Cambiar(Tomar de bd)
    tiempoConsulta = int(Settings.objects.get(setting = "tiempoConsulta").value) #Cambiar(Tomar de bd)
    individuos = Individuo.objects.select_related().all()
    prestadores = Prestador.objects.select_related().all()
    centros = Centro.objects.select_related().all()
    pedi = Pediatra.objects.select_related()
    for individuo in individuos:
        print(individuo.id)
        tiempoRestante = 0
        tiempoInicio = time.time()
        prest      = prestadores#[individuo.prestador]#arreglar
        transporte = individuo.tipo_transporte.id
        trabajo    = individuo.trabajo
        jardin     = individuo.jardin
        secHogarAuto   = newGetSector(individuo.hogar,1)
        secTrabajoAuto = newGetSector(trabajo,1)
        secJardinAuto  = newGetSector(jardin,1)
        ######
        secHogarCaminando   = newGetSector(individuo.hogar,0)
        secTrabajoCaminando = newGetSector(trabajo,0)
        secJardinCaminando  = newGetSector(jardin,0)
        #####
        secHogarBus   = newGetSector(individuo.hogar,1)
        secTrabajoBus = newGetSector(trabajo,1)
        secJardinBus = newGetSector(jardin,1)
        ####
        tHogarTrabajoAuto = newCalcularTiempos([secHogarAuto, secTrabajoAuto],1)
        tHogarJardinAuto =  newCalcularTiempos([secHogarAuto, secJardinAuto],1)
        tJardinTrabajoAuto =newCalcularTiempos([secJardinAuto, secTrabajoAuto],1)
        tTrabajoJardinAuto = newCalcularTiempos([secJardinAuto, secHogarAuto],1)
        tTrabajoHogarAuto = newCalcularTiempos([secTrabajoAuto, secHogarAuto],1)
#######################
        tHogarTrabajoCaminando = newCalcularTiempos([secHogarCaminando, secTrabajoCaminando],0)
        tHogarJardinCaminando =  newCalcularTiempos([secHogarCaminando, secJardinCaminando],0)
        tJardinTrabajoCaminando =newCalcularTiempos([secJardinCaminando, secTrabajoCaminando],0)
        tTrabajoJardinCaminando = newCalcularTiempos([secJardinCaminando, secHogarCaminando],0)
        tTrabajoHogarCaminando = newCalcularTiempos([secTrabajoCaminando, secHogarCaminando],0)
#######################
        tHogarTrabajoBus = newCalcularTiempos([secHogarBus, secTrabajoBus],2)
        tHogarJardinBus =  newCalcularTiempos([secHogarBus, secJardinBus],2)
        tJardinTrabajoBus =newCalcularTiempos([secJardinBus, secTrabajoBus],2)
        tTrabajoJardinBus = newCalcularTiempos([secJardinBus, secHogarBus],2)
        tTrabajoHogarBus = newCalcularTiempos([secTrabajoBus, secHogarBus],2)

        tiempoRestante += time.time() - tiempoInicio
        loopTime = 0
        tiemposCentros = []
        for centro in centros:
            aux = time.time()
            secCentroAuto = newGetSector(centro,1)
            secCentroCaminando = newGetSector(centro,0)
            secCentroBus = newGetSector(centro,1)
            horas     = Pediatra.objects.filter(centro = centro)
            tHogarCentroAuto = newCalcularTiempos([secHogarAuto, secCentroAuto],1)
            tJardinCentroAuto= newCalcularTiempos([secJardinAuto, secCentroAuto],1)
            tCentroHogarAuto =newCalcularTiempos([secCentroAuto, secHogarAuto],1)
            tCentroJardinAuto =newCalcularTiempos([secCentroAuto, secJardinAuto],1)
####################
            tHogarCentroCaminando = newCalcularTiempos([secHogarCaminando, secCentroCaminando],0)
            tJardinCentroCaminando= newCalcularTiempos([secJardinCaminando, secCentroCaminando],0)
            tCentroHogarCaminando =newCalcularTiempos([secCentroCaminando, secHogarCaminando],0)
            tCentroJardinCaminando =newCalcularTiempos([secCentroCaminando, secJardinCaminando],0)
#########################
            tHogarCentroBus = newCalcularTiempos([secHogarBus, secCentroBus],2)
            tJardinCentroBus= newCalcularTiempos([secJardinBus, secCentroBus],2)
            tCentroHogarBus =newCalcularTiempos([secCentroBus, secHogarBus],2)
            tCentroJardinBus =newCalcularTiempos([secCentroBus, secJardinBus],2)

            listaHoras = []
            tiempoRestante += time.time()-aux
            ini = time.time()
            q = IndividuoCentro(individuo = individuo , centro = centro, tHogarTrabajoAuto = tHogarTrabajoAuto/60,
                                tHogarJardinAuto = tHogarJardinAuto/60,tJardinTrabajoAuto = tJardinTrabajoAuto/60,
                                tTrabajoJardinAuto = tTrabajoJardinAuto/60,tTrabajoHogarAuto = tTrabajoHogarAuto/60,
                                tHogarCentroAuto = tHogarCentroAuto/60,tJardinCentroAuto = tJardinCentroAuto/60,
                                tCentroHogarAuto = tCentroHogarAuto/60,tCentroJardinAuto = tCentroJardinAuto/60,
            tHogarTrabajoCaminando = tHogarTrabajoCaminando/60,
                                tHogarJardinCaminando = tHogarJardinCaminando/60,tJardinTrabajoCaminando = tJardinTrabajoCaminando/60,
                                tTrabajoJardinCaminando = tTrabajoJardinCaminando/60,tTrabajoHogarCaminando = tTrabajoHogarCaminando/60,
                                tHogarCentroCaminando = tHogarCentroCaminando/60,tJardinCentroCaminando = tJardinCentroCaminando/60,
                                tCentroHogarCaminando = tCentroHogarCaminando/60,tCentroJardinCaminando = tCentroJardinCaminando/60,
            tHogarTrabajoBus = tHogarTrabajoBus/60,
                                tHogarJardinBus = tHogarJardinBus/60,tJardinTrabajoBus = tJardinTrabajoBus/60,
                                tTrabajoJardinBus = tTrabajoJardinBus/60,tTrabajoHogarBus = tTrabajoHogarBus/60,
                                tHogarCentroBus = tHogarCentroBus/60,tJardinCentroBus = tJardinCentroBus/60,
                                tCentroHogarBus = tCentroHogarBus/60,tCentroJardinBus = tCentroJardinBus/60)
            tiemposCentros.append(q)
            loopTime += time.time()-ini    #q.save()
        IndividuoCentro.objects.bulk_create(tiemposCentros)
        print("Termino el individuo: "+str(individuo.id))
        print("El loopTime es: "+str(loopTime))
        print("El restante es: "+str(tiempoRestante))
        print("El tiempoTotal es: "+str(time.time()-tiempoInicio))
def newCalcularTiempos(anclas,transporte):
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
            #print(sector1.id,sector2.id)
            tiempoViaje += (SectorTiempo.objects.get(sector_1 = sector1, sector_2 = sector2).tiempo)
            if(sector1.id == 114 and sector2.id == 8):
                print(tiempoViaje)
            return tiempoViaje
    else:
        for i in range(len(anclas)-1):
            if(anclas[i] is None or anclas[i+1] is None):
                return -7000
            #print(anclas[i].id)
            #print(anclas[i+1].id)
            tiempoViaje += (SectorTiempoOmnibus.objects.get(sectorO_1 = anclas[i], sectorO_2 = anclas[i+1])).tiempo
            return tiempoViaje

def newGetSector(lugar, transporte):
    #print(transporte):
    if(lugar is None):
        return None
    if(transporte == 'AUTO' or transporte == 1):
        return lugar.sector_auto
    elif(transporte == 'CAMINANDO' or transporte == 0):
        return lugar.sector_caminando
    else:
        return lugar.sector_auto

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
