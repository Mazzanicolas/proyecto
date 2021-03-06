from django.db import models
import math
# Create your models here.

class AnclaTemporal(models.Model):
    x_coord          = models.FloatField()
    y_coord          = models.FloatField()
    tipo             = models.CharField(max_length=100)
    hora_inicio      = models.IntegerField(blank=True, null=True)
    hora_fin         = models.IntegerField(blank=True, null=True)
    dias             = models.CharField(max_length = 20)
    sector_auto      = models.ForeignKey('SectorAuto', models.CASCADE,blank=True, null=True,related_name='sector_auto')
    sector_caminando = models.ForeignKey('SectorCaminando', models.CASCADE,blank=True, null=True,related_name='sector_caminando')
    sector_bus       = models.ForeignKey('SectorOmnibus', models.CASCADE,blank=True, null=True,related_name='sector_omnibus')

class Centro(models.Model):
    id_centro        = models.IntegerField(primary_key = True)
    x_coord          = models.FloatField()
    y_coord          = models.FloatField()
    sector_auto      = models.ForeignKey('SectorAuto', models.CASCADE,blank=True, null=True,related_name='sectorCentro_auto')
    sector_caminando = models.ForeignKey('SectorCaminando', models.CASCADE, blank=True, null=True,related_name='sectorCentro_caminando')
    sector_bus       = models.ForeignKey('SectorOmnibus', models.CASCADE,blank=True, null=True,related_name='sectorCentro_omnibus')
    prestador        = models.ForeignKey('Prestador', models.CASCADE)

    class Meta:
        ordering = ['id_centro']

class Settings(models.Model):
    setting = models.CharField(primary_key=True, max_length=100)
    value   = models.CharField(max_length=100,   blank=True, null=True)

class Individuo(models.Model):
    id = models.IntegerField(primary_key=True)
    tipo_transporte = models.ForeignKey('TipoTransporte', models.DO_NOTHING)
    tieneJardin     = models.BooleanField()
    tieneTrabajo    = models.BooleanField()
    prestador       = models.ForeignKey('Prestador', models.CASCADE)
    hogar           = models.ForeignKey(AnclaTemporal, models.CASCADE, related_name='hogar')
    trabajo         = models.ForeignKey(AnclaTemporal, models.CASCADE, blank = True, null = True, related_name = 'trabajo')
    jardin          = models.ForeignKey(AnclaTemporal, models.CASCADE, blank = True, null = True, related_name = 'jardin')

    class Meta:
        ordering = ['id']

class IndividuoCentro(models.Model):
    individuo               = models.ForeignKey(Individuo, models.CASCADE)
    centro                  = models.ForeignKey(Centro,    models.CASCADE)
    tHogarCentroAuto        = models.IntegerField(null = True)
    tHogarTrabajoAuto       = models.IntegerField(null = True)
    tHogarJardinAuto        = models.IntegerField(null = True)
    tCentroHogarAuto        = models.IntegerField(null = True)
    tCentroJardinAuto       = models.IntegerField(null = True)
    tTrabajoJardinAuto      = models.IntegerField(null = True)
    tTrabajoHogarAuto       = models.IntegerField(null = True)
    tJardinHogarAuto        = models.IntegerField(null = True)
    tJardinTrabajoAuto      = models.IntegerField(null = True)
    tJardinCentroAuto       = models.IntegerField(null = True)
    tHogarCentroCaminando   = models.IntegerField(null = True)
    tHogarTrabajoCaminando  = models.IntegerField(null = True)
    tHogarJardinCaminando   = models.IntegerField(null = True)
    tCentroHogarCaminando   = models.IntegerField(null = True)
    tCentroJardinCaminando  = models.IntegerField(null = True)
    tTrabajoJardinCaminando = models.IntegerField(null = True)
    tTrabajoHogarCaminando  = models.IntegerField(null = True)
    tJardinHogarCaminando   = models.IntegerField(null = True)
    tJardinTrabajoCaminando = models.IntegerField(null = True)
    tJardinCentroCaminando  = models.IntegerField(null = True)
    tHogarCentroBus         = models.IntegerField(null = True)
    tHogarTrabajoBus        = models.IntegerField(null = True)
    tHogarJardinBus         = models.IntegerField(null = True)
    tCentroHogarBus         = models.IntegerField(null = True)
    tCentroJardinBus        = models.IntegerField(null = True)
    tTrabajoJardinBus       = models.IntegerField(null = True)
    tTrabajoHogarBus        = models.IntegerField(null = True)
    tJardinHogarBus         = models.IntegerField(null = True)
    tJardinTrabajoBus       = models.IntegerField(null = True)
    tJardinCentroBus        = models.IntegerField(null = True)
    class Meta:
        ordering        = ['individuo',  'centro']
        unique_together = (('individuo', 'centro'),)

class IndividuoTiempoCentro(models.Model):
    individuo          = models.ForeignKey(Individuo, models.CASCADE)
    centro             = models.ForeignKey(Centro,    models.CASCADE)
    dia                = models.IntegerField()
    hora               = models.IntegerField()
    tiempoViaje        = models.IntegerField(blank=True, null=True)
    cantidad_pediatras = models.IntegerField(null=True)
    llegaGeografico    = models.CharField(max_length = 20, blank=True, null=True)
    llega              = models.CharField(max_length = 20, blank=True, null=True)
    class Meta:
        ordering        = ['individuo','centro','dia','hora']
        unique_together = (('individuo', 'centro', 'dia', 'hora'),)

class Pediatra(models.Model):
    centro             = models.ForeignKey(Centro, models.CASCADE)
    dia                = models.IntegerField()
    hora               = models.IntegerField()
    cantidad_pediatras = models.IntegerField()

    class Meta:
        unique_together = (('centro', 'dia', 'hora'),)
        ordering        = ['centro', 'dia','hora']


class Prestador(models.Model):
    id     = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return u'{0}'.format(self.nombre)
    class Meta:
        ordering = ['id']

class SectorAuto(models.Model):
    shapeid       = models.CharField(max_length = 50,primary_key=True)
    x_centroide   = models.IntegerField()
    y_centroide   = models.IntegerField()
    shapePosition = models.IntegerField()
    class Meta:
        ordering = ['shapeid']
    def __str__(self):
        return u'{0}'.format(self.shapeid)

class SectorCaminando(models.Model):
    shapeid       = models.CharField(max_length = 50, primary_key=True)
    x_centroide   = models.IntegerField()
    y_centroide   = models.IntegerField()
    shapePosition = models.IntegerField()
    class Meta:
        ordering = ['shapeid']
    def __str__(self):
        return u'{0}'.format(self.shapeid)
        
class SectorOmnibus(models.Model):
    shapeid       = models.CharField(max_length = 50, primary_key=True)
    x_centroide   = models.IntegerField()
    y_centroide   = models.IntegerField()
    shapePosition = models.IntegerField()
    class Meta:
        ordering = ['shapeid']
    def __str__(self):
        return u'{0}'.format(self.shapeid)
class SectorTiempoAuto(models.Model):
    sector_1  = models.ForeignKey(SectorAuto, models.CASCADE, blank=True, null=True, related_name='sector_1')
    sector_2  = models.ForeignKey(SectorAuto, models.CASCADE, blank=True, null=True, related_name='sector_2')
    tiempo    = models.FloatField()
    distancia = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = (('sector_1', 'sector_2'),)
        ordering        = ['id']
class SectorTiempoCaminando(models.Model):
    sector_1  = models.ForeignKey(SectorCaminando, models.CASCADE, blank=True, null=True, related_name='sectorCaminando_1')
    sector_2  = models.ForeignKey(SectorCaminando, models.CASCADE, blank=True, null=True, related_name='sectorCaminando_2')
    tiempo    = models.FloatField()
    distancia = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = (('sector_1', 'sector_2'),)
        ordering        = ['id']

class SectorTiempoOmnibus(models.Model):
    sectorO_1 = models.ForeignKey(SectorOmnibus, models.CASCADE, blank=True, null=True,related_name='sectorO_1')
    sectorO_2 = models.ForeignKey(SectorOmnibus, models.CASCADE, blank=True, null=True,related_name='sectorO_2')
    tiempo    = models.FloatField()
    class Meta:
        unique_together = (('sectorO_1', 'sectorO_2'),)
        ordering        = ['id']
    
class TipoTransporte(models.Model):
    id     = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return u'{0}'.format(self.nombre)
    class Meta:
        ordering = ['id']

class MedidasDeResumen(models.Model):
    persona = models.ForeignKey(Individuo, models.CASCADE)
    cantidadTotalHoras         = models.IntegerField()
    cantidadHorasLunes         = models.IntegerField()
    cantidadHorasMartes        = models.IntegerField()
    cantidadHorasMiercoles     = models.IntegerField()
    cantidadHorasJueves        = models.IntegerField()
    cantidadHorasViernes       = models.IntegerField()
    cantidadHorasSabado        = models.IntegerField()
    cantidadMaximaHoras        = models.IntegerField()
    cantidadConsultasLunes     = models.IntegerField()
    cantidadConsultasMartes    = models.IntegerField()
    cantidadConsultasMiercoles = models.IntegerField()
    cantidadConsultasJueves    = models.IntegerField()
    cantidadConsultasViernes   = models.IntegerField()
    cantidadConsultasSabado    = models.IntegerField()
    cantidadTotalConsultas     = models.IntegerField()
    cantidadCentrosLunes       = models.IntegerField()
    cantidadCentrosMartes      = models.IntegerField()
    cantidadCentrosMiercoles   = models.IntegerField()
    cantidadCentrosJueves      = models.IntegerField()
    cantidadCentrosViernes     = models.IntegerField()
    cantidadCentrosSabado      = models.IntegerField()
    cantidadTotalCentros       = models.IntegerField()
    centroOptimo = models.ForeignKey(Centro, models.CASCADE)

    class Meta:
        ordering = ['persona']

class IndividuoCentroOptimo(models.Model):
    individuo             = models.ForeignKey(Individuo, models.CASCADE)
    centroOptimoOmnibus   = models.ForeignKey(Centro, models.CASCADE, null=True, related_name='centroOptimoOmnibus')
    centroOptimoAuto      = models.ForeignKey(Centro, models.CASCADE, null=True, related_name='centroOptimoAuto')
    centroOptimoCaminando = models.ForeignKey(Centro, models.CASCADE, null=True, related_name='centroOptimoCaminando')
    tHogarCentroAuto      = models.IntegerField(null=True)
    tHogarCentroCaminando = models.IntegerField(null=True)
    tHogarCentroOmnibus   = models.IntegerField(null=True)
