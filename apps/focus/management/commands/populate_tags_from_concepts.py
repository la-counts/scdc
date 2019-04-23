from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Q, F
from django.utils.text import slugify

from apps.datasets.models import CatalogRecord
from apps.focus.models import Concept
from apps.stories.models import Story
from taggit.models import Tag



class Command(BaseCommand):
    help = """
    All concepts will generate a tag and associate itself to any tags matching its various names.
    Datasets with tags associated to concepts will have their concept associations updated.
    """

    def handle(self, *args, **options):
        for concept in Concept.objects.all():
            labels = concept.our_search_labels()
            concept.tags.add(*labels)
        self.stdout.write(self.style.SUCCESS("Concept tags synced"))
        for cr in CatalogRecord.objects.all():
            concepts = Concept.objects.all().from_tags(cr.tags.all())
            cr.concepts.add(*concepts)
        self.stdout.write(self.style.SUCCESS("Catalog Record concepts synced"))
        for story in Story.objects.all():
            concepts = Concept.objects.all().from_tags(story.tags.all())
            story.concepts.add(*concepts)
        self.stdout.write(self.style.SUCCESS("Story concepts synced"))
