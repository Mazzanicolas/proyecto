import shapefile
from   app.models import Individuo, IndividuoCentroOptimo, Centro
from   shapely    import geometry
import app.utils as utils
import csv
from django.conf import settings

def getIDCentroXYCoordDictionary(centros):
    xyCoordCentrosDictionary = dict()
    for centro in centros:
        xyCoordCentrosDictionary[centro.id_centro] = [centro.x_coord,centro.y_coord]
    return xyCoordCentrosDictionary

def saveShapeFiles(fileName, userId, shapeWriter, pathToFilesToDownlaod):
    directory = settings.BASE_DIR + '/app/data/users/user'+userId+'/shpOut/'
    utils.createFolder(directory)
    shapeWriter.save(directory+fileName)
    shapeWriter = shapefile.Writer(shapefile.POINT)
    pathToFilesToDownlaod.extend([directory+fileName+'.shp',directory+fileName+'.shx',directory+fileName+'.dbf'])
    return pathToFilesToDownlaod

def generarShapeLlega(path, fields, xyCoordCentrosDictionary, fileName, userId, pathToFilesToDownlaod):
    shapeWriter = shapefile.Writer(shapefile.POINT)
    #shapeWriter.autoBalance = 1 //Descomentar en release
    shapeWriter = createShapeFields(shapeWriter,fields)
    with open(path, newline='') as csvfile:
        aFile = csv.reader(csvfile, delimiter=',', quotechar='|')
        removeCsvHeader(aFile)
        for individuo in aFile:
            if(llega(individuo)):
                xCoordCentro,yCoordCentro = xyCoordCentrosDictionary.get(int(individuo[2]))
                shapeWriter.point(xCoordCentro,yCoordCentro)
                shapeWriter.record(individuo[0],individuo[2],individuo[3],individuo[4],individuo[5],individuo[6],individuo[7],individuo[9])
    saveShapeFiles(fileName, userId, shapeWriter, pathToFilesToDownlaod)

def generarResumenLlega(path, fields, xyCoordCentrosDictionary, fileName, userId, pathToFilesToDownlaod):
    shapeWriter = shapefile.Writer(shapefile.POINT)
    #shapeWriter.autoBalance = 1 //Descomentar en release
    shapeWriter = createShapeFields(shapeWriter,fields)
    currentIdsInDBF = []
    dictionaryOfIdOccurences = getDictionaryCantidadLlega(path)
    with open(path, newline='') as csvfile:
        aFile = csv.reader(csvfile, delimiter=',', quotechar='|')
        removeCsvHeader(aFile)
        for individuo in aFile:
            if(llega(individuo)):
                if(not idIsDuplicated(individuo[0],individuo[2],currentIdsInDBF)):
                    xCoordCentro,yCoordCentro = xyCoordCentrosDictionary.get(int(individuo[2]))
                    shapeWriter.point(xCoordCentro,yCoordCentro)
                    shapeWriter.record(individuo[0],individuo[2],dictionaryOfIdOccurences.get(str(individuo[0])+'_'+str(individuo[2]), '?'))
                    currentIdsInDBF.append(str(individuo[0])+'_'+str(individuo[2]))
    saveShapeFiles(fileName, userId, shapeWriter, pathToFilesToDownlaod)

def idIsDuplicated(idIndividuoToCheck,idCentroToCheck,listOfIds):
    combinationToCheck = str(idIndividuoToCheck)+'_'+str(idCentroToCheck)
    if(combinationToCheck in listOfIds):
        return True
    return False

def getDictionaryCantidadLlega(path):
    dictionaryOfIdOccurences = dict()
    with open(path, newline='') as csvfile:
        aFile = csv.reader(csvfile, delimiter=',', quotechar='|')
        removeCsvHeader(aFile)
        for individuo in aFile:
            if(llega(individuo)):
                dictionaryOfIdOccurences[str(individuo[0])+'_'+str(individuo[2])] = dictionaryOfIdOccurences.get(str(individuo[0])+'_'+str(individuo[2]), 0)+1
    print(dictionaryOfIdOccurences)
    return dictionaryOfIdOccurences


def generarShapeHogares(fields, individuos, fileName, userId, pathToFilesToDownlaod):
    shapeWriter = shapefile.Writer(shapefile.POINT)
    #shapeWriter.autoBalance = 1 //Descomentar en release
    shapeWriter = createShapeFields(shapeWriter,fields)
    for individuo in individuos:
        xCoordHogar,yCoordHogar = individuo.hogar.x_coord, individuo.hogar.y_coord
        shapeWriter.point(xCoordHogar,yCoordHogar)
        shapeWriter.record(individuo.id)
    saveShapeFiles(fileName, userId, shapeWriter, pathToFilesToDownlaod)

def generarShapeJardines(fields, individuos, fileName, userId, pathToFilesToDownlaod):
    shapeWriter = shapefile.Writer(shapefile.POINT)
    #shapeWriter.autoBalance = 1 //Descomentar en release
    shapeWriter = createShapeFields(shapeWriter,fields)
    for individuo in individuos:
        if(individuo.tieneJardin):
            xCoordJardin,yCoordJardin = individuo.jardin.x_coord, individuo.jardin.y_coord
            shapeWriter.point(xCoordJardin,yCoordJardin)
            shapeWriter.record(individuo.id,individuo.jardin.hora_inicio,individuo.jardin.hora_fin)
    saveShapeFiles(fileName, userId, shapeWriter, pathToFilesToDownlaod)
    
def generarShapeTrabajos(fields, individuos, fileName, userId, pathToFilesToDownlaod):
    shapeWriter = shapefile.Writer(shapefile.POINT)
    #shapeWriter.autoBalance = 1 #Descomentar en release
    shapeWriter = createShapeFields(shapeWriter,fields)
    for individuo in individuos:
        if(individuo.tieneTrabajo):
            xCoordTrabajo,yCoordTrabajo = individuo.trabajo.x_coord, individuo.trabajo.y_coord
            shapeWriter.point(xCoordTrabajo,yCoordTrabajo)
            shapeWriter.record(individuo.id,individuo.trabajo.hora_inicio,individuo.trabajo.hora_fin)
    saveShapeFiles(fileName, userId, shapeWriter, pathToFilesToDownlaod)

def generarShapeCentroOptimoAuto(fields, individuos, fileName, userId, pathToFilesToDownlaod):
    shapeWriter = shapefile.Writer(shapefile.POINT)
    #shapeWriter.autoBalance = 1 #Descomentar en release
    shapeWriter = createShapeFields(shapeWriter,fields)
    for individuo in individuos:
        centroOptimo = IndividuoCentroOptimo.objects.get(individuo = individuo)
        xCoordCentroAuto,yCoordCentroAuto = centroOptimo.centroOptimoAuto.x_coord, centroOptimo.centroOptimoAuto.y_coord
        shapeWriter.point(xCoordCentroAuto,yCoordCentroAuto)
        shapeWriter.record(individuo.id, centroOptimo.centroOptimoAuto.id_centro, secondsToMinsRounded(centroOptimo.tHogarCentroAuto))
    saveShapeFiles(fileName, userId, shapeWriter, pathToFilesToDownlaod)

def generarShapeCentroOptimoOmnibus(fields, individuos, fileName, userId, pathToFilesToDownlaod):
    shapeWriter = shapefile.Writer(shapefile.POINT)
    #shapeWriter.autoBalance = 1 #Descomentar en release
    shapeWriter = createShapeFields(shapeWriter,fields)
    for individuo in individuos:
        centroOptimo = IndividuoCentroOptimo.objects.get(individuo = individuo)
        xCoordCentroOmnibus,yCoordCentroOmnibus = centroOptimo.centroOptimoOmnibus.x_coord, centroOptimo.centroOptimoOmnibus.y_coord
        shapeWriter.point(xCoordCentroOmnibus,yCoordCentroOmnibus)
        shapeWriter.record(individuo.id, centroOptimo.centroOptimoOmnibus.id_centro, secondsToMinsRounded(centroOptimo.tHogarCentroOmnibus))
    saveShapeFiles(fileName, userId, shapeWriter, pathToFilesToDownlaod)

def generarShapeCentroOptimoCaminando(fields, individuos, fileName, userId, pathToFilesToDownlaod):
    shapeWriter = shapefile.Writer(shapefile.POINT)
    #shapeWriter.autoBalance = 1 #Descomentar en release
    shapeWriter = createShapeFields(shapeWriter,fields)
    for individuo in individuos:
        centroOptimo = IndividuoCentroOptimo.objects.get(individuo = individuo)
        xCoordCentroCaminando,yCoordCentroCaminando = centroOptimo.centroOptimoCaminando.x_coord, centroOptimo.centroOptimoCaminando.y_coord
        shapeWriter.point(xCoordCentroCaminando,yCoordCentroCaminando)
        shapeWriter.record(individuo.id, centroOptimo.centroOptimoCaminando.id_centro, secondsToMinsRounded(centroOptimo.tHogarCentroCaminando))
    saveShapeFiles(fileName, userId, shapeWriter, pathToFilesToDownlaod)

def generarShapeLineaHogarCentroAuto(fields, individuos, fileName, userId, pathToFilesToDownlaod):
    lineParts = []        
    shapeWriter = shapefile.Writer(shapefile.POLYLINE)
    #shapeWriter.autoBalance = 1 #Descomentar en release
    shapeWriter = createShapeFields(shapeWriter,fields)
    for individuo in individuos:
        centroOptimo = IndividuoCentroOptimo.objects.get(individuo = individuo)
        xCoordHogar,yCoordHogar = individuo.hogar.x_coord, individuo.hogar.y_coord
        xCoordCentroAuto,yCoordCentroAuto = centroOptimo.centroOptimoAuto.x_coord, centroOptimo.centroOptimoAuto.y_coord
        lineParts.append([[xCoordHogar,yCoordHogar],[xCoordCentroAuto,yCoordCentroAuto]])
        shapeWriter.record(individuo.id, centroOptimo.centroOptimoAuto.id_centro, secondsToMinsRounded(centroOptimo.tHogarCentroAuto))
        shapeWriter.line(parts=lineParts)
        lineParts=[]
    saveShapeFiles(fileName, userId, shapeWriter, pathToFilesToDownlaod)

def genrerarShapeLineaHogarCentroOmnibus(fields, individuos, fileName, userId, pathToFilesToDownlaod):
    lineParts = []
    shapeWriter = shapefile.Writer(shapefile.POLYLINE)
    #shapeWriter.autoBalance = 1 #Descomentar en release
    shapeWriter = createShapeFields(shapeWriter,fields)
    for individuo in individuos:
        centroOptimo = IndividuoCentroOptimo.objects.get(individuo = individuo)
        xCoordHogar,yCoordHogar = individuo.hogar.x_coord, individuo.hogar.y_coord
        xCoordCentroOmnibus,yCoordCentroOmnibus = centroOptimo.centroOptimoOmnibus.x_coord, centroOptimo.centroOptimoOmnibus.y_coord
        lineParts.append([[xCoordHogar,yCoordHogar],[xCoordCentroOmnibus,yCoordCentroOmnibus]])
        shapeWriter.record(individuo.id, centroOptimo.centroOptimoOmnibus.id_centro, secondsToMinsRounded(centroOptimo.tHogarCentroOmnibus))
        shapeWriter.line(parts=lineParts)
        lineParts=[]
    saveShapeFiles(fileName, userId, shapeWriter, pathToFilesToDownlaod)

def generarShapeLineaHogarCentroCaminando(fields, individuos, fileName, userId, pathToFilesToDownlaod):
    lineParts = []
    shapeWriter = shapefile.Writer(shapefile.POLYLINE)
    #shapeWriter.autoBalance = 1 #Descomentar en release
    shapeWriter = createShapeFields(shapeWriter,fields)
    for individuo in individuos:
        centroOptimo = IndividuoCentroOptimo.objects.get(individuo = individuo)
        xCoordHogar,yCoordHogar = individuo.hogar.x_coord, individuo.hogar.y_coord
        xCoordCentroCaminando,yCoordCentroCaminando = centroOptimo.centroOptimoCaminando.x_coord, centroOptimo.centroOptimoCaminando.y_coord
        lineParts.append([[xCoordHogar,yCoordHogar],[xCoordCentroCaminando,yCoordCentroCaminando]])
        shapeWriter.record(individuo.id, centroOptimo.centroOptimoCaminando.id_centro, secondsToMinsRounded(centroOptimo.tHogarCentroCaminando))
        shapeWriter.line(parts=lineParts)
        lineParts=[]
    saveShapeFiles(fileName, userId, shapeWriter, pathToFilesToDownlaod)

def createShapeFields(shapeWriter,fields):
    for field in fields:
        shapeWriter.field(field)
    return shapeWriter

def secondsToMinsRounded(timeInSeconds):
    return round(timeInSeconds/60,2)

def llegaToCsv(path):
    individuosLlega = []
    with open(path, newline='') as csvfile:
        aFile = csv.reader(csvfile, delimiter=',', quotechar='|')
        removeCsvHeader(aFile)
        for indivudoCentroDiaHora in aFile:
            if(llega(indivudoCentroDiaHora)):
                individuosLlega.append(indivudoCentroDiaHora)
        print(len(individuosLlega))
    temporalFilePath = writeCsvFile(individuosLlega)
    return temporalFilePath

def llega(indivudoCentroDiaHora):
    if(indivudoCentroDiaHora[-1]=='Si'):
        return True
    return False

def writeCsvFile(afile):
    baseDirectory = settings.BASE_DIR + '/app/data/shpOut/'
    utils.createFolder(baseDirectory)
    path = settings.BASE_DIR + '/app/data/shpOut/Llega.csv'
    with open(path, 'w', newline='') as temporalFile:
        writer = csv.writer(temporalFile)
        writer.writerows(afile)
    return path

def generarShape(request,userId,pathToSourceData):
    baseDirectory = settings.BASE_DIR + '/app/data/users/user'+userId+'/shpOut/'
    utils.createFolder(baseDirectory)
    utils.cleanAllFolderFiles(settings.BASE_DIR + '/app/data/users/user'+userId+'/shpOut/')
    values = request.GET
    xyCoordCentrosDictionary = getIDCentroXYCoordDictionary(Centro.objects.all())
    individuos = Individuo.objects.all()
    pathToFilesToDownlaod = []
    if('generar_llega' in values):
        path = pathToSourceData+'.csv'
        temporalFilePath = llegaToCsv(path)
        generarShapeLlega(temporalFilePath, ['IDHogar','IDCentro','IDPrestador','Transporte','DiasLlega','Hora','TiempoDeViaje','CantidadDePediatras'],xyCoordCentrosDictionary,'Llega', userId, pathToFilesToDownlaod)
    if('generar_resumen_llega' in values):
        path = pathToSourceData+'.csv'
        temporalFilePath = llegaToCsv(path)
        generarResumenLlega(temporalFilePath,['IDHogar','IDCentro','CantidadLlega'],xyCoordCentrosDictionary,'LlegaResumido', userId, pathToFilesToDownlaod)
    if('generar_hogares' in  values):
        generarShapeHogares(['IDHogar'], individuos, 'Hogares', userId, pathToFilesToDownlaod)
    if('generar_jardines' in  values):
        generarShapeJardines(['IDHogar','HoraInicio','HoraFin'], individuos, 'Jardines', userId, pathToFilesToDownlaod)
    if('generar_trabajos' in  values):
        generarShapeTrabajos(['IDHogar','HoraInicio','HoraFin'], individuos, 'Trabajos', userId, pathToFilesToDownlaod)
    if('generar_autos' in  values):
        generarShapeCentroOptimoAuto(['IDHogar','IDCentroOptimoAuto','TiempoAuto'], individuos, 'CentrosOptimosAuto', userId, pathToFilesToDownlaod)
    if('generar_omnibus' in  values):
        generarShapeCentroOptimoOmnibus(['IDHogar','IDCentroOptimoOmnibus','TiempoOmnibus'], individuos, 'CentrosOptimosOmnibus', userId, pathToFilesToDownlaod)
    if('generar_caminando' in  values):
        generarShapeCentroOptimoCaminando(['IDHogar','IDCentroOptimoCaminando','TiempoCaminando'], individuos, 'CentrosOptimosCaminando', userId, pathToFilesToDownlaod)
    if('generar_hogar_autos' in  values):
        generarShapeLineaHogarCentroAuto(['IDHogar','IDCentroOptimoAuto','TiempoAuto'], individuos, 'LineaHogarCentrosOptimosAuto', userId, pathToFilesToDownlaod)
    if('generar_hogar_omnibus' in  values):
        genrerarShapeLineaHogarCentroOmnibus(['IDHogar','IDCentroOptimoOmnibus','TiempoOmnibus'], individuos, 'LineaHogarCentrosOptimosOmnibus', userId, pathToFilesToDownlaod)
    if('generar_hogar_caminando' in  values):
        generarShapeLineaHogarCentroCaminando(['IDHogar','IDCentroOptimoCaminando','TiempoCaminando'], individuos, 'LineaHogarCentrosOptimosCaminando', userId, pathToFilesToDownlaod)
    return pathToFilesToDownlaod

def removeCsvHeader(aFile):
    next(aFile)
    return aFile

