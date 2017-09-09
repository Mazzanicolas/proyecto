from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^calcAll/$', views.calcAll, name='calcAll'),
    url(r'^res/$', views.res, name='res'),
    url(r'^noLlegan/$', views.noLlegan, name='noLlegan'),
]
