
import django_tables2 as tables
from .models import IndividuoTiempoCentro,IndividuoCentro, MedidasDeResumen, Settings
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin


class PersonTable(tables.Table):
    individuo = tables.Column(accessor = 'individuo.id',verbose_name='Individuo')
    centro = tables.Column(accessor='centro.id_centro',verbose_name='Centro')
    prestador = tables.Column(accessor = 'individuo.prestador.nombre', verbose_name = 'Prestador')
    tipoTransporte = tables.Column(accessor = 'individuo.tipo_transporte.nombre', verbose_name = 'Transporte')
    llegar = tables.Column(verbose_name = 'Llega', empty_values = ())
    def render_llegar(self,record):
        return record.dia
    class Meta:
        per_page = 200
        model = IndividuoTiempoCentro
        attrs = {"class": "paleblue"}
        exclude = ('id',)
class TestPersonTable(tables.Table):
    tVia = 0
    individuo = tables.Column(accessor = 'individuo.id',verbose_name='Individuo')
    centro = tables.Column(accessor='centro.id_centro',verbose_name='Centro')
    prestador = tables.Column(accessor = 'individuo.prestador.nombre', verbose_name = 'Prestador')
    tipoTransporte = tables.Column(accessor = 'individuo.tipo_transporte.nombre', verbose_name = 'Transporte')
    tiempoViaje = tables.Column(verbose_name = 'Tiempo de viaje', empty_values = ())
    llega = tables.Column(verbose_name = 'Llega', empty_values = ())
    def render_llega(self, record):
        return checkLlega(record.individuo,record.centro,record.dia,record.hora,record.tiempoViaje,record.cantidad_pediatras)
    def render_tiempoViaje(self, record):
        return calcTiempoDeViaje(record.individuo,record.centro,record.dia,record.hora)
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

def checkLlega(individuo,centro, dia,hora,tiempoViaje, cantidad_pediatras):
    tiempoViaje = calcTiempoDeViaje(individuo,centro,dia,hora)
    tiempoMaximo = int(Settings.objects.get(setting = "tiempoMaximo").value)  # Cambiar(Tomar de bd)
    tiempoConsulta = int(Settings.objects.get(setting = "tiempoConsulta").value) #Cambiar(Tomar de bd)
    trabajo = individuo.trabajo
    jardin = individuo.jardin
    hogar = individuo.hogar
    horaAcumulada = hora
    tiempos = IndividuoCentro.objects.get(individuo = individuo, centro = centro)
    if(tiempoViaje > tiempoMaximo or tiempoViaje == -1 or individuo.prestador.id == centro.prestador.id):
        return "No"
    if(trabajo and dia in getListOfDays(trabajo.dias)):
        if(hora < trabajo.hora_inicio):
            horaAcumulada += tiempoConsulta
            if(jardin and dia in getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    horaAcumulada += tiempos.tCentroJardin
                    if(horaAcumulada <= jardin.hora):
                        horaAcumulada += tiempos.tJardinTrabajo
                        if(horaAcumulada <= trabajo.hora_inicio):
                            return "Si"
                else:
                    if(jardin.hora_fin + tiempos.tJardinCentro <= hora):
                        horaAcumulada += tiempos.tCentroHogar + tiempos.tHogarTrabajo
                        if(horaAcumulada <= trabajo.hora_inicio):
                            return "Si"
            else:
                horaAcumulada += tiempos.tCentroHogar + tiempos.tHogarTrabajo
                if(horaAcumulada <= trabajo.hora_inicio):
                    return "Si"
        else:
            if(jardin and dia in getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    horaAcumulada += tiempoConsulta
                    horaAcumulada += tiempos.tCentroJardin
                    if(trabajo.hora_fin + tiempos.tTrabajoHogar + tiempos.tHogarCentro <= hora and tiempos.tTrabajoHogar+horaAcumulada <= jardin.hora_inicio):
                        return "Si"
                else:
                    if(trabajo.hora_fin + tiempos.tTrabajoJardin <= jardin.hora_fin and jardin.hora_fin + tiempos.tJardinCentro <= hora):
                        return "Si"
            else:
                if(trabajo.hora_fin+ tiempos.tTrabajoHogar+tiempos.tHogarCentro <= hora):
                    return "Si"
    else:
        if(jardin and dia in getListOfDays(jardin.dias)):
            if(hora < jardin.hora_inicio):
                horaAcumulada += tiempoConsulta
                horaAcumulada += tiempos.tCentroJardin
                if(horaAcumulada <= jardin.hora_inicio):
                    return "Si"
            else:
                if(jardin.hora_fin + tiempos.tJardinCentro <= hora):
                    return "Si"
        else:
            return "Si"
    return "No"
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
def calcTiempoDeViaje(individuo,centro,dia,hora):
    print(individuo.id)
    tieneTrabajo = individuo.tieneTrabajo
    tieneJardin = individuo.tieneJardin
    hogar = individuo.hogar
    trabajo = individuo.trabajo
    jardin = individuo.jardin
    tiempos = IndividuoCentro.objects.get(individuo = individuo,centro = centro)
    if(tieneTrabajo and hora in range(trabajo.hora_inicio,trabajo.hora_fin) or tieneJardin and hora in range(jardin.hora_inicio,jardin.hora_fin)):
        return -1
    if(tieneTrabajo and dia in getListOfDays(trabajo.dias)):
        if(hora < trabajo.hora_inicio):
            if(tieneJardin and dia in getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    return tiempos.tHogarCentro
                else:
                    return tiempos.tHogarJardin + tJardinCentro
            else:
                return tiempos.tHogarCentro
        else:
            if(tieneJardin and dia in getListOfDays(jardin.dias)):
                if(hora < jardin.hora_inicio):
                    return tiempos.tTrabajoHogar + tHogarCentro
                else:
                    return tiempos.tTrabajoJardin + tJardinCentro
            else:
                return tiempos.tHogarCentro
    else:
        if(jardin and dia in getListOfDays(jardin.dias)):
            if(hora < jardin.hora_inicio):
                return tiempos.tHogarCentro
            else:
                return tiempos.tHogarJardin + tiempos.tJardinCentro
        else:
            return tiempos.tHogarCentro
