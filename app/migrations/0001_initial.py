# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-13 14:45
from __future__ import unicode_literals

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
                ('dia', models.IntegerField()),
                ('horaInicio', models.FloatField(blank=True, null=True)),
                ('horaFin', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Individuo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_transporte', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='IndividuoTiempoCentro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.IntegerField()),
                ('hora', models.IntegerField()),
                ('tiempo_caminando', models.IntegerField(blank=True, null=True)),
                ('tiempo_auto', models.IntegerField(blank=True, null=True)),
                ('tiempo_omnibus', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Lugar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x_coord', models.FloatField()),
                ('y_coord', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='LugarPrestador',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.IntegerField()),
                ('hora', models.IntegerField()),
                ('cant_pediatras', models.IntegerField(blank=True, null=True)),
                ('id_lugar', models.ForeignKey(db_column='id_lugar', on_delete=django.db.models.deletion.DO_NOTHING, to='app.Lugar')),
            ],
        ),
        migrations.CreateModel(
            name='Prestador',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=100, null=True)),
                ('centros', models.ManyToManyField(through='app.LugarPrestador', to='app.Lugar')),
            ],
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x_centroide', models.FloatField(blank=True, null=True)),
                ('y_centroide', models.FloatField(blank=True, null=True)),
                ('id_shape', models.IntegerField(blank=True, null=True)),
                ('tipoSector', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SectorTiempo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sector1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origen', to='app.Sector')),
                ('sector2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destino', to='app.Sector')),
                ('time', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='TipoLugar',
            fields=[
                ('id_tipoLugar', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TipoTransporte',
            fields=[
                ('id_tipoTransporte', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='tipotransporte',
            unique_together=set([('id_tipoTransporte', 'nombre')]),
        ),
        migrations.AlterUniqueTogether(
            name='tipolugar',
            unique_together=set([('id_tipoLugar', 'nombre')]),
        ),
        migrations.AddField(
            model_name='sector',
            name='sectors',
            field=models.ManyToManyField(through='app.SectorTiempo', to='app.Sector'),
        ),
        migrations.AddField(
            model_name='lugarprestador',
            name='id_prestador',
            field=models.ForeignKey(db_column='id_prestador', on_delete=django.db.models.deletion.DO_NOTHING, to='app.Prestador'),
        ),
        migrations.AddField(
            model_name='lugar',
            name='id_sector_aut',
            field=models.ForeignKey(db_column='id_sector_aut', on_delete=django.db.models.deletion.DO_NOTHING, related_name='sector_auto', to='app.Sector'),
        ),
        migrations.AddField(
            model_name='lugar',
            name='id_sector_cam',
            field=models.ForeignKey(db_column='id_sector_cam', on_delete=django.db.models.deletion.DO_NOTHING, related_name='sector_caminando', to='app.Sector'),
        ),
        migrations.AddField(
            model_name='lugar',
            name='id_tipoLugar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='id_tipo_lugar', to='app.TipoLugar'),
        ),
        migrations.AddField(
            model_name='individuotiempocentro',
            name='id_centro',
            field=models.ForeignKey(db_column='id_centro', on_delete=django.db.models.deletion.DO_NOTHING, related_name='id_centro', to='app.Lugar'),
        ),
        migrations.AddField(
            model_name='individuotiempocentro',
            name='id_individuo',
            field=models.ForeignKey(db_column='id_individuo', on_delete=django.db.models.deletion.DO_NOTHING, related_name='id_individuo', to='app.Individuo'),
        ),
        migrations.AddField(
            model_name='individuo',
            name='anclas',
            field=models.ManyToManyField(related_name='anclas', through='app.AnclaTemporal', to='app.Lugar'),
        ),
        migrations.AddField(
            model_name='individuo',
            name='centros',
            field=models.ManyToManyField(related_name='centros', through='app.IndividuoTiempoCentro', to='app.Lugar'),
        ),
        migrations.AddField(
            model_name='individuo',
            name='id_hogar',
            field=models.ForeignKey(blank=True, db_column='id_hogar', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='id_hogar', to='app.Lugar'),
        ),
        migrations.AddField(
            model_name='individuo',
            name='id_jardin',
            field=models.ForeignKey(blank=True, db_column='id_jardin', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='id_jardin', to='app.Lugar'),
        ),
        migrations.AddField(
            model_name='individuo',
            name='id_prestador',
            field=models.ForeignKey(blank=True, db_column='id_prestador', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='app.Prestador'),
        ),
        migrations.AddField(
            model_name='individuo',
            name='id_trabajo',
            field=models.ForeignKey(blank=True, db_column='id_trabajo', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='id_trabajo', to='app.Lugar'),
        ),
        migrations.AddField(
            model_name='anclatemporal',
            name='id_individuo',
            field=models.ForeignKey(db_column='id_individuo', on_delete=django.db.models.deletion.DO_NOTHING, related_name='id_individuoAncla', to='app.Individuo'),
        ),
        migrations.AddField(
            model_name='anclatemporal',
            name='id_lugar',
            field=models.ForeignKey(db_column='id_lugar', on_delete=django.db.models.deletion.DO_NOTHING, related_name='id_lugarAncla', to='app.Lugar'),
        ),
        migrations.AlterUniqueTogether(
            name='lugarprestador',
            unique_together=set([('id_prestador', 'id_lugar', 'dia', 'hora')]),
        ),
        migrations.AlterUniqueTogether(
            name='individuotiempocentro',
            unique_together=set([('id_individuo', 'id_centro', 'dia', 'hora')]),
        ),
        migrations.AlterUniqueTogether(
            name='anclatemporal',
            unique_together=set([('id_individuo', 'id_lugar', 'dia')]),
        ),
    ]
