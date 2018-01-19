
import django_tables2 as tables
from .models import IndividuoTiempoCentro,IndividuoCentro, MedidasDeResumen, Settings, Prestador
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import SingleTableView
from django_tables2.export.views import ExportMixin
from crequest.middleware import CrequestMiddleware
import app.utils as utils
from app.forms import IndTieCenHelper
from app.filters import IndividuoTiempoCentroFilter
from django_tables2 import RequestConfig

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
        return self.daysList[record.dia]
    def render_llegaGeografico(self, record):
        return checkLlega(record.individuo,record.centro,record.dia,record.hora,record.tiempoViaje,record,record.individuo.tieneTrabajo,record.individuo.tieneJardin,self.tiempos)
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
        else:
            return "Bus"
    def render_tiempoViaje(self, record):
        if(self.currentUser == -1 or self.currentUser != record.individuo.id):
            self.tiempos = utils.getTiempos(record.individuo,record.centro,self.tipoTrans)
            self.currentUser =  record.individuo.id
        return calcTiempoDeViaje(record.individuo,record.centro,record.dia,record.hora,self.trabaja,self.jardin,self.tiempos,record)
    def render_llegaGeografico(self, record):
        return checkLlega(record.individuo,record.centro,record.dia,record.hora,record.tiempoViaje,record,self.trabaja,self.jardin,self.tiempos)
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
def checkLlega(individuo,centro, dia,hora,tiempoViaje,record,tieneTrabajo,tieneJardin,tiempos):
    tiempoMaximo = int(Settings.objects.get(setting = "tiempoMaximo").value)  # Cambiar(Tomar de bd)
    tiempoConsulta = int(Settings.objects.get(setting = "tiempoConsulta").value) #Cambiar(Tomar de bd)
    trabajo = individuo.trabajo
    jardin = individuo.jardin
    hogar = individuo.hogar
    horaAcumulada = hora
    if(tiempoViaje > tiempoMaximo or tiempoViaje == -1):
        record.llegaGeografico = "No"
        return "No"
    if(tieneTrabajo and trabajo and dia in utils.getListOfDays(trabajo.dias)):
        if(hora < trabajo.hora_inicio):
            horaAcumulada += tiempoConsulta
            if(tieneJardin and jardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    horaAcumulada += tiempos['tCentroJardin']
                    if(horaAcumulada <= jardin.hora_inicio):
                        horaAcumulada += tiempos['tJardinTrabajo']
                        if(horaAcumulada <= trabajo.hora_inicio):
                            record.llegaGeografico = "Si"
                            return "Si"
                else:
                    if(jardin.hora_fin + tiempos['tJardinCentro'] <= hora):
                        horaAcumulada += tiempos['tCentroHogar'] + tiempos['tHogarTrabajo']
                        if(horaAcumulada <= trabajo.hora_inicio):
                            record.llegaGeografico = "Si"
                            return "Si"
            else:
                horaAcumulada += tiempos['tCentroHogar'] + tiempos['tHogarTrabajo']
                if(horaAcumulada <= trabajo.hora_inicio):
                    record.llegaGeografico = "Si"
                    return "Si"
        else:
            if(tieneJardin and jardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    horaAcumulada += tiempoConsulta
                    horaAcumulada += tiempos['tCentroJardin']
                    if(trabajo.hora_fin + tiempos['tTrabajoHogar'] + tiempos['tHogarCentro'] <= hora and tiempos['tTrabajoHogar+horaAcumulada'] <= jardin.hora_inicio):
                        record.llegaGeografico = "Si"
                        return "Si"
                else:
                    if(trabajo.hora_fin + tiempos['tTrabajoJardin'] <= jardin.hora_fin and jardin.hora_fin + tiempos['tJardinCentro'] <= hora):
                        record.llegaGeografico = "Si"
                        return "Si"
            else:
                if(trabajo.hora_fin+ tiempos['tTrabajoHogar']+tiempos['tHogarCentro'] <= hora):
                    record.llegaGeografico = "Si"
                    return "Si"
    else:
        if(tieneJardin and jardin and dia in utils.getListOfDays(jardin.dias)):
            if(hora < jardin.hora_inicio):
                horaAcumulada += tiempoConsulta
                horaAcumulada += tiempos['tCentroJardin']
                if(horaAcumulada <= jardin.hora_inicio):
                    record.llegaGeografico = "Si"
                    return "Si"
            else:
                if(jardin.hora_fin + tiempos['tJardinCentro'] <= hora):
                    record.llegaGeografico = "Si"
                    return "Si"
        else:
            record.llegaGeografico = "Si"
            return "Si"
    record.llegaGeografico = "No"
    return "No"
def calcTiempoDeViaje(individuo,centro,dia,hora,tieneTrabajo,tieneJardin,tiempos,record):
    hogar = individuo.hogar
    trabajo = individuo.trabajo
    jardin = individuo.jardin
    if(tieneTrabajo and trabajo and hora in range(trabajo.hora_inicio,trabajo.hora_fin) or tieneJardin and jardin and hora in range(jardin.hora_inicio,jardin.hora_fin)):
        record.tiempoViaje = -1
        return record.tiempoViaje
    if(tieneTrabajo and trabajo and dia in utils.getListOfDays(trabajo.dias)):
        if(hora < trabajo.hora_inicio):
            if(tieneJardin and jardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    record.tiempoViaje = tiempos['tHogarCentro']
                    return record.tiempoViaje
                else:
                    record.tiempoViaje = tiempos['tHogarJardin'] + tiempos['tJardinCentro']
                    return record.tiempoViaje
            else:
                record.tiempoViaje = tiempos['tHogarCentro']
                return record.tiempoViaje
        else:
            if(tieneJardin and jardin and dia in utils.getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    record.tiempoViaje = tiempos['tTrabajoHogar'] + tiempos['tHogarCentro']
                    return record.tiempoViaje
                else:
                    record.tiempoViaje = tiempos['tTrabajoJardin'] + tiempos['tJardinCentro']
                    return record.tiempoViaje
            else:
                record.tiempoViaje = tiempos['tHogarCentro']
                return record.tiempoViaje
    else:
        if(tieneJardin and jardin  and dia in utils.getListOfDays(jardin.dias)):
            if(hora < jardin.hora_inicio):
                record.tiempoViaje = tiempos['tHogarCentro']
                return record.tiempoViaje
            else:
                record.tiempoViaje = tiempos['tHogarJardin'] + tiempos['tJardinCentro']
                return record.tiempoViaje
        else:
            record.tiempoViaje = tiempos['tHogarCentro']
            return record.tiempoViaje
