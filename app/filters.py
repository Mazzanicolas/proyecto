import django_filters
from django import forms
from django.forms import widgets
from app.models import Individuo, Settings, TipoTransporte,Sector, Prestador, AnclaTemporal, SectorTiempo,Centro,Pediatra,IndividuoTiempoCentro,MedidasDeResumen

class IndividuoTiempoCentroFilter(django_filters.FilterSet):
    DIAS = (
    (0, 'L'),
    (1, 'M'),
    (2, 'Mi'),
    (3, 'J'),
    (4, 'V'),
    (5, 'S'),
    )
    dia = django_filters.MultipleChoiceFilter(label = 'Filtrar por Dia', name='dia',choices = DIAS)
    tiempoViaje = django_filters.NumberFilter(name='tiempoViaje',label="Tiempo de viaje maximo", lookup_expr='lte')
    individuo = django_filters.NumberFilter(label = 'Filtrar por Individuo', name='individuo__id')
    trabajo = django_filters.BooleanFilter(label = "Trabaja", name = "individuo__trabajo", lookup_expr='isnull')
    centro = django_filters.NumberFilter(label = 'Filtrar por Centro', name = 'centro__id_centro')
    ##tipoTransporte = django_filters.CharFilter(label = 'Transporte', name = 'individuo__tipo_transporte__nombre')
    hora = django_filters.RangeFilter(label = 'Filtrar Rango Horario', name = 'hora')
    prestador = django_filters.filters.ModelMultipleChoiceFilter(
        name='centro__prestador__nombre',
        to_field_name='nombre',
        label = "Prestadores",
        queryset=Prestador.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    transporte = django_filters.filters.ModelMultipleChoiceFilter(
        name='individuo__tipo_transporte',
        to_field_name='id',
        label = "Transporte",
        queryset= TipoTransporte.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    class Meta:
        model = IndividuoTiempoCentro
        fields = ['individuo', 'centro','hora','dia','trabajo','prestador','transporte','tiempoViaje']
