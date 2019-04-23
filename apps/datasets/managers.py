from django.db import models
from treebeard.mp_tree import MP_NodeManager, MP_NodeQuerySet


class CatalogRecordQuerySet(models.QuerySet):
    def display(self):
        #we may want to display only published in the future...
        return self.active()

    def active(self):
        return self.exclude(state__in=[
            'archived',
            'rejected',
        ])

    def published(self):
        '''
        Filter Catalog Records whose state is "published"
        '''
        return self.filter(state='published')

    def search_concepts(self, concepts):
        '''
        Filter records to those that are search matched to the given concepts.

        This will expand the criteria to also include concepts that are matched to the given concepts as well as descendent concepts.
        '''
        c_tree = concepts.get_descendants(include_self=True).search_matched()
        return self.filter(concepts__in=c_tree)

    def select_concepts(self, concepts):
        '''
        Exclude records that are not in the given concepts or their descendent concepts.
        '''
        c_tree = concepts.get_descendants(include_self=True)
        return self.filter(concepts__in=c_tree)


CatalogRecordManager = models.Manager.from_queryset(CatalogRecordQuerySet)


class PublisherQuerySet(MP_NodeQuerySet):
    def with_record_count(self):
        return self.annotate(
            record_count=models.Count('catalogrecord'),
        )

    def active(self):
        '''
        Publishers with who have records
        '''
        return self.with_record_count().filter(record_count__gt=0)

    def root_nodes(self):
        return self.filter(depth=1)


PublisherManager = models.Manager.from_queryset(PublisherQuerySet)
