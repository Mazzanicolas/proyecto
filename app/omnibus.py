from shapely.geometry import Point
from geopy.distance import vincenty
import math

#http://www.montevideo.gub.uy/aquehorapasa/aquehorapasa.html

global VELOCIDAD_CAMINANDO
VELOCIDAD_CAMINANDO = 1.4

global horarios

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
	#print(origen.lineas,cod_linea,cod_variante)
	t = float('inf')
	if [cod_linea,cod_variante] in [x[:2] for x in origen.lineas]:
		ord_origen = list(filter(
			lambda x: x[0]==cod_linea and x[1]==cod_variante,origen.lineas))[0][2]
		ord_destino = list(filter(
			lambda x: x[0]==cod_linea and x[1]==cod_variante,destino.lineas))[0][2]
		if ord_origen < ord_destino:
			recorrido = list()
			for h in horarios:
				if h[1]==cod_linea and h[2]==cod_variante:
					if int(ord_origen) <= int(h[3]) < int(ord_destino):
						recorrido.append(h)
			recorrido = sorted(recorrido, key=lambda x: int(x[3]))
			if len(recorrido) > 0:
				t_omnibus = int(recorrido[0][-2]) #incializo el tiempo con la espera en la parada
				for parada in recorrido:
					t_omnibus += int(parada[-1]) #en cada paso le sumo el tiempo de viaje a la proxima parada
				t = min(t,t_omnibus) #me quedo con el menor tiempo
	return t

def tiempo_caminando(origen,destino):
	origen = translate(origen[0],origen[1])
	destino = translate(destino[0],destino[1])
	t = vincenty(origen,destino).kilometers * VELOCIDAD_CAMINANDO
	return t

def get_parada(lista_nodos,cod_parada):
	try:
		index = [lista_nodos.index(nodo) for nodo in lista_nodos
					if nodo.cod_parada == cod_parada][0]
		return lista_nodos[index]
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

	def to_string(self): #devuelve cod_parada,x,y,lineas,adyacentes para un nodo
		s = '{},{},{}'.format(self.cod_parada,self.coords[0],self.coords[1])
		if len(self.lineas) > 0:
			lineas = ';'.join([':'.join(linea) for linea in self.lineas])
			s += ',{}'.format(lineas)
		if len(self.adyacentes) > 0:
			adyacentes = ';'.join(
				[':'.join(map(str,ady)) for ady in self.adyacentes])
			s += ',{}'.format(adyacentes)
		return s

	def search(self, lista_nodos, destino, horarios, hora = 0):
		#lista de lineas accesibles desde un nodo
		def cercanos(nodo,lista_nodos):
			res = [l[:2] + [nodo] for l in nodo.lineas]
			for p in nodo.adyacentes: # p = [cod_parada, tiempo]
				parada = get_parada(lista_nodos,p[0])
				if parada is not None:
					for l in parada.lineas:
						if l[:2] not in [x[:2] for x in res]:
							res.append(l[:2] + [parada])
			return res

		c_origen = cercanos(self,lista_nodos)
		c_destino = cercanos(destino,lista_nodos)
		paradas = list()
		for orig in c_origen:
			for dest in c_destino:
				if orig[:2] == dest[:2]:
					paradas.append([orig[0],orig[1],orig[2],dest[2]])
		if len(paradas) != 0:
			t = float('inf')
			res_origen = None
			res_destino = None
			for parada in paradas:
				#get_tiempo(cod_linea,cod_variante,origen,destino,horarios,hora=0)
				aux = get_tiempo(parada[0],parada[1],parada[2],parada[3],horarios,hora)
				if aux < t:
					t = aux
					res_origen = parada[2]
					res_destino = parada[3]
			m,s = divmod(t,60)
			print("{}:{}".format(m,s),"b")
			return t,res_origen,res_destino
		else:
			'''Si no encuentro un omnibus directo busco en la mala
			todas las paradas que conecten el origen con el destino
			Si encuentro para una parada una linea que conecte con el origen
			y otra con el destino, corto y la agrego a la lista.'''
			for nodo in nodos:
				conecta_origen = list()
				conecta_destino = list()
				for linea in nodo.lineas:
					if linea[:2] in [x[:2] for x in self.lineas]:
						conecta_origen.append(linea[:2])
					elif linea[:2] in [x[:2] for x in destino.lineas]:
						conecta_destino.append(linea[:2])
				if conecta_origen and conecta_destino:
					paradas.append([nodo,conecta_origen,conecta_destino])
			if len(paradas) != 0:
				t = float('inf')
				for parada in paradas:
					#print(paradas)
					for linea_o in parada[1]:
						for linea_d in parada[2]:
							#print(parada,linea_o,linea_d)
							primer_tramo = get_tiempo(linea_o[0],linea_o[1],
								self,parada[0],horarios,hora)
							segundo_tramo = get_tiempo(linea_d[0],linea_d[1],
								parada[0],destino,horarios,hora)
							#print(primer_tramo,segundo_tramo)
							if primer_tramo > 0 and segundo_tramo > 0:
								t = min(t,primer_tramo + segundo_tramo)
				m,s = divmod(t,60)
				print("{}:{}".format(m,s),"a")
				return t,self,destino

def busqueda(origen, destino, hora):
	nodos = load('nodos.csv')
	with open('test/test_horarios2.csv') as f:
		horarios = f.read().split('\n')
		horarios = list(map(lambda x: x.split(','),horarios))
	nodo_origen = get_parada(nodos,parada_mas_cercana(origen[0],origen[1],nodos))
	#print(nodo_origen)
	nodo_destino = get_parada(nodos,parada_mas_cercana(destino[0],destino[1],nodos))
	#print(nodo_destino)
	t,parada_origen,parada_destino = nodo_origen.search(nodos,nodo_destino,horarios,hora)
	t_caminando_tramo1 = tiempo_caminando(origen,parada_origen.coords)
	t_caminando_tramo2 = tiempo_caminando(destino,parada_destino.coords)
	t_total = (t + t_caminando_tramo1 + t_caminando_tramo2)
	return t_total

def cargar_nodos(file_name):
	nodos = list()
	aux = list()
	with open(file_name) as f:
		a = f.read().split('\n')[1:]
		for linea in a:
			linea = linea.split(',')
			if linea[0] not in aux: #Si no hay un nodo creado para la parada
				nodo = Nodo(linea[0],linea[4],linea[5]) #Codigo parada, x, y
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
		area = Point(nodo.coords[0],nodo.coords[1]).buffer(500)
		for otro_nodo in lista_nodos:
			if (otro_nodo is not nodo and
				area.contains(Point(otro_nodo.coords[0],otro_nodo.coords[1]))):
				nodo.adyacentes.append([otro_nodo.cod_parada])

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
					nodo.adyacentes.append(ady.split(':'))
		nodos.append(nodo)
	return nodos

def get_horarios(file_name):
	with open(file_name) as f:
		horarios = f.read().split('\n')
		horarios = list(map(lambda x: x.split(','),horarios))
	return horarios
	
if __name__ == '__main__':
	#nodos = cargar_nodos('test/test_horarios.csv')
	#cargar_adyacentes(nodos)
	#save(nodos,'nodos2.csv')
	nodos = load('nodos.csv')
	#horarios = get_horarios('test/test_horarios2.csv')
	#index_0 = [nodos.index(nodo) for nodo in nodos if nodo.cod_parada == '3847'][0] #2968
	#index_1 = [nodos.index(nodo) for nodo in nodos if nodo.cod_parada == '6017'][0] #3183
	#a = nodos[index_0].search(nodos,nodos[index_1],horarios,15)
	#-----------------------------
	origen = [575168,6137630]
	destino = [576443,6138480]
	print(parada_mas_cercana(origen[0],origen[1],nodos))
	print(parada_mas_cercana(destino[0],destino[1],nodos))
	print(busqueda(origen,destino,15))