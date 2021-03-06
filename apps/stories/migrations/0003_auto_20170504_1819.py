# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-04 18:19
from __future__ import unicode_literals

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0002_auto_20170502_2359'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='story',
            name='published',
        ),
        migrations.AddField(
            model_name='story',
            name='state',
            field=django_fsm.FSMField(choices=[('new', 'New'), ('published', 'Published'), ('rejected', 'Rejected')], db_index=True, default='new', max_length=50, protected=True),
        ),
    ]
