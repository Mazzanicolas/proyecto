
import django_tables2 as tables
from .models import *
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import SingleTableView
from django_tables2.export.views import ExportMixin
from crequest.middleware import CrequestMiddleware
import app.utils as utils
from app.forms import *
from app.filters import *
from django_tables2 import RequestConfig
import math

class PagedFilteredTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = Individuo.objects.all()
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
class PersonTable(tables.Table):
    individuo = tables.Column(accessor = 'individuo.id',verbose_name='Individuo')
    centro = tables.Column(accessor='centro.id_centro',verbose_name='Centro')
    prestadorIndividuo = tables.Column(accessor = 'individuo.prestador.nombre', verbose_name = 'Prestador del Individuo')
    prestadorCentro = tables.Column(accessor = 'centro.prestador.nombre', verbose_name = 'Prestador del Centro')
    tipoTransporte = tables.Column(accessor = 'individuo.tipo_transporte.nombre', verbose_name = 'Transporte')
    tiempoViaje = tables.Column(verbose_name = 'Tiempo de viaje')
    llegaGeografico = tables.Column(verbose_name = 'Llega Geografico')
    llega = tables.Column(verbose_name = 'Llega')
    class Meta:
        per_page = 200
        model = IndividuoTiempoCentro
        attrs = {"class": "paleblue"}
        exclude = ('id',)
        sequence = ('individuo', 'prestadorIndividuo', 'centro','prestadorCentro','tipoTransporte','dia','hora','tiempoViaje','llegaGeografico','llega')
class TestPersonTable(ExportMixin, tables.Table):
    currentUser = -1
    request = None
    tiempos = dict()
    daysList = {0:'Lunes',1:'Martes',2:'Miercoles',3:'Jueves',4:'Viernes',5:'Sabado'}
    individuo = tables.Column(accessor = 'individuo.id',verbose_name='Individuo')
    centro = tables.Column(accessor='centro.id_centro',verbose_name='Centro')
    dia = tables.Column(verbose_name = 'Dia', empty_values = ())
    prestadorIndividuo = tables.Column(accessor = 'individuo.prestador.nombre', verbose_name = 'Prestador del Individuo')
    prestadorCentro = tables.Column(accessor = 'centro.prestador.nombre', verbose_name = 'Prestador del Centro')
    tipoTransporte = tables.Column(accessor = 'individuo.tipo_transporte.nombre', verbose_name = 'Transporte')
    tiempoViaje = tables.Column(verbose_name = 'Tiempo de viaje', empty_values = ())
    llegaGeografico = tables.Column(verbose_name = 'Llega Geografico', empty_values = ())
    llega = tables.Column(verbose_name = 'Llega', empty_values = ())

    def render_dia(self,record):
        if(not self.request):
            self.request = CrequestMiddleware.get_request()
        return self.daysList[record.dia]
    def render_llegaGeografico(self, record):
        return checkLlega(self,record.individuo,record.centro,record.dia,record.hora,record.tiempoViaje,record,record.individuo.tieneTrabajo,record.individuo.tieneJardin,self.tiempos)
    def render_tiempoViaje(self, record):
        if(self.currentUser == -1 or self.currentUser != record.individuo.id):
            self.tiempos = utils.getTiempos(record.individuo,record.centro,record.individuo.tipo_transporte.id)
        return calcTiempoDeViaje(record.individuo,record.centro,record.dia,record.hora,record.individuo.tieneTrabajo,record.individuo.tieneJardin,self.tiempos,record)
    def render_llega(self, record):
        return checkIfPedAndMut(record.llegaGeografico,record.individuo,record.centro,record.cantidad_pediatras,record.individuo.prestador.id)
    class Meta:
        per_page = 200
        model = IndividuoTiempoCentro
        attrs = {"class": "paleblue"}
        exclude = ('id',)
        sequence = ('individuo', 'prestadorIndividuo', 'centro','prestadorCentro','tipoTransporte','dia','hora','tiempoViaje','llegaGeografico','llega')
class SimPersonTable(TestPersonTable):
    init = False
    tipoTrans = '-1'
    trabaja = True
    jardin = True
    mutualista = '-1'
    dict_prestadores = utils.getPrestadores()
    prestadorIndividuo = tables.Column(empty_values = (), verbose_name = 'Prestador del Individuo')
    tipoTransporte = tables.Column(empty_values = (), verbose_name = 'Transporte')

    def render_prestadorIndividuo(self, record):
        if(not self.init):
            self.init = True
            utils.setParams(self, CrequestMiddleware.get_request().COOKIES)
        if(self.mutualista == '-1'):
            mutualista = str(record.individuo.prestador.id)
        elif (self.mutualista == '-2'):
            mutualista = str(record.centro.prestador.id)
        else:
            mutualista = self.mutualista
        return self.dict_prestadores.get(mutualista,0)
    def render_tipoTransporte(self,record):
        if(self.tipoTrans == '1'):
            return 'Auto'
        elif(self.tipoTrans == '0'):
            return "Caminando"
        elif(self.tipoTrans == '2'):
            return "Bus"
        return record.individuo.tipo_transporte.nombre

    def render_tiempoViaje(self, record):
        if(self.currentUser == -1 or self.currentUser != record.individuo.id):
            self.tiempos = utils.getTiempos(record.individuo,record.centro,self.tipoTrans)
            self.currentUser =  record.individuo.id
        return calcTiempoDeViaje(record.individuo,record.centro,record.dia,record.hora,self.trabaja,self.jardin,self.tiempos,record)
    def render_llegaGeografico(self, record):
        return checkLlega(self,record.individuo,record.centro,record.dia,record.hora,record.tiempoViaje,record,self.trabaja,self.jardin,self.tiempos)
    def render_llega(self, record):
        if(self.mutualista == '-1'):
            mutualista = record.individuo.prestador.id
        elif (self.mutualista == '-2'):
            mutualista = record.centro.prestador.id
        else:
            mutualista = int(self.mutualista)
        return checkIfPedAndMut(record.llegaGeografico,record.individuo,record.centro,record.cantidad_pediatras,mutualista)
    class Meta:
        per_page = 200
        model = IndividuoTiempoCentro
        attrs = {"class": "paleblue"}
        exclude = ('id',)
        sequence = ('individuo', 'prestadorIndividuo', 'centro','prestadorCentro','tipoTransporte','dia','hora','tiempoViaje','llegaGeografico','llega')
class FilteredPersonListView(ExportMixin,PagedFilteredTableView):
    table_class = TestPersonTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = IndividuoTiempoCentroFilter
    formhelper_class = IndTieCenHelper
class SimPersonView(ExportMixin,PagedFilteredTableView):
    table_class = SimPersonTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = IndividuoTiempoCentroFilter
    formhelper_class = IndTieCenHelper
class ResumenTable(ExportMixin,tables.Table):
    persona = tables.Column(accessor = 'persona.id',verbose_name='Individuo')
    centroOptimo = tables.Column(accessor='centroOptimo.id_centro',verbose_name='Centro Optimo')
    class Meta:
        model = MedidasDeResumen
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue"}
        sequence = ('persona', 'cantidadTotalHoras' ,'cantidadHorasLunes' ,
                    'cantidadHorasMartes' ,'cantidadHorasMiercoles' , 'cantidadHorasJueves' ,
                    'cantidadHorasViernes' ,'cantidadHorasSabado' , 'cantidadMaximaHoras' ,
                    'cantidadConsultasLunes' , 'cantidadConsultasMartes' ,'cantidadConsultasMiercoles' ,
                    'cantidadConsultasJueves' , 'cantidadConsultasViernes' ,'cantidadConsultasSabado' ,
                    'cantidadTotalConsultas' , 'cantidadCentrosLunes' , 'cantidadCentrosMartes' ,
                    'cantidadCentrosMiercoles' ,'cantidadCentrosJueves' , 'cantidadCentrosViernes' ,
                    'cantidadCentrosSabado' , 'cantidadTotalCentros' , 'centroOptimo')
        exclude = ('id',)
def checkIfPedAndMut(llega,individuo,centro,cantidad_pediatras,mutualista):
    if(llega == "Si"):
        if(mutualista == centro.prestador.id and cantidad_pediatras > 0):
            return "Si"
    return "No"
def checkLlega(self,individuo,centro, dia,hora,tiempoViaje,record,tieneTrabajo,tieneJardin,tiempos):
    tiempoMaximo = int(self.request.COOKIES.get("tiempoMaximo"))  # Cambiar(Tomar de bd)
    tiempoConsulta = int(self.request.COOKIES.get("tiempoConsulta")) #Cambiar(Tomar de bd)
    tiReLle = int(self.request.COOKIES.get('tiempoLlega'))
    trabajo = individuo.trabajo
    jardin = individuo.jardin
    hogar = individuo.hogar
    horaAcumulada = hora
    if(tiempoViaje > tiempoMaximo or tiempoViaje == -1):
        record.llegaGeografico = "No"
        return "No"
    if(tieneTrabajo and trabajo and dia in utils.getListOfDays(trabajo.dias)):
        if(hora < trabajo.hora_inicio):
            if(jardin and tieneJardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    resultTimpo = utils.minsToMil(tiempos['tHogarCentro'])
                    record.llegaGeografico =  "Si" if (utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroJardin']) <= jardin.hora_inicio and utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroJardin'] + tiempos['tJardinTrabajo'])<= trabajo.hora_inicio) else "No"
                    return record.llegaGeografico
                else:
                    horaTerCons1 = utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo'])
                    horaTerCons2  = utils.minsToMil(jardin.hora_fin + tiempos['tJardinCentro'] + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo'])
                    horaViajeMasConsulta = max(horaTerCons1, horaTerCons2)
                    record.llegaGeografico = "Si" if (horaViajeMasConsulta <= trabajo.hora_inicio and utils.minsToMil(jardin.hora_fin + tiempos['tJardinCentro']) <= utils.minsToMil(hora + tiReLle)) else "No"
                    return record.llegaGeografico
            else:
                horaViajeMasConsulta = utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroHogar'] + tiempos['tHogarTrabajo'])
                record.llegaGeografico = "Si" if (horaViajeMasConsulta <= trabajo.hora_inicio) else "No"
                return record.llegaGeografico
        else:
            if(jardin and tieneJardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    horaTerCons1 = utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroJardin'])
                    horaTerCons2 = utils.minsToMil(trabajo.hora_fin + tiempos['tTrabajoHogar'] + tiempos['tHogarCentro'] + tiempoConsulta + tiempos['tCentroJardin'])
                    horaViajeMasConsulta = max(horaTerCons1, horaTerCons2) 
                    record.llegaGeografico = "Si" if (horaViajeMasConsulta<= jardin.hora_inicio and utils.minsToMil(trabajo.hora_fin + resultTimpo) <= utils.minsToMil(hora + tiReLle)) else "No"
                    return record.llegaGeografico
                else:
                    resultTimpo = utils.minsToMil(tiempos['tTrabajoJardin'] + tiempos['tJardinCentro'])
                    horaLlegadaJardin = utils.minsToMil(trabajo.hora_fin + tiempos['tTrabajoJardin'])
                    horaSalidaJardin = jardin.hora_fin if (horaLlegadaJardin <= jardin.hora_fin) else horaLlegadaJardin
                    record.llegaGeografico = "Si" if (utils.minsToMil(horaSalidaJardin + tiempos['tJardinCentro']) <= utils.minsToMil(hora + tiReLle)) else "No"
                    return record.llegaGeografico
            else:
                resultTimpo = utils.minsToMil(tiempos['tTrabajoHogar'] + tiempos['tHogarCentro'])
                record.llegaGeografico = "Si" if (utils.minsToMil(trabajo.hora_fin + resultTimpo) <= utils.minsToMil(hora + tiReLle)) else "No"
                return record.llegaGeografico
    else:
        if(jardin and dia in utils.getListOfDays(jardin.dias)):
            if(hora < jardin.hora_inicio):
                resultTimpo = utils.minsToMil(tiempos['tHogarCentro'])
                resultLlegaG = "Si" if (utils.minsToMil(hora + tiempoConsulta + tiempos['tCentroJardin']) <= jardin.hora_inicio) else "No"
                return record.llegaGeografico
            else:
                resultTimpo = utils.minsToMil(tiempos['tHogarJardin']+ tiempos['tJardinCentro'])
                resultLlegaG = "Si" if (utils.minsToMil(jardin.hora_fin + tiempos['tJardinCentro']) <= utils.minsToMil(hora + tiReLle)) else "No"
                return record.llegaGeografico
        else:
            resultTimpo = utils.minsToMil(tiempos['tHogarCentro'])
            resultLlegaG = "Si" if (resultTimpo<=tiempoMaximo) else "No"
            return record.llegaGeografico

def calcTiempoDeViaje(individuo,centro,dia,hora,tieneTrabajo,tieneJardin,tiempos,record):
    hogar = individuo.hogar
    trabajo = individuo.trabajo
    jardin = individuo.jardin
    if(tieneTrabajo and trabajo and hora in range(trabajo.hora_inicio,trabajo.hora_fin) and 
            dia in utils.getListOfDays(trabajo.dias) or tieneJardin and 
            jardin and hora in range(jardin.hora_inicio,jardin.hora_fin) and dia in utils.getListOfDays(jardin.dias)):
        record.tiempoViaje = -1
        return record.tiempoViaje
    if(tieneTrabajo and trabajo and dia in utils.getListOfDays(trabajo.dias)):
        if(hora < trabajo.hora_inicio):
            if(tieneJardin and jardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    record.tiempoViaje = utils.minsToMil(tiempos['tHogarCentro'])
                    return record.tiempoViaje
                else:
                    record.tiempoViaje = utils.minsToMil(tiempos['tHogarJardin'] + tiempos['tJardinCentro'])
                    return record.tiempoViaje
            else:
                record.tiempoViaje = utils.minsToMil(tiempos['tHogarCentro'])
                return record.tiempoViaje
        else:
            if(tieneJardin and jardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    record.tiempoViaje = utils.minsToMil(tiempos['tTrabajoHogar'] + tiempos['tHogarCentro'])
                    return record.tiempoViaje
                else:
                    record.tiempoViaje = utils.minsToMil(tiempos['tTrabajoJardin'] + tiempos['tJardinCentro'])
                    return record.tiempoViaje
            else:
                record.tiempoViaje = utils.minsToMil(tiempos['tTrabajoHogar'] + tiempos['tHogarCentro'])
                return record.tiempoViaje
    else:
        if(tieneJardin and jardin  and dia in utils.getListOfDays(jardin.dias)):
            if(hora < jardin.hora_inicio):
                record.tiempoViaje = utils.minsToMil(tiempos['tHogarCentro'])
                return record.tiempoViaje
            else:
                record.tiempoViaje = utils.minsToMil(tiempos['tHogarJardin'] + tiempos['tJardinCentro'])
                return record.tiempoViaje
        else:
            record.tiempoViaje = utils.minsToMil(tiempos['tHogarCentro'])
            return record.tiempoViaje

class IndividuoTable(tables.Table):
    id              = tables.Column(accessor = 'id',verbose_name='Individuo')
    tipo_transporte = tables.Column(accessor = 'tipo_transporte',verbose_name='Tipo de Transporte')
    tieneJardin     = tables.Column(accessor = 'tieneJardin',verbose_name='Tiene Jardin')
    tieneTrabajo    = tables.Column(accessor = 'tieneTrabajo',verbose_name='Tiene Trabajo')
    prestador       = tables.Column(accessor = 'prestador.nombre',verbose_name='Prestador')
    hogar           = tables.Column(accessor = 'hogar.id',verbose_name='Hogar')
    trabajo         = tables.Column(accessor = 'trabajo.id',verbose_name='Trabajo')
    jardin          = tables.Column(accessor = 'jardin.id',verbose_name='Jardin')

    class Meta:
        model = Individuo
        per_page = 200
        attrs = {"class": "paleblue"}
        sequence = ('id', 'tipo_transporte', 'tieneJardin','tieneTrabajo', 'prestador', 'hogar', 'trabajo','jardin')

class IndividuoTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = Individuo.objects.all()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(IndividuoTableView, self).get_table()
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(IndividuoTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context
class IndividuoListView(IndividuoTableView):
    table_class = IndividuoTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = IndividuoFilter
    formhelper_class = IndHelper

class CentrosTable(tables.Table):
    sector_auto = tables.Column(accessor = 'sector_auto.shapeid', verbose_name = "Sector Auto")
    sector_caminando = tables.Column(accessor = 'sector_caminando.shapeid', verbose_name = "Sector Caminando")
    class Meta:
        model = Centro
        attrs = {"class": "paleblue"}

class CentrosTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = Centro.objects.all()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(CentrosTableView, self).get_table()
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(CentrosTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context
class CentrosListView(CentrosTableView):
    table_class = CentrosTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = CentroFilter
    formhelper_class = CenHelper

class AnclasTable(tables.Table):
    sector_auto= tables.Column(accessor = 'sector_auto.shapeid', verbose_name = "Sector Auto")
    sector_caminando = tables.Column(accessor = 'sector_caminando.shapeid', verbose_name = "Sector Caminando")
    class Meta:
        model = AnclaTemporal
        attrs = {"class": "paleblue"}

class AnclasTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = AnclaTemporal.objects.all()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(AnclasTableView, self).get_table()
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(AnclasTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context
class AnclasListView(AnclasTableView):
    table_class = AnclasTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = AnclasFilter
    formhelper_class = AncHelper

class IndividuoCentroTable(tables.Table):
    individuo = tables.Column(accessor = 'individuo.id', verbose_name = "Individuo")
    centro = tables.Column(accessor = 'centro.id_centro', verbose_name = "Centro")
    class Meta:
        model = IndividuoCentro
        attrs = {"class": "paleblue"}

class IndividuoCentroTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = IndividuoCentro.objects.all()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(IndividuoCentroTableView, self).get_table()
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(IndividuoCentroTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context
class IndividuoCentroListView(IndividuoCentroTableView):
    table_class = IndividuoCentroTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = IndividuoCentroFilter
    formhelper_class = IndCenHelper

class PediatraTable(tables.Table):
    centro = tables.Column(accessor = 'centro.id_centro', verbose_name = "Centro")
    class Meta:
        model = Pediatra
        exclude = ('id',)
        attrs = {"class": "paleblue"}

class PediatraTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = Pediatra.objects.all()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(PediatraTableView, self).get_table()
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(PediatraTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context
class PediatraListView(PediatraTableView):
    table_class = PediatraTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = PediatraFilter
    formhelper_class = PedHelper

class PrestadorTable(tables.Table):
    class Meta:
        model = Prestador
        attrs = {"class": "paleblue"}

class PrestadorTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = Prestador.objects.all()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(PrestadorTableView, self).get_table()
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(PrestadorTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context
class PrestadorListView(PrestadorTableView):
    table_class = PrestadorTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = PrestadorFilter
    formhelper_class =PresHelper
#####################################################SECTORES
class SectorAutoTable(tables.Table):
    class Meta:
        model = SectorAuto
        attrs = {"class": "paleblue"}

class SectorAutoTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = SectorAuto.objects.all()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(SectorAutoTableView, self).get_table()
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(SectorAutoTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context
class SectorAutoListView(SectorAutoTableView):
    table_class = SectorAutoTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = SectorAutoFilter
    formhelper_class = SecAutHelper
############################################
class SectorCaminandoTable(tables.Table):
    class Meta:
        model = SectorCaminando
        attrs = {"class": "paleblue"}

class SectorCaminandoTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = SectorCaminando.objects.all()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(SectorCaminandoTableView, self).get_table()
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(SectorCaminandoTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context
class SectorCaminandoListView(SectorCaminandoTableView):
    table_class = SectorCaminandoTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = SectorCaminandoFilter
    formhelper_class = SecCamHelper
#################################################################
class SectorOmnibusTable(tables.Table):
    class Meta:
        model = SectorAuto
        attrs = {"class": "paleblue"}

class SectorOmnibusTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = SectorAuto.objects.all()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(SectorOmnibusTableView, self).get_table()
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(SectorOmnibusTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context
class SectorOmnibusListView(SectorOmnibusTableView):
    table_class = SectorOmnibusTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = SectorOmnibusFilter
    formhelper_class = SecOmnHelper
###################################################################
class SectorTiempoAutoTable(tables.Table):
    sector_1 = tables.Column(accessor='sector_1.shapeid',verbose_name="Sector 1")
    sector_2 = tables.Column(accessor='sector_2.shapeid',verbose_name="Sector 2")
    tiempo = tables.Column(verbose_name = 'Tiempo (Minutos)', empty_values = ())
    distancia = tables.Column(verbose_name = 'Distancia (Metros)')
    class Meta:
        model = SectorTiempoAuto
        exclude = ('id',)
        attrs = {"class": "paleblue"}
    def render_tiempo(self,record):
        return record.tiempo/60

class SectorTiempoAutoTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = SectorTiempoAuto.objects.all()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(SectorTiempoAutoTableView, self).get_table()
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(SectorTiempoAutoTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context
class SectorTiempoAutoListView(SectorTiempoAutoTableView):
    table_class = SectorTiempoAutoTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = SectorTiempoAutoFilter
    formhelper_class = SecTieAutHelper
##################################################################
class SectorTiempoCaminandoTable(tables.Table):
    sector_1 = tables.Column(accessor='sector_1.shapeid',verbose_name="Sector 1")
    sector_2 = tables.Column(accessor='sector_2.shapeid',verbose_name="Sector 2")
    tiempo = tables.Column(verbose_name = 'Tiempo (Minutos)', empty_values = ())
    distancia = tables.Column(verbose_name = 'Distancia (Metros)')
    class Meta:
        model = SectorTiempoCaminando
        exclude = ('id',)
        attrs = {"class": "paleblue"}
    def render_tiempo(self,record):
        return math.ceil(record.tiempo/60)
class SectorTiempoCaminandoTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = SectorTiempoCaminando.objects.all()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(SectorTiempoCaminandoTableView, self).get_table()
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(SectorTiempoCaminandoTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context
class SectorTiempoCaminandoListView(SectorTiempoCaminandoTableView):
    table_class = SectorTiempoCaminandoTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = SectorTiempoCaminandoFilter
    formhelper_class = SecTieCamHelper
#########################################################
class SectorTiempoOmnibusTable(tables.Table):
    sectorO_1 = tables.Column(accessor='sector_1.shapeid',verbose_name="Sector 1")
    sectorO_2 = tables.Column(accessor='sector_2.shapeid',verbose_name="Sector 2")
    tiempo = tables.Column(verbose_name = 'Tiempo (Minutos)', empty_values = ())
    class Meta:
        model = SectorTiempoOmnibus
        exclude = ('id',)
        attrs = {"class": "paleblue"}
    def render_tiempo(self,record):
        return record.tiempo/60

class SectorTiempoOmnibusTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = SectorTiempoAuto.objects.all()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(SectorTiempoOmnibusTableView, self).get_table()
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(SectorTiempoOmnibusTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context
class SectorTiempoOmnibusListView(SectorTiempoOmnibusTableView):
    table_class = SectorTiempoOmnibusTable
    template_name = 'app/filterTable.html'
    paginate_by = 200
    filter_class = SectorTiempoOmnibusFilter
    formhelper_class = SecTieOmnHelper