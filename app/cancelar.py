from celery import result
from app.models import Settings
from django.shortcuts import redirect
from celery.task.control import revoke
from celery.contrib.abortable import AbortableAsyncResult


def cancelarCentro(request):
    asyncTask = result.AsyncResult(id = Settings.objects.get(setting = 'asyncKeyCentro').value)
    asyncTask.revoke(terminate = True)
    status = Settings.objects.get(setting = 'statusMatrizCentro')

def cancelarIndividuo(request):
    asyncTask = result.AsyncResult(id = Settings.objects.get(setting = 'asyncKeyIndividuo').value)
    asyncTask.revoke(terminate = True)
    status = Settings.objects.get(setting = 'statusMatrizIndividuo')

def cancelarAuto(request):
    
    asyncTask =  AbortableAsyncResult(id = Settings.objects.get(setting = 'asyncKeyAuto').value)
    asyncTask.abort()
    #asyncTask.revoke(terminate = True)
    #status = Settings.objects.get(setting = 'statusMatrizAuto')
    #revoke(Settings.objects.get(setting = 'asyncKeyAuto').value,  terminate=True)
    if(request):
        return redirect('index')
    return None
def cancelarCaminando(request):
    asyncTask = result.AsyncResult(id = Settings.objects.get(setting = 'asyncKeyCaminando').value)
    asyncTask.revoke(terminate = True)
    status = Settings.objects.get(setting = 'statusMatrizCaminando')

def cancelarBus(request):
    asyncTask = result.AsyncResult(id = Settings.objects.get(setting = 'asyncKeyBus').value)
    asyncTask.revoke(terminate = True)
    status = Settings.objects.get(setting = 'statusMatrizBus')

def cancelarIndividuoTiempoCentro(request):
    asyncTask = result.AsyncResult(id = Settings.objects.get(setting = 'asyncKeyIndividuosTiempoCentros').value)
    asyncTask.revoke(terminate = True)
    status = Settings.objects.get(setting = 'statusMatrizIndividuoTiempoCentro')
