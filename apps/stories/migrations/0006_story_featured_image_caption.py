# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-01 22:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0005_storiespluginmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='featured_image_caption',
            field=models.TextField(blank=True),
        ),
    ]
