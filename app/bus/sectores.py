from shapely.geometry import Polygon, Point
import shapefile
from omnibus import parada_mas_cercana, load, busqueda, get_parada

'''
    A partir de un shape dado devuelve una lista con el centroide de cada sector
'''
def write_centroides(shape,file_name):
    centroides = list()
    for s in shape:
        p = Polygon(s.points)
        if(p.is_valid):
            punto = (p.representative_point().x,p.representative_point().y)
            centroides.append(punto)
        else:
            punto = (p.centroid.x,p.centroid.y)
            centroides.append(punto)
    with open(file_name,'w') as f:
        f.write(('\n').join(list(map(lambda x: "{},{}".format(x[0],x[1]),centroides))))

'''
    A partir de un archivo con los puntos del centroide correspondiente a un sector,
    asigna la parada mas cercana. Guarda el mismo archivo con la parada asociada al
    centroide.
'''
def asignar_paradas(centroides_file,nodos_file):
    aux = open(centroides_file).read().split('\n')[:-1]
    centroides = list()
    for elem in aux:
        a = elem.split(',')
        centroides.append((float(a[0]),float(a[1])))
    nodos = load(nodos_file)
    res = list()
    for punto in centroides:
        res.append((punto[0],punto[1],parada_mas_cercana(punto[0],punto[1],nodos)))
    with open(centroides_name,'w') as f:
        f.write(('\n').join(list(map(lambda x: "{},{},{}".format(x[0],x[1],x[2]),res))))
    print("done")

def buscar_duplicados(centroides_file):
    lineas = open(centroides_file).read().split('\n')
    lineas = list(map(lambda x: x.split(',')[-1],lineas))
    a = 0
    for i in range(len(lineas)):
        for j in range(i,len(lineas)):
            if lineas[i] == lineas[j] and i != j:
                a += 1
    print(a)

def calcular_tiempos(nodos,sectores,out_file,start=0,end=1063):
    res = [[(0,0,0) for _ in range(len(sectores))] for _ in range(len(sectores))]
    for i in range(len(sectores)):
        nodo_origen = get_parada(nodos,sectores[i][-1])
        for j in range(len(sectores)):
            if i != j:
                nodo_destino = get_parada(nodos,sectores[j][-1])
                res[i][j] = busqueda(nodo_origen,nodo_origen.coords,nodo_destino,nodo_destino.coords,nodos,0,0)
        print(i)
    with open(out_file,'w') as f:
        #f.write('\n'.join(list(map(lambda x: ','.join(list(map(lambda y: str(y),x))),res))))
        f.write('\n'.join(list(map(lambda x: ','.join(list(map(lambda y: "{};{};{}".format(*y),x))),res))))

def main():
    # sf = shapefile.Reader('../app/files/shapeAuto.shp')
    # shapeAuto = sf.shapes()
    # centroides = write_centroides(shapeAuto,'centroides.csv')
    # asignar_paradas('centroides.csv','nodos.csv')
    # buscar_duplicados('centroides.csv')
    sectores = open('centroides.csv').read().split('\n')
    sectores = list(map(lambda x: x.split(','),sectores))
    nodos = load('test_nodos_cercanos.csv')
    print("done loading")
    calcular_tiempos(nodos,sectores,'matrizOmnibus.csv')

if __name__ == '__main__':
    main()
