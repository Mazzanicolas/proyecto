from celery import result
from app.models import Settings
from django.shortcuts import redirect
from celery.task.control import revoke
from celery.contrib.abortable import AbortableAsyncResult


def cancelarCentro(request):
    if not request.user.is_authenticated:
        return redirect('login')
    asyncTask = AbortableAsyncResult(id = Settings.objects.get(setting = 'asyncKeyCentro').value)
    if(asyncTask and asyncTask.state == 'PENDING' or asyncTask.state == 'STARTED'):
        asyncTask.abort()
    else:
        status  = Settings.objects.get(setting='statusMatrizCentro')
        status.value  =  -1
        status.save()
    if(request):
        return redirect('index')
    return None
    #asyncTask.revoke(terminate = True)
    #status = Settings.objects.get(setting = 'statusMatrizCentro')

def cancelarIndividuo(request):
    if not request.user.is_authenticated:
        return redirect('login')
    asyncTask = AbortableAsyncResult(id = Settings.objects.get(setting = 'asyncKeyIndividuo').value)
    if(asyncTask and asyncTask.state == 'PENDING' or asyncTask.state == 'STARTED'):
        asyncTask.abort()
    else:
        status  = Settings.objects.get(setting='statusMatrizIndividuo')
        status.value  =  -1
        status.save()
    if(request):
        return redirect('index')
    return None
    #asyncTask.revoke(terminate = True)
    #status = Settings.objects.get(setting = 'statusMatrizIndividuo')

def cancelarAuto(request):
    if not request.user.is_authenticated:
        return redirect('login')
    asyncTask =  AbortableAsyncResult(id = Settings.objects.get(setting = 'asyncKeyAuto').value)
    if(asyncTask and (asyncTask.state == 'PENDING' or asyncTask.state == 'STARTED')):
        asyncTask.abort()
    else:
        status  = Settings.objects.get(setting='statusMatrizAuto')
        status.value  =  -1
        status.save()
    if(request):
        return redirect('index')
def cancelarCaminando(request):
    if not request.user.is_authenticated:
        return redirect('login')
    asyncTask = AbortableAsyncResult(id = Settings.objects.get(setting = 'asyncKeyCaminando').value)
    if(asyncTask and asyncTask.state == 'PENDING' or asyncTask.state == 'STARTED'):
        asyncTask.abort()
    else:
        status  = Settings.objects.get(setting='statusMatrizCaminando')
        status.value  =  -1
        status.save()
    if(request):
        return redirect('index')
    #asyncTask.revoke(terminate = True)
    #status = Settings.objects.get(setting = 'statusMatrizCaminando')

def cancelarBus(request):
    if not request.user.is_authenticated:
        return redirect('login')
    asyncTask = AbortableAsyncResult(id = Settings.objects.get(setting = 'asyncKeyBus').value)
    if(asyncTask and asyncTask.state == 'PENDING' or asyncTask.state == 'STARTED'):
        asyncTask.abort()
    else:
        status  = Settings.objects.get(setting='statusMatrizBus')
        status.value  =  -1
        status.save()
    if(request):
        return redirect('index')
    return None
    #asyncTask.revoke(terminate = True)
    #status = Settings.objects.get(setting = 'statusMatrizBus')

def cancelarIndividuoTiempoCentro(request):
    if not request.user.is_authenticated:
        return redirect('login')
    asyncTask = AbortableAsyncResult(id = Settings.objects.get(setting = 'asyncKeyMatrizIndividuoTiempoCentro').value)
    if(asyncTask and asyncTask.state == 'PENDING' or asyncTask.state == 'STARTED'):
        asyncTask.abort()
    else:
        status  = Settings.objects.get(setting='statusMatrizIndividuoTiempoCentro')
        status.value  =  -1
        status.save()
    if(request):
        return redirect('index')
    return None
    #asyncTask.revoke(terminate = True)
    #status = Settings.objects.get(setting = 'statusMatrizIndividuoTiempoCentro')

def deleteConsultaResults(request):
    if not request.user.is_authenticated:
        return redirect('login')
    request.session['isIndividual'] = 0
    request.session['isResumen'] = 0
    asyncKey = request.session.get('asyncKey',None)
    if(asyncKey and not asyncKey == -404):
        asyncResult = result.AsyncResult(asyncKey)
        if(asyncResult):
            print(asyncResult)
            asyncResult.revoke(terminate = True)
            asyncResult.forget()
            request.session['asyncKey'] = -404
    request.session['calculationStatus'] = - 1
    request.session['current'] = -1
    request.session.save()
    return redirect('index')
def resetSettings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    Settings.objects.all().delete()
    return redirect('index')