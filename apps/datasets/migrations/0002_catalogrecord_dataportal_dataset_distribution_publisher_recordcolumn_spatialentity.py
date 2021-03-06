# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-25 03:01
from __future__ import unicode_literals

import ckeditor_uploader.fields
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.hstore
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('datasets', '0001_extensions'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='A name given to the dataset.', max_length=255)),
                ('state', django_fsm.FSMField(choices=[('new', 'New'), ('published', 'Published'), ('rejected', 'Rejected'), ('broken', 'Broken')], db_index=True, default='new', max_length=50)),
                ('curated_collection', models.CharField(blank=True, help_text='Collections were developed for CCF, following requested thematic topics and existing focus areas. Note: At a future data this field will meet requirements for optional “theme” adopted by USPRO and DCAT.', max_length=50, verbose_name='primary topic')),
                ('description', models.TextField(blank=True, help_text='free-text account of the dataset.')),
                ('keyword', models.TextField(blank=True, help_text='A keyword or tag describing the dataset.', verbose_name='keyword/tag')),
                ('modified', models.DateTimeField(blank=True, help_text='Most recent date on which the dataset was changed, updated or modified.', null=True, verbose_name='update/modification date')),
                ('contact_point', models.TextField(blank=True, help_text='All relevant contact information (including name and email) for the person(s) to whom questions about the dataset should be sent.')),
                ('identifier', models.CharField(blank=True, help_text='A unique identifier of the dataset.', max_length=255)),
                ('access_level', models.CharField(blank=True, choices=[('public', 'public'), ('restricted public', 'restricted public'), ('non-public', 'non-public')], help_text='\n        The degree to which this dataset could be made publicly-available, regardless of whether it has been made available. Choices:\n        public (Data asset is or could be made publicly available to all without restrictions),\n        restricted public (Data asset is available under certain use restrictions), or\n        non-public (Data asset is not available to members of the public).\n        ', max_length=20)),
                ('license', models.TextField(blank=True, help_text='This links to the license document under which the distribution is made available.')),
                ('rights', models.CharField(blank=True, help_text='Information about rights held in and over the distribution.', max_length=255)),
                ('spatial', models.TextField(blank=True, help_text='Spatial coverage of the dataset.', verbose_name='spatial/geographical coverage')),
                ('spatial_granularity', models.TextField(blank=True, help_text='Sub field of spatial coverage, required where applicable.')),
                ('temporal', models.TextField(blank=True, help_text='The temporal period that the dataset covers.', verbose_name='temporal coverage')),
                ('sync_strategy', models.CharField(blank=True, choices=[('apps.datasets.sync.static_link', 'Static Link'), ('apps.datasets.sync.socrata', 'Socrata'), ('apps.datasets.sync.arcgis', 'ArcGIS')], help_text='Plugin for automatically syncing metadata', max_length=50)),
                ('distribution', models.CharField(blank=True, help_text='Available distributions, or specific data formats (ex: csv, Socrata API); type(s) of format(s)', max_length=255)),
                ('distribution_fields', models.CharField(blank=True, help_text='URL of most commonly accessed distribution', max_length=255)),
                ('accrual_periodicity', models.TextField(blank=True, help_text='The frequency at which dataset is published.')),
                ('reports_to', models.TextField(blank=True, help_text='All legislation that requires or informs the collection and reporting of these data points.')),
                ('collection_protocol', models.TextField(blank=True, help_text='Description of the frequency and mode of data collection\n        (different from periodicity of dataset publication).\n        Links to original data collection plan or proposals may also be added here.')),
                ('conforms_to', models.TextField(blank=True, help_text='Data standard dataset meets.')),
                ('described_by', models.CharField(blank=True, help_text='Machine readable documentation (typically used for APIs)', max_length=255)),
                ('described_by_type', models.CharField(blank=True, help_text='Machine readable documentation type (typically used for APIs)', max_length=255)),
                ('is_part_of', models.TextField(blank=True, help_text='The collection of which the dataset is a subset')),
                ('issued', models.DateTimeField(blank=True, help_text='Date of formal issuance (e.g., publication) of the dataset.', null=True, verbose_name='listing date')),
                ('language', models.CharField(blank=True, max_length=20)),
                ('landing_page', models.URLField(blank=True, help_text='A Web page that can be navigated to in a Web browser to gain access to the dataset, its distributions and/or additional information.')),
                ('funded_by', models.TextField(blank=True, help_text='All groups and/or individuals that financially support the collection of this dataset.\nThese entities may be the same or different from the dataset’s publisher')),
                ('notes', models.TextField(blank=True, help_text='For use by SCDC project only')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('percentage_complete', models.FloatField(default=0.0, verbose_name='% complete')),
            ],
        ),
        migrations.CreateModel(
            name='DataPortal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(blank=True, max_length=50)),
                ('url', models.URLField(unique=True)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('vendor', models.CharField(blank=True, max_length=50)),
                ('datasets_estimate', models.IntegerField(blank=True, null=True)),
                ('license', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='A name given to the dataset.', max_length=255)),
                ('description', models.TextField(blank=True, help_text='free-text account of the dataset.')),
                ('issued', models.DateTimeField(blank=True, help_text='Date of formal issuance (e.g., publication) of the dataset.', null=True, verbose_name='release date')),
                ('modified', models.DateTimeField(blank=True, help_text='Most recent date on which the dataset was changed, updated or modified.', null=True, verbose_name='update/modification date')),
                ('identifier', models.CharField(blank=True, help_text='A unique identifier of the dataset.', max_length=255)),
                ('keyword', models.TextField(blank=True, help_text='A keyword or tag describing the dataset.', verbose_name='keyword/tag')),
                ('language', models.CharField(blank=True, help_text='The language of the dataset.', max_length=20)),
                ('temporal', models.TextField(blank=True, help_text='The temporal period that the dataset covers.', verbose_name='temporal coverage')),
                ('spatial', models.TextField(blank=True, help_text='Spatial coverage of the dataset.', verbose_name='spatial/geographical coverage')),
                ('accrual_periodicity', models.TextField(blank=True, help_text='The frequency at which dataset is published.', verbose_name='frequency')),
                ('landing_page', models.URLField(blank=True, help_text='A Web page that can be navigated to in a Web browser to gain access to the dataset, its distributions and/or additional information.')),
                ('theme', models.TextField(blank=True, help_text='The main category of the dataset. A dataset can have multiple themes.', verbose_name='theme/category')),
                ('publisher', models.TextField(blank=True, help_text='An entity responsible for making the dataset available.')),
                ('contact_point', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_sync', models.DateTimeField(editable=False, help_text='Last time the data automatically synced', null=True)),
                ('sourced_meta_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('issued', models.DateTimeField(blank=True, help_text='Date of formal issuance (e.g., publication) of the distribution.', null=True, verbose_name='release date')),
                ('modified', models.DateTimeField(blank=True, help_text='Most recent date on which the distribution was changed, updated or modified.', null=True, verbose_name='update/modification date')),
                ('license', models.TextField(blank=True, help_text='This links to the license document under which the distribution is made available.')),
                ('rights', models.TextField(blank=True, help_text='Information about rights held in and over the distribution.')),
                ('access_url', models.URLField(blank=True, help_text='A landing page, feed, SPARQL endpoint or other type of resource that gives access to the distribution of the dataset')),
                ('download_url', models.URLField(blank=True, help_text='A file that contains the distribution of the dataset in a given format')),
                ('byte_size', models.PositiveIntegerField(blank=True, help_text='The size of a distribution in bytes.', null=True)),
                ('media_type', models.CharField(blank=True, help_text='The media type of the distribution as defined by IANA.', max_length=50)),
                ('format', models.CharField(blank=True, help_text='The file format of the distribution.', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(help_text='appears in the url', max_length=100, unique=True)),
                ('agency_type', models.CharField(blank=True, max_length=50)),
                ('agency_url', models.URLField(blank=True)),
                ('primary_data_portal', models.URLField(blank=True)),
                ('body', ckeditor_uploader.fields.RichTextUploadingField(blank=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RecordColumn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('data_type', models.CharField(max_length=255)),
                ('render_type', models.CharField(blank=True, max_length=255)),
                ('catalog_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datasets.CatalogRecord')),
            ],
        ),
        migrations.CreateModel(
            name='SpatialEntity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(srid=4326)),
                ('granularity', models.TextField(blank=True)),
                ('data', django.contrib.postgres.fields.hstore.HStoreField(blank=True, default=dict)),
            ],
            options={
                'verbose_name_plural': 'spatial entities',
            },
        ),
    ]
