import datetime
from haystack import indexes
from .models import Story


as_ids = lambda x: list(x.values_list('pk', flat=True))

class StoryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title_s = indexes.CharField(indexed=False)
    tags = indexes.MultiValueField(faceted=True)
    concepts = indexes.MultiValueField(faceted=True)
    issued = indexes.DateTimeField(model_attr='published_at', null=True)
    author = indexes.CharField(model_attr='posted_by', faceted=True)
    #TODO publisher via author association
    publisher = indexes.CharField(model_attr='organization_id', faceted=True, null=True)

    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return Story

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.published().select_related()

    def get_updated_field(self):
        return 'updated_at'

    def prepare_title_s(self, obj):
        return obj.title.lower()

    def prepare_tags(self, obj):
        return list(obj.tags.names())

    def prepare_concepts(self, obj):
        return as_ids(obj.concepts.all())
