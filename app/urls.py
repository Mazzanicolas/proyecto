from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^consulta/$', views.FilteredPersonListView.as_view(), name='consultaConFiltro'),
    url(r'^Simulacion/$', views.SimPersonView.as_view(), name='Simulacion'),
    url(r'^resumen/$', views.resumenConFiltroOSinFiltroPeroNingunoDeLosDos, name='resumen'),
    url(r'^test/$', views.test, name='test'),
    url(r'^redirectSim/$', views.redirectSim, name='redirectSim'),
    url(r'^leTest/$', views.consultaToCSV, name='leTest'),
]
