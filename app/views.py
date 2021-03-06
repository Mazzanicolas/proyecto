from __future__ import absolute_import, unicode_literals
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from app.tables import *
from app.models import Individuo, Settings, SectorAuto,SectorCaminando, Prestador,Centro,Pediatra,IndividuoTiempoCentro,IndividuoCentro, IndividuoCentroOptimo
import math
import shapefile
import time
import csv
from app.forms import EjecutarForm,SimularForm,EjecutarHelper,SimularHelper
from celery import result
from proyecto.celery import app
from app.checkeo_errores import *
from app.task import *
import app.utils as utils
import app.load as load
from django.contrib.sessions.models import Session
from django.http import JsonResponse, HttpResponseForbidden
import os
import zipfile
from io import BytesIO
from app.shpModule import *
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.views.generic import View
from .forms import UserForm
from  django.utils.decorators import classonlymethod
from celery.signals import task_postrun
from django.conf import settings


def initSettingsStatus():
    firstTime = list(Settings.objects.filter(setting='firstTime'))
    if(firstTime):
        return
    utils.getOrCreateSettigs('firstTime',1)
    utils.getOrCreateSettigs('currentMatrizAuto',0)
    utils.getOrCreateSettigs('totalMatrizAuto',0)
    utils.getOrCreateSettigs('statusMatrizAuto',-1)
    utils.getOrCreateSettigs('currentMatrizCaminando',0)
    utils.getOrCreateSettigs('totalMatrizCaminando',0)
    utils.getOrCreateSettigs('statusMatrizCaminando',-1)
    utils.getOrCreateSettigs('currentMatrizBus',0)
    utils.getOrCreateSettigs('totalMatrizBus',0)
    utils.getOrCreateSettigs('statusMatrizBus',-1)
    utils.getOrCreateSettigs('currentMatrizIndividuo',0)
    utils.getOrCreateSettigs('totalMatrizIndividuo',0)
    utils.getOrCreateSettigs('statusMatrizIndividuo',-1)
    utils.getOrCreateSettigs('currentMatrizCentro',0)
    utils.getOrCreateSettigs('totalMatrizCentro',0)
    utils.getOrCreateSettigs('statusMatrizCentro',-1)
    utils.getOrCreateSettigs('currentMatrizIndividuoCentro',0)
    utils.getOrCreateSettigs('totalMatrizIndividuoCentro',0)
    utils.getOrCreateSettigs('statusMatrizIndividuoCentro',-1)
    utils.getOrCreateSettigs('currentMatrizIndividuoTiempoCentro',0)
    utils.getOrCreateSettigs('totalMatrizIndividuoTiempoCentro',0)
    utils.getOrCreateSettigs('statusMatrizIndividuoTiempoCentro',-1)
    utils.getOrCreateSettigs('shapeAutoStatus',-1)
    utils.getOrCreateSettigs('shapeCaminandoStatus',-1)
    utils.getOrCreateSettigs('shapeBusStatus',-1)
    utils.getOrCreateSettigs("statusPrestador", -1);

def index(request):
    initSettingsStatus()
    if not request.user.is_authenticated:
        return redirect('login')
    if(not Settings.objects.filter(setting = "tiempoMaximo")):
        s = Settings(setting = "tiempoMaximo",value = "60")
        s.save()
    if(not Settings.objects.filter(setting = "tiempoConsulta")):
        s = Settings(setting = "tiempoConsulta",value = "30")
        s.save()
    if (not Settings.objects.filter(setting = "tiempoLlega")):
        s = Settings(setting = "tiempoLlega",value = "30")
        s.save()
    post = request.POST
    cookies = request.COOKIES
    if(cookies and 'tiempoMaximo' in cookies):
        maxT = cookies.get("tiempoMaximo")
    else:
        maxT = Settings.objects.get(setting = "tiempoMaximo").value
    if(cookies and 'tiempoConsulta' in cookies):
        consT = cookies.get("tiempoConsulta")
    else:
        consT = Settings.objects.get(setting = "tiempoConsulta").value
    if(cookies and "tiempoLlega" in cookies):
        tiempoL = cookies.get("tiempoLlega")
    else:
        tiempoL = Settings.objects.get(setting = "tiempoLlega").value
    if(post):
        tiempoMax = post.get("tiempoTransporte",None)
        tiempoCons = post.get("tiempoConsulta",None)
        tiempoLlega = post.get("tiempoLlega",None)
        radioCargado = post.get("optionsRadios",None)
        radioMatrix =  radioCargado
        if(radioCargado):
            if(radioCargado == "option1"):
                lineas = load.cargarMutualistas(request)
            elif(radioCargado == "option2"):
                lineas = load.cargarIndividuoAnclas(request)
            elif(radioMatrix == "option3"):
                lineas = load.cargarTiempos(1,request)
            elif(radioMatrix == "option4"):
                lineas = load.cargarTiempos(0,request)
            elif(radioMatrix == "option5"):
                lineas = load.cargarCentroPediatras(request)
            elif(radioMatrix == "option6"): # omnibus
                lineas = load.cargarTiemposBus(request)
            elif(radioMatrix == "option7"):
                lineas = load.cargarTiposTransporte(request)
            elif(radioMatrix == 'option10'):
                lineas = load.loadShapes(request,1)
            elif(radioMatrix == 'option11'):
                lineas = load.loadShapes(request,2)
            elif(radioMatrix == 'option12'):
                lineas = load.loadShapes(request,0)
            if lineas is not None:
                pseudo_buffer = utils.Echo()
                writer = csv.writer(pseudo_buffer)
                response = StreamingHttpResponse((writer.writerow(row) for row in lineas),
                                                 content_type="text/csv")
                response['Content-Disposition'] = 'attachment; filename="errores.csv"'
                return response
        if(tiempoMax):
            maxT = tiempoMax
        if(tiempoCons):
            consT = tiempoCons
        if(tiempoLlega):
            tiempoL = tiempoLlega
    ejecutarForm = EjecutarForm() 
    ejecutarHelper = EjecutarHelper()
    simularForm = SimularForm()
    simularHelper = SimularHelper()
    username = request.user.username
    try:
        statusAuto = int(Settings.objects.get(setting = 'shapeAutoStatus').value)
    except:
        statusAuto = -1
    try:
        statusCaminando = int(Settings.objects.get(setting = 'shapeCaminandoStatus').value)
    except:
        statusCaminando = -1
    try:
        statusBus = int(Settings.objects.get(setting = 'shapeBusStatus').value)
    except:
        statusBus = -1
    statuses = {0:int(Settings.objects.get(setting = 'statusMatrizAuto').value),                  1:int(Settings.objects.get(setting = 'statusMatrizCaminando').value), 
                2:int(Settings.objects.get(setting = 'statusMatrizBus').value),                   3:int(Settings.objects.get(setting = 'statusMatrizIndividuo').value),             
                4:int(Settings.objects.get(setting = 'statusMatrizCentro').value),                5:int(Settings.objects.get(setting = 'statusMatrizIndividuoTiempoCentro').value), 
                6:TipoTransporte.objects.count(),                                                 7:Prestador.objects.count(),
                10:statusAuto, 12:statusCaminando, 11:statusBus, 
                8:int(request.session.get('calculationStatus', -1))
        }
    
    context = {'tiempoMaximo': maxT, 'tiempoConsulta': consT,"tiempoLlega": tiempoL, 'simularForm' : simularForm,'simularHelper' : simularHelper,'ejecutarForm':ejecutarForm, 'ejecutarHelper':ejecutarHelper, 'username':username, 'statuses':statuses }
    response = render(request, 'app/index.html',context)
    response.set_cookie(key = 'tiempoMaximo',  value = maxT)
    response.set_cookie(key = 'tiempoConsulta',value = consT)
    response.set_cookie(key = 'tiempoLlega',   value = tiempoL)
    return response
 


def secureUserCreation(request):

    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden()
    if request.method == "GET":
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden()
        form =  UserForm()
        helper = UserRegistryHelper()
        return render(request, 'app/registration_form.html',{'form':form,'helper':helper})  
    
        
    if request.method == "POST":
        helper = UserRegistryHelper()
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden()       
        helper = UserRegistryHelper()
        form =  UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password  = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            user = authenticate(username=username,password=password)

            if user is not None:
                if user.is_active:
                    #login(request, user)
                    return redirect('index')
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden()
        return render(request, 'app/registration_form.html',{'form':form,'helper':helper})
    


def genShape(request):
    filenames    = generarShape(request, request.session.session_key)
    zip_subdir   = "Shapefiles"
    zip_filename = "%s.zip" % zip_subdir
    s  = BytesIO()
    zf = zipfile.ZipFile(s, "w")
    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path    = os.path.join(zip_subdir, fname)
        zf.write(fpath, zip_path)
    zf.close()
    resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp

def redirectIndex(request):
    return redirect('index')

def redirectConsulta(request):
    if not request.user.is_authenticated:
        return redirect('login')
    getReq = request.GET
    if(getReq.get('checkRango', '0') == '-1' or getReq.get('generarResumen',0) == '1'):
        return generateCsvResults(request)
    response = redirect('consultaConFiltro')
    return response


def redirectSim(request):
    if not request.user.is_authenticated:
        return redirect('login')
    getReq = request.GET
    if(getReq.get('checkRango','0') == '-1' or getReq.get('generarResumen',0) == '1'):
        return generateCsvResults(request)
    response = redirect('Simulacion')
    if(getReq.get('checkB',0) == '-1'):
        response.set_cookie(key='mutualista',value='-1')
    else:
        response.set_cookie(key='mutualista',value=int(getReq.get('prestador','-1')))
    if(getReq.get('checkM','0') == '-1'):
        response.set_cookie(key='tipoTransporte',value='-1')
    else:
        response.set_cookie(key='tipoTransporte',value=int(getReq.get('tipoTransporte','-1')))
    response.set_cookie(key='trabaja', value=int(getReq.get('anclaTra','0')))
    response.set_cookie(key='jardin', value=int(getReq.get('anclaJar','0')))
    return response


def guardarArchivo(nombre, archivo):
    with default_storage.open('tmp/'+nombre, 'wb+') as destination:
        for chunk in archivo.chunks():
            destination.write(chunk)
        csv = os.path.join(settings.MEDIA_ROOT, destination)
        return csv

def generateCsvResults(request):
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if(not utils.allLoaded() or request.session.get('calculationStatus', -1) == 0):
                return JsonResponse({'Error':"Faltan cargar matrices o se estan cargando alguna"})
            indvList,dictParam,dictSettings = utils.getIndivList_ParamDict_SettingsDict(request.GET, request.COOKIES)
            print(dictParam)
            utils.writeSettings(str(request.user.id) ,dictSettings,dictParam)
            asyncKey = delegator.apply_async(args=[request.GET,request.session.session_key,request.COOKIES,str(request.user.id)], queue = 'delegate')
            request.session['asyncKey'] = asyncKey.id
            request.session['calculationStatus'] = 0 
            response = redirect('index')
            task_postrun.connect(shutdown_worker, sender=delegator)
            return response
        else:
            return redirect('index')
            print("Did not acquire lock.")
    except:
        request.session['calculationStatus'] = -1
        print("Crash")
        return redirect('index')
    finally:
        if have_lock:
            my_lock.release()    
    
    return response

def downloadFile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    sessionKey = request.session.session_key
    userId = str(request.user.id)
    zip_subdir   = "Resultados"
    zip_filename = "%s.zip" % zip_subdir
    s  = BytesIO()
    zf = zipfile.ZipFile(s, "w",zipfile.ZIP_DEFLATED)
    if(not request.session.get('isIndividual',0) == 0):
        indvPath = settings.BASE_DIR + '/app/data/users/user'+userId+"/consultOut/"+'IndividualResult.csv'
        fdir, fname = os.path.split(indvPath)
        zip_path    = os.path.join(zip_subdir, 'Resultado individual.csv')
        zf.write(indvPath, zip_path)
    if(not request.session.get('isResumen',0) == 0):
        resumenPath = settings.BASE_DIR + '/app/data/users/user'+userId+"/consultOut/"+'ResumenResult.csv'
        fdir, fname = os.path.split(resumenPath)
        zip_path    = os.path.join(zip_subdir, 'Resumen.csv')
        zf.write(resumenPath, zip_path)
    parameterPath = settings.BASE_DIR + '/app/data/users/user'+userId+"/consultOut/"+'Parametros.txt'
    fdir, fname = os.path.split(parameterPath)
    zip_path    = os.path.join(zip_subdir, 'Parametros.txt')
    zf.write(parameterPath, zip_path)
    zf.close()
    resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp

def redirectTable(request):
    if not request.user.is_authenticated:
        return redirect('login')
    verDatos = request.GET.get('datosAVer',0)
    if(verDatos == '1'):
        response = redirect('individuosTable')
        return response
    elif(verDatos == '2'):
        response = redirect('centrosTable')
        return response
    elif(verDatos == '3'):
        response = redirect('anclasTable')
        return response
    elif(verDatos == '4'):
        response = redirect('individuoCentroTable')
        return response
    elif(verDatos == '5'):
        response = redirect('pediatrasTable')
        return response
    elif(verDatos == '6'):
        response = redirect('prestadorTable')
        return response
    elif(verDatos == '7'):
        response = redirect('sectorAutoTable')
        return response
    elif(verDatos == '8'):
        response = redirect('sectorCaminandoTable')
        return response
    elif(verDatos == '9'):
        response = redirect('sectorOmnibusTable')
        return response
    elif(verDatos == '10'):
        response = redirect('sectorTiempoAutoTable')
        return response
    elif(verDatos == '11'):
        response = redirect('sectorTiempoCaminandoTable')
        return response
    elif(verDatos == '12'):
        response = redirect('sectorTiempoOmnibusTable')
        return response
    return

def downloadShapeFile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    userId = str(request.user.id)
    path = settings.BASE_DIR + '/app/data/users/user'+userId+'/consultOut/IndividualResult'
    filenames    = generarShape(request, userId, path)
    resp = zipFile("Shapefiles",filenames)
    return resp
    #[['individuo', 'prestadorIndividuo', 'centro','prestadorCentro','tipoTransporte','dia','hora','tiempoViaje','llegaGeografico','cantidadPediatras','llega'],  ..]

def getCleanFileName(aFile):
    name = aFile.split("$")[0]
    extentsion = aFile[-4:]
    return name+extentsion

def zipFile(zip_subdir, filenames):
    zip_filename = "%s.zip" % zip_subdir
    s  = BytesIO()
    zf = zipfile.ZipFile(s, "w")
    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path    = os.path.join(zip_subdir, fname)
        zf.write(fpath, zip_path)
    zf.close()
    resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp

def shutdown_worker(**kwargs):
    raise SystemExit()

def calcularTiemposMatrixIndi(request):
    my_lock = redis.Redis().lock("Cargar")
    try:
        have_lock = my_lock.acquire(blocking=False)
        if have_lock:
            if(not (Settings.objects.get(setting = 'statusMatrizIndividuo').value == '1' and Settings.objects.get(setting = 'statusMatrizCentro').value == '1'and Settings.objects.get(setting = 'statusMatrizAuto').value == '1' and Settings.objects.get(setting = 'statusMatrizBus').value == '1'and Settings.objects.get(setting = 'statusMatrizCaminando').value == '1')):
                return redirect('index')#[["Faltan cargar matrizes o se estan cargando"]]
            progressDone  = Settings.objects.get(setting='currentMatrizIndividuoTiempoCentro')
            progressTotal = Settings.objects.get(setting='totalMatrizIndividuoTiempoCentro')
            progressDone.value  = 0.1
            progressTotal.value = Individuo.objects.count()*2
            progressDone.save()
            progressTotal.save()
            IndividuoTiempoCentro.objects.all().delete()
            IndividuoCentro.objects.all().delete()
            IndividuoCentroOptimo.objects.all().delete()
            progressStatus = Settings.objects.get(setting='statusMatrizIndividuoTiempoCentro')
            progressStatus.value = 0
            progressStatus.save()
            asyncKey = calcularTiemposMatrix.apply_async(args=[],queue = 'delegate')
            utils.getOrCreateSettigs('asyncKeyMatrizIndividuoTiempoCentro',asyncKey)
            return redirect('index')
        else:
            return JsonResponse({'Error':"Faltan cargar matrices o se estan cargando alguna"})
    except:
        utils.getOrCreateSettigs("statusMatrizIndividuoTiempoCentro", -1);    
        return JsonResponse({'Error':"Error 500"})
    finally:
        if have_lock:
            my_lock.release()
