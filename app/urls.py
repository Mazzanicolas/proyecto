from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^consulta/$', views.FilteredPersonListView.as_view(), name='consultaConFiltro'),
    url(r'^resumen/$', views.resumenConFiltroOSinFiltroPeroNingunoDeLosDos, name='resumen'),
]
