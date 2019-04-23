import datetime
from django.core.exceptions import ObjectDoesNotExist
from haystack import indexes
from .models import CatalogRecord, Dataset
from apps.focus.models import Concept


as_ids = lambda x: list(x.values_list('pk', flat=True))


class CatalogRecordIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    title_s = indexes.CharField(indexed=False) #for sort purposes only
    #tags = indexes.MultiValueField(faceted=True)
    concepts = indexes.MultiValueField(faceted=True)
    web_domains = indexes.MultiValueField(faceted=True, model_attr='web_domains')
    geometry = indexes.LocationField(null=True)
    spatial = indexes.CharField(null=True, faceted=True)
    license = indexes.CharField(null=True, faceted=True, model_attr='license')

    temporal_start = indexes.DateField(null=True, faceted=True, model_attr='temporal_start')
    temporal_end = indexes.DateField(null=True, model_attr='temporal_end')

    publisher = indexes.CharField(faceted=True)
    language = indexes.CharField(faceted=True)
    accrual_periodicity = indexes.CharField(null=True)
    funded_by = indexes.CharField(null=True, faceted=True, model_attr='funded_by')

    duration = indexes.IntegerField(null=True)
    download_count = indexes.IntegerField(null=True)

    issued = indexes.DateTimeField(null=True)
    modified = indexes.DateTimeField(null=True)
    last_sync = indexes.DateTimeField(null=True)
    access_level = indexes.CharField(null=True, faceted=True)

    percentage_complete = indexes.FloatField(model_attr='percentage_complete')

    rendered = indexes.CharField(use_template=True, indexed=False)

    #TODO autocomplete
    #tags_auto = indexes.EdgeNgramField() #prepare_tags

    def get_model(self):
        return CatalogRecord

    def prepare_title_s(self, obj):
        return obj.title.lower()

    def prepare_concepts(self, obj):
        return as_ids(obj.all_concepts())

    def prepare_spatial(self, obj):
        if obj.spatial_entity_id:
            return str(obj.spatial_entity_id)
        return obj.spatial

    def prepare_publisher(self, obj):
        return str(obj.publisher_id)

    def prepare_language(self, obj):
        return obj.lookup('language') or 'en'

    def prepare_accrual_periodicity(self, obj):
        return obj.lookup('accrual_periodicity')

    def prepare_duration(self, obj):
        start, end = obj.temporal_range()
        if start and end:
            return int((end - start).total_seconds())
        return None

    def prepare_download_count(self, obj):
        try:
            md = obj.dataset.sourced_meta_data
        except Dataset.DoesNotExist as error:
            return None
        else:
            return md and md.get('downloadCount', None)

    def prepare_issued(self, obj):
        return obj.lookup('issued')

    def prepare_modified(self, obj):
        return obj.lookup('modified')

    def prepare_geometry(self, obj):
        if obj.geometry:
            c = obj.geometry.centroid.tuple
            return "%s,%s" % (c[1], c[0])
        return None

    def prepare_last_sync(self, obj):
        return obj.lookup('last_sync')

    def prepare_access_level(self, obj):
        return obj.lookup('access_level')

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.active().select_related()

    def get_updated_field(self):
        return 'updated_at'
