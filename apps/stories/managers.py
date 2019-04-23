from django.db import models


class StoryQuerySet(models.QuerySet):
    def published(self):
        return self.filter(state='published')

    def search_concepts(self, concepts):
        '''
        Filter stories to those that are search matched to the given concepts.

        This will expand the criteria to also include concepts that are matched to the given concepts as well as descendent concepts.
        '''
        c_tree = concepts.get_descendants(include_self=True).search_matched()
        return self.filter(concepts__in=c_tree)

    def select_concepts(self, concepts):
        '''
        Exclude stories that are not in the given concepts or their descendent concepts.
        '''
        c_tree = concepts.get_descendants(include_self=True)
        return self.filter(concepts__in=c_tree)


StoryManager = models.Manager.from_queryset(StoryQuerySet)
