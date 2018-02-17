from io import StringIO
import csv

def checkTiempos(tipo):
    errores = list()
    #csvfile = 'matrizAuto.csv'
    with open('matrizAuto.csv', 'r') as csvfile:
        csvf = StringIO(csvfile.read())#.decode())
        if(tipo == 0):
            l = csv.reader(csvf, delimiter=',')
            print("el tipo es 0")
        else:
            l = csv.reader(csvf, delimiter=';')
        lineas=[]
        lineas.extend(l)
        lineas = lineas[1:]
        i = 0
        for caso in lineas:
            if(i%1000 == 0):
                print(i)
            i = i + 1
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
            return True,lineas
        else:
            print('\n'.join(errores))
            return False,[[x] for x in errores]
