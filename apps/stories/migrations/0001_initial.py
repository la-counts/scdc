# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-28 07:40
from __future__ import unicode_literals

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0002_auto_20150616_2121'),
        ('datasets', '0003_auto_20170524_2001'),
        ('focus', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Headline')),
                ('slug', models.SlugField()),
                ('subheader', models.CharField(blank=True, max_length=255, verbose_name='Subheader')),
                ('published', models.BooleanField(db_index=True, default=False)),
                ('body', ckeditor.fields.RichTextField()),
                ('published_at', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('featured_image', models.ImageField(blank=True, upload_to='stories')),
                ('concepts', models.ManyToManyField(blank=True, to='focus.Concept')),
                ('datasets', models.ManyToManyField(blank=True, to='datasets.CatalogRecord')),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='datasets.Publisher')),
                ('posted_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('related', models.ManyToManyField(blank=True, related_name='_story_related_+', to='stories.Story')),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'verbose_name_plural': 'stories',
            },
        ),
        migrations.CreateModel(
            name='StoryImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='stories')),
                ('caption', models.TextField(blank=True)),
                ('story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='stories.Story')),
            ],
        ),
        migrations.AlterOrderWithRespectTo(
            name='storyimage',
            order_with_respect_to='story',
        ),
    ]