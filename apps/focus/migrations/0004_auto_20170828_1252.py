# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-08-28 19:52
from __future__ import unicode_literals

from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('focus', '0003_auto_20170529_2044'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='interestpage',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='interestpage',
            name='order',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='interestpage',
            name='state',
            field=django_fsm.FSMField(choices=[('new', 'New'), ('published', 'Published'), ('archived', 'Archived')], db_index=True, default='published', max_length=50),
        ),
    ]
