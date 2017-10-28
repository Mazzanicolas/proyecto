
import django_tables2 as tables
from .models import IndividuoTiempoCentro
import django_filters

class PersonTable(tables.Table):
    individuo = tables.Column(accessor = 'individuo.id',verbose_name='Individuo')
    centro = tables.Column(accessor='centro.id_centro',verbose_name='Centro')
    class Meta:
        model = IndividuoTiempoCentro
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue"}

class PersonFilter(django_filters.FilterSet):
    class Meta:
        model = IndividuoTiempoCentro
        fields = ['individuo', 'centro', 'tiempo_auto']
