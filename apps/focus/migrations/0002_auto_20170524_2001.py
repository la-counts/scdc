# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-25 03:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('datasets', '0003_auto_20170524_2001'),
        ('stories', '0001_initial'),
        ('focus', '0001_initial'),
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.AddField(
            model_name='interestpage',
            name='featured_stories',
            field=models.ManyToManyField(blank=True, related_name='featured_interests', through='focus.FeaturedStory', to='stories.Story'),
        ),
        migrations.AddField(
            model_name='featuredstory',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='focus.InterestPage'),
        ),
        migrations.AddField(
            model_name='featuredstory',
            name='story',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stories.Story'),
        ),
        migrations.AddField(
            model_name='featuredcatalogrecord',
            name='catalog_record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datasets.CatalogRecord'),
        ),
        migrations.AddField(
            model_name='featuredcatalogrecord',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='focus.InterestPage'),
        ),
        migrations.AddField(
            model_name='concept',
            name='alternative_parents',
            field=models.ManyToManyField(blank=True, related_name='_concept_alternative_parents_+', to='focus.Concept'),
        ),
        migrations.AddField(
            model_name='concept',
            name='close_match',
            field=models.ManyToManyField(blank=True, related_name='_concept_close_match_+', to='focus.Concept'),
        ),
        migrations.AddField(
            model_name='concept',
            name='exact_match',
            field=models.ManyToManyField(blank=True, related_name='_concept_exact_match_+', to='focus.Concept'),
        ),
        migrations.AddField(
            model_name='concept',
            name='related_match',
            field=models.ManyToManyField(blank=True, related_name='_concept_related_match_+', to='focus.Concept'),
        ),
        migrations.AddField(
            model_name='concept',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='these tags will automatically be mapped to this concept', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterUniqueTogether(
            name='label',
            unique_together=set([('label', 'language_code', 'scheme')]),
        ),
        migrations.AlterUniqueTogether(
            name='featuredstory',
            unique_together=set([('page', 'story')]),
        ),
        migrations.AlterOrderWithRespectTo(
            name='featuredstory',
            order_with_respect_to='page',
        ),
        migrations.AlterUniqueTogether(
            name='featuredcatalogrecord',
            unique_together=set([('page', 'catalog_record')]),
        ),
        migrations.AlterOrderWithRespectTo(
            name='featuredcatalogrecord',
            order_with_respect_to='page',
        ),
    ]
