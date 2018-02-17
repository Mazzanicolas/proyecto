# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-17 04:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_auto_20180217_0104'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectorAuto',
            fields=[
                ('shapeId', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('x_centroide', models.IntegerField()),
                ('y_centroide', models.IntegerField()),
                ('shapePosition', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SectorCaminando',
            fields=[
                ('shapeId', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('x_centroide', models.IntegerField()),
                ('y_centroide', models.IntegerField()),
                ('shapePosition', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='anclatemporal',
            name='sector_auto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sector_auto', to='app.SectorAuto'),
        ),
        migrations.AlterField(
            model_name='anclatemporal',
            name='sector_caminando',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sector_caminando', to='app.SectorCaminando'),
        ),
        migrations.AlterField(
            model_name='centro',
            name='sector_auto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sectorCentro_auto', to='app.SectorAuto'),
        ),
        migrations.AlterField(
            model_name='centro',
            name='sector_caminando',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sectorCentro_caminando', to='app.SectorCaminando'),
        ),
        migrations.AlterField(
            model_name='sectortiempoauto',
            name='sector_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sector_1', to='app.SectorAuto'),
        ),
        migrations.AlterField(
            model_name='sectortiempoauto',
            name='sector_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sector_2', to='app.SectorAuto'),
        ),
        migrations.AlterField(
            model_name='sectortiempocaminando',
            name='sector_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sectorCaminando_1', to='app.SectorCaminando'),
        ),
        migrations.AlterField(
            model_name='sectortiempocaminando',
            name='sector_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sectorCaminando_2', to='app.SectorCaminando'),
        ),
        migrations.AlterField(
            model_name='sectortiempoomnibus',
            name='sectorO_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sectorO_1', to='app.SectorAuto'),
        ),
        migrations.AlterField(
            model_name='sectortiempoomnibus',
            name='sectorO_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sectorO_2', to='app.SectorAuto'),
        ),
        migrations.DeleteModel(
            name='Sector',
        ),
    ]