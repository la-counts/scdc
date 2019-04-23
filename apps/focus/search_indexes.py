import datetime
from django.core.exceptions import ObjectDoesNotExist
from haystack import indexes
from .models import Concept, InterestPage


as_ids = lambda x: list(x.values_list('pk', flat=True))


class ConceptIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    rendered = indexes.CharField(use_template=True, indexed=False)

    #TODO autocomplete
    #text_auto = indexes.EdgeNgramField()

    def get_model(self):
        return Concept

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all().select_related()


class InterestPageIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return InterestPage

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.display().select_related()
