from django.http import HttpResponse
from django.shortcuts import render
from app.models import Individuo, Settings, Prestador, AnclaTemporal,TipoTransporte,Sector, SectorTiempo,IndividuoTiempoCentro, Centro,Pediatra
from shapely.geometry import Polygon, Point
import shapefile
from app.omnibus import get_horarios, load_nodos, busqueda
import csv

shapeAuto = None
shapeCaminando = None
global horarios
global nodos
horarios = None
nodos = None

def index(request):
    Individuo.objects.all().delete()
    Sector.objects.all().delete()
    AnclaTemporal.objects.all().delete()
    Pediatra.objects.all().delete()
    Centro.objects.all().delete()
    TipoTransporte.objects.all().delete()
    Prestador.objects.all().delete()
    p = Prestador(11,"Medica Uruguaya")
    p.save()
    p = Prestador(2,"Asociacion Española")
    p.save()
    t =TipoTransporte(1,"Auto")
    t.save()
    t = TipoTransporte(0,"Caminando")
    t.save()
    t = TipoTransporte(2,"bus")
    t.save()
    t = TipoTransporte(3,"bus")
    t.save()
    p = Prestador(1,"ASSE")
    p.save()
    p = Prestador(3,"CASA DE GALICIA")
    p.save()
    p = Prestador(4,"CASMU")
    p.save()
    p = Prestador(5,"CIRCULO CATOLICO")
    p.save()
    p = Prestador(6,"COSEM")
    p.save()
    p = Prestador(7,"CUDAM")
    p.save()
    p = Prestador(8,"GREMCA")
    p.save()
    p = Prestador(9,"HOSPITAL BRITANICO")
    p.save()
    p = Prestador(10,"HOSPITAL EVANGELICO")
    p.save()
    p = Prestador(12,"MP")
    p.save()
    p = Prestador(13,"SMI")
    p.save()
    p = Prestador(14,"UNIVERSAL")
    p.save()
    p = Prestador(15,"NOEXISTE")
    p.save()
    cargarSectores()
    cargarIndividuoAnclas()
    cargarCentroPediatras()
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
    print("********************************************************************************************************************************************************")
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
        prest = getPrestador(request,prestadores,individuo,pr)
        transporte = getTransporte(request,individuo)
        trabajo = individuo.trabajo
        jardin = individuo.jardin
        SecHogar = getSector(individuo.hogar,transporte)
        secTrabajo = getSector(trabajo,transporte)
        secJardin = getSector(jardin,transporte)
        for prestador in prest:
            print(prestador.id)
            centros = Centro.objects.filter(prestador = prestador)
            todosPutos = Centro.objects.all()
            print(todosPutos[138].prestador.id)
            print(len(centros))
            print("Mah Nigga")
            for centro in centros:
                secCenro = getSector(centro,transporte)
                print(centro.id_centro)
                horas = Pediatra.objects.get(centro__id_centro = centro.id_centro)
                print("xDDD")
                for hora in horas:
                    if(trabajo and istrabajo):
                        if(hora.hora < trabajo.hora_inicio):
                            if(isJardin and jardin):
                                tiempoViaje = calcularTiempos([secCentro, secJardin, secTrabajo])
                            else:
                                tiempoViaje = calcularTiempos([secCentro,secHogar, secTrabajo])
                            print(tiempoViaje)
                            if(trabajo.hora_inicio >=  centro.hora +tiempoViaje + tiempoConsulta/60 and tiempoViaje < tiempoMaximo/60):
                                q = IndividuoTiempoCentro(id = individuo , id_centro = centro, dia =hora.dia, hora = hora.hora ,tiempo_auto = tiempoViaje*60)
                                q.save()
                        else:
                            if(jardin and isJardin):
                                tiempoViaje = calcularTiempos([secTrabajo, secJardin, secCentro])
                            else:
                                tiempoViaje = calcularTiempos([secTrabajo, secHogar, secCentro])
                            print(tiempoViaje)
                            if(centro.hora >=  trabajo.hora_fin + tiempoViaje and tiempoViaje < tiempoMaximo/60):
                                q = IndividuoTiempoCentro(id = individuo , id_centro = centro, dia = hora.dia, hora = hora.hora ,tiempo_auto = tiempoViaje*60)
                                q.save()
                    else:
                        if(isJardin and jardin):
                            if(centro.hora < hora_inicio):
                                tiempoViaje = calcularTiempos([secCentro, secJardin])
                                print(tiempoViaje)
                                if(jardin.hora_inicio >=  centro.hora + tiempoViaje + tiempoConsulta/60 and tiempoViaje < tiempoMaximo/60):
                                    q = IndividuoTiempoCentro(id = individuo , id_centro = centro, dia = hora.dia, hora = hora.hora ,tiempo_auto = tiempoViaje*60)
                                    q.save()
                            if(centro.hora > jardin.hora_fin):
                                tiempoViaje = calcularTiempos([secJardin, secCentro])
                                print(tiempoViaje)
                                if(centro.hora >=  jardin.hora_fin + tiempoViaje and tiempoViaje < tiempoMaximo/60):
                                    q = IndividuoTiempoCentro(id = individuo , id_centro = centro, dia = hora.dia, hora = hora.hora ,tiempo_auto = tiempoViaje*60)
                                    q.save()
                        else:
                            tiempoViaje = calcularTiempos([secHogar, secCentro])
                            print(tiempoViaje)
                            if(tiempoViaje < tiempoMaximo/60):
                                q = IndividuoTiempoCentro(id = individuo , id_centro = centro, dia = hora.dia, hora = hora.hora ,tiempo_auto = tiempoViaje*60)
                                q.save()
    print("idk")
    dias = ["Lunes","Martes","Miercoles", "Jueves","Viernes","Sabado","Domingo"]
    context = {'result': IndividuoTiempoCentro.objects.all(), 'dias':dias}
    return render(request, 'app/calcAll.html', context)
    #return render(request, 'app/res.html')

def getPrestador(request,prestadores,individuo,pr):
    if (pr == 'default'):
        prest = [individuo.prestador]
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
    if(not (transporte == "bus" or transporte == 2) ):
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
        if(transporte == 'Auto' or transporte == 1):
            return lugar.sector_auto
    elif (transporte == 'Caminando' or transporte == 0):
            return lugar.sector_caminando
    else:
        return lugar
    return None
def cargarSectores():
    sf = shapefile.Reader('app/okkk.shp')
    global shapeAuto
    shapeAuto = sf.shapes()
    global shapeCaminando
    sf = shapefile.Reader('app/shpWkng.shp')
    shapeCaminando = sf.shapes()
    for i in range(len(shapeAuto)):
        centroide = centroid(shapeAuto[i])
        sector = Sector(i,centroide.x,centroide.y,"Auto",i)
        sector.save()
    for i in range(len(shapeCaminando)):
        centroide = centroid(shapeCaminando[i])
        sector = Sector(i+len(shapeAuto),centroide.x,centroide.y,"Caminando",i)
def centroid(shape):
    poligono = Polygon(shape.points)
    if poligono.is_valid:
        return poligono.representative_point()
    else:
        return poligono.centroid
def saveTimes(request):
    return render(request, 'app/index.html')
def parsear_hora(hora):
    if(not "." in hora):
        str(float(hora))
    h,m = hora.split('.')
    return int(h.zfill(2) + m.zfill(2))

def cargarIndividuoAnclas():
    with open('app/Ejemplo datos 5oct.csv', newline='') as csvfile:
        l = csv.reader(csvfile, delimiter=',', quotechar='"')
        lineas=[]
        lineas.extend(l)
        lineas = lineas[1:] 
        idAncla = 0
        for caso in lineas:
            ## Ancla
            #Coordenada X, Coordenada Y, Tipo, Hora inicio, Hora fin, Dias, Sector auto, Sector caminando
            #Duda Tecnica -Contemplar casos donde no hay jardin y/o trabajo
            anclaJardin  = AnclaTemporal(idAncla,float(caso[10]),float(caso[11]),"jardin" ,parsear_hora(caso[7]) ,parsear_hora(caso[8]) ,caso[6] ,None,None)
            anclaJardin.sector_auto = getSectorForPoint(anclaJardin,"Auto")
            anclaJardin.sector_caminando = getSectorForPoint(anclaJardin,"Caminando")
            anclaJardin.save()
            anclaTrabajo = AnclaTemporal(idAncla,float(caso[14]),float(caso[15]),"trabajo",parsear_hora(caso[17]),parsear_hora(caso[18]),caso[16],None,None)
            anclaTrabajo.sector_auto = getSectorForPoint(anclaTrabajo,"Auto")
            anclaTrabajo.sector_caminando = getSectorForPoint(anclaTrabajo,"Caminando")
            anclaTrabajo.save()
            anclaHogar   = AnclaTemporal(idAncla,float(caso[22]),float(caso[23]),"hogar",None,None,"L-D",None,None)
            anclaHogar.sector_auto = getSectorForPoint(anclaHogar,"Auto")
            anclaHogar.sector_caminando = getSectorForPoint(anclaHogar,"Caminando")
            anclaHogar.save()
            idAncla +=1
            ## Individuo
            #Id, Tipo transporte, Prestador, Hogar, Trabajo, Jardin
            individuo  = Individuo(int(caso[0]),int(caso[19]),int(caso[1]),anclaHogar.id,anclaTrabajo.id,anclaJardin.id)
            individuo.save()

def getSectorForPoint(ancal,tipo):
    point = Point(ancal.x_coord,ancal.x_coord)
    for i in range(len(shapeAuto)):
        polygon = Polygon(shapeAuto[i].points)
        if(polygon.contains(point)):
            return Sector.objects.get(shape = i, tipo = tipo)

def cargarCentroPediatras():
    with open('app/centros.csv', newline='') as csvfile:
        l = csv.reader(csvfile, delimiter=',', quotechar='"')
        lineas=[]
        lineas.extend(l)
        lineas = lineas[1:] 
        inti = 0
        horas = ["6.0","7.0","8.0","9.0","10.0","11.0","12.0","13.0","14.0","15.0","16.0","17.0","18.0","19.0","20.0","21.0"]
        id = 0
        for caso in lineas:
        ## Centro
        #Id, Coordenada X, Coordenada Y, Sector, Direccion, Prestador
            if(caso[2]!=""):
                #int(caso[3] id para cuando sean unicas
                centro = Centro(inti,float(caso[9]),float(caso[10]),None,None,caso[7],int(caso[2]))
                centro.save()
            ## Pediatra
            #Centro, Dia, Hora, Cantidad de pediatras
            #dias = ["LUNES","MARTES","MIERCOLES","JUEVES","VIERNES","SABADO"]
                contador_dias = 11
                for i in range(5):
                    for j in horas:
                        if(contador_dias >106): ##Arreglar
                            break
                        if ((caso[contador_dias]) == ''):
                            caso[contador_dias]=0
                            pediatra = Pediatra (centro_id = inti,dia = i, hora = parsear_hora(j), cantidad_pediatras = int(caso[contador_dias]))
                            pediatra.save()
                            contador_dias +=1
                        else:
                            pediatra = Pediatra (centro_id = inti,dia = i, hora = parsear_hora(j), cantidad_pediatras = int(caso[contador_dias]))
                            contador_dias +=1
                            pediatra.save()
                inti +=1
