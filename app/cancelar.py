from celery import result
from app.models import Settings
from django.shortcuts import redirect
from celery.task.control import revoke
from celery.contrib.abortable import AbortableAsyncResult


def cancelarCentro(request):
    asyncTask = result.AsyncResult(id = Settings.objects.get(setting = 'asyncKeyCentro').value)
    if(asyncTask and asyncTask.state == 'PENDING' or asyncTask.state == 'STARTED'):
        asyncTask.abort()
    else:
        status  = Settings.objects.get(setting='statusMatrizCentro')
        status.value  =  -1
        status.save()
        return
    if(request):
        return redirect('index')
    return None
    #asyncTask.revoke(terminate = True)
    #status = Settings.objects.get(setting = 'statusMatrizCentro')

def cancelarIndividuo(request):
    asyncTask = result.AsyncResult(id = Settings.objects.get(setting = 'asyncKeyIndividuo').value)
    if(asyncTask and asyncTask.state == 'PENDING' or asyncTask.state == 'STARTED'):
        asyncTask.abort()
    else:
        status  = Settings.objects.get(setting='statusMatrizIndividuo')
        status.value  =  -1
        status.save()
        return
    if(request):
        return redirect('index')
    return None
    #asyncTask.revoke(terminate = True)
    #status = Settings.objects.get(setting = 'statusMatrizIndividuo')

def cancelarAuto(request):
    
    asyncTask =  AbortableAsyncResult(id = Settings.objects.get(setting = 'asyncKeyAuto').value)
    if(asyncTask and asyncTask.state == 'PENDING' or asyncTask.state == 'STARTED'):
        asyncTask.abort()
    else:
        status  = Settings.objects.get(setting='statusMatrizAuto')
        status.value  =  -1
        status.save()
        return
    if(request):
        return redirect('index')
    return None
def cancelarCaminando(request):
    asyncTask = result.AsyncResult(id = Settings.objects.get(setting = 'asyncKeyCaminando').value)
    if(asyncTask and asyncTask.state == 'PENDING' or asyncTask.state == 'STARTED'):
        asyncTask.abort()
    else:
        status  = Settings.objects.get(setting='statusMatrizCaminando')
        status.value  =  -1
        status.save()
        return
    if(request):
        return redirect('index')
    return None
    #asyncTask.revoke(terminate = True)
    #status = Settings.objects.get(setting = 'statusMatrizCaminando')

def cancelarBus(request):
    asyncTask = result.AsyncResult(id = Settings.objects.get(setting = 'asyncKeyBus').value)
    if(asyncTask and asyncTask.state == 'PENDING' or asyncTask.state == 'STARTED'):
        asyncTask.abort()
    else:
        status  = Settings.objects.get(setting='statusMatrizBus')
        status.value  =  -1
        status.save()
        return
    if(request):
        return redirect('index')
    return None
    #asyncTask.revoke(terminate = True)
    #status = Settings.objects.get(setting = 'statusMatrizBus')

def cancelarIndividuoTiempoCentro(request):
    asyncTask = result.AsyncResult(id = Settings.objects.get(setting = 'asyncKeyIndividuosTiempoCentros').value)
    if(asyncTask and asyncTask.state == 'PENDING' or asyncTask.state == 'STARTED'):
        asyncTask.abort()
    else:
        status  = Settings.objects.get(setting='statusMatrizIndividuoTiempoCentro')
        status.value  =  -1
        status.save()
        return
    if(request):
        return redirect('index')
    return None
    #asyncTask.revoke(terminate = True)
    #status = Settings.objects.get(setting = 'statusMatrizIndividuoTiempoCentro')
