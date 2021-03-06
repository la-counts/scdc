# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-25 03:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('focus', '0001_initial'),
        ('datasets', '0002_catalogrecord_dataportal_dataset_distribution_publisher_recordcolumn_spatialentity'),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='concepts',
            field=models.ManyToManyField(blank=True, to='focus.Concept'),
        ),
        migrations.AddField(
            model_name='user',
            name='publisher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='datasets.Publisher'),
        ),
    ]
