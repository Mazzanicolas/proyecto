from django.conf.urls import url
from . import views
from . import tables
from app.forms import SuperLogin
from django.contrib.auth.views import login,logout
from django.views.generic import RedirectView

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
    url(r'^individuos/$', tables.IndividuoListView.as_view(), name='individuosTable'),
    url(r'^centros/$', tables.CentrosListView.as_view(), name='centrosTable'),
    url(r'^anclas/$', tables.AnclasListView.as_view(), name='anclasTable'),
    url(r'^IndividuosCentros/$', tables.IndividuoCentroListView.as_view(), name='individuoCentroTable'),
    url(r'^pediatras/$', tables.PediatraListView.as_view(), name='pediatrasTable'),
    url(r'^prestadores/$', tables.PrestadorListView.as_view(), name='prestadorTable'),
    url(r'^SectoresAutos/$', tables.SectorAutoListView.as_view(), name='sectorAutoTable'),
    url(r'^SectoresCaminandos/$', tables.SectorCaminandoListView.as_view(), name='sectorCaminandoTable'),
    url(r'^SectoresOmnibuss/$', tables.SectorOmnibusListView.as_view(), name='sectorOmnibusTable'),
    url(r'^SectoresTiemposAutos/$', tables.SectorTiempoAutoListView.as_view(), name='sectorTiempoAutoTable'),
    url(r'^SectoresTiemposCaminandos/$', tables.SectorTiempoCaminandoListView.as_view(), name='sectorTiempoCaminandoTable'),
    url(r'^SectoresTiemposOmnibuss/$', tables.SectorTiempoOmnibusListView.as_view(), name='sectorTiempoOmnibusTable'),
    url(r'^register/$', views.secureUserCreation, name='register'),
    url(r'^login/$', login, {'template_name':'accounts/login.html','authentication_form':SuperLogin}, name='login'),
    url(r'^logout/$', logout, {'next_page':'login'}),
    url(r'cancelarCentro/$', views.cancelarCentro, name='cancelarCentro'),
    url(r'CalculateTimeMatrix/$', views.calcularTiemposMatrix, name='calculateTimeMatrix'),
    url(r'^testing/$', views.testing, name='testing'),
    url(r'^testing/progressMatrizAuto/$', views.progressMatrizAuto, name='progressMatrizAuto'),
]
