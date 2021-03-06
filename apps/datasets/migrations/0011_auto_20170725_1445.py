# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-07-25 21:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0010_auto_20170724_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalogrecord',
            name='publisher',
            field=models.ForeignKey(blank=True, help_text='An entity responsible for making the dataset available (may not be responsible for collecting the data).', null=True, on_delete=django.db.models.deletion.SET_NULL, to='datasets.Publisher'),
        ),
    ]
