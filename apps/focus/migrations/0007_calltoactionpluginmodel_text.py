# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-11-17 19:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('focus', '0006_calltoactionpluginmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='calltoactionpluginmodel',
            name='text',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]