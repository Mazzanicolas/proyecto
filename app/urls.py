from django.conf.urls import url

from . import views
from . import tables
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^consulta/$', tables.FilteredPersonListView.as_view(), name='consultaConFiltro'),
    url(r'^Simulacion/$', tables.SimPersonView.as_view(), name='Simulacion'),
    url(r'^redirectConsulta/$', views.redirectConsulta, name='redirectConsulta'),
    url(r'^redirectSim/$', views.redirectSim, name='redirectSim'),
    url(r'^progress/$', views.progress, name='progress'),
    url(r'^descargar/$', views.downloadFile, name='descargar'),
    url(r'^descargarShape/$', views.downloadShapeFile, name='descargarShape'),
    url(r'^plot/$', views.plot, name='plot'),
    url(r'^generate_shape/$', views.genShape, name='genrate_shape'),
    url(r'^redirectTable/$', views.redirectTable, name='redirectTable'),
    url(r'^individuos/$', tables.CentrosListView.as_view(), name='individuosTable'),
]
