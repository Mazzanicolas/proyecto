from shapely.geometry import Point
from geopy.distance import vincenty
from queue import PriorityQueue
import math
import time

#http://www.montevideo.gub.uy/aquehorapasa/aquehorapasa.html

global VELOCIDAD_CAMINANDO
VELOCIDAD_CAMINANDO = 5000/60 # 5000 metros en 60 minutos
global TIEMPO_ESPERA
TIEMPO_ESPERA = 5*60 # 5 minutos en segundos
global TIEMPO_VIAJE
TIEMPO_VIAJE = 45 # 45 segundos entre paradas
global RADIO_CERCANO
RADIO_CERCANO = 500 # distancia maxima en metros para que dos paradas se consideren cercanas
global RADIO_CERCANO_ORIGEN
RADIO_CERCANO_ORIGEN = 2 * RADIO_CERCANO # distancia maxima en metros para que una parada se considere cercana al origen de la busqueda
global TIEMPO_CAMINANDO
TIEMPO_CAMINANDO = 60 * (RADIO_CERCANO / 2) * (1 / VELOCIDAD_CAMINANDO) # Regla de 3 para sacar el tiempo caminando promedio entre dos paradas cercanas
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

def get_tiempo(cod_linea,cod_variante,origen,destino):
    #tiempo entre 2 paradas cercanas o conectadas en omnibus
    t = list()
    linea = str(cod_linea)
    variante = str(cod_variante)
    ord_origen = int(list(filter(
        lambda x: x[0]==linea and x[1]==variante,origen.lineas))[0][2])
    ord_destino = int(list(filter(
        lambda x: x[0]==linea and x[1]==variante,destino.lineas))[0][2])
    if ord_origen < ord_destino:
        t = [1,ord_destino - ord_origen,0]
    return t

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
        self.cercanos = list()
        self.cercanos_desde_origen = list()

    def __str__(self):
        return str(self.cod_parada)

    def __repr__(self):
        return 'Parada {}'.format(self.cod_parada)

    # devuelve cod_parada,x,y,lineas,adyacentes para un nodo
    def to_string(self):
        s = '{},{},{}'.format(self.cod_parada,self.coords[0],self.coords[1])
        # if len(self.lineas) > 0:
        lineas = ';'.join([':'.join(linea) for linea in self.lineas])
        s += ',{}'.format(lineas)
        # if len(self.adyacentes) > 0:
        adyacentes = ';'.join(
            [ady.cod_parada for ady in self.adyacentes])
        s += ',{}'.format(adyacentes)
        # if len(self.cercanos) > 0:
        cercanos = ';'.join(
            [cer.cod_parada for cer in self.cercanos])
        s += ',{}'.format(cercanos)
        # if len(self.cercanos_desde_origen) > 0:
        cercanos = ';'.join(
            [cer.cod_parada for cer in self.cercanos_desde_origen])
        s += ',{}'.format(cercanos)
        return s

    def crear_nodos_cercanos(self,lista_nodos):
        intersect = lambda l1,l2: [inner_list for inner_list in l1 if inner_list in l2]
        cercanos = list()
        cercanos_desde_origen = list()
        origen = translate(self.coords[0],self.coords[1])
        lineas_sin_ord = [x[:2] for x in self.lineas]
        for nodo in lista_nodos:
            if intersect(lineas_sin_ord,[x[:2] for x in nodo.lineas]) == list():
                destino = translate(nodo.coords[0],nodo.coords[1])
                dist = vincenty(origen,destino).meters
                if dist <= RADIO_CERCANO:
                    cercanos.append(nodo)
                if dist <= RADIO_CERCANO_ORIGEN:
                    cercanos_desde_origen.append(nodo)
        setattr(self,'cercanos',cercanos)
        setattr(self,'cercanos_desde_origen',cercanos_desde_origen)
        #self.cercanos = cercanos
        #self.cercanos_desde_origen = cercanos_desde_origen

def busqueda(nodo_origen, nodo_destino, nodos):
    if nodo_origen is nodo_destino:
        return -2,-2,-2,
    else:
        return search(nodo_origen,nodo_destino,nodos)

def search(start,goal,lista_nodos):
    # Si la parada destino esta dentro del radio de las paradas cercanas al origen, se devuelve el tiempo caminando
    if goal in start.cercanos_desde_origen: # el tiempo caminando se calcula a partir de radio_cercano.
        return [0,0,2]  # como RADIO_CERCANO_ORIGEN es el doble, se suma 2 veces el tiempo caminando del radio normal

    # Si existe una linea que conecte directamente el nodo origen o uno de los nodos cercanos al origen
    # con el destino, se calcula y devuelve ese tiempo.
    intersect = lambda l1,l2: [inner_list for inner_list in l1 if inner_list in l2]
    lineas_destino = [x[:2] for x in goal.lineas] # [linea,variante] sin ordinal
    lista_tiempos = list()
    for nodo in ([start] + start.cercanos_desde_origen):
        lineas = intersect([x[:2] for x in nodo.lineas],lineas_destino)
        if lineas != list():
            for l in lineas:
                tiempo = get_tiempo(l[0],l[1],nodo,goal)
                if tiempo != list():
                    if nodo is not start: # si el nodo actual no es el origen,
                        tiempo[2] += 2    # agregar el tiempo caminando
                    lista_tiempos.append(tiempo)
    if lista_tiempos != list():
        res = (float('inf'),list())
        for tiempo in lista_tiempos:
            t = tiempo[0]*TIEMPO_ESPERA + tiempo[1]*TIEMPO_VIAJE + tiempo[2]*TIEMPO_CAMINANDO
            if t < res[0]:
                res = (t,tiempo)
        return tiempo
    else:
        return actual_search(lista_nodos,start,goal)

def actual_search(lista_nodos,start,goal):
    def logica(tiempo,nodo_actual,nodo_siguiente,lineas,tiempos,resultado=False):
        lineas_directas = list()
        tiempos_directos = list()
        lineas_sin_ord = [x[:2] for x in lineas]
        lineas_nodo_actual_sin_ord = [x[:2] for x in nodo_actual.lineas]
        lineas_con_espera = list()
        tiempos_con_espera = list()
        for linea in nodo_siguiente.lineas:
            if linea[:2] in lineas_sin_ord:
                i = lineas_sin_ord.index(linea[:2])
                if linea[2] > lineas[i][2]:
                    lineas_directas.append(linea)
                    tiempos_directos.append(tiempos[i] + 1)
            elif linea[:2] in lineas_nodo_actual_sin_ord:
                    lineas_con_espera.append(linea)
                    tiempos_con_espera.append(1)

        if resultado:
            t = float('inf')
            time_so_far = tiempo[0]*TIEMPO_ESPERA + tiempo[1]*TIEMPO_VIAJE + tiempo[2]*TIEMPO_CAMINANDO
            res = list()
            if lineas_directas != list():
                for i in range(len(lineas_directas)):
                    aux_t = time_so_far + tiempos_directos[i]*TIEMPO_VIAJE
                    if aux_t < t:
                        t = aux_t
                        res = [tiempo[0],tiempo[1]+tiempos_directos[i],tiempo[2]]
            elif lineas_con_espera != list():
                aux_t = time_so_far + min(tiempos,default=0)*TIEMPO_VIAJE + TIEMPO_ESPERA
                if aux_t < t:
                    t = aux_t
                    res = [tiempo[0]+1,tiempo[1]+1+min(tiempos,default=0),tiempo[2]]
            if t == float('inf'):
                res = [tiempo[0],tiempo[1]+min(tiempos,default=0),tiempo[2]+1]
            return (res,list(),list())
        elif lineas_directas != list():
            return (tiempo, lineas_directas,tiempos_directos) # hay por lo menos un omnibus directo, se devuelve ese
        elif lineas_con_espera != list():
            new_t = [tiempo[0]+1,tiempo[1]+min(tiempos,default=0),tiempo[2]] # se suma una espera y se devuelven las lineas que interesectan el
            return (new_t,lineas_con_espera,tiempos_con_espera)              # actual con el siguiente que no estaban en la lista de lineas que llego
        else:
            new_t = [tiempo[0],tiempo[1]+min(tiempos,default=0),tiempo[2]+1] # se suma un tiempo caminando y se agregan el tiempo minimo en paradas
            return (new_t,list(),list()) # si lineas_directas == [] entonces tiempos_directos == []

    visited = set()
    q = PriorityQueue()
    for nodo in ([start] + start.cercanos_desde_origen):
        item = [nodo,[nodo],[1,0,0],list(),list()]
        q.put((0,id(item),item))
    resultados = list()
    while not q.empty():
        (nodo,path,t,lineas,tiempos) = q.get()[2]
        if lineas == list(): #Si no tiene lineas, se agregan todas las lineas
            #t[0] += 1        #del nodo actual y se agrega una espera de omnibus
            lineas = nodo.lineas
            tiempos = [0 for _ in range(len(lineas))]
        for ady in (nodo.adyacentes - set(path)):
            if ady not in visited:
                if ady in ([goal] + goal.cercanos):
                    aux_t = logica(t,nodo,ady,lineas,tiempos,resultado=True)[0]
                    #print(path+[ady])
                    return aux_t
                t,lineas,tiempos = logica(t,nodo,ady,lineas,tiempos)
                tiempo = t[0]*TIEMPO_ESPERA + t[1]*TIEMPO_VIAJE + t[2]*TIEMPO_CAMINANDO
                item = [ady,path + [ady ],t,lineas,tiempos]
                q.put((tiempo,id(item),item))
                visited.add(nodo)
    return -1,-1,-1

'''
carga los datos del grafo del archivo especificado

Formato del archivo de carga:
    cod_parada,x,y,lineas,adyacentes,[cercanos,cercanos_desde_origen]
'''
def load(file_name):
    with open(file_name) as f:
        a = f.read().split('\n')[1:]
    nodos = list()
    for linea in a:
        linea = linea.split(',')
        nodo = Nodo(linea[0],linea[1],linea[2])    # cod_parada,x,y
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
                    nodo.cercanos.append(cer)
                cercanos_desde_origen = linea[6].split(';')
                for c_orig in cercanos_desde_origen:
                    nodo.cercanos_desde_origen.append(c_orig)
        nodos.append(nodo)
    return cargar_adyacentes(nodos)

'''
cambia los codigos parada de las listas adyacente y cercanos de cada nodo
a nodos del grafo
'''
def cargar_adyacentes(lista_nodos):
    print("adyacentes")
    counter = 0
    for nodo in lista_nodos:
        adyacentes = set()
        cercanos = list()
        cercanos_desde_origen = list()
        for ady in nodo.adyacentes:
            if len(ady) > 0:
                nodo_aux = get_parada(lista_nodos,ady)
                adyacentes.add(nodo_aux)
        setattr(nodo,'adyacentes',adyacentes) # nodo.adyacentes = adyacentes
        if nodo.cercanos != list() and nodo.cercanos_desde_origen != list():
            for cer in nodo.cercanos:
                if len(cer) > 0:
                    nodo_aux = get_parada(lista_nodos,cer)
                    cercanos.append(nodo_aux)
            for cer in nodo.cercanos_desde_origen:
                if len(cer) > 0:
                    nodo_aux = get_parada(lista_nodos,cer)
                    cercanos_desde_origen.append(nodo_aux)
            setattr(nodo,'cercanos',cercanos) # nodo.cercanos = cercanos
            setattr(nodo,'cercanos_desde_origen',cercanos_desde_origen)
        else:
            nodo.crear_nodos_cercanos(lista_nodos)
        if counter % 100 == 0:
            print(counter)
        counter += 1
    return lista_nodos

'''
escribe la informacion del modelo a un archivo
'''
def save(lista_nodos,file_name):
    l = list()
    for nodo in lista_nodos:
        l.append(nodo.to_string())
    with open(file_name,'w') as f:
        f.write("CODIGO_PARADA,X,Y,LINEAS,ADYACENTES,CERCANOS,CERCANOS AL ORIGEN\n")
        f.write('\n'.join(l))

def quicksearch(nodos,i0,i1):
    index_0 = [nodos.index(nodo) for nodo in nodos if nodo.cod_parada == str(i0)][0] #3999 . 4836 . 1931
    index_1 = [nodos.index(nodo) for nodo in nodos if nodo.cod_parada == str(i1)][0] #4568 . 3183 . 4012
    a = busqueda(nodos[index_0],nodos[index_1],nodos)
    t = a[0]*TIEMPO_ESPERA + a[1]*TIEMPO_VIAJE + a[2]*TIEMPO_CAMINANDO
    print(a)
    print(t)
    print(t/60)

def test():
    nodo0 = Nodo("a",0,0)
    nodo1 = Nodo("b",0,0)
    nodo2 = Nodo("c",0,0)
    nodo3 = Nodo("d",0,0)
    nodo4 = Nodo("e",0,0)
    #setattr(nodo0,'lineas',[['1','1','1']])
    #setattr(nodo0,'adyacentes',{nodo1})
    setattr(nodo0,'cercanos',[nodo1])
    #setattr(nodo1,'lineas',[['1','1','2'],['2','1','1']])
    #setattr(nodo1,'adyacentes',{nodo2})
    setattr(nodo1,'cercanos',[nodo2])
    #setattr(nodo2,'lineas',[['2','1','2']])
    #setattr(nodo2,'adyacentes',{nodo3})
    setattr(nodo2,'cercanos',[nodo3])
    #setattr(nodo3,'lineas',[['2','1','3']])
    #setattr(nodo3,'adyacentes',{nodo4})
    setattr(nodo3,'cercanos',[nodo4])

    nodos = [nodo0,nodo1,nodo2,nodo3,nodo4]
    a = quicksearch(nodos,"a","e")

def main():
    t0 = time.time()
    nodos = load('omnibus_final_ver.csv')
    t1 = time.time()
    print("load",t1-t0)
    t0 = time.time()
    # save(nodos,'omnibus_final_ver.csv')
    # t1 = time.time()
    # print(t1-t0)

    index_0 = [nodos.index(nodo) for nodo in nodos if nodo.cod_parada == "4836"][0] #3999 . 4836 . 1931
    index_1 = [nodos.index(nodo) for nodo in nodos if nodo.cod_parada == "3183"][0] #4568 . 3183 . 4012

    t0 = time.time()
    a = busqueda(nodos[index_0],nodos[index_1],nodos)
    t1 = time.time()
    print("calc",t1-t0)
    print(a)
    t = a[0]*TIEMPO_ESPERA + a[1]*TIEMPO_VIAJE + a[2]*TIEMPO_CAMINANDO
    print(t)

if __name__ == '__main__':
    #main()
    test()
