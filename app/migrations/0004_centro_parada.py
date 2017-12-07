# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20171111_1140'),
    ]

    operations = [
        migrations.AddField(
            model_name='centro',
            name='parada',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
