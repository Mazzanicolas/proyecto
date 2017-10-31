
import django_tables2 as tables
from .models import IndividuoTiempoCentro, MedidasDeResumen
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin


class PersonTable(tables.Table):
    individuo = tables.Column(accessor = 'individuo.id',verbose_name='Individuo')
    centro = tables.Column(accessor='centro.id_centro',verbose_name='Centro')
    prestador = tables.Column(accessor = 'individuo.prestador.nombre', verbose_name = 'Prestador')
    tipoTransporte = tables.Column(accessor = 'individuo.tipo_transporte.nombre', verbose_name = 'Transporte')
    class Meta:
        per_page = 200
        model = IndividuoTiempoCentro
        attrs = {"class": "paleblue"}
        exclude = ('id',)

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
