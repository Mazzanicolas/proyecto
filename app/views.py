from django.http import HttpResponse
from django.shortcuts import render
from app.models import Individuo, Settings, Prestador, AnclaTemporal, SectorTiempo,IndividuoTiempoCentro, Centro

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
    result = []
    #print([isTrabajo,isJardin,transporte,request.POST.get("checkB")])
    for dia in range(7):
        for individuo in individuos:
            if(request.POST.get("checkM") == "default"):
                transporte = individuo.tipo_transporte.id
            else:
                transporte = request.POST.get("transporteRadio")
            if (pr == 'default'):
                prest = [individuo.id_prestador]
            elif (pr == 'ignorar'):
                prest = prestadores
            else:
                prest = prestadores.filter(nombre = pr)
            anclas = AnclaTemporal.objects.filter(id_individuo = individuo.id)
            if (isTrabajo):
                trabajo = anclas.filter(tipo = 'Trabajo')
            else:
                trabajo = None
            if (isJardin):
                jardin = anclas.filter(tipo = 'Jardin')
            else:
                jardin = None
            hogar =  individuo.id_hogar
            secHogar = getSector(hogar, transporte)
            if(trabajo and isTrabajo):
                secTrabajo = getSector(trabajo.first(), transporte)
                for prestador in prest:
                    centros = Centro.objects.filter(id_prestador__id = prestador.id, dia = dia)
                    for centro in centros:
                        secCentro = getSector(centro, transporte)
                        if(centro.hora < trabajo.first().hora_inicio):
                            if(jardin and isJardin):
                                secJardin = getSector(jardin.first(),transporte)
                                tiempoViaje = calcularTiempos([secCentro.id, secJardin.id, secTrabajo])
                            else:
                                tiempoViaje = calcularTiempos([secCentro.id, secHogar.id, secTrabajo])
                            if(trabajo.first().hora_inicio >=  centro.hora +tiempoViaje + tiempoConsulta/60 and tiempoViaje < tiempoMaximo/60):
                                q = IndividuoTiempoCentro(id_individuo = individuo , id_centro = centro.id_lugar, dia = dia, hora = centro.hora ,tiempo_auto = tiempoViaje*60)
                                q.save()
                        if(centro.hora > trabajo.first().hora_fin):
                            tiempoViaje = 999999
                            if(jardin and isJardin):
                                secJardin = getSector(jardin.first().id_lugar,transporte)
                                tiempoViaje = calcularTiempos([secTrabajo.id, secJardin.id, secCentro.id])
                            else:
                                tiempoViaje = calcularTiempos([secTrabajo.id, secHogar.id, secCentro.id])
                            if(centro.hora >=  trabajo.first().hora_fin + tiempoViaje and tiempoViaje < tiempoMaximo/60):
                                q = IndividuoTiempoCentro(id_individuo = individuo , id_centro = centro.id_lugar, dia = dia, hora = centro.hora ,tiempo_auto = tiempoViaje*60)
                                q.save()
            else:
                for prestador in prest:
                    centros = Centro.objects.filter(id_prestador__id = prestador.id, dia = dia)
                    for centro in centros:
                        secCentro = getSector(centro, transporte)
                        if(isJardin and jardin):
                            tiempoViaje = 9999999
                            if(centro.hora < jardin.first().hora_inicio):
                                secJardin = getSector(jardin.first(),transporte)
                                tiempoViaje = calcularTiempos([secCentro.id, secJardin.id])
                                if(jardin.first().hora_inicio >=  centro.hora + tiempoViaje + tiempoConsulta/60 and tiempoViaje < tiempoMaximo/60):
                                    q = IndividuoTiempoCentro(id_individuo = individuo , id_centro = centro.id_lugar, dia = dia, hora = centro.hora ,tiempo_auto = tiempoViaje*60)
                                    q.save()
                            if(centro.hora > jardin.first().hora_fin):
                                secJardin = getSector(jardin.first(),transporte)
                                tiempoViaje = calcularTiempos([secJardin.id, secCentro.id])
                                if(centro.hora >=  jardin.first().hora_fin + tiempoViaje and tiempoViaje < tiempoMaximo/60):
                                    q = IndividuoTiempoCentro(id_individuo = individuo , id_centro = centro.id_lugar, dia = dia, hora = centro.hora ,tiempo_auto = tiempoViaje*60)
                                    q.save()
                        else:
                            tiempoViaje = calcularTiempos([secHogar.id, secCentro.id])
                            if(tiempoViaje < tiempoMaximo/60):
                                q = IndividuoTiempoCentro(id_individuo = individuo , id_centro = centro.id_lugar, dia = dia, hora = centro.hora ,tiempo_auto = tiempoViaje*60)
                                q.save()

    dias = ["Lunes","Martes","Miercoles", "Jueves","Viernes","Sabado","Domingo"]
    context = {'result': IndividuoTiempoCentro.objects.all(), 'dias':dias}
    return render(request, 'app/calcAll.html', context)
    return render(request, 'app/res.html')
def calcAll(request):
    IndividuoTiempoCentro.objects.all().delete()
    individuos = Individuo.objects.all()
    prestadores = Prestador.objects.all()
    result = []
    for dia in range(7):
        for individuo in individuos:
            prest = prestadores.filter(nombre = individuo.id_prestador.nombre)
            anclas = AnclaTemporal.objects.filter(id_individuo = individuo.id)
            trabajo = anclas.filter(id_lugar__id_tipoLugar__nombre = 'Trabajo')
            jardin = anclas.filter(id_lugar__id_tipoLugar__nombre = 'Jardin')
            hogar =  individuo.id_hogar
            secHogar = hogar.id_sector_aut
            if(trabajo):
                secTrabajo = trabajo.first().id_lugar.id_sector_aut
                for prestador in prest:
                    centros = LugarPrestador.objects.filter(id_prestador__id = prestador.id, dia = dia)
                    for centro in centros:
                        secCentro = centro.id_lugar.id_sector_aut
                        if(centro.hora < trabajo.first().hora_inicio):
                            if(jardin):
                                secJardin = jardin.first().id_lugar.id_sector_aut
                                tiempoViaje = calcularTiempos([secCentro.id, secJardin.id, secTrabajo])
                            else:
                                tiempoViaje = calcularTiempos([secCentro.id, secHogar.id, secTrabajo])
                            if(trabajo.first().hora_inicio >=  centro.hora +tiempoViaje + 30/60):
                                q = IndividuoTiempoCentro(id_individuo = individuo , id_centro = centro.id_lugar, dia = dia, hora = centro.hora ,tiempo_auto = tiempoViaje*60)
                                q.save()
                        if(centro.hora > trabajo.first().hora_fin):
                            tiempoViaje = 0
                            if(jardin):
                                secJardin = jardin.first().id_lugar.id_sector_aut
                                tiempoViaje = calcularTiempos([secTrabajo.id, secJardin.id, secCentro.id])
                            else:
                                tiempoViaje = calcularTiempos([secTrabajo.id, secHogar.id, secCentro.id])
                            if(centro.hora >=  trabajo.first().hora_fin + tiempoViaje):
                                q = IndividuoTiempoCentro(id_individuo = individuo , id_centro = centro.id_lugar, dia = dia, hora = centro.hora ,tiempo_auto = tiempoViaje*60)
                                q.save()
            else:
                print("Hay alguien qur no trabaja")
    context = {'result': IndividuoTiempoCentro.objects.all()}
    return render(request, 'app/calcAll.html', context)
def noLlegan(request):
    IndividuoTiempoCentro.objects.all().delete()
    individuos = Individuo.objects.all()
    prestadores = Prestador.objects.all()
    result = []
    for dia in range(7):
        for individuo in individuos:
            prest = prestadores.filter(nombre = individuo.id_prestador.nombre)
            anclas = AnclaTemporal.objects.filter(id_individuo = individuo.id)
            trabajo = anclas.filter(id_lugar__id_tipoLugar__nombre = 'Trabajo')
            jardin = anclas.filter(id_lugar__id_tipoLugar__nombre = 'Jardin')
            hogar =  individuo.id_hogar
            secHogar = hogar.id_sector_aut
            if(trabajo):
                secTrabajo = trabajo.first().id_lugar.id_sector_aut
                for prestador in prest:
                    centros = LugarPrestador.objects.filter(id_prestador__id = prestador.id, dia = dia)
                    #print(centros.count())
                    for centro in centros:
                        secCentro = centro.id_lugar.id_sector_aut
                        if(centro.hora < trabajo.first().hora_inicio):
                            if(jardin):
                                secJardin = jardin.first().id_lugar.id_sector_aut
                                tiempoHogarCentro = SectorTiempo.objects.get(sector1__id = secHogar.id, sector2__id = secCentro.id).time
                                tiempoCentroJardin = SectorTiempo.objects.get(sector1__id = secCentro.id, sector2__id = secJardin.id).time
                                tiempoJardinTrabajo = SectorTiempo.objects.get(sector1__id = secJardin.id, sector2__id = secTrabajo.id).time
                                tiempoViaje = (tiempoCentroJardin/60 + tiempoJardinTrabajo/60 + tiempoHogarCentro/60)/60
                                if(trabajo.first().hora_inicio < centro.hora + tiempoViaje + 30/60):
                                    q = IndividuoTiempoCentro(id_individuo = individuo , id_centro = centro.id_lugar, dia = dia, hora = centro.hora ,tiempo_auto = tiempoViaje*60)
                                    q.save()
                            else:
                                tiempoCentroHogar = SectorTiempo.objects.get(sector1__id = secCentro.id, sector2__id = secHogar.id).time
                                tiempoHogarTrabajo = SectorTiempo.objects.get(sector1__id = secHogar.id, sector2__id = secTrabajo.id).time
                                tiempoViaje = centro.hora + (tiempoCentroHogar/60 + tiempoHogarTrabajo/60)/60
                                #print(tiempoViaje)
                                if(trabajo.first().hora_inicio <  centro.hora + tiempoViaje + 30/60):
                                    q = IndividuoTiempoCentro(id_individuo = individuo , id_centro = centro.id_lugar, dia = dia, hora = centro.hora ,tiempo_auto = tiempoViaje*60)
                                    q.save()
                        if(centro.hora > trabajo.first().hora_fin):
                            if(jardin):
                                secJardin = jardin.first().id_lugar.id_sector_aut
                                tiempoTJ= SectorTiempo.objects.get(sector1__id = secTrabajo.id, sector2__id = secJardin.id).time
                                tiempoJC = SectorTiempo.objects.get(sector1__id = secJardin.id, sector2__id = secCentro.id).time
                                tiempoViaje = (tiempoTJ/60 + tiempoJC/60)/60
                                if(centro.hora <  trabajo.first().hora_fin + tiempoViaje):
                                    q = IndividuoTiempoCentro(id_individuo = individuo , id_centro = centro.id_lugar, dia = dia, hora = centro.hora ,tiempo_auto = tiempoViaje*60)
                                    q.save()
                            else:
                                tiempoTH= SectorTiempo.objects.get(sector1__id = secTrabajo.id, sector2__id = secHogar.id).time
                                tiempoHC = SectorTiempo.objects.get(sector1__id = secHogar.id, sector2__id = secCentro.id).time
                                tiempoViaje = (tiempoTH/60 + tiempoHC/60)/60
                                if(centro.hora < trabajo.first().hora_fin + tiempoViaje):
                                    q = IndividuoTiempoCentro(id_individuo = individuo , id_centro = centro.id_lugar, dia = dia, hora = centro.hora ,tiempo_auto = tiempoViaje*60)
                                    q.save()
            else:
                pass
                #print("XD")
    dias = ["Lunes","Martes","Miercoles", "Jueves","Viernes","Sabado","Domingo"]
    context = {'result': IndividuoTiempoCentro.objects.all(), 'dias':dias}
    return render(request, 'app/noLlegan.html', context)
def tiempo3(ancla1, ancla2, ancla3, ancla4):
    tiempoHogarCentro = SectorTiempo.objects.get(sector1__id = ancla1, sector2__id = ancla2).time
    tiempoCentroJardin = SectorTiempo.objects.get(sector1__id = ancla2, sector2__id = ancla3).time
    tiempoJardinTrabajo = SectorTiempo.objects.get(sector1__id = ancla3, sector2__id = ancla4).time
    tiempoViaje = (tiempoCentroJardin/60 + tiempoJardinTrabajo/60 + tiempoHogarCentro/60)/60
    return tiempoViaje
def calcularTiempos(anclas):
    tiempoViaje = 0
    for i in range(0,len(anclas)-1):
        tiempoViaje += (SectorTiempo.objects.get(sector1 = anclas[i], sector2 = anclas[i+1]).time)/60
    return tiempoViaje/60
def getSector(lugar, transporte):
    #print(transporte)
    if(transporte == 'auto' or transporte == 1):
        return lugar.id_sector_auto
    elif (transporte == 'caminando' or transporte == 0):
        return lugar.id_sector_caminando
    else:
        return lugar.id_sector_aut
def saveTimes(request):
    return render(request, 'app/index.html')