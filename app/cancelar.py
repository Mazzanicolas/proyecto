from celery import result
from app.models import Settings

def cancelarCentro(request):
    asyncTask = result.AsyncResult(id = Setting.objects.get(key = 'AsyncKeyCentro'))
    asyncTask.revoke(terminate = True)

def cancelarIndividuo(request):
    asyncTask = result.AsyncResult(id = Setting.objects.get(key = 'AsyncKeyIndividuo'))
    asyncTask.revoke(terminate = True)

def cancelarAuto(request):
    asyncTask = result.AsyncResult(id = Setting.objects.get(key = 'AsyncKeyAutos'))
    asyncTask.revoke(terminate = True)

def cancelarCaminando(request):
    asyncTask = result.AsyncResult(id = Setting.objects.get(key = 'AsyncKeyCaminando'))
    asyncTask.revoke(terminate = True)

def cancelarBus(request):
    asyncTask = result.AsyncResult(id = Setting.objects.get(key = 'AsyncKeyBus'))
    asyncTask.revoke(terminate = True)

def cancelarIndividuoTiempoCentro(request):
    asyncTask = result.AsyncResult(id = Setting.objects.get(key = 'AsyncKeyIndividuosTiempoCentros'))
    asyncTask.revoke(terminate = True)
