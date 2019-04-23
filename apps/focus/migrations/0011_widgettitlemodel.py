# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-11-18 00:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
        ('focus', '0010_searchwidgetmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='WidgetTitleModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='focus_widgettitlemodel', serialize=False, to='cms.CMSPlugin')),
                ('title', models.CharField(max_length=250)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
