import django_filters
from app.models import Individuo, Settings, TipoTransporte,Sector, Prestador, AnclaTemporal, SectorTiempo,Centro,Pediatra,IndividuoTiempoCentro,MedidasDeResumen

class IndividuoTiempoCentroFilter(django_filters.FilterSet):
    dia = django_filters.NumberFilter(label = 'Dia', name='dia')
    individuo = django_filters.NumberFilter(label = 'Individuo', name='individuo__id')
    centro = django_filters.NumberFilter(label = 'Centro', name = 'centro__id_centro')
    tipoTransporte = django_filters.CharFilter(label = 'Transporte', name = 'individuo__tipo_transporte__nombre')
    class Meta:
        model = IndividuoTiempoCentro
        fields = ['individuo', 'centro','dia']
