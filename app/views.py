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
from django.shortcuts import redirect
from proyecto.celery import app
from app.checkeo_errores import *
from app.task import delegator
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
global shapeAuto
global shapeCaminando
global recordsAuto
global recordsCaminando


def progressMatrizAuto(request):
    progressDone  = Settings.objects.get(setting='currentMatrizAuto')
    progressTotal = Settings.objects.get(setting='totalMatrizAuto')
    done = calculatePercetage(progressDone.value,progressTotal.value)
    data = {"progressStatus":done}
    return JsonResponse(data)

def calculatePercetage(lhs,rhs):
    if(int(rhs) <= 0 ):
        return 0
    return int(lhs)/int(rhs)

def initSettingsStatus():
    firstTime = list(Settings.objects.filter(setting='firstTime'))
    print(bool(Settings.objects.filter(setting='firstTime')))
    if(firstTime):
        return
    utils.getOrCreateSettigs('firstTime',1)
    utils.getOrCreateSettigs('currentMatrizAuto',0)
    utils.getOrCreateSettigs('totalMatrizAuto',0)
    utils.getOrCreateSettigs('statusMatrizAuto',-1)


def testing(request):
    initSettingsStatus()
    if not request.user.is_authenticated:
        return redirect('login')
    init()
    if(not SectorAuto.objects.all() or not SectorCaminando.objects.all()):
        load.cargarSectores(shapeAuto,recordsAuto,shapeCaminando,recordsCaminando)
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
                lineas = load.cargarIndividuoAnclas(request,shapeAuto,recordsAuto, shapeCaminando,recordsCaminando)
            elif(radioMatrix == "option3"):
                lineas = load.cargarTiempos(1,request,shapeAuto,recordsAuto, shapeCaminando,recordsCaminando)
            elif(radioMatrix == "option4"):
                lineas = load.cargarTiempos(0,request,shapeAuto,recordsAuto, shapeCaminando,recordsCaminando)
            elif(radioMatrix == "option5"):
                lineas = load.cargarCentroPediatras(request,shapeAuto,recordsAuto, shapeCaminando,recordsCaminando)
            elif(radioMatrix == "option6"): # omnibus
                lineas = load.cargarTiemposBus(request)
            elif(radioMatrix == "option7"):
                lineas = load.cargarTiposTransporte(request)
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
    context = {'tiempoMaximo': maxT, 'tiempoConsulta': consT,"tiempoLlega": tiempoL, 'simularForm' : simularForm,'simularHelper' : simularHelper,'ejecutarForm':ejecutarForm, 'ejecutarHelper':ejecutarHelper, 'username':username }
    response = render(request, 'app/index.html',context)
    response.set_cookie(key = 'tiempoMaximo',  value = maxT)
    response.set_cookie(key = 'tiempoConsulta',value = consT)
    response.set_cookie(key = 'tiempoLlega',   value = tiempoL)
    return response

class UserFormView(View):
    form_class = UserForm
    template_name = 'app/registration_form.html'
    
    def get(self, request):
        if not request.user.is_authenticated and not request.user.is_superuser:
            print("orazio el kaker")
            return HttpResponseForbidden()
        form =  self.form_class(None)
        helper = UserRegistryHelper()
        return render(request, self.template_name,{'form':form,'helper':helper})  
    
    def post(self,request):
        if not request.user.is_authenticated and not request.user.is_superuser:
            print("orazio el kaker 2")
            return HttpResponseForbidden()
        form =  self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password  = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            user = authenticate(username=username,password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('index')
        if not request.user.is_authenticated and not request.user.is_superuser:
            print("orazio el kaker 3")
            return HttpResponseForbidden()
        return render(request, self.template_name,{'form':form})


sf = shapefile.Reader('app/files/shapeAuto.shp')
shapeAuto = sf.shapes()
recordsAuto = sf.records()
sf = shapefile.Reader('app/files/shapeCaminando.shp')
shapeCaminando = sf.shapes()
recordsCaminando = sf.records()

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
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden()       
        
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
                    login(request, user)
                    return redirect('index')
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden()
        return render(request, 'app/registration_form.html',{'form':form})
    

#( ͡° ͜ʖ ͡°)
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
    if(IndividuoCentro.objects.count() < Individuo.objects.count()*Centro.objects.count() and Individuo.objects.count() > 0 and
            Centro.objects.count() > 0):
        print("*****************************")
        newCalcTimes()
    getReq = request.GET
    if(getReq.get('checkRango', '0') == '-1' or getReq.get('generarResumen',0) == '1'):
        return generateCsvResults(request)
    response = redirect('consultaConFiltro')
    return response


def progress(request):
    print("PROGRESS")
    done = request.session.get('current',-1)
    total = request.session.get('total', 100)
    data = {"Done":done,"Total":total}
    return JsonResponse(data)

def cancelarConsulta(request):
    if not request.user.is_authenticated:
        return redirect('login')
    print("CANCELAR CONSULTA")
    deleteConsultaResults(request)
    return redirect('index')

def deleteConsultaResults(request):
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
    request.session['current'] = -1
    request.session.save()

def redirectSim(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if(IndividuoCentro.objects.count() < Individuo.objects.count()*Centro.objects.count() and 
            Individuo.objects.count() > 0 and Centro.objects.count() > 0):
        print("**************************************************")
        newCalcTimes()
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

def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    init()
    if(not SectorAuto.objects.all() or not SectorCaminando.objects.all()):
        load.cargarSectores(shapeAuto,recordsAuto,shapeCaminando,recordsCaminando)
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
                lineas = load.cargarIndividuoAnclas(request,shapeAuto,recordsAuto, shapeCaminando,recordsCaminando)
            elif(radioMatrix == "option3"):
                lineas = load.cargarTiempos(1,request,shapeAuto,recordsAuto, shapeCaminando,recordsCaminando)
            elif(radioMatrix == "option4"):
                lineas = load.cargarTiempos(0,request,shapeAuto,recordsAuto, shapeCaminando,recordsCaminando)
            elif(radioMatrix == "option5"):
                lineas = load.cargarCentroPediatras(request,shapeAuto,recordsAuto, shapeCaminando,recordsCaminando)
            elif(radioMatrix == "option6"): # omnibus
                lineas = load.cargarTiemposBus(request)
            elif(radioMatrix == "option7"):
                lineas = load.cargarTiposTransporte(request)
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
    context = {'tiempoMaximo': maxT, 'tiempoConsulta': consT,"tiempoLlega": tiempoL, 'simularForm' : simularForm,'simularHelper' : simularHelper,'ejecutarForm':ejecutarForm, 'ejecutarHelper':ejecutarHelper, 'username':username }
    response = render(request, 'app/index2.html',context)
    response.set_cookie(key = 'tiempoMaximo',  value = maxT)
    response.set_cookie(key = 'tiempoConsulta',value = consT)
    response.set_cookie(key = 'tiempoLlega',   value = tiempoL)
    return response

def guardarArchivo(nombre, archivo):
    with default_storage.open('tmp/'+nombre, 'wb+') as destination:
        for chunk in archivo.chunks():
            destination.write(chunk)
        csv = os.path.join(settings.MEDIA_ROOT, destination)
        return csv

def generateCsvResults(request):
    deleteConsultaResults(request)
    indvList,dictParam,dictSettings = utils.getIndivList_ParamDict_SettingsDict(request.GET, request.COOKIES)
    utils.writeSettings(request.session.session_key,dictSettings,dictParam)
    asyncKey = delegator.apply_async(args=[request.GET,request.session.session_key,request.COOKIES],queue = 'delegate')
    request.session['asyncKey'] = asyncKey.id   
    response = redirect('index')
    return response

def downloadFile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    sessionKey = request.session.session_key
    zip_subdir   = "Resultados"
    zip_filename = "%s.zip" % zip_subdir
    s  = BytesIO()
    print("Valor isIndividual es: " + str(request.session.get('isIndividual',-40)))
    print("Valor isResumen es: " + str(request.session.get('isResumen',-40)))
    zf = zipfile.ZipFile(s, "w",zipfile.ZIP_DEFLATED)
    if(not request.session.get('isIndividual',0) == 0):
        indvPath = './app/files/consultOut/IndividualResult'+sessionKey+'.csv'
        fdir, fname = os.path.split(indvPath)
        zip_path    = os.path.join(zip_subdir, 'Resultado individual.csv')
        zf.write(indvPath, zip_path)
    if(not request.session.get('isResumen',0) == 0):
        resumenPath = './app/files/consultOut/ResumenResult'+sessionKey+'.csv'
        fdir, fname = os.path.split(resumenPath)
        zip_path    = os.path.join(zip_subdir, 'Resumen.csv')
        zf.write(resumenPath, zip_path)
    parameterPath = './app/files/consultOut/Parametros'+sessionKey+'.txt'
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

    print(request.GET)
    return

def downloadShapeFile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    path = './app/files/consultOut/IndividualResult'
    filenames    = generarShape(request, request.session.session_key, path)
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
        zip_path    = os.path.join(zip_subdir, getCleanFileName(fname))
        zf.write(fpath, zip_path)
    zf.close()
    resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp

def plot(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request,'app/plot.html')

def newCalcTimes():
    tiempoMaximo   = int(Settings.objects.get(setting = "tiempoMaximo").value)  # Cambiar(Tomar de bd)
    tiempoConsulta = int(Settings.objects.get(setting = "tiempoConsulta").value) #Cambiar(Tomar de bd)
    individuos     = Individuo.objects.select_related().all()
    prestadores    = Prestador.objects.select_related().all()
    centros        = Centro.objects.select_related().all()
    pedi           = Pediatra.objects.select_related()
    for individuo in individuos:
        print(individuo.id)
        prest      = prestadores#[individuo.prestador]#arreglar
        transporte = individuo.tipo_transporte.id
        trabajo    = individuo.trabajo
        jardin     = individuo.jardin
        secHogarAuto   = utils.newGetSector(individuo.hogar,1)
        secTrabajoAuto = utils.newGetSector(trabajo,1)
        secJardinAuto  = utils.newGetSector(jardin,1)
        ######
        secHogarCaminando   = utils.newGetSector(individuo.hogar,0)
        secTrabajoCaminando = utils.newGetSector(trabajo,0)
        secJardinCaminando  = utils.newGetSector(jardin,0)
        #####
        secHogarBus   = utils.newGetSector(individuo.hogar,1)
        secTrabajoBus = utils.newGetSector(trabajo,1)
        secJardinBus  = utils.newGetSector(jardin,1)
        ####
        tHogarTrabajoAuto  = utils.calcularTiempoViaje([secHogarAuto, secTrabajoAuto],1)
        tHogarJardinAuto   =  utils.calcularTiempoViaje([secHogarAuto, secJardinAuto],1)
        tJardinTrabajoAuto = utils.calcularTiempoViaje([secJardinAuto, secTrabajoAuto],1)
        tTrabajoJardinAuto = utils.calcularTiempoViaje([secJardinAuto, secHogarAuto],1)
        tTrabajoHogarAuto  = utils.calcularTiempoViaje([secTrabajoAuto, secHogarAuto],1)
#######################
        tHogarTrabajoCaminando  = utils.calcularTiempoViaje([secHogarCaminando, secTrabajoCaminando],0)
        tHogarJardinCaminando   =  utils.calcularTiempoViaje([secHogarCaminando, secJardinCaminando],0)
        tJardinTrabajoCaminando = utils.calcularTiempoViaje([secJardinCaminando, secTrabajoCaminando],0)
        tTrabajoJardinCaminando = utils.calcularTiempoViaje([secJardinCaminando, secHogarCaminando],0)
        tTrabajoHogarCaminando  = utils.calcularTiempoViaje([secTrabajoCaminando, secHogarCaminando],0)
#######################
        tHogarTrabajoBus  = utils.calcularTiempoViaje([secHogarBus, secTrabajoBus],2)
        tHogarJardinBus   =  utils.calcularTiempoViaje([secHogarBus, secJardinBus],2)
        tJardinTrabajoBus = utils.calcularTiempoViaje([secJardinBus, secTrabajoBus],2)
        tTrabajoJardinBus = utils.calcularTiempoViaje([secJardinBus, secHogarBus],2)
        tTrabajoHogarBus  = utils.calcularTiempoViaje([secTrabajoBus, secHogarBus],2)
        tiemposCentros = []
        auxOptimo = IndividuoCentroOptimo(individuo = individuo)
        for centro in centros:
            aux = time.time()
            secCentroAuto      = utils.newGetSector(centro,1)
            secCentroCaminando = utils.newGetSector(centro,0)
            secCentroBus       = utils.newGetSector(centro,1)
            horas              = Pediatra.objects.filter(centro = centro)
            tHogarCentroAuto   = utils.calcularTiempoViaje([secHogarAuto, secCentroAuto],1)
            tJardinCentroAuto  = utils.calcularTiempoViaje([secJardinAuto, secCentroAuto],1)
            tCentroHogarAuto   = utils.calcularTiempoViaje([secCentroAuto, secHogarAuto],1)
            tCentroJardinAuto  = utils.calcularTiempoViaje([secCentroAuto, secJardinAuto],1)
####################
            tHogarCentroCaminando  = utils.calcularTiempoViaje([secHogarCaminando, secCentroCaminando],0)
            tJardinCentroCaminando = utils.calcularTiempoViaje([secJardinCaminando, secCentroCaminando],0)
            tCentroHogarCaminando  = utils.calcularTiempoViaje([secCentroCaminando, secHogarCaminando],0)
            tCentroJardinCaminando = utils.calcularTiempoViaje([secCentroCaminando, secJardinCaminando],0)
#########################
            tHogarCentroBus  = utils.calcularTiempoViaje([secHogarBus, secCentroBus],2)
            tJardinCentroBus = utils.calcularTiempoViaje([secJardinBus, secCentroBus],2)
            tCentroHogarBus  = utils.calcularTiempoViaje([secCentroBus, secHogarBus],2)
            tCentroJardinBus = utils.calcularTiempoViaje([secCentroBus, secJardinBus],2)

            listaHoras = []
            ini = time.time()
            q = IndividuoCentro(individuo          = individuo , centro = centro, tHogarTrabajoAuto = tHogarTrabajoAuto/60,
                                tHogarJardinAuto   = tHogarJardinAuto/60,tJardinTrabajoAuto  = tJardinTrabajoAuto/60,
                                tTrabajoJardinAuto = tTrabajoJardinAuto/60,tTrabajoHogarAuto = tTrabajoHogarAuto/60,
                                tHogarCentroAuto   = tHogarCentroAuto/60,tJardinCentroAuto   = tJardinCentroAuto/60,
                                tCentroHogarAuto   = tCentroHogarAuto/60,tCentroJardinAuto   = tCentroJardinAuto/60,
            tHogarTrabajoCaminando = tHogarTrabajoCaminando/60,
                                tHogarJardinCaminando   = tHogarJardinCaminando/60,tJardinTrabajoCaminando  = tJardinTrabajoCaminando/60,
                                tTrabajoJardinCaminando = tTrabajoJardinCaminando/60,tTrabajoHogarCaminando = tTrabajoHogarCaminando/60,
                                tHogarCentroCaminando   = tHogarCentroCaminando/60,tJardinCentroCaminando   = tJardinCentroCaminando/60,
                                tCentroHogarCaminando   = tCentroHogarCaminando/60,tCentroJardinCaminando   = tCentroJardinCaminando/60,
            tHogarTrabajoBus = tHogarTrabajoBus/60,
                                tHogarJardinBus   = tHogarJardinBus/60,tJardinTrabajoBus  = tJardinTrabajoBus/60,
                                tTrabajoJardinBus = tTrabajoJardinBus/60,tTrabajoHogarBus = tTrabajoHogarBus/60,
                                tHogarCentroBus   = tHogarCentroBus/60,tJardinCentroBus   = tJardinCentroBus/60,
                                tCentroHogarBus   = tCentroHogarBus/60,tCentroJardinBus   = tCentroJardinBus/60)
            tiemposCentros.append(q)
            auxOptimo = setOptimo(auxOptimo, centro, tHogarCentroAuto, tHogarCentroBus, tHogarCentroCaminando)
        IndividuoCentro.objects.bulk_create(tiemposCentros)
        auxOptimo.save()
        print("Termino el individuo: "+str(individuo.id))

def setOptimo(auxOptimo, centro, tHogarCentroAuto, tHogarCentroOmnibus, tHogarCentroCaminando):
    if(auxOptimo.centroOptimoAuto is None):
        auxOptimo.centroOptimoAuto      = centro
        auxOptimo.centroOptimoOmnibus   = centro
        auxOptimo.centroOptimoCaminando = centro
        auxOptimo.tHogarCentroAuto      = tHogarCentroAuto
        auxOptimo.tHogarCentroOmnibus   = tHogarCentroOmnibus
        auxOptimo.tHogarCentroCaminando = tHogarCentroCaminando
        return auxOptimo

    if(auxOptimo.tHogarCentroAuto  > tHogarCentroAuto):
        auxOptimo.centroOptimoAuto = centro
        auxOptimo.tHogarCentroAuto = tHogarCentroAuto

    if(auxOptimo.tHogarCentroOmnibus  > tHogarCentroOmnibus):
        auxOptimo.centroOptimoOmnibus = centro
        auxOptimo.tHogarCentroOmnibus = tHogarCentroOmnibus

    if(auxOptimo.tHogarCentroCaminando  > tHogarCentroCaminando):
        auxOptimo.centroOptimoCaminando = centro
        auxOptimo.tHogarCentroCaminando = tHogarCentroCaminando
    return auxOptimo

def init():
    if(IndividuoTiempoCentro.objects.count() < Individuo.objects.count() * Pediatra.objects.count() and Centro.objects.count() > 0 and Individuo.objects.count() > 0):
        individuos = Individuo.objects.all()
        centros = Centro.objects.all()
        for individuo in individuos:
            print("IndividuoCentro: "+str(individuo.id))
            for centro in centros:
                consultas = Pediatra.objects.filter(centro = centro)
                listaHoras = []
                for consulta in consultas:
                    q = IndividuoTiempoCentro(individuo = individuo,centro=centro,dia = consulta.dia,hora = consulta.hora,cantidad_pediatras = consulta.cantidad_pediatras)
                    listaHoras.append(q)
                IndividuoTiempoCentro.objects.bulk_create(listaHoras)
