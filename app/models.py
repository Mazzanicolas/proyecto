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

class Centro(models.Model):
    id_centro = models.IntegerField(primary_key = True)
    x_coord = models.FloatField()
    y_coord = models.FloatField()
    sector = models.ForeignKey('Sector', models.SET_NULL,blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    prestador = models.ForeignKey('Prestador', models.CASCADE)

class Settings(models.Model):
    setting = models.CharField(primary_key=True, max_length=100)
    value = models.CharField(max_length=100, blank=True, null=True)

class Individuo(models.Model):
    id = models.IntegerField(primary_key=True)
    tipo_transporte = models.ForeignKey('TipoTransporte', models.DO_NOTHING)
    prestador = models.ForeignKey('Prestador', models.CASCADE)
    hogar = models.ForeignKey(AnclaTemporal, models.CASCADE, related_name='hogar')
    trabajo = models.ForeignKey(AnclaTemporal, models.SET_NULL, blank=True, null=True,related_name='trabajo')
    jardin = models.ForeignKey(AnclaTemporal, models.SET_NULL, blank=True, null=True,related_name='jardin')


class IndividuoTiempoCentro(models.Model):
    individuo = models.ForeignKey(Individuo, models.CASCADE)
    centro = models.ForeignKey(Centro, models.CASCADE)
    dia = models.IntegerField()
    hora = models.IntegerField()
    tiempo_caminando = models.IntegerField(blank=True, null=True)
    tiempo_omnibus = models.IntegerField(blank=True, null=True)
    tiempo_auto = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (('individuo', 'centro', 'dia', 'hora'),)

class Pediatra(models.Model):
    centro = models.ForeignKey(Centro, models.CASCADE)
    dia = models.IntegerField()
    hora = models.IntegerField()
    cantidad_pediatras = models.IntegerField()

    class Meta:
        unique_together = (('centro', 'dia', 'hora'),)


class Prestador(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)

class Sector(models.Model):
    x_centroide = models.IntegerField()
    y_centroide = models.IntegerField()
    tipo_sector = models.IntegerField()
    id_shape = models.IntegerField()

class SectorTiempo(models.Model):
    sector_1 = models.ForeignKey(Sector, models.CASCADE,related_name='sector_1')
    sector_2 = models.ForeignKey(Sector, models.CASCADE,related_name='sector_2')
    tiempo = models.IntegerField()
    distancia = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (('sector_1', 'sector_2'),)


class TipoTransporte(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
