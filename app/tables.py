
import django_tables2 as tables
from .models import IndividuoTiempoCentro, MedidasDeResumen, Settings
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin


class PersonTable(tables.Table):
    individuo = tables.Column(accessor = 'individuo.id',verbose_name='Individuo')
    centro = tables.Column(accessor='centro.id_centro',verbose_name='Centro')
    prestador = tables.Column(accessor = 'individuo.prestador.nombre', verbose_name = 'Prestador')
    tipoTransporte = tables.Column(accessor = 'individuo.tipo_transporte.nombre', verbose_name = 'Transporte')
    llegar = tables.Column(verbose_name = 'WEW', empty_values = ())
    def render_llegar(self,record):
        return record.dia
    class Meta:
        per_page = 200
        model = IndividuoTiempoCentro
        attrs = {"class": "paleblue"}
        exclude = ('id',)
class TestPersonTable(tables.Table):
    individuo = tables.Column(accessor = 'individuo.id',verbose_name='Individuo')
    centro = tables.Column(accessor='centro.id_centro',verbose_name='Centro')
    prestador = tables.Column(accessor = 'individuo.prestador.nombre', verbose_name = 'Prestador')
    tipoTransporte = tables.Column(accessor = 'individuo.tipo_transporte.nombre', verbose_name = 'Transporte')
    llega = tables.Column(empty_values = ())
    def render_llega(self, record):
        return plsWhy(record.individuo,record.dia,record.hora,record.tiempoViaje,record.cantidad_pediatras)
    class Meta:
        per_page = 200
        model = IndividuoTiempoCentro
        attrs = {"class": "paleblue"}
        exclude = ('id',)
        sequence = ('individuo', 'prestador', 'centro','tipoTransporte','dia','hora','tiempoViaje','llega',)
class ResumenTable(tables.Table):
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
def plsWhy(individuo,dia,hora,tiempoViaje, cantidad_pediatras):
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
