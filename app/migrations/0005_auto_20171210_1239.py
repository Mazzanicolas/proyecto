# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-10 15:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_centro_parada'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndividuoCentro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tiempoViajeAntesTrabajo', models.IntegerField(blank=True, null=True)),
                ('tiempoViajeDespuesTrabajo', models.IntegerField(blank=True, null=True)),
                ('tHogarCentro', models.IntegerField(null=True)),
                ('tHogarTrabajo', models.IntegerField(null=True)),
                ('tHogarJardin', models.IntegerField(null=True)),
                ('tCentroHogar', models.IntegerField(null=True)),
                ('tCentroJardin', models.IntegerField(null=True)),
                ('tTrabajoJardin', models.IntegerField(null=True)),
                ('tTrabajoHogar', models.IntegerField(null=True)),
                ('tJardinTrabajo', models.IntegerField(null=True)),
                ('tJardinCentro', models.IntegerField(null=True)),
                ('centro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Centro')),
            ],
            options={
                'ordering': ['individuo', 'centro'],
            },
        ),
        migrations.RemoveField(
            model_name='individuotiempocentro',
            name='tCentroHogar',
        ),
        migrations.RemoveField(
            model_name='individuotiempocentro',
            name='tCentroJardin',
        ),
        migrations.RemoveField(
            model_name='individuotiempocentro',
            name='tHogarCentro',
        ),
        migrations.RemoveField(
            model_name='individuotiempocentro',
            name='tHogarJardin',
        ),
        migrations.RemoveField(
            model_name='individuotiempocentro',
            name='tHogarTrabajo',
        ),
        migrations.RemoveField(
            model_name='individuotiempocentro',
            name='tJardinCentro',
        ),
        migrations.RemoveField(
            model_name='individuotiempocentro',
            name='tJardinTrabajo',
        ),
        migrations.RemoveField(
            model_name='individuotiempocentro',
            name='tTrabajoHogar',
        ),
        migrations.RemoveField(
            model_name='individuotiempocentro',
            name='tTrabajoJardin',
        ),
        migrations.AddField(
            model_name='individuo',
            name='tieneJardin',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='individuo',
            name='tieneTrabajo',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='individuocentro',
            name='individuo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Individuo'),
        ),
        migrations.AlterUniqueTogether(
            name='individuocentro',
            unique_together=set([('individuo', 'centro')]),
        ),
    ]
