# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-17 04:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_auto_20180217_0101'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sector',
            old_name='idShape',
            new_name='shapeId',
        ),
    ]