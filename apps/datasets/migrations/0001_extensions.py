# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.postgres.operations import HStoreExtension, CreateExtension
from django.db import migrations


class Migration(migrations.Migration):
    '''
    Our initial migration turns on extensions. Tables are created in the next migration.
    '''

    initial = True

    dependencies = [
    ]

    operations = [
        CreateExtension('postgis'),
        HStoreExtension(),
    ]
