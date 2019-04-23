from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Q, F
from django.utils.text import slugify

from apps.datasets.models import CatalogRecord
from apps.focus.models import Concept, FeaturedCatalogRecord


#curated_collection => slug + tag
#slug -> concept
#tag -> concept

class Command(BaseCommand):
    help = "Create a concept entry for each curated collection and add the datasets."

    def handle(self, *args, **options):
        concept_titles = list(Concept.objects.all().values_list('title', flat=True))
        concept_slugs = list(Concept.objects.all().values_list('slug', flat=True))
        qs = CatalogRecord.objects.exclude(
                #Q(curated_collection__in=concept_titles) |
                Q(curated_collection=''))
        new_titles = set(qs.values_list('curated_collection', flat=True).distinct())
        concepts = dict()
        for title in new_titles:
            slug = slugify(title.replace('&', 'and'))
            concept = Concept.objects.filter(slug=slug).first()
            if not concept:
                concept = Concept.add_root(
                    title = title,
                    slug = slug,
                )
                #add the first 10
                #matched_records = CatalogRecord.objects.filter(curated_collection=title)[:10]
                #for record in matched_records:
                #    FeaturedCatalogRecord.objects.create(catalog_record=record, concept=concept)
                #concept.catalog_records.add(matched_records)
                self.stdout.write(self.style.SUCCESS('Created concept "%s"' % concept))
            concepts[title] = concept
            concept.tags.add(title)

        #call records with a collection but doesnt have it registered as a concept
        qs = CatalogRecord.objects.exclude(
            Q(curated_collection='')# |
            #Q(concepts__title=F('curated_collection'))
        )
        for cr in qs:
            title = cr.curated_collection
            if title not in concepts:
                slug = slugify(title.replace('&', 'and'))
                concept = Concept.objects.filter(slug=slug).first()
                if concept:
                    concepts[title] = concept
            if title in concepts:
                cr.concepts.add(concepts[title])
        self.stdout.write(self.style.SUCCESS("Concepts synced"))
