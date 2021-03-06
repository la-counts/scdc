# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-11-29 21:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
        ('datasets', '0013_datasetsgrouppluginmodel_show_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatasetsCustomPluginModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='datasets_datasetscustompluginmodel', serialize=False, to='cms.CMSPlugin')),
                ('title', models.CharField(max_length=250)),
                ('show_title', models.BooleanField(default=True)),
                ('datasets', models.ManyToManyField(to='datasets.CatalogRecord')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
