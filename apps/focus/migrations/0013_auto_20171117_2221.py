# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-11-18 06:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('focus', '0012_sliderimagemodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sliderimagemodel',
            name='icon',
            field=models.FileField(upload_to='images'),
        ),
    ]
