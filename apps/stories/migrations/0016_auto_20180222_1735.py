# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-23 01:35
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0015_auto_20180222_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='bodyFeaturedText',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='Body Featured Text'),
        ),
        migrations.AlterField(
            model_name='story',
            name='repostPermissionLine',
            field=models.CharField(blank=True, max_length=255, verbose_name='Reposted with Permission Text'),
        ),
    ]
