from django.http import HttpResponse
from django.shortcuts import render
from app.models import Individuo, Settings, TipoTransporte,Sector, Prestador, AnclaTemporal, SectorTiempo,Centro,Pediatra,IndividuoTiempoCentro,MedidasDeResumen
from django.db.models import F
from app.filters import IndividuoTiempoCentroFilter
from app.tables import PersonTable,ResumenTable,TestPersonTable
from django_tables2 import RequestConfig
from shapely.geometry import Polygon, Point
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div
from crispy_forms.bootstrap import Tab, TabHolder,InlineCheckboxes,InlineRadios
import shapefile
from io import StringIO
import time
from app.bus.omnibus import get_horarios, load, busqueda, parada_mas_cercana, get_parada
import csv
from django.shortcuts import redirect
from django_tables2 import SingleTableView
global shapeAuto
global shapeCaminando
global horarios
global nodos
horarios = get_horarios('app/bus/horarios.csv')
nodos = load('app/bus/test_nodos_cercanos.csv')
sf = shapefile.Reader('app/files/shapeAuto.shp')
shapeAuto = sf.shapes()
sf = shapefile.Reader('app/files/shapeCaminando.shp')
shapeCaminando = sf.shapes()

def test(request):
    if(not IndividuoTiempoCentro.objects.all()):
        newCalcTimes()
    response = redirect('consultaConFiltro')
    response['Location'] += '?individuo=87'
    return response
    return redirect('consultaConFiltro')

class PagedFilteredTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = IndividuoTiempoCentro.objects.filter(individuo__prestador = F('centro__prestador'));
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
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary')),
    )
class FilteredPersonListView(PagedFilteredTableView):
    table_class = TestPersonTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = IndividuoTiempoCentroFilter
    formhelper_class = FooFilterFormHelper
class TestFilteredPersonListView(SingleTableMixin, FilterView):
    table_class = TestPersonTable
    model = IndividuoTiempoCentro
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filterset_class = IndividuoTiempoCentroFilter
    page = 2
def printCentroids():
    for shape in shapeAuto:
        p = Polygon(shape.points)
        if(p.is_valid):
            return p.representative_point()
        else:
            return p.centroid
def index(request):
    printCentroids()
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
        print("Individuo "+caso[0])
        ## Ancla
        #Coordenada X, Coordenada Y, Tipo, Hora inicio, Hora fin, Dias, Sector auto, Sector caminando
        #Duda Tecnica -Contemplar casos donde no hay jardin y/o trabajo
        if(caso[5] == "1"):
            anclaJardin  = AnclaTemporal(idAncla,float(caso[10]),float(caso[11]),"jardin" ,parsear_hora(caso[7]) ,parsear_hora(caso[8]) ,caso[6] ,None,None)
            anclaJardin.sector_auto = getSectorForPoint(anclaJardin,"Auto")
            anclaJardin.sector_caminando = getSectorForPoint(anclaJardin,"Caminando")
            anclaJardin.parada = parada_mas_cercana(float(caso[10]),float(caso[11]),nodos)
            anclaJardin.save()
            idAncla +=1
        else:
            anclaJardin = None
        if(caso[12] == "1"):
            anclaTrabajo = AnclaTemporal(idAncla,float(caso[14]),float(caso[15]),"trabajo",parsear_hora(caso[17]),parsear_hora(caso[18]),caso[16],None,None)
            anclaTrabajo.sector_auto = getSectorForPoint(anclaTrabajo,"Auto")
            anclaTrabajo.sector_caminando = getSectorForPoint(anclaTrabajo,"Caminando")
            anclaTrabajo.parada = parada_mas_cercana(float(caso[14]),float(caso[15]),nodos)
            anclaTrabajo.save()
            idAncla +=1
        else:
            anclaTrabajo = None
        anclaHogar   = AnclaTemporal(idAncla,float(caso[22]),float(caso[23]),"hogar",None,None,"L-D",None,None)
        anclaHogar.sector_auto = getSectorForPoint(anclaHogar,"Auto")
        anclaHogar.sector_caminando = getSectorForPoint(anclaHogar,"Caminando")
        anclaHogar.parada = parada_mas_cercana(float(caso[22]),float(caso[23]),nodos)
        anclaHogar.save()
        idAncla +=1
        ## Individuo
        #Id, Tipo transporte, Prestador, Hogar, Trabajo, Jardin
        individuo  = Individuo(int(caso[0]),int(caso[19]),int(caso[1]),anclaHogar.id,anclaTrabajo.id if anclaTrabajo is not None else None,anclaJardin.id if anclaJardin is not None else None)
        individuo.save()

def getSectorForPoint(ancal,tipo):
    if(tipo == "Auto" or tipo == 1 ):
        shapes = shapeAuto
    else:
        shapes = shapeCaminando
    point = Point(ancal.x_coord,ancal.y_coord)
    for i in range(len(shapes)):
        polygon = Polygon(shapes[i].points)
        if(ancal.x_coord == polygon.centroid.wkt):
            print("Same x")
        if(point.within(polygon)):
            return Sector.objects.get(shape = i, tipo_sector = tipo)
    if(tipo == "Auto"):
        print(point.wkt)

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
            centro.parada = parada_mas_cercana(float(caso[9]),float(caso[10]),nodos)
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
def resumenConFiltroOSinFiltroPeroNingunoDeLosDos(request):
    tiempoInicio = time.time()
    if(MedidasDeResumen.objects.all()):
        individuos = []
    else:
        individuos = Individuo.objects.all()[0:3]
    resultList = []
    for individuo in individuos:
        print("Individuo: "+str(individuo.id))
        tiempoIni = time.time()
        tiempos = IndividuoTiempoCentro.objects.filter(individuo = individuo)#, centro__prestador__id = individuo.prestador.id)
        dictConsultasPorDia = {0:0,1:0,2:0,3:0,4:0,5:0}
        dictHorasPorDia = {0:set(),1:set(),2:set(),3:set(),4:set(),5:set()}
        dictCentrosPorDia = {0:set(),1:set(),2:set(),3:set(),4:set(),5:set()}
        centros = dict()
        for tiempo in tiempos:
            llega = checkLlega(individuo,tiempo.dia,tiempo.hora,tiempo.tiempoViaje,tiempo.cantidad_pediatras)
            if(llega == "Si"):
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
        resultList.append(leResumen)
        print("Tiempo en el individuo: "+str(time.time()-tiempoIni))
        #leResumen.save()
    consulta = MedidasDeResumen.objects.all()
    table  = ResumenTable(resultList)
    RequestConfig(request, paginate={'per_page': 1000}).configure(table)
    print("Tiempo total: "+str(time.time()-tiempoInicio))
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
def checkLlega(individuo,dia,hora,tiempoViaje, cantidad_pediatras):
    tiempoMaximo = int(Settings.objects.get(setting = "tiempoMaximo").value)  # Cambiar(Tomar de bd)
    tiempoConsulta = int(Settings.objects.get(setting = "tiempoConsulta").value) #Cambiar(Tomar de bd)
    trabajo = individuo.trabajo
    jardin = individuo.jardin
    hogar = individuo.hogar
    if(cantidad_pediatras<=0 or tiempoViaje < tiempoMaximo/60):
        return "No"
    if(trabajo and dia in getListOfDays(trabajo.dias)):
        if(hora < trabajo.hora_inicio):
            horaFinConsulta = hora + tiempoConsulta/60
            if(trabajo.hora_inicio >= tiempoViaje + horaFinConsulta):
                return "Si"
            else:
                return "No"
        else:
            if(hora >=  trabajo.hora_fin + tiempoViaje):
                return "Si"
            else:
                return "No"
    else:
        if(jardin and dia in getListOfDays(jardin.dias)):
            if(hora < jardin.hora_inicio):
                horaFinConsulta = hora + tiempoConsulta/60
                if(jardin.hora_inicio >= horaFinConsulta + tiempoViaje):
                    return "Si"
                else:
                    return "No"
            else:
                if(hora >=  jardin.hora_fin + tiempoViaje):
                    return "Si"
                else:
                    return "No"
        else:
            return "Si"
def newCalcTimes():
    tiempoMaximo = int(Settings.objects.get(setting = "tiempoMaximo").value)  # Cambiar(Tomar de bd)
    tiempoConsulta = int(Settings.objects.get(setting = "tiempoConsulta").value) #Cambiar(Tomar de bd)
    individuos = Individuo.objects.select_related().all()
    prestadores = Prestador.objects.select_related().all()
    centros = Centro.objects.select_related().all()
    pedi = Pediatra.objects.select_related()
    for individuo in individuos:
        tiempoRestante = 0
        tiempoInicio = time.time()
        prest      = prestadores#[individuo.prestador]#arreglar
        transporte = individuo.tipo_transporte.id
        trabajo    = individuo.trabajo
        jardin     = individuo.jardin
        secHogar   = newGetSector(individuo.hogar,transporte)
        secTrabajo = newGetSector(trabajo,transporte)
        secJardin  = newGetSector(jardin,transporte)
        tHogarTrabajo = newCalcularTiempos([secHogar, secTrabajo],transporte)
        tHogarJardin =  newCalcularTiempos([secHogar, secJardin],transporte)
        tJardinTrabajo =newCalcularTiempos([secJardin, secTrabajo],transporte)
        tTrabajoJardin = newCalcularTiempos([secJardin, secHogar],transporte)
        tTrabajoHogar = newCalcularTiempos([secTrabajo, secHogar],transporte)
        tiempoRestante += time.time() - tiempoInicio
        loopTime = 0
        for centro in centros:
            aux = time.time()
            secCentro = newGetSector(centro,transporte)
            horas     = Pediatra.objects.filter(centro = centro)
            tHogarCentro = newCalcularTiempos([secHogar, secCentro],transporte)
            tJardinCentro= newCalcularTiempos([secJardin, secCentro],transporte)
            tCentroHogar =newCalcularTiempos([secCentro, secHogar],transporte)
            tCentroJardin =newCalcularTiempos([secCentro, secJardin],transporte)
            listaHoras = []
            tiempoRestante += time.time()-aux
            ini = time.time()
            for hora in horas:
                if((not (trabajo is None)) and hora.dia in getListOfDays(trabajo.dias)):
                    if(hora.hora < trabajo.hora_inicio):
                        if((not (jardin is None)) and hora.dia in getListOfDays(jardin.dias)):
                            tiempoViaje = tCentroJardin + tJardinTrabajo #calcularTiempos([secCentro, secJardin, secTrabajo],transporte,hora.hora)
                        else:
                            tiempoViaje = tCentroHogar + tHogarTrabajo ## calcularTiempos([secCentro,secHogar, secTrabajo],transporte,hora.hora)
                        q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia =hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje/60,
                                cantidad_pediatras=hora.cantidad_pediatras,tHogarTrabajo = tHogarTrabajo/60, tHogarJardin = tHogarJardin/60,tJardinTrabajo = tJardinTrabajo/60,
                                tTrabajoJardin = tTrabajoJardin/60,tTrabajoHogar = tTrabajoHogar/60,
                                tHogarCentro = tHogarCentro/60,tJardinCentro = tJardinCentro/60,
                                tCentroHogar = tCentroHogar/60,tCentroJardin = tCentroJardin/60)
                        listaHoras.append(q)
                        #q.save()
                    else:
                        if((not (jardin is None)) and hora.dia in getListOfDays(jardin.dias)):
                            tiempoViaje = tTrabajoJardin + tJardinCentro ##calcularTiempos([secTrabajo, secJardin, secCentro],transporte,hora.hora)
                        else:
                            tiempoViaje = tTrabajoHogar + tHogarCentro ##calcularTiempos([secTrabajo, secHogar, secCentro],transporte,hora.hora)
                        q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia =hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje/60,
                                cantidad_pediatras=hora.cantidad_pediatras,tHogarTrabajo = tHogarTrabajo/60, tHogarJardin = tHogarJardin/60,tJardinTrabajo = tJardinTrabajo/60,
                                tTrabajoJardin = tTrabajoJardin/60,tTrabajoHogar = tTrabajoHogar/60,
                                tHogarCentro = tHogarCentro/60,tJardinCentro = tJardinCentro/60,
                                tCentroHogar = tCentroHogar/60,tCentroJardin = tCentroJardin/60)
                        listaHoras.append(q)
                        #q.save()
                else:
                    if((not (jardin is None)) and hora.dia in getListOfDays(jardin.dias)):
                        if(hora.hora < jardin.hora_inicio):
                            tiempoViaje     = tCentroJardin #calcularTiempos([secCentro, secJardin],transporte,hora.hora)
                            q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia =hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje/60,
                                    cantidad_pediatras=hora.cantidad_pediatras,tHogarTrabajo = tHogarTrabajo/60, tHogarJardin = tHogarJardin/60,tJardinTrabajo = tJardinTrabajo/60,
                                    tTrabajoJardin = tTrabajoJardin/60,tTrabajoHogar = tTrabajoHogar/60,
                                    tHogarCentro = tHogarCentro/60,tJardinCentro = tJardinCentro/60,
                                    tCentroHogar = tCentroHogar/60,tCentroJardin = tCentroJardin/60)
                            listaHoras.append(q)
                            #q.save()
                        else:
                            tiempoViaje = tJardinCentro ##calcularTiempos([secJardin, secCentro],transporte,hora.hora)
                            q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia =hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje/60,
                                    cantidad_pediatras=hora.cantidad_pediatras,tHogarTrabajo = tHogarTrabajo/60, tHogarJardin = tHogarJardin/60,tJardinTrabajo = tJardinTrabajo/60,
                                    tTrabajoJardin = tTrabajoJardin/60,tTrabajoHogar = tTrabajoHogar/60,
                                    tHogarCentro = tHogarCentro/60,tJardinCentro = tJardinCentro/60,
                                    tCentroHogar = tCentroHogar/60,tCentroJardin = tCentroJardin/60)
                            listaHoras.append(q)
                            #q.save()
                    else:
                        tiempoViaje = tHogarCentro ##calcularTiempos([secHogar, secCentro],transporte,hora.hora)
                        q = IndividuoTiempoCentro(individuo = individuo , centro = centro, dia =hora.dia, hora = hora.hora ,tiempoViaje = tiempoViaje/60,
                                cantidad_pediatras=hora.cantidad_pediatras,tHogarTrabajo = tHogarTrabajo/60, tHogarJardin = tHogarJardin/60,tJardinTrabajo = tJardinTrabajo/60,
                                tTrabajoJardin = tTrabajoJardin/60,tTrabajoHogar = tTrabajoHogar/60,
                                tHogarCentro = tHogarCentro/60,tJardinCentro = tJardinCentro/60,
                                tCentroHogar = tCentroHogar/60,tCentroJardin = tCentroJardin/60)
                        listaHoras.append(q)
            loopTime += time.time()-ini    #q.save()
            IndividuoTiempoCentro.objects.bulk_create(listaHoras)
        print("Termino el individuo: "+str(individuo.id))
        print("El loopTime es: "+str(loopTime))
        print("El restante es: "+str(tiempoRestante))
        print("El tiempoTotal es: "+str(time.time()-tiempoInicio))
def newCalcularTiempos(anclas,transporte):
    tiempoViaje = 0
    hora = 0
    if(True):#not (transporte == "bus" or transporte == 2 or transporte == 3)):
        for i in range(0,len(anclas)-1):
            if(anclas[i] is None or anclas[i+1] is None):
                return -7000#-1/60
            tiempoViaje += (SectorTiempo.objects.get(sector_1 = anclas[i], sector_2 = anclas[i+1])).tiempo
            return tiempoViaje
    else:
        print(anclas)
        for i in range(0,len(anclas)-1):
            if(anclas[i] is None or anclas[i+1] is None):
                return -7000#-1/60
            print(nodos)
            print(get_parada(nodos,anclas[i]))
            print(get_parada(nodos,anclas[i+1]))
            parada_origen = get_parada(nodos,anclas[i])
            parada_destino = get_parada(nodos,anclas[i+1])
            #print("*******************Coords origen: "+str(coords_origen)+" Coords destino: "+str(coords_destino))
            tiempoViaje += busqueda(parada_origen,parada_origen.coords,parada_destino,parada_destino.coords,nodos,horarios,hora)
            return tiempoViaje
def newGetSector(lugar, transporte):
    #print(transporte):
    if(lugar is None):
        return None
    if(True):#transporte == 'Auto' or transporte == 1):
        return lugar.sector_auto
    elif(transporte == 'Caminando' or transporte == 0):
        #return lugar.sector_caminando
        return lugar.sector_auto
    else:
        return lugar
