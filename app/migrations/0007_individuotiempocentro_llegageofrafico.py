# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-28 22:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_merge_20171228_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='individuotiempocentro',
            name='llegaGeofrafico',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]