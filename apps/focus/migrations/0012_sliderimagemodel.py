# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-11-18 06:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
        ('focus', '0011_widgettitlemodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='SliderImageModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='focus_sliderimagemodel', serialize=False, to='cms.CMSPlugin')),
                ('text', models.CharField(max_length=250)),
                ('link', models.CharField(blank=True, max_length=200)),
                ('icon', models.ImageField(upload_to='images')),
                ('image', models.ImageField(upload_to='images')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
