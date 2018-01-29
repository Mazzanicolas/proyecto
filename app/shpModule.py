import shapefile
from   app.models import Individuo, IndividuoCentroOptimo, Centro
from   shapely    import geometry

def generarShape(values,idRange,idName):
    cache = []
    files = []
    Individuos = Individuo.objects.filter(id__gte = idRange[0],id__lte = idRange[1])
    #POINTS HOGARES
    if('generar_hogares' in  values):
        w = shapefile.Writer(shapefile.POINT)
        #w.autoBalance = 1 //Descomentar en release
        w.field('IDHogar')
        for individuo in Individuos:
            x1,y1 = individuo.hogar.x_coord, individuo.hogar.y_coord
            w.point(x1, y1)
            w.record(individuo.id)
        w.save('app/files/shpOut/hogares'+idName)
        w = shapefile.Writer(shapefile.POINT)
        files.extend(['app/files/shpOut/hogares'+idName+'.shp','app/files/shpOut/hogares'+idName+'.shx','app/files/shpOut/hogares'+idName+'.dbf'])
    ###WIP VVV
    #POINTS HOGARES
    if('generar_jardines' in  values):
        w = shapefile.Writer(shapefile.POINT)
        #w.autoBalance = 1 //Descomentar en release
        w.field('IDHogar')
        w.field('HoraInicio')
        w.field('HoraFin')
        for individuo in Individuos:
            if(individuo.tieneJardin):
                x1,y1 = individuo.jardin.x_coord, individuo.jardin.y_coord
                w.point(x1, y1)
                w.record(individuo.id,individuo.jardin.hora_inicio,individuo.jardin.hora_fin)
        w.save('app/files/shpOut/jardines'+idName)
        w = shapefile.Writer(shapefile.POINT)
        files.extend(['app/files/shpOut/jardines'+idName+'.shp','app/files/shpOut/jardines'+idName+'.shx','app/files/shpOut/jardines'+idName+'.dbf'])
    if('generar_trabajos' in  values):
        w = shapefile.Writer(shapefile.POINT)
        #w.autoBalance = 1 //Descomentar en release
        w.field('IDHogar')
        w.field('HoraInicio')
        w.field('HoraFin')
        for individuo in Individuos:
            if(individuo.tieneTrabajo):
                x1,y1 = individuo.trabajo.x_coord, individuo.trabajo.y_coord
                w.point(x1, y1)
                w.record(individuo.id,individuo.trabajo.hora_inicio,individuo.trabajo.hora_fin)
        w.save('app/files/shpOut/trabajos'+idName)
        w = shapefile.Writer(shapefile.POINT)
        files.extend(['app/files/shpOut/trabajos'+idName+'.shp','app/files/shpOut/trabajos'+idName+'.shx','app/files/shpOut/trabajos'+idName+'.dbf'])
    ###WIP ^^^
    #POINTS CENTROS OPTIMOS AUTO
    if('generar_autos' in  values):
        w = shapefile.Writer(shapefile.POINT)
        #w.autoBalance = 1 #Descomentar en release
        w.field('IDHogar')
        w.field('IDCentroOptimoAuto')
        w.field('TiempoAuto')
        for individuo in Individuos:
            CentroOpt = IndividuoCentroOptimo.objects.get(individuo = individuo)
            x1,y1     = CentroOpt.centroOptimoAuto.x_coord, CentroOpt.centroOptimoAuto.y_coord
            w.point(x1, y1)
            w.record(individuo.id, CentroOpt.centroOptimoAuto.id_centro, CentroOpt.tHogarCentroAuto)
        w.save('app/files/shpOut/centrosOptimosAuto'+idName)
        w = shapefile.Writer(shapefile.POINT)
        files.extend(['app/files/shpOut/centrosOptimosAuto'+idName+'.shp','app/files/shpOut/centrosOptimosAuto'+idName+'.shx','app/files/shpOut/centrosOptimosAuto'+idName+'.dbf'])
    #POINTS CENTROS OPTIMOS OMNIBUS
    if('generar_omnibus' in  values):
        w = shapefile.Writer(shapefile.POINT)
        #w.autoBalance = 1 #Descomentar en release
        w.field('IDHogar')
        w.field('IDCentroOptimoOmnibus')
        w.field('TiempoOmnibus')
        for individuo in Individuos:
            CentroOpt = IndividuoCentroOptimo.objects.get(individuo = individuo)
            x1,y1     = CentroOpt.centroOptimoOmnibus.x_coord, CentroOpt.centroOptimoOmnibus.y_coord
            w.point(x1, y1)
            w.record(individuo.id, CentroOpt.centroOptimoOmnibus.id_centro, CentroOpt.tHogarCentroOmnibus)
        w.save('app/files/shpOut/centrosOptimosOmnibus'+idName)
        w = shapefile.Writer(shapefile.POINT)
        files.extend(['app/files/shpOut/centrosOptimosOmnibus'+idName+'.shp','app/files/shpOut/centrosOptimosOmnibus'+idName+'.shx','app/files/shpOut/centrosOptimosOmnibus'+idName+'.dbf'])
    #POINTS CENTROS OPTIMOS CAMINANDO
    if('generar_caminando' in  values):
        w = shapefile.Writer(shapefile.POINT)
        #w.autoBalance = 1 #Descomentar en release
        w.field('IDHogar')
        w.field('IDCentroOptimoCaminando')
        w.field('TiempoCaminando')
        for individuo in Individuos:
            CentroOpt = IndividuoCentroOptimo.objects.get(individuo = individuo)
            x1,y1     = CentroOpt.centroOptimoCaminando.x_coord, CentroOpt.centroOptimoCaminando.y_coord
            w.point(x1, y1)
            w.record(individuo.id, CentroOpt.centroOptimoCaminando.id_centro, CentroOpt.tHogarCentroCaminando)
        w.save('app/files/shpOut/centrosOptimosCaminando'+idName)
        w = shapefile.Writer(shapefile.POINT)
        files.extend(['app/files/shpOut/centrosOptimosCaminando'+idName+'.shp','app/files/shpOut/centrosOptimosCaminando'+idName+'.shx','app/files/shpOut/centrosOptimosCaminando'+idName+'.dbf'])
    #LINES HOGAR <---> CENTROS OPTIMOS AUTO
    if('generar_hogar_autos' in  values):
        lineParts = []
        w = shapefile.Writer(shapefile.POLYLINE)
        #w.autoBalance = 1 #Descomentar en release
        w.field('IDHogar')
        w.field('IDCentroOptimoAuto')
        w.field('TiempoAuto')
        for individuo in Individuos:
            CentroOpt = IndividuoCentroOptimo.objects.get(individuo = individuo)
            x1,y1     = individuo.hogar.x_coord, individuo.hogar.y_coord
            x2,y2     = CentroOpt.centroOptimoAuto.x_coord, CentroOpt.centroOptimoAuto.y_coord
            lineParts.append([[x1,y1],[x2,y2]])
            w.record(individuo.id, CentroOpt.centroOptimoAuto.id_centro, CentroOpt.tHogarCentroAuto)
            w.line(parts=lineParts)
            lineParts=[]
        w.save('app/files/shpOut/lineaHogaresCentroOptimoAuto'+idName)
        files.extend(['app/files/shpOut/lineaHogaresCentroOptimoAuto'+idName+'.shp','app/files/shpOut/lineaHogaresCentroOptimoAuto'+idName+'.shx','app/files/shpOut/lineaHogaresCentroOptimoAuto'+idName+'.dbf'])
    #LINES HOGAR <---> CENTROS OPTIMOS OMNIBUS
    if('generar_hogar_omnibus' in  values):
        lineParts = []
        w = shapefile.Writer(shapefile.POLYLINE)
        #w.autoBalance = 1 #Descomentar en release
        w.field('IDHogar')
        w.field('IDCentroOptimoOmnibus')
        w.field('TiempoOmnibus')
        for individuo in Individuos:
            CentroOpt = IndividuoCentroOptimo.objects.get(individuo = individuo)
            x1,y1     = individuo.hogar.x_coord, individuo.hogar.y_coord
            x2,y2     = CentroOpt.centroOptimoOmnibus.x_coord, CentroOpt.centroOptimoOmnibus.y_coord
            lineParts.append([[x1,y1],[x2,y2]])
            w.record(individuo.id, CentroOpt.centroOptimoOmnibus.id_centro, CentroOpt.tHogarCentroOmnibus)
            w.line(parts=lineParts)
            lineParts=[]
        w.save('app/files/shpOut/lineaHogaresCentroOptimoOmnibus'+idName)
        files.extend(['app/files/shpOut/lineaHogaresCentroOptimoOmnibus'+idName+'.shp','app/files/shpOut/lineaHogaresCentroOptimoOmnibus'+idName+'.shx','app/files/shpOut/lineaHogaresCentroOptimoOmnibus'+idName+'.dbf'])
    #LINES HOGAR <---> CENTROS OPTIMOS CAMINANDO
    if('generar_hogar_caminando' in  values):
        lineParts = []
        w = shapefile.Writer(shapefile.POLYLINE)
        #w.autoBalance = 1 #Descomentar en release
        w.field('IDHogar')
        w.field('IDCentroOptimoCaminando')
        w.field('TiempoCaminando')
        for individuo in Individuos:
            CentroOpt = IndividuoCentroOptimo.objects.get(individuo = individuo)
            x1,y1     = individuo.hogar.x_coord, individuo.hogar.y_coord
            x2,y2     = CentroOpt.centroOptimoCaminando.x_coord, CentroOpt.centroOptimoCaminando.y_coord
            lineParts.append([[x1,y1],[x2,y2]])
            w.record(individuo.id, CentroOpt.centroOptimoCaminando.id_centro, CentroOpt.tHogarCentroCaminando)
            w.line(parts=lineParts)
            lineParts=[]
        w.save('app/files/shpOut/lineaHogaresCentroOptimoCaminando'+idName)
        files.extend(['app/files/shpOut/lineaHogaresCentroOptimoCaminando'+idName+'.shp','app/files/shpOut/lineaHogaresCentroOptimoCaminando'+idName+'.shx','app/files/shpOut/lineaHogaresCentroOptimoCaminando'+idName+'.dbf'])

    return files
