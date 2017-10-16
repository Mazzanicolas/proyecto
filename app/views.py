from django.http import HttpResponse
from django.shortcuts import render
from app.models import Individuo, Settings, Prestador, AnclaTemporal, SectorTiempo,IndividuoTiempoCentro, Centro
import shapely
import shapefile
from omnibus import get_horarios, load_nodos, busqueda

shapeAuto = None
shapeCaminando = None
global horarios
global nodos
horarios = None
nodos = None

def index(request):
    post = request.POST
    if(not Settings.objects.filter(setting = "tiempoMaximo")):
        s = Settings(setting = "tiempoMaximo",value = "60")
        s.save()
    if(not Settings.objects.filter(setting = "tiempoConsulta")):
        s = Settings(setting = "tiempoConsulta",value = "30")
        s.save()
    if(post):
        tiempoMax = post.get("tiempoTransporte")
        tiempoCons = post.get("tiempoConsulta")
        if(tiempoMax):
            maxT = Settings.objects.get(setting = "tiempoMaximo")
            maxT.value = tiempoMax
            maxT.save()
        if(tiempoCons):
            consT = Settings.objects.get(setting = "tiempoConsulta")
            consT.value = tiempoCons
            consT.save()
    maxT = Settings.objects.get(setting = "tiempoMaximo").value
    consT = Settings.objects.get(setting = "tiempoConsulta").value
    context = {'tiempoMaximo': maxT, 'tiempoConsulta': consT}
    return render(request, 'app/index2.html',context)
def res(request):
  isJardin = request.POST.get("anclaJar")
    isTrabajo = request.POST.get("anclaTra")
    if (request.POST.get("checkB") == 'default'):
        pr = request.POST.get("checkB")
    else:
        pr = request.POST.get("mutualistasRadio")
    tiempoMaximo = int(Settings.objects.get(setting = "tiempoMaximo").value) #Cambiar(Tomar de bd)
    tiempoConsulta = int(Settings.objects.get(setting = "tiempoConsulta").value) #Cambiar(Tomar de bd)
    #print(request.POST)
    transporte = ""
    IndividuoTiempoCentro.objects.all().delete()
    individuos = Individuo.objects.all()
    prestadores = Prestador.objects.all()
    for individuo in individuos:
        prest = getPrestador(request,prestador,individuo)
        transporte = getTransporte(request,individuo)
        trabajo = individuo.trabajo
        jardin = individuo.jardin
        SecHogar = getSector(individuo.hogar)
        secTrabajo = getSector(trabajo)
        secJardin = getSector(jardin)
        for prestador in prest:
            centros = Centro.objects.filter(prestador = prestador)
            for centro in centros:
                secCenro = getSector(centro)
                horas = Pediatra.object.get(centro = centro)
                for hora in horas:
                        if(trabajo and istrabajo):
                            if(hora.hora < trabajo.hora_inicio):
                                if(isJardin and jardin):
                                    tiempoViaje = calcularTiempos([secCentro, secJardin, secTrabajo])
                                else:
                                    tiempoViaje = calcularTiempos([secCentro,secHogar, secTrabajo])
                                if(trabajo.hora_inicio >=  centro.hora +tiempoViaje + tiempoConsulta/60 and tiempoViaje < tiempoMaximo/60):
                                    q = IndividuoTiempoCentro(id = individuo , id_centro = centro, dia =hora.dia, hora = hora.hora ,tiempo_auto = tiempoViaje*60)
                                    q.save()
                            else:
                                if(jardin and isJardin):
                                    tiempoViaje = calcularTiempos([secTrabajo, secJardin, secCentro])
                                else:
                                    tiempoViaje = calcularTiempos([secTrabajo, secHogar, secCentro])
                                if(centro.hora >=  trabajo.hora_fin + tiempoViaje and tiempoViaje < tiempoMaximo/60):
                                    q = IndividuoTiempoCentro(id = individuo , id_centro = centro, dia = hora.dia, hora = hora.hora ,tiempo_auto = tiempoViaje*60)
                                    q.save()
                        else:
                            if(isJardin and jardin):
                                if(centro.hora < hora_inicio):
                                    tiempoViaje = calcularTiempos([secCentro, secJardin])
                                    if(jardin.hora_inicio >=  centro.hora + tiempoViaje + tiempoConsulta/60 and tiempoViaje < tiempoMaximo/60):
                                        q = IndividuoTiempoCentro(id = individuo , id_centro = centro, dia = hora.dia, hora = hora.hora ,tiempo_auto = tiempoViaje*60)
                                        q.save()
                                if(centro.hora > jardin.hora_fin):
                                    tiempoViaje = calcularTiempos([secJardin, secCentro])
                                    if(centro.hora >=  jardin.hora_fin + tiempoViaje and tiempoViaje < tiempoMaximo/60):
                                        q = IndividuoTiempoCentro(id = individuo , id_centro = centro, dia = hora.dia, hora = hora.hora ,tiempo_auto = tiempoViaje*60)
                                        q.save()
                            else:
                                tiempoViaje = calcularTiempos([secHogar, secCentro])
                                if(tiempoViaje < tiempoMaximo/60):
                                    q = IndividuoTiempoCentro(id = individuo , id_centro = centro, dia = hora.dia, hora = hora.hora ,tiempo_auto = tiempoViaje*60)
                                    q.save()
    dias = ["Lunes","Martes","Miercoles", "Jueves","Viernes","Sabado","Domingo"]
    context = {'result': IndividuoTiempoCentro.objects.all(), 'dias':dias}
    return render(request, 'app/calcAll.html', context)
    #return render(request, 'app/res.html')

def getPrestador(request,prestadores,individuo):
    if (pr == 'default'):
        prest = [individuo.id_prestador]
    elif (pr == 'ignorar'):
        prest = prestadores
    else:
        prest = prestadores.filter(nombre = pr)
    return prest
def getTransporte(request,individuo):
    if(request.POST.get("checkM") == "default"):
        transporte = individuo.tipo_transporte.id
    else:
        transporte = request.POST.get("transporteRadio")
    return transporte
def calcularTiempos(anclas,transporte,nodos,horarios,hora):
    tiempoViaje = 0
    if(not (transporte = "bus" or transporte = 2) ):
        for i in range(0,len(anclas)-1):
            tiempoViaje += (SectorTiempo.objects.get(sector1 = anclas[i], sector2 = anclas[i+1]).time)/60
    else:
        horarios = get_horarios('omnibus/horarios.csv') if horarios is None else horarios
        nodos = load_nodos('omnibus/nodos.csv') if nodos is None else nodos
        for i in range(0,len(anclas)-1):
            coords_origen = (anclas[i].x_coord,anclas[i].y_coord)
            coords_destino = (anclas[i+1].x_coord,anclas[i+1].y_coord)
            tiempoViaje += busqueda(ancals[i],anclas[i+1],nodos,horarios,hora)
    return tiempoViaje/60
def getSector(lugar, transporte):
    #print(transporte)
    if(lugar):
        if(transporte == 'auto' or transporte == 1):
            return lugar.id_sector_auto
        elif (transporte == 'caminando' or transporte == 0):
            return lugar.id_sector_caminando
        else:
            return lugar
    return None
def cargarSectores():
    sf = shapefile.Reader('okkk.shp')
    global shapesAuto = sf.shapes()
    sf = shapefile.Reader('okkk.shp')
    global shapesCaminando = sf.shapes()
    for i in len(shapesAuto):
        centroide = centroid(shapesAuto[i])
        sector = Sector(centroide.x,centroide.y,"Auto",i)
        sector.save()
    for i in len(shapeCaminando):
        centroide = centroid(shapesCaminando[i])
        sector = Sector(centroid.x,centroid.y,"Caminando",i+(len(shapesAuto)))

def centroid(shape):
        poligono = Polygon(shape.points)
        if poligono.is_valid:
            return poligono.representative_point()
        else:
            return poligono.centroid



def saveTimes(request):
    return render(request, 'app/index.html')
