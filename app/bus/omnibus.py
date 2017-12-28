from shapely.geometry import Point
from geopy.distance import vincenty
from queue import PriorityQueue
import math
import time

#http://www.montevideo.gub.uy/aquehorapasa/aquehorapasa.html

global VELOCIDAD_CAMINANDO
VELOCIDAD_CAMINANDO = 5/3600 # 5km/h en segundos

global newVELOCIDAD_CAMINANDO
newVELOCIDAD_CAMINANDO = 5000/60 # 5000 metros en 60 minutos

global TIEMPO_ESPERA
TIEMPO_ESPERA = 5*60 # 5 minutos en segundos

global TIEMPO_VIAJE
TIEMPO_VIAJE = 45 # 45 segundos entre paradas

global RADIO_CERCANO
RADIO_CERCANO = 500 # distancia maxima en metros para que dos paradas se consideren cercanas

global TIEMPO_CAMBIO_PARADA
TIEMPO_CAMBIO_PARADA = (RADIO_CERCANO / 2) * (1 / newVELOCIDAD_CAMINANDO) # Regla de 3 para sacar el tiempo caminando promedio entre dos paradas cercanas
                                                                          # con los valores por defecto es 3 minutos.

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
    t = list()
    if [cod_linea,cod_variante] in [x[:2] for x in origen.lineas]:
        ord_origen = int(list(filter(
            lambda x: x[0]==cod_linea and x[1]==cod_variante,origen.lineas))[0][2])
        ord_destino = int(list(filter(
            lambda x: x[0]==cod_linea and x[1]==cod_variante,destino.lineas))[0][2])
        if ord_origen < ord_destino:
            t = [1,ord_destino - ord_origen,0]
    return t

'''
tiempo caminando desde el origen hasta el destino, a partir de coordenadas x,y
'''
def tiempo_caminando(origen,destino):
    origen = translate(origen[0],origen[1])
    destino = translate(destino[0],destino[1])
    km = vincenty(origen,destino).kilometers
    return (km / VELOCIDAD_CAMINANDO)

'''
busca un nodo de la lista a partir del codigo parada
'''
def get_parada(lista_nodos,cod_parada):
    cod_parada = str(cod_parada)
    for nodo in lista_nodos:
        if nodo.cod_parada == cod_parada:
            return nodo
    return None

'''
devuelve el codigo de la parada mas cercana a un par de coordenadas x,y
'''
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
        self.adyacentes = set() # cod_parada
        self.cercanos = set()

    def __str__(self):
        return str(self.cod_parada)

    def __repr__(self):
        return 'Parada {}'.format(self.cod_parada)

    def __lt__(a,b):
        return a

    # devuelve cod_parada,x,y,lineas,adyacentes para un nodo
    def to_string(self):
        s = '{},{},{}'.format(self.cod_parada,self.coords[0],self.coords[1])
        if len(self.lineas) > 0:
            lineas = ';'.join([':'.join(linea) for linea in self.lineas])
            s += ',{}'.format(lineas)
        if len(self.adyacentes) > 0:
            adyacentes = ';'.join(
                [ady.cod_parada for ady in self.adyacentes])
            s += ',{}'.format(adyacentes)
        if len(self.cercanos) > 0:
            cercanos = ';'.join(
                [cer.cod_parada for cer in self.cercanos])
            s += ',{}'.format(cercanos)
        return s

    # busca los nodos que esten a menos de 500m
    def cargar_nodos_cercanos(self,lista_nodos):
        cercanos = list()
        origen = translate(self.coords[0],self.coords[1])
        for nodo in lista_nodos:
            destino = translate(nodo.coords[0],nodo.coords[1])
            if vincenty(origen,destino).meters <= RADIO_CERCANO:
                cercanos.append(nodo)
        self.cercanos = cercanos

def busqueda(nodo_origen, coords_origen, nodo_destino, coords_destino, nodos,horarios,hora):
    if nodo_origen is nodo_destino:
        return -2 #Si las paradas origen y destino son la misma, no hay tiempo de viaje
    # t = float('inf')
    # parada_origen = nodo_origen
    # print(len(nodo_origen.cercanos))
    # for parada in nodo_origen.cercanos:
    #     search_res = bfs_search(nodos,parada,nodo_destino,horarios,hora)
    #     caminando = tiempo_caminando(parada.coords,nodo_origen.coords)
    #     # search_res = a_star_search(parada,nodo_destino,nodos,horarios)
    #     aux = search_res + caminando
    #     print(parada,search_res,caminando)
    #     if aux < t:
    #         parada_origen = parada
    #         t = aux
    t = bfs_search(nodos,nodo_origen,nodo_destino,horarios,hora)
    # return t
    if t == list():
        return -1
    else:
        return t[0]*TIEMPO_ESPERA + t[1]*TIEMPO_VIAJE + t[2]*TIEMPO_CAMBIO_PARADA
    # if t < 0 :
    #     return t
    # elif t == float('inf'):
    #     print("????",nodo_origen,nodo_destino)
    #     return -1
    # return t/60

def heuristic(nodo_o, nodo_d,linea,came_from):
    origen = translate(nodo_o.coords[0],nodo_o.coords[1])
    destino = translate(nodo_d.coords[0],nodo_d.coords[1])
    dist = vincenty(origen,destino).meters
    if linea != came_from:
        dist *= 10
    return dist

def cost(cost_so_far,linea,came_from,horarios):
    c = cost_so_far + TIEMPO_VIAJE
    if linea != came_from:
        c += TIEMPO_ESPERA
    return c

def a_star_search(start, goal, nodos, horarios):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = (None,None)
    cost_so_far[start] = 0
    path = {}
    path[start] = []
    while not frontier.empty():
        nodo = frontier.get()
        if nodo == goal:
            return path[nodo] + [nodo] #path_to_time((path[nodo] + [nodo]),nodos,horarios) #cost_so_far[nodo] # path[nodo] + [nodo]
        for next in nodo.adyacentes:
            new_cost = float('inf')
            new_cost = 0
            linea = "l"
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, goal, linea, came_from[nodo][1])
                frontier.put(next, priority)
                came_from[next] = (nodo,linea)
                path[next] = path[nodo] + [nodo]
    return -2 #cost_so_far

def bfs(lista_nodos,start,goal,horarios):
    def intersect_lineas(tiempo,nodo_actual,nodo_siguiente,lineas,tiempos,horarios,resultado=False):
        # tiempo = [esperas_omnibus,tiempos_viaje,cambios_parada] es la lista a partir de la cual se
        #    calcula el tiempo de viaje. Cada numero corresponde a una variable global configurable
        #    esperas_omnibus -> TIEMPO_ESPERA
        #    tiempos_viaje -> TIEMPO_VIAJE
        #    cambios_parada -> TIEMPO_CAMBIO_PARADA
        # nodo_actual = <-
        # nodo_siguiente = <-
        # lineas = lista de lineas con las que se puede haber llegado hasta el nodo actual.
        # tiempos = lista de tiempos en los que se puede haber llegado hasta el nodo actual.
        #     La posicion i de la lista tiempos corresponde a la posicion i de la lista lineas.
        # horarios = Lista de horarios para recuperar el tiempo de viaje de las lineas.
        # resultado = Si es True se calcula el tiempo sabiendo que se llego a destino.
        #
        # Para cada linea de nodo_siguiente miro si esta en la lista "lineas".
        # Si esta y el ordinal en nodo_siguiente es mayor (esta mas adelante en el recorrido),
        #     se agrega a la nueva lista de lineas y se aumenta el tiempo de viaje.
        # Si no se calcula el tiempo caminando desde nodo_actual a nodo_siguiente.
        #
        # Si la lista "res_lineas" esta vacia significa que no hay ninguna linea que conecte
        #     nodo_actual con nodo_siguiente, por lo tanto hay que actualizar el tiempo de viaje.
        # Si "resultado" es True, se calcula el tiempo total del viaje.
        # Si no se tiene que devolver el resultado y existe alguna linea que conecte las dos paradas
        #     se devuelve el tiempo de viaje sin cambiar, con las nuevas listas de lineas y tiempos.
        #     Basicamente se prefiere seguir en omnibus que caminar siempre que sea posible.
        #
        # Devuelve una tupla ([esperas_omnibus,tiempos_viaje,cambios_parada],lista_lineas,lista_tiempos)
        res_lineas = list()
        tiempos_omnibus = list()
        caminando = False
        lineas_sin_ord = [x[:2] for x in lineas]
        for linea in nodo_siguiente.lineas:
            if linea[:2] in lineas_sin_ord:
                i = lineas_sin_ord.index(linea[:2])
                if linea[2] > lineas[i][2]:
                    res_lineas.append(linea)
                    tiempos_omnibus.append(tiempos[i] + 1) #TIEMPO_VIAJE)
                else:
                    caminando = True
            else:
                caminando = True
        if res_lineas == list() or resultado:
            #new_t = tiempo + (TIEMPO_CAMBIO_PARADA * caminando) + min(tiempos, default = 0) # El nuevo tiempo es el tiempo anterior mas el tiempo de caminar hasta la proxima parada y el tiempo que paso en el omnibus
            new_t = [tiempo[0],tiempo[1]+min(tiempos,default=0),tiempo[2] + (caminando & 1)]
            return (new_t,list(),list()) # si res_lineas == [] entonces tiempos_omnibus == []
        else:
            return (tiempo,res_lineas,tiempos_omnibus)

    visited = set()
    queue = [(nodo,[nodo],[0,0,0],list(),list()) for nodo in start.cercanos]
    while queue != list():
        (nodo,path,t,lineas,tiempos) = queue.pop(0)
        if lineas == list():
            t[0] += 1
            lineas = nodo.lineas
            tiempos = [0 for _ in range(len(lineas))]
        if nodo not in visited:
            for ady in (nodo.adyacentes - set(path)):
                if ady in goal.cercanos: #ady.cod_parada == goal.cod_parada:
                    (aux_t,aux_lineas,aux_tiempos) = intersect_lineas(t,nodo,ady,lineas,tiempos,horarios,resultado=True)
                    return aux_t #path + [ady]
                else:
                    (aux_t,aux_lineas,aux_tiempos) = intersect_lineas(t,nodo,ady,lineas,tiempos,horarios)
                    queue.append((ady,path + [ady],aux_t,aux_lineas,aux_tiempos))
            visited.add(nodo)
        #print(t,path)
    return queue

def bfs_search(lista_nodos,start,goal,horarios,hora):
    # Si existe una o mas lineas que conecten directamente el origen con el
    # destino saco el tiempo. Si no, hay un transbordo y tengo que hacer bfs
    intersect = lambda l1,l2: [inner_list for inner_list in l1 if inner_list in l2]
    lineas_origen = [x[:2] for x in start.lineas]
    lineas = intersect(lineas_origen,[x[:2] for x in goal.lineas])
    if lineas != list():
        t = list()
        for l in lineas:
            t = min(t,get_tiempo(l[0],l[1],start,goal,horarios,hora))
        if t != list():
            return t
    t = bfs(lista_nodos,start,goal,horarios) #a_star_search(start,goal,lista_nodos,horarios)
    # print(path)
    # return path_to_time(path,lista_nodos,horarios)
    return t

def path_to_time(path,nodos,horarios, hora=0):
    intersect = lambda l1,l2: [inner_list for inner_list in l1 if inner_list in l2]
    if path != []:
        t = 0
        index = 0
        while index < len(path):
            nodo_a = path[index]
            lineas_a = [x[:2] for x in nodo_a.lineas]
            index += 1
            while index < len(path):
                nodo_aux = path[index]
                aux = intersect(lineas_a,[x[:2] for x in nodo_aux.lineas])
                if aux != list():
                    lineas_a = aux
                    index += 1
                else:
                    break
            lineas = intersect(lineas_a,[x[:2] for x in path[index-1].lineas])
            # print(path,lineas)
            if lineas != list():
                t_aux = float('inf')
                for l in lineas:
                    t_aux = min(t_aux,get_tiempo(l[0],l[1],nodo_a,path[index-1],horarios,hora))
                t += t_aux
            else:
                print("oops")
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

'''
cambia los codigos parada de las listas adyacente y cercanos de cada nodo
a nodos del grafo
'''
def cargar_adyacentes(lista_nodos):
    intersect = lambda l1,l2: [inner_list for inner_list in l1 if inner_list in l2]
    for nodo in lista_nodos:
        adyacentes = set()
        cercanos = set()
        for ady in nodo.adyacentes:
            nodo_aux = get_parada(lista_nodos,ady)
            adyacentes.add(nodo_aux)
        for cer in nodo.cercanos:
            nodo_aux = get_parada(lista_nodos,cer)
            if intersect(nodo.lineas,nodo_aux.lineas) == list():
                cercanos.add(nodo_aux)
        setattr(nodo,'adyacentes',adyacentes) # nodo.adyacentes = adyacentes
        setattr(nodo,'cercanos',cercanos) # nodo.cercanos = cercanos
    return lista_nodos
    # for nodo in lista_nodos:
    #     adyacentes = list()
    #     for ady in nodo.adyacentes:
    #         nodo_aux = get_parada(lista_nodos,ady)
    #         adyacentes.append(nodo_aux)No limit
    #     nodo.adyacentes = adyacentes

#def cargar_cercanos(lista_nodos):
#    for nodo in lista_nodos:
#        nodo.cargar_nodos_cercanos(lista_nodos)

'''
escribe la informacion del grafo a un archivo
'''
def save(lista_nodos,file_name):
    l = list()
    for nodo in lista_nodos:
        l.append(nodo.to_string())
    with open(file_name,'w') as f:
        f.write("CODIGO_PARADA,X,Y,LINEAS,ADYACENTES,CERCANOS\n")
        f.write('\n'.join(l))

'''
carga los datos del grafo del archivo especificado
'''
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
            if len(linea) >= 5:
                adyacentes = linea[4].split(';')
                for ady in adyacentes:
                    nodo.adyacentes.add(ady)
            if len(linea) >= 6:
               cercanos = linea[5].split(';')
               for cer in cercanos:
                   nodo.cercanos.add(cer)
        nodos.append(nodo)
    return cargar_adyacentes(nodos)

'''
carga la lista de horarios a partir del archivo especificado
'''
def get_horarios(file_name):
    with open(file_name) as f:
        horarios = f.read().split('\n')
        horarios = list(map(lambda x: x.split(','),horarios))
    return horarios

if __name__ == '__main__':
    #nodos = cargar_nodos('v_uptu_paradas.csv')
    t0 = time.time()
    nodos = load('test_nodos_cercanos.csv')
    horarios = get_horarios('horarios.csv')
    t1 = time.time()
    print(t1-t0)
    #save(nodos,'test_nodos_cercanos.csv')
    index_0 = [nodos.index(nodo) for nodo in nodos if nodo.cod_parada == "3607"][0] #3999 . 4836 . 1931
    index_1 = [nodos.index(nodo) for nodo in nodos if nodo.cod_parada == "4416"][0] #4568 . 3183 . 4012
    # print(bfs_search(nodos,nodos[index_0],nodos[index_1],horarios,15))
    t0 = time.time()
    a = busqueda(nodos[index_0],nodos[index_0].coords,nodos[index_1],nodos[index_1].coords,nodos,horarios,15)
    # a = bfs_search(nodos,nodos[index_0],nodos[index_1],horarios,15)
    # b = a_star_search(nodos[index_0],nodos[index_1],nodos,horarios)
    t1 = time.time()
    print("calc",t1-t0)
    print(a)
    # print(tiempo_caminando(nodos[index_0].coords,nodos[index_0].coords))
