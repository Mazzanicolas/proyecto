from shapely.geometry import Point
from geopy.distance import vincenty
import math
import time

#http://www.montevideo.gub.uy/aquehorapasa/aquehorapasa.html

global VELOCIDAD_CAMINANDO
VELOCIDAD_CAMINANDO = 1.4 # 1.4 km/h

global TIEMPO_ESPERA
TIEMPO_ESPERA = 5*60 # 5 minutos en segundos

def translate(easting, northing, zone = 21, northernHemisphere=False):
    if not northernHemisphere:
        northing = 10000000 - northing
    a = 6378137
    e = 0.081819191
    e1sq = 0.006739497
    k0 = 0.9996
    arc = northing / k0
    mu = arc / (a * (1 - math.pow(e, 2) / 4.0 - 3 * math.pow(e, 4) / 64.0 - 5 * math.pow(e, 6) / 256.0))
    ei = (1 - math.pow((1 - e * e), (1 / 2.0))) / (1 + math.pow((1 - e * e), (1 / 2.0)))
    ca = 3 * ei / 2 - 27 * math.pow(ei, 3) / 32.0
    cb = 21 * math.pow(ei, 2) / 16 - 55 * math.pow(ei, 4) / 32
    cc = 151 * math.pow(ei, 3) / 96
    cd = 1097 * math.pow(ei, 4) / 512
    phi1 = mu + ca * math.sin(2 * mu) + cb * math.sin(4 * mu) + cc * math.sin(6 * mu) + cd * math.sin(8 * mu)
    n0 = a / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (1 / 2.0))
    r0 = a * (1 - e * e) / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (3 / 2.0))
    fact1 = n0 * math.tan(phi1) / r0
    _a1 = 500000 - easting
    dd0 = _a1 / (n0 * k0)
    fact2 = dd0 * dd0 / 2
    t0 = math.pow(math.tan(phi1), 2)
    Q0 = e1sq * math.pow(math.cos(phi1), 2)
    fact3 = (5 + 3 * t0 + 10 * Q0 - 4 * Q0 * Q0 - 9 * e1sq) * math.pow(dd0, 4) / 24
    fact4 = (61 + 90 * t0 + 298 * Q0 + 45 * t0 * t0 - 252 * e1sq - 3 * Q0 * Q0) * math.pow(dd0, 6) / 720
    lof1 = _a1 / (n0 * k0)
    lof2 = (1 + 2 * t0 + Q0) * math.pow(dd0, 3) / 6.0
    lof3 = (5 - 2 * Q0 + 28 * t0 - 3 * math.pow(Q0, 2) + 8 * e1sq + 24 * math.pow(t0, 2)) * math.pow(dd0, 5) / 120
    _a2 = (lof1 - lof2 + lof3) / math.cos(phi1)
    _a3 = _a2 * 180 / math.pi
    latitude = 180 * (phi1 - fact1 * (fact2 + fact3 + fact4)) / math.pi
    if not northernHemisphere:
        latitude = -latitude
    longitude = ((zone > 0) and (6 * zone - 183.0) or 3.0) - _a3
    return (latitude, longitude)

def get_tiempo(cod_linea,cod_variante,origen,destino,horarios,hora=0):
    #tiempo entre 2 paradas cercanas o conectadas en omnibus
    t = float('inf')
    if [cod_linea,cod_variante] in [x[:2] for x in origen.lineas]:
        ord_origen = int(list(filter(
            lambda x: x[0]==cod_linea and x[1]==cod_variante,origen.lineas))[0][2])
        ord_destino = int(list(filter(
            lambda x: x[0]==cod_linea and x[1]==cod_variante,destino.lineas))[0][2])
        if ord_origen < ord_destino:
            t_viaje_parada = 45
            for h in horarios:
                if h[0] == cod_linea and h[1] == cod_variante:
                    t_viaje_parada = int(h[2])
                    break
            #incializo el tiempo con la espera en la parada
            t_omnibus = TIEMPO_ESPERA + (ord_destino - ord_origen)*t_viaje_parada
            t = min(t,t_omnibus) #me quedo con el menor tiempo
    return t

def tiempo_caminando(origen,destino):
    origen = translate(origen[0],origen[1])
    destino = translate(destino[0],destino[1])
    km = vincenty(origen,destino).kilometers
    t = (km / VELOCIDAD_CAMINANDO) * 3600
    return t

def get_parada(lista_nodos,cod_parada):
    try:

        return [nodo for nodo in lista_nodos if nodo.cod_parada == str(cod_parada)][0]
        #index = [lista_nodos.index(nodo) for nodo in lista_nodos
        #            if nodo.cod_parada == cod_parada][0]
        #return lista_nodos[index]
    except:
        return None

def parada_mas_cercana(x,y,nodos):
    dist = float('inf')
    cod_parada = str()
    origen = translate(x,y)
    for parada in nodos:
        destino = translate(parada.coords[0],parada.coords[1])
        aux = vincenty(origen,destino).meters
        if aux < dist:
            dist = aux
            cod_parada = parada.cod_parada
    return cod_parada

class Nodo:
    def __init__(self,cod_parada,x,y):
        self.cod_parada = cod_parada
        self.coords = [float(x), float(y)]
        self.lineas = list() # cod_linea,cod_variante,ordinal
        self.adyacentes = list() # cod_parada

    def __str__(self):
        return str(self.cod_parada)

    def __repr__(self):
        return 'Parada {}'.format(self.cod_parada)

    '''
    devuelve cod_parada,x,y,lineas,adyacentes para un nodo
    '''
    def to_string(self):
        s = '{},{},{}'.format(self.cod_parada,self.coords[0],self.coords[1])
        if len(self.lineas) > 0:
            lineas = ';'.join([':'.join(linea) for linea in self.lineas])
            s += ',{}'.format(lineas)
        if len(self.adyacentes) > 0:
            adyacentes = ';'.join(
                [ady.cod_parada for ady in self.adyacentes])
            s += ',{}'.format(adyacentes)
        return s

def busqueda(cod_origen, coords_origen, cod_destino, coords_destino, nodos,horarios,hora):
    t0=time.time()
    nodo_origen = get_parada(nodos,cod_origen)
    nodo_destino = get_parada(nodos,cod_destino)
    t1 = time.time()
    print("t",t1-t0)
    if nodo_origen is nodo_destino:
        return 0 #Si las paradas origen y destino son la misma, no hay tiempo de viaje
    t_caminando = tiempo_caminando(coords_origen,coords_destino)
    if (t_caminando/60) < 30:
        return t_caminando
    #t,parada_origen,parada_destino = nodo_origen.search(nodos,nodo_destino,horarios,hora)
    t = bfs_search(nodos,nodo_origen,nodo_destino,horarios,hora)
    if t < 0:
        return t
    t_caminando_tramo1 = tiempo_caminando(coords_origen,nodo_origen.coords)
    t_caminando_tramo2 = tiempo_caminando(coords_destino,nodo_destino.coords)
    t_total = (t + t_caminando_tramo1 + t_caminando_tramo2)
    return t_total

def bfs(lista_nodos,start,goal):
    visited = set()
    queue = [(start,[start])]
    while queue:
        (nodo,path) = queue.pop(0)
        if nodo not in visited:
            for ady in (set(nodo.adyacentes) - set(path)):
                if ady.cod_parada == goal.cod_parada:
                    return path + [ady]
                else:
                    queue.append((ady,path + [ady]))
            visited.add(nodo)
    return queue

def bfs_search(lista_nodos,start,goal,horarios,hora):
    # Si existe una o mas lineas que conecten directamente el origen con el
    # destino saco el tiempo. Si no, hay un transbordo y tengo que hacer bfs
    interseccion = lambda l1,l2: [inner_list for inner_list in l1 if inner_list in l2]
    lineas_origen = [x[:2] for x in start.lineas]
    lineas = interseccion(lineas_origen,[x[:2] for x in goal.lineas])
    if lineas != list():
        t = float('inf')
        for l in lineas:
            t = min(t,get_tiempo(l[0],l[1],start,goal,horarios,hora))
        if t != float('inf'):
            return t
    path = bfs(lista_nodos,start,goal)
    if path != []:
        t = 0
        index = 0
        while index < len(path):
            nodo_a = path[index]
            lineas_a = [x[:2] for x in nodo_a.lineas]
            index += 1
            while index < len(path):
                nodo_aux = path[index]
                if interseccion(lineas_a,[x[:2] for x in nodo_aux.lineas]):
                    index += 1
                else:
                    break
            lineas = interseccion(lineas_a,[x[:2] for x in nodo_aux.lineas])
            if lineas != list():
                t_aux = float('inf')
                for l in lineas:
                    t_aux = min(t_aux,get_tiempo(l[0],l[1],nodo_a,nodo_aux,horarios,hora))
                    t += t_aux
        return t
    return -1

def cargar_nodos(file_name):
    nodos = list()
    aux = list()
    with open(file_name) as f:
        a = f.read().split('\n')[1:]
        for linea in a:
            linea = linea.split(',')
            if linea[0] not in aux: #Si no hay un nodo creado para la parada
                nodo = Nodo(linea[0],linea[-2],linea[-1]) #Codigo parada, x, y
                aux.append(linea[0])
                nodos.append(nodo)
            else:
                index = [nodos.index(nodo) for nodo in nodos
                if nodo.cod_parada == linea[0]][0]
                nodo = nodos[index]
            nodo.lineas.append([linea[1],linea[2],linea[3]]) #cod_linea, cod_variante, ordinal
    return nodos

def cargar_adyacentes(lista_nodos):
    for nodo in lista_nodos:
        adyacentes = list()
        for ady in nodo.adyacentes:
            nodo_aux = get_parada(lista_nodos,ady)
            adyacentes.append(nodo_aux)
        nodo.adyacentes = adyacentes

def save(lista_nodos,file_name):
    l = list()
    for nodo in lista_nodos:
        l.append(nodo.to_string())
    with open(file_name,'w') as f:
        f.write("CODIGO_PARADA,X,Y,LINEAS,ADYACENTES\n")
        f.write('\n'.join(l))

def load(file_name):
    with open(file_name) as f:
        a = f.read().split('\n')[1:]
    nodos = list()
    for linea in a:
        linea = linea.split(',')
        nodo = Nodo(linea[0],linea[1],linea[2])
        if len(linea) >= 4:
            lineas = linea[3].split(';')
            for l in lineas:
                nodo.lineas.append(l.split(':'))
            if len(linea) == 5:
                adyacentes = linea[4].split(';')
                for ady in adyacentes:
                    nodo.adyacentes.append(ady)
        nodos.append(nodo)
    cargar_adyacentes(nodos)
    return nodos

def get_horarios(file_name):
    with open(file_name) as f:
        horarios = f.read().split('\n')
        horarios = list(map(lambda x: x.split(','),horarios))
    return horarios

if __name__ == '__main__':
    #nodos = cargar_nodos('v_uptu_paradas.csv')
    #save(nodos,'nodos.csv')
    nodos = load('nodos.csv')
    #cargar_adyacentes2(nodos)
    horarios = get_horarios('horarios.csv')
    index_0 = [nodos.index(nodo) for nodo in nodos if nodo.cod_parada == '4836'][0] #4836
    index_1 = [nodos.index(nodo) for nodo in nodos if nodo.cod_parada == '5788'][0] #3183
    #print(bfs_search(nodos,nodos[index_0],nodos[index_1],horarios,15))
    t0 = time.time()
    a = busqueda(4836,nodos[index_0].coords,5788,nodos[index_1].coords,nodos,horarios,15)
    t1 = time.time()
    print("calc",t1-t0)
    print(a)
