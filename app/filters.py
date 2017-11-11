import django_filters
from django import forms
from django.forms import widgets
from app.models import Individuo, Settings, TipoTransporte,Sector, Prestador, AnclaTemporal, SectorTiempo,Centro,Pediatra,IndividuoTiempoCentro,MedidasDeResumen

class IndividuoTiempoCentroFilter(django_filters.FilterSet):
    dia = django_filters.NumberFilter(label = 'Filtrar por Dia', name='dia')
    individuo = django_filters.NumberFilter(label = 'Filtrar por Individuo', name='individuo__id')
    centro = django_filters.NumberFilter(label = 'Filtrar por Centro', name = 'centro__id_centro')
    #tipoTransporte = django_filters.CharFilter(label = 'Transporte', name = 'individuo__tipo_transporte__nombre')
    prestador = django_filters.filters.ModelMultipleChoiceFilter(
        name='centro__prestador__nombre',
        to_field_name='nombre',
        queryset=Prestador.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    transporte = django_filters.filters.ModelMultipleChoiceFilter(
        name='individuo__tipo_transporte',
        to_field_name='id',
        label = "Transporte",
        queryset= TipoTransporte.objects.all()
    )
    class Meta:
        model = IndividuoTiempoCentro
        fields = ['individuo', 'centro','dia']
