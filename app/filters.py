import django_filters
from django import forms
from django.forms import widgets
from app.models import *
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
    individuo = django_filters.NumberFilter(label = 'Filtrar por Individuo', name='individuo__id')
    trabajo = django_filters.BooleanFilter(label = "Trabaja", name = "individuo__tieneTrabajo")
    jardin = django_filters.BooleanFilter(label = "Jardin", name = "individuo__tieneJardin")
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

class IndividuoFilter(django_filters.FilterSet):
    individuo = django_filters.NumberFilter(label = 'Filtrar por Individuo', name='id')
    trabajo =  django_filters.BooleanFilter(label = "Trabaja", name = "tieneTrabajo")
    jardin =  django_filters.BooleanFilter(label = "Trabaja", name = "tieneJardin")
    prestador = django_filters.filters.ModelMultipleChoiceFilter(
        name='prestador__nombre',
        to_field_name='nombre',
        label = "Prestadores",
        queryset=Prestador.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    transporte = django_filters.filters.ModelMultipleChoiceFilter(
        name='tipo_transporte',
        to_field_name='id',
        label = "Transporte",
        queryset= TipoTransporte.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    class Meta:
        model = Individuo
        fields = ['individuo', 'jardin','trabajo','prestador','transporte']

class CentroFilter(django_filters.FilterSet):
    id_centro = django_filters.NumberFilter(label = 'Filtrar por Centro', name='id_centro')
    prestador = django_filters.filters.ModelMultipleChoiceFilter(
        name='prestador__nombre',
        to_field_name='nombre',
        label = "Prestadores",
        queryset=Prestador.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    sector_auto = django_filters.CharFilter(label = "Sector Auto", name = 'sector_auto')
    sector_caminando = django_filters.CharFilter(label = "Sector Caminando", name = 'sector_caminando')
    class Meta:
        model = Individuo
        fields = ['id_centro','prestador','sector_auto','sector_caminando']
class AnclasFilter(django_filters.FilterSet):
    tipos = ( ('hogar', 'Hogar'),
              ('trabajo', 'Trabajo'),
              ('jardin', 'Jardin'),)
    id = django_filters.NumberFilter(label = 'Filtrar por Ancla id', name='id')
    tipo = django_filters.filters.MultipleChoiceFilter(label = 'Tipo del Ancla', name='tipo',choices = tipos)
    sector_auto = django_filters.CharFilter(label = "Sector Auto", name = 'sector_auto')
    sector_caminando = django_filters.CharFilter(label = "Sector Caminando", name = 'sector_caminando')
    hora_inicio = django_filters.NumberFilter(label = 'Hora inicio mayor o igual a', name='hora_inicio',lookup_expr='gte')
    hora_fin = django_filters.NumberFilter(label = 'Hora fin menor o igual a', name='hora_fin',lookup_expr='lte')
    class Meta:
        model = Individuo
        fields = ['id','tipo','sector_auto','sector_caminando','hora_inicio','hora_fin']
class IndividuoCentroFilter(django_filters.FilterSet):
    individuo = django_filters.NumberFilter(label = 'Filtrar por Individuo', name='individuo__id')
    centro = django_filters.NumberFilter(label = 'Filtrar por Centro', name = 'centro__id_centro')
    class Meta:
        model = IndividuoCentro
        fields = ['individuo', 'centro']
class PediatraFilter(django_filters.FilterSet):
    DIAS = (
    (0, 'L'),
    (1, 'M'),
    (2, 'Mi'),
    (3, 'J'),
    (4, 'V'),
    (5, 'S'),
    )
    centro = django_filters.NumberFilter(label = 'Centro', name = 'centro__id_centro')
    dia = django_filters.MultipleChoiceFilter(label = 'Filtrar por Dia', name='dia',choices = DIAS)
    hora = django_filters.RangeFilter(label = 'Filtrar Rango Horario', name = 'hora')
    cantidad_pediatras = django_filters.RangeFilter(label = 'Cantidad de Pediatras', name = 'cantidad_pediatras')

    class Meta:
        model = Pediatra
        fields = ['centro','dia','hora','cantidad_pediatras']
class PrestadorFilter(django_filters.FilterSet):
    prestador = django_filters.NumberFilter(label = 'Filtrar por id Prestador', name='id')
    class Meta:
        model = Prestador
        fields = ['prestador']
class SectorAutoFilter(django_filters.FilterSet):
    shapeid = django_filters.NumberFilter(label = 'Shape ID', name='shapeid')
    class Meta:
        model = SectorAuto
        fields = ['shapeid']
class SectorCaminandoFilter(django_filters.FilterSet):
    shapeid = django_filters.NumberFilter(label = 'Shape ID', name='shapeid')
    class Meta:
        model = SectorCaminando
        fields = ['shapeid']

class SectorOmnibusFilter(django_filters.FilterSet):
    shapeid = django_filters.NumberFilter(label = 'Shape ID', name='shapeid')
    class Meta:
        model = SectorAuto
        fields = ['shapeid']

class SectorTiempoAutoFilter(django_filters.FilterSet):
    sector_1 = django_filters.NumberFilter(label = 'Sector 1', name='sector_1__shapeid')
    sector_2 = django_filters.NumberFilter(label = 'Sector 2', name='sector_2__shapeid')
    class Meta:
        model = SectorTiempoAuto
        fields = ['sector_1','sector_2']

class SectorTiempoCaminandoFilter(django_filters.FilterSet):
    sector_1 = django_filters.NumberFilter(label = 'Sector 1', name='sector_1__shapeid')
    sector_2 = django_filters.NumberFilter(label = 'Sector 2', name='sector_2__shapeid')
    class Meta:
        model = SectorTiempoCaminando
        fields = ['sector_1','sector_2']

class SectorTiempoOmnibusFilter(django_filters.FilterSet):
    sectorO_1 = django_filters.NumberFilter(label = 'Sector 1', name='sectorO_1__shapeid')
    sectorO_2 = django_filters.NumberFilter(label = 'Sector 2', name='sectorO_2__shapeid')
    class Meta:
        model = SectorTiempoAuto
        fields = ['sectorO_1','sectorO_2']
