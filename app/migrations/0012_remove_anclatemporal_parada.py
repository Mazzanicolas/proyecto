# Generated by Django 2.0 on 2018-01-18 15:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_individuotiempocentro_llega'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='anclatemporal',
            name='parada',
        ),
    ]
