# Generated by Django 2.0.2 on 2018-02-26 04:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnclaTemporal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x_coord', models.FloatField()),
                ('y_coord', models.FloatField()),
                ('tipo', models.CharField(max_length=100)),
                ('hora_inicio', models.IntegerField(blank=True, null=True)),
                ('hora_fin', models.IntegerField(blank=True, null=True)),
                ('dias', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Centro',
            fields=[
                ('id_centro', models.IntegerField(primary_key=True, serialize=False)),
                ('x_coord', models.FloatField()),
                ('y_coord', models.FloatField()),
            ],
            options={
                'ordering': ['id_centro'],
            },
        ),
        migrations.CreateModel(
            name='Individuo',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('tieneJardin', models.BooleanField()),
                ('tieneTrabajo', models.BooleanField()),
                ('hogar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hogar', to='app.AnclaTemporal')),
                ('jardin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='jardin', to='app.AnclaTemporal')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='IndividuoCentro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tHogarCentroAuto', models.IntegerField(null=True)),
                ('tHogarTrabajoAuto', models.IntegerField(null=True)),
                ('tHogarJardinAuto', models.IntegerField(null=True)),
                ('tCentroHogarAuto', models.IntegerField(null=True)),
                ('tCentroJardinAuto', models.IntegerField(null=True)),
                ('tTrabajoJardinAuto', models.IntegerField(null=True)),
                ('tTrabajoHogarAuto', models.IntegerField(null=True)),
                ('tJardinHogarAuto', models.IntegerField(null=True)),
                ('tJardinTrabajoAuto', models.IntegerField(null=True)),
                ('tJardinCentroAuto', models.IntegerField(null=True)),
                ('tHogarCentroCaminando', models.IntegerField(null=True)),
                ('tHogarTrabajoCaminando', models.IntegerField(null=True)),
                ('tHogarJardinCaminando', models.IntegerField(null=True)),
                ('tCentroHogarCaminando', models.IntegerField(null=True)),
                ('tCentroJardinCaminando', models.IntegerField(null=True)),
                ('tTrabajoJardinCaminando', models.IntegerField(null=True)),
                ('tTrabajoHogarCaminando', models.IntegerField(null=True)),
                ('tJardinHogarCaminando', models.IntegerField(null=True)),
                ('tJardinTrabajoCaminando', models.IntegerField(null=True)),
                ('tJardinCentroCaminando', models.IntegerField(null=True)),
                ('tHogarCentroBus', models.IntegerField(null=True)),
                ('tHogarTrabajoBus', models.IntegerField(null=True)),
                ('tHogarJardinBus', models.IntegerField(null=True)),
                ('tCentroHogarBus', models.IntegerField(null=True)),
                ('tCentroJardinBus', models.IntegerField(null=True)),
                ('tTrabajoJardinBus', models.IntegerField(null=True)),
                ('tTrabajoHogarBus', models.IntegerField(null=True)),
                ('tJardinHogarBus', models.IntegerField(null=True)),
                ('tJardinTrabajoBus', models.IntegerField(null=True)),
                ('tJardinCentroBus', models.IntegerField(null=True)),
                ('centro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Centro')),
                ('individuo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Individuo')),
            ],
            options={
                'ordering': ['individuo', 'centro'],
            },
        ),
        migrations.CreateModel(
            name='IndividuoCentroOptimo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tHogarCentroAuto', models.IntegerField(null=True)),
                ('tHogarCentroCaminando', models.IntegerField(null=True)),
                ('tHogarCentroOmnibus', models.IntegerField(null=True)),
                ('centroOptimoAuto', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='centroOptimoAuto', to='app.Centro')),
                ('centroOptimoCaminando', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='centroOptimoCaminando', to='app.Centro')),
                ('centroOptimoOmnibus', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='centroOptimoOmnibus', to='app.Centro')),
                ('individuo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Individuo')),
            ],
        ),
        migrations.CreateModel(
            name='IndividuoTiempoCentro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.IntegerField()),
                ('hora', models.IntegerField()),
                ('tiempoViaje', models.IntegerField(blank=True, null=True)),
                ('cantidad_pediatras', models.IntegerField(null=True)),
                ('llegaGeografico', models.CharField(blank=True, max_length=20, null=True)),
                ('llega', models.CharField(blank=True, max_length=20, null=True)),
                ('centro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Centro')),
                ('individuo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Individuo')),
            ],
            options={
                'ordering': ['individuo', 'centro', 'dia', 'hora'],
            },
        ),
        migrations.CreateModel(
            name='MedidasDeResumen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidadTotalHoras', models.IntegerField()),
                ('cantidadHorasLunes', models.IntegerField()),
                ('cantidadHorasMartes', models.IntegerField()),
                ('cantidadHorasMiercoles', models.IntegerField()),
                ('cantidadHorasJueves', models.IntegerField()),
                ('cantidadHorasViernes', models.IntegerField()),
                ('cantidadHorasSabado', models.IntegerField()),
                ('cantidadMaximaHoras', models.IntegerField()),
                ('cantidadConsultasLunes', models.IntegerField()),
                ('cantidadConsultasMartes', models.IntegerField()),
                ('cantidadConsultasMiercoles', models.IntegerField()),
                ('cantidadConsultasJueves', models.IntegerField()),
                ('cantidadConsultasViernes', models.IntegerField()),
                ('cantidadConsultasSabado', models.IntegerField()),
                ('cantidadTotalConsultas', models.IntegerField()),
                ('cantidadCentrosLunes', models.IntegerField()),
                ('cantidadCentrosMartes', models.IntegerField()),
                ('cantidadCentrosMiercoles', models.IntegerField()),
                ('cantidadCentrosJueves', models.IntegerField()),
                ('cantidadCentrosViernes', models.IntegerField()),
                ('cantidadCentrosSabado', models.IntegerField()),
                ('cantidadTotalCentros', models.IntegerField()),
                ('centroOptimo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Centro')),
                ('persona', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Individuo')),
            ],
            options={
                'ordering': ['persona'],
            },
        ),
        migrations.CreateModel(
            name='Pediatra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.IntegerField()),
                ('hora', models.IntegerField()),
                ('cantidad_pediatras', models.IntegerField()),
                ('centro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Centro')),
            ],
            options={
                'ordering': ['centro', 'dia', 'hora'],
            },
        ),
        migrations.CreateModel(
            name='Prestador',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='SectorAuto',
            fields=[
                ('shapeid', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('x_centroide', models.IntegerField()),
                ('y_centroide', models.IntegerField()),
                ('shapePosition', models.IntegerField()),
            ],
            options={
                'ordering': ['shapeid'],
            },
        ),
        migrations.CreateModel(
            name='SectorCaminando',
            fields=[
                ('shapeid', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('x_centroide', models.IntegerField()),
                ('y_centroide', models.IntegerField()),
                ('shapePosition', models.IntegerField()),
            ],
            options={
                'ordering': ['shapeid'],
            },
        ),
        migrations.CreateModel(
            name='SectorOmnibus',
            fields=[
                ('shapeid', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('x_centroide', models.IntegerField()),
                ('y_centroide', models.IntegerField()),
                ('shapePosition', models.IntegerField()),
            ],
            options={
                'ordering': ['shapeid'],
            },
        ),
        migrations.CreateModel(
            name='SectorTiempoAuto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tiempo', models.FloatField()),
                ('distancia', models.FloatField(blank=True, null=True)),
                ('sector_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sector_1', to='app.SectorAuto')),
                ('sector_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sector_2', to='app.SectorAuto')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='SectorTiempoCaminando',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tiempo', models.FloatField()),
                ('distancia', models.FloatField(blank=True, null=True)),
                ('sector_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sectorCaminando_1', to='app.SectorCaminando')),
                ('sector_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sectorCaminando_2', to='app.SectorCaminando')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='SectorTiempoOmnibus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tiempo', models.FloatField()),
                ('sectorO_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sectorO_1', to='app.SectorOmnibus')),
                ('sectorO_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sectorO_2', to='app.SectorOmnibus')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('setting', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('value', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TipoTransporte',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='individuo',
            name='prestador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Prestador'),
        ),
        migrations.AddField(
            model_name='individuo',
            name='tipo_transporte',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='app.TipoTransporte'),
        ),
        migrations.AddField(
            model_name='individuo',
            name='trabajo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trabajo', to='app.AnclaTemporal'),
        ),
        migrations.AddField(
            model_name='centro',
            name='prestador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Prestador'),
        ),
        migrations.AddField(
            model_name='centro',
            name='sector_auto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sectorCentro_auto', to='app.SectorAuto'),
        ),
        migrations.AddField(
            model_name='centro',
            name='sector_bus',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sectorCentro_omnibus', to='app.SectorOmnibus'),
        ),
        migrations.AddField(
            model_name='centro',
            name='sector_caminando',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sectorCentro_caminando', to='app.SectorCaminando'),
        ),
        migrations.AddField(
            model_name='anclatemporal',
            name='sector_auto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sector_auto', to='app.SectorAuto'),
        ),
        migrations.AddField(
            model_name='anclatemporal',
            name='sector_bus',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sector_omnibus', to='app.SectorOmnibus'),
        ),
        migrations.AddField(
            model_name='anclatemporal',
            name='sector_caminando',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sector_caminando', to='app.SectorCaminando'),
        ),
        migrations.AlterUniqueTogether(
            name='sectortiempoomnibus',
            unique_together={('sectorO_1', 'sectorO_2')},
        ),
        migrations.AlterUniqueTogether(
            name='sectortiempocaminando',
            unique_together={('sector_1', 'sector_2')},
        ),
        migrations.AlterUniqueTogether(
            name='sectortiempoauto',
            unique_together={('sector_1', 'sector_2')},
        ),
        migrations.AlterUniqueTogether(
            name='pediatra',
            unique_together={('centro', 'dia', 'hora')},
        ),
        migrations.AlterUniqueTogether(
            name='individuotiempocentro',
            unique_together={('individuo', 'centro', 'dia', 'hora')},
        ),
        migrations.AlterUniqueTogether(
            name='individuocentro',
            unique_together={('individuo', 'centro')},
        ),
    ]
