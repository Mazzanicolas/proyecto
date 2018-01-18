from io import StringIO
import csv

def checkTiempos(tipo,request):
    errores = list()
    csvfile = request.FILES['inputFile']
    csvf = StringIO(csvfile.read().decode())
    if(tipo == 0):
        l = csv.reader(csvf, delimiter=',')
    else:
        l = csv.reader(csvf, delimiter=';')
    lineas=[]
    lineas.extend(l)
    lineas = lineas[1:]
    for caso in lineas:
        if len(caso) != 4:
            errores.append("La cantidad de columnas en la linea {} es incorrecta".format(lineas.index(caso)))
            continue
        try:
            sector1 = int(caso[0])
        except ValueError:
            errores.append("Error en el campo idOrigen de la linea {}".format(lineas.index(caso)))
        try:
            sector2 = int(caso[1])
        except ValueError:
            errores.append("Error en el campo idDestino de la linea {}".format(lineas.index(caso)))
        try:
            t = float(caso[2])
        except ValueError:
            errores.append("Error en el campo tiempo de la linea {}".format(lineas.index(caso)))
        try:
            dist = float(caso[3])
        except ValueError:
            errores.append("Error en el campo distancia de la linea {}".format(lineas.index(caso)))
    if errores == list():
        return lineas
    else:
        print('\n'.join(errores))
        return None

def checkMutualistas(request):
    errores = list()
    csvfile = request.FILES['inputFile']
    csvf = StringIO(csvfile.read().decode())
    l = csv.reader(csvf, delimiter=',', quotechar='"')
    lineas=[]
    lineas.extend(l)
    for linea in lineas:
        if len(linea) != 2:
            errores.append("La cantidad de columnas en la linea {} es incorrecta".format(lineas.index(linea)))
            continue
        try:
            id = int(linea[0])
        except ValueError:
            errores.append("Error en el campo id de la linea {}".format(lineas.index(linea)))
        try:
            name = linea[1]
        except:
            errores.append("Error en el campo nombre de la linea {}".format(lineas.index(linea)))
    if errores == list():
        return lineas
    else:
        print('\n'.join(errores))
        return None

def checkTiemposBus(request):
    errores = list()
    csvfile = request.FILES['inputFile']
    csvf = StringIO(csvfile.read().decode())
    lineas = []
    lineas.extend(csv.reader(csvf, delimiter=','))
    for i in range(len(lineas)):
        linea = lineas[i]
        if len(linea) != 1063:
            errores.append("La cantidad de columnas en la linea {} es incorrecta".format(lineas.index(linea)))
            continue
        for j in range(len(lineas[i])):
            if i != j:
                try:
                    t = float(lineas[i][j])
                except ValueError:
                    errores.append("Error en el campo {} de la linea {}".format(j,lineas.index(linea)))
    if errores == list():
        return lineas
    else:
        print('\n'.join(errores))
        return None

def checkTiposTransporte(request):
    errores = list()
    csvfile = request.FILES['inputFile']
    csvf = StringIO(csvfile.read().decode())
    l = csv.reader(csvf, delimiter=',', quotechar='"')
    lineas=[]
    lineas.extend(l)
    for linea in lineas:
        if len(linea) != 2:
            errores.append("La cantidad de columnas en la linea {} es incorrecta".format(lineas.index(linea)))
            continue
        try:
            id = int(linea[0])
        except ValueError:
            errores.append("Error en el campo id de la linea {}".format(lineas.index(linea)))
        try:
            name = linea[1]
        except:
            errores.append("Error en el campo nombre de la linea {}".format(lineas.index(linea)))
    if errores == list():
        return lineas
    else:
        print('\n'.join(errores))
        return None

def checkCentroPediatras(request,dict_prestadores):
    errores = list()

    csvfile = request.FILES['inputFile']
    csvf = StringIO(csvfile.read().decode())
    l = csv.reader(csvf, delimiter=',')
    lineas=[]
    lineas.extend(l)
    lineas = lineas[1:]
    horas = [str(float(x)) for x in range(6,22)] # ["6.0".."21.0"]
    for caso in lineas:
        if len(caso) != 101:
            errores.append("La cantidad de columnas en la linea {} es incorrecta".format(lineas.index(caso)))
        ## Centro
        try:
            id_centro = int(caso[0])
        except ValueError:
            errores.append("Error en el campo idCentro de la linea {}".format(lineas.index(caso)))
        try:
            xcoord = float(caso[3])
        except ValueError:
            errores.append("Error en el campo xcoord de la linea {}".format(lineas.index(caso)))
        try:
            ycoord = float(caso[4])
        except ValueError:
            errores.append("Error en el campo ycoord de la linea {}".format(lineas.index(caso)))
        try:
            id_prestador = dict_prestadores.get(caso[1])
        except KeyError:
            errores.append("El prestaodr {} no se encontro en la base de datos. Error en la linea {}".format(caso[1],lineas.index(caso)))
        ## Pediatra
        #Centro, Dia, Hora, Cantidad de pediatras
        contador_dias = 5
        pediatras = list()
        for i in range(6):
            for j in horas:
                if(contador_dias > len(caso)): # Nunca deberia pasar, pero supongo?
                    break
                try:
                    if ((caso[contador_dias]) == '0' or caso[contador_dias] == ''):
                        cantPediatras = 0
                    else:
                        cantPediatras = int(caso[contador_dias].rstrip('0').replace('.','')) # "10.0" -> "10." -> "10" -> 10
                except ValueError:
                    errores.append("Error en el campo {} de la linea {}".format(contador_dias,lineas.index(caso)))
                contador_dias +=1
    if errores == list():
        return lineas
    else:
        print('\n'.join(errores))
        return None

def checkIndividuoAnclas(requestf,prestadores,tipos_transporte):
    errores = list()

    csvfile = requestf.FILES['inputFile']
    csvf = StringIO(csvfile.read().decode())
    l = csv.reader(csvf, delimiter=',', quotechar='"')
    lineas=[]
    lineas.extend(l)
    lineas = lineas[1:]
    idAncla = 0
    for caso in lineas:
        #id_nino,Prestador,Direccion_Local,X_local,Y_local,Asiste_jardin,Dias_jardin,Horario_entrada_jardin,Horario_salida_jardin,Direccion_jardin,X_jardines,Y_jardines,Trabaja,Direccion_trabajo,X_trabajos,Y_trabajos,Dias_trabajo,Horario_entrada_trabajo,Horario_sa
        if(caso[5] == "1"):
            try:
                x_jardin = float(caso[10])
            except ValueError:
                errores.append("Error en el campo x_jardin de la linea {}".format(lineas.index(caso)))
            try:
                y_jardin = float(caso[11])
            except ValueError:
                errores.append("Error en el campo y_jardin de la linea {}".format(lineas.index(caso)))
            try:
                hora_inicio = parsear_hora(caso[7])
            except ValueError:
                errores.append("Error en el campo horaInicioJardin de la linea {}".format(lineas.index(caso)))
            try:
                hora_fin = parsear_hora(caso[8])
            except ValueError:
                errores.append("Error en el campo horaFinJardin de la linea {}".format(lineas.index(caso)))
            # if hora_inicio > hora_fin:
            #     errores.append("La hora inicio del jardin es mayor a la hora fin en la linea {}".format(lineas.index(caso)))
            if not parsear_dias(caso[6]):
                errores.append("Error en el campo diasJardin de la linea {}".format(lineas.index(caso)))
        if(caso[12] == "1"):
            try:
                x_trabajo = float(caso[14])
            except ValueError:
                errores.append("Error en el campo x_trabajo de la linea {}".format(lineas.index(caso)))
            try:
                y_trabajo = float(caso[15])
            except ValueError:
                errores.append("Error en el campo y_trabajo de la linea {}".format(lineas.index(caso)))
            try:
                hora_inicio = parsear_hora(caso[17])
            except ValueError:
                errores.append("Error en el campo horaInicioTrabajo de la linea {}".format(lineas.index(caso)))
            try:
                hora_fin = parsear_hora(caso[18])
            except ValueError:
                errores.append("Error en el campo horaFinTrabajo de la linea {}".format(lineas.index(caso)))
            # if hora_inicio > hora_fin:
            #     errores.append("La hora inicio del trabajo es mayor a la hora fin en la linea {}".format(lineas.index(caso)))
            if not parsear_dias(caso[16]):
                print(caso)
                errores.append("Error en el campo diasTrabajo de la linea {}".format(lineas.index(caso)))
        try:
            x_hogar = float(caso[22])
        except ValueError:
            errores.append("Error en el campo x_hogar de la linea {}".format(lineas.index(caso)))
        try:
            y_hogar = float(caso[23])
        except ValueError:
            errores.append("Error en el campo y_hogar de la linea {}".format(lineas.index(caso)))
        try:
            id = int(caso[0])
        except ValueError:
            errores.append("Error en el campo id de la linea {}".format(lienas.index(caso)))
        try:
            tipo = caso[19]
            if tipo not in tipos_transporte:
                errores.append("El tipo de transpote en la linea {} es invalido".format(lineas.index(caso)))
        except ValueError:
            errores.append("Error en el campo tipoTransporte de la linea {}".format(lineas.index(caso)))
        try:
            prestador = int(caso[1])
            if prestador not in prestadores:
                errores.append("El prestador en la linea {} es invalido".format(lineas.index(caso)))
        except ValueError:
            errores.append("Error en el campo prestador de la linea {}".format(lineas.index(caso)))
    if errores == list():
        return lineas
    else:
        print('\n'.join(errores))
        return None

def parsear_hora(hora):
    if(not "." in hora):
        return int(hora)
    h,m = hora.split('.')
    return int(h.zfill(2) + m.zfill(2))

def parsear_dias(str):
    dias_validos = ["L","M","MI","J","V","S"]
    dias = str.split('-')
    for elem in dias:
        elem = elem.split('.')
        for dia in elem:
            if dia.lstrip().rstrip() not in dias_validos:
                return False
    return True
