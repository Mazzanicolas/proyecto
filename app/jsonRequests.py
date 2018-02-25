from django.http import JsonResponse
import app.utils as utils
from app.models import Settings
from django.contrib.sessions.models import Session



def progressCalculation(request):
    current = request.session.get('current',None)
    total   = request.session.get('total',None)
    status = calculatePercetage(current,total)
    data = {'progressStatus':status}
    print("C"+str(current))
    print("T"+str(total))
    print("S"+str(status))
    return JsonResponse(data)

def progressMatrizAuto(request):
    progressDone  = Settings.objects.get(setting='currentMatrizAuto')
    progressTotal = Settings.objects.get(setting='totalMatrizAuto')
    done = calculatePercetage(progressDone.value,progressTotal.value)
    data = {"progressStatus":done}
    return JsonResponse(data)

def progressMatrizCaminando(request):
    progressDone  = Settings.objects.get(setting='currentMatrizCaminando')
    progressTotal = Settings.objects.get(setting='totalMatrizCaminando')
    done = calculatePercetage(progressDone.value,progressTotal.value)
    data = {"progressStatus":done}
    return JsonResponse(data)

def progressMatrizBus(request):
    progressDone  = Settings.objects.get(setting='currentMatrizBus')
    progressTotal = Settings.objects.get(setting='totalMatrizBus')
    done = calculatePercetage(progressDone.value,progressTotal.value)
    data = {"progressStatus":done}
    return JsonResponse(data)

def progressCentro(request):
    progressDone  = Settings.objects.get(setting='currentMatrizCentro')
    progressTotal = Settings.objects.get(setting='totalMatrizCentro')
    done = calculatePercetage(progressDone.value,progressTotal.value)
    data = {"progressStatus":done}
    return JsonResponse(data)
    
def progressIndividuo(request):
    progressDone  = Settings.objects.get(setting='currentMatrizIndividuo')
    progressTotal = Settings.objects.get(setting='totalMatrizIndividuo')
    done = calculatePercetage(progressDone.value,progressTotal.value)
    data = {"progressStatus":done}
    return JsonResponse(data)

def progressIndividuoTiempoCentro(request):
    progressDone  = Settings.objects.get(setting='currentMatrizIndividuoTiempoCentro')
    progressTotal = Settings.objects.get(setting='totalMatrizIndividuoTiempoCentro')
    done = calculatePercetage(progressDone.value,progressTotal.value)
    data = {"progressStatus":done}
    return JsonResponse(data)

def calculatePercetage(lhs,rhs):
    if(float(rhs) <= 0 ):
        return 0
    return float(lhs)/float(rhs)