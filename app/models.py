from django.db import models

# Create your models here.

class AnclaTemporal(models.Model):
    x_coord = models.FloatField()
    y_coord = models.FloatField()
    tipo = models.CharField(max_length=100)
    hora_inicio = models.IntegerField(blank=True, null=True)
    hora_fin = models.IntegerField(blank=True, null=True)
    dias = models.CharField(max_length = 20)
    sector_auto = models.ForeignKey('Sector', models.SET_NULL,blank=True, null=True,related_name='sector_auto')
    sector_caminando = models.ForeignKey('Sector', models.SET_NULL,blank=True, null=True,related_name='sector_caminando')
    parada = models.IntegerField(blank=True, null=True)

class Centro(models.Model):
    id_centro = models.IntegerField(primary_key = True)
    x_coord = models.FloatField()
    y_coord = models.FloatField()
    sector_auto = models.ForeignKey('Sector', models.SET_NULL,blank=True, null=True,related_name='sectorCentro_auto')
    sector_caminando = models.ForeignKey('Sector', models.SET_NULL,blank=True, null=True,related_name='sectorCentro_caminando')
    direccion = models.CharField(max_length=100, blank=True, null=True)
    prestador = models.ForeignKey('Prestador', models.CASCADE)
    parada = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['id_centro']

class Settings(models.Model):
    setting = models.CharField(primary_key=True, max_length=100)
    value = models.CharField(max_length=100, blank=True, null=True)

class Individuo(models.Model):
    id = models.IntegerField(primary_key=True)
    tipo_transporte = models.ForeignKey('TipoTransporte', models.DO_NOTHING)
    tieneJardin = models.BooleanField()
    tieneTrabajo = models.BooleanField()
    prestador = models.ForeignKey('Prestador', models.CASCADE)
    hogar = models.ForeignKey(AnclaTemporal, models.CASCADE, related_name='hogar')
    trabajo = models.ForeignKey(AnclaTemporal, models.SET_NULL, blank=True, null=True,related_name='trabajo')
    jardin = models.ForeignKey(AnclaTemporal, models.SET_NULL, blank=True, null=True,related_name='jardin')

    class Meta:
        ordering = ['id']

class IndividuoCentro(models.Model):
    individuo = models.ForeignKey(Individuo, models.CASCADE)
    centro    = models.ForeignKey(Centro, models.CASCADE)
    tiempoViajeAntesTrabajo = models.IntegerField(blank=True, null=True)
    tiempoViajeDespuesTrabajo = models.IntegerField(blank=True, null=True)
    tHogarCentro = models.IntegerField(null=True)
    tHogarTrabajo = models.IntegerField(null=True)
    tHogarJardin = models.IntegerField(null=True)
    tCentroHogar = models.IntegerField(null=True)
    tCentroJardin = models.IntegerField(null=True)
    tTrabajoJardin= models.IntegerField(null=True)
    tTrabajoHogar= models.IntegerField(null=True)
    tJardinTrabajo= models.IntegerField(null=True)
    tJardinCentro= models.IntegerField(null=True)
    class Meta:
        ordering = ['individuo','centro']
        unique_together = (('individuo', 'centro'),)

class IndividuoTiempoCentro(models.Model):
    individuo = models.ForeignKey(Individuo, models.CASCADE)
    centro    = models.ForeignKey(Centro, models.CASCADE)
    dia       = models.IntegerField()
    hora      = models.IntegerField()
    tiempoViaje = models.IntegerField(blank=True, null=True)
    cantidad_pediatras = models.IntegerField(null=True)
    llegaGeografico = models.CharField(max_length = 20,blank=True, null=True)
    class Meta:
        ordering = ['individuo','centro','dia','hora']
        unique_together = (('individuo', 'centro', 'dia', 'hora'),)

class Pediatra(models.Model):
    centro = models.ForeignKey(Centro, models.CASCADE)
    dia = models.IntegerField()
    hora = models.IntegerField()
    cantidad_pediatras = models.IntegerField()

    class Meta:
        unique_together = (('centro', 'dia', 'hora'),)
        ordering = ['centro', 'dia','hora']


class Prestador(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return u'{0}'.format(self.nombre)

class Sector(models.Model):
    x_centroide = models.IntegerField()
    y_centroide = models.IntegerField()
    tipo_sector = models.CharField(max_length = 20)
    shape = models.IntegerField()

class SectorTiempo(models.Model):
    sector_1 = models.ForeignKey(Sector, models.SET_NULL, blank=True, null=True,related_name='sector_1')
    sector_2 = models.ForeignKey(Sector, models.SET_NULL, blank=True, null=True,related_name='sector_2')
    tiempo = models.FloatField()
    distancia = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = (('sector_1', 'sector_2'),)

class SectorTiempoOmnibus(models.Model):
    sectorO_1 = models.ForeignKey(Sector, models.SET_NULL, blank=True, null=True,related_name='sectorO_1')
    sectorO_2 = models.ForeignKey(Sector, models.SET_NULL, blank=True, null=True,related_name='sectorO_2')
    tiempo = models.FloatField()
    class Meta:
        unique_together = (('sectorO_1', 'sectorO_2'),)

class TipoTransporte(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return u'{0}'.format(self.nombre)
class MedidasDeResumen(models.Model):
    persona = models.ForeignKey(Individuo, models.CASCADE)
    cantidadTotalHoras = models.IntegerField()
    cantidadHorasLunes = models.IntegerField()
    cantidadHorasMartes = models.IntegerField()
    cantidadHorasMiercoles = models.IntegerField()
    cantidadHorasJueves = models.IntegerField()
    cantidadHorasViernes = models.IntegerField()
    cantidadHorasSabado = models.IntegerField()
    cantidadMaximaHoras = models.IntegerField()
    cantidadConsultasLunes = models.IntegerField()
    cantidadConsultasMartes = models.IntegerField()
    cantidadConsultasMiercoles = models.IntegerField()
    cantidadConsultasJueves = models.IntegerField()
    cantidadConsultasViernes = models.IntegerField()
    cantidadConsultasSabado = models.IntegerField()
    cantidadTotalConsultas = models.IntegerField()
    cantidadCentrosLunes = models.IntegerField()
    cantidadCentrosMartes = models.IntegerField()
    cantidadCentrosMiercoles = models.IntegerField()
    cantidadCentrosJueves = models.IntegerField()
    cantidadCentrosViernes = models.IntegerField()
    cantidadCentrosSabado = models.IntegerField()
    cantidadTotalCentros = models.IntegerField()
    centroOptimo = models.ForeignKey(Centro, models.CASCADE)

    class Meta:
        ordering = ['persona']
