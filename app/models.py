from django.db import models

# Create your models here.
class Sector(models.Model):
    x_centroide = models.FloatField(blank=True, null=True)
    y_centroide = models.FloatField(blank=True, null=True)
    id_shape = models.IntegerField(blank=True, null=True)
    tipoSector = models.IntegerField(blank=True, null=True)
    sectors = models.ManyToManyField(
        'self',
        through='SectorTiempo',
        symmetrical=False,
    )
    
class TipoLugar(models.Model):
    id_tipoLugar = models.IntegerField(primary_key = True)
    nombre = models.CharField(max_length = 100)

    class Meta:
        unique_together = (('id_tipoLugar', 'nombre'),)

class Lugar(models.Model):
    x_coord = models.FloatField()
    y_coord = models.FloatField()
    id_tipoLugar = models.ForeignKey(TipoLugar,on_delete = models.CASCADE, related_name = 'id_tipo_lugar')
    id_sector_aut = models.ForeignKey('Sector', models.DO_NOTHING, db_column='id_sector_aut',related_name = "sector_auto")
    id_sector_cam = models.ForeignKey('Sector', models.DO_NOTHING, db_column='id_sector_cam', related_name = 'sector_caminando')

class Prestador(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)
    centros = models.ManyToManyField(
        Lugar,
        through='LugarPrestador',
        symmetrical=False,
    )
class SectorTiempo(models.Model):
    sector1 = models.ForeignKey(Sector, on_delete=models.CASCADE,related_name='origen')
    sector2 = models.ForeignKey(Sector, on_delete=models.CASCADE,related_name='destino')
    time = models.FloatField()

class Individuo(models.Model):
    tipo_transporte = models.IntegerField(blank=True, null=True)
    id_prestador = models.ForeignKey(Prestador, models.DO_NOTHING, db_column='id_prestador', blank=True, null=True)
    id_hogar = models.ForeignKey(Lugar, models.DO_NOTHING, db_column='id_hogar', blank=True, null=True, related_name='id_hogar')
    id_trabajo = models.ForeignKey(Lugar, models.DO_NOTHING, db_column='id_trabajo', blank=True, null=True,related_name='id_trabajo')
    id_jardin = models.ForeignKey(Lugar, models.DO_NOTHING, db_column='id_jardin', blank=True, null=True,related_name='id_jardin')
    centros = models.ManyToManyField(
        Lugar,
        through='IndividuoTiempoCentro',
        symmetrical=False,
        related_name = 'centros',
    )
    anclas = models.ManyToManyField(
        Lugar,
        through='AnclaTemporal',
        symmetrical=False,
        related_name = 'anclas',

    )

class IndividuoTiempoCentro(models.Model):
    id_individuo = models.ForeignKey(Individuo, models.DO_NOTHING, db_column='id_individuo', related_name = 'id_individuo')
    id_centro = models.ForeignKey(Lugar, models.DO_NOTHING, db_column='id_centro',related_name ='id_centro')
    dia = models.IntegerField()
    hora = models.IntegerField()
    tiempo_caminando = models.IntegerField(blank=True, null=True)
    tiempo_auto = models.IntegerField(blank=True, null=True)
    tiempo_omnibus = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (('id_individuo', 'id_centro', 'dia', 'hora'),)


class AnclaTemporal(models.Model):
    id_individuo = models.ForeignKey(Individuo, models.DO_NOTHING, db_column='id_individuo', related_name = 'id_individuoAncla')
    id_lugar = models.ForeignKey(Lugar, models.DO_NOTHING, db_column='id_lugar', related_name='id_lugarAncla')
    dia = models.IntegerField()
    horaInicio = models.FloatField(blank=True,null=True)
    horaFin = models.FloatField(blank=True,null=True)

    class Meta:
        unique_together = (('id_individuo', 'id_lugar', 'dia'),)
class TipoTransporte(models.Model):
    id_tipoTransporte = models.IntegerField(primary_key = True)
    nombre = models.CharField(max_length=100)

    class Meta:
        unique_together = (('id_tipoTransporte', 'nombre'),)

class LugarPrestador(models.Model):
    id_prestador = models.ForeignKey(Prestador, models.DO_NOTHING, db_column='id_prestador')
    id_lugar = models.ForeignKey(Lugar, models.DO_NOTHING, db_column='id_lugar')
    dia = models.IntegerField()
    hora = models.IntegerField()
    cant_pediatras = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (('id_prestador', 'id_lugar', 'dia', 'hora'),)
