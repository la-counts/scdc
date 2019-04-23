from django.db import models
from django.db.models import Q
from treebeard.mp_tree import MP_NodeManager, MP_NodeQuerySet


#CONSIDER hold off on distrinct calls till the very end, dont include in queryset calls
class ConceptQuerySet(MP_NodeQuerySet):
    def get_ancestors(self, include_self=False):
        if include_self:
            qs = self
        else:
            qs = self.none()
        for selection in self:
            qs = qs | selection.get_ancestors()
        return qs

    def get_descendants(self, include_self=False):
        qs = self.none()
        for selection in self:
            if include_self:
                f = self.model.get_tree(selection)
            else:
                f = selection.get_descendants()
            qs = qs | f
        return qs

    def search_matched(self):
        '''
        Expand the queryset to include matches to this concept
        '''
        qs = self.model.objects.filter(
            Q(related_match__in=self) | Q(exact_match__in=self) | Q(close_match__in=self)
        ) | self
        return qs

    def from_tags(self, tags):
        #CONSIDER: we do not want case-insensitive matching.
        #Case matters for acronyms and proper titles
        #ultimately let the moderator be explicit
        tagnames = list(map(lambda x: x.name, tags))
        qs = self.filter(
            Q(tags__in=tags) | Q(title__in=tagnames)
        )
        return qs

    def alternative_ancestors(self, include_self=True):
        '''
        Query ancestors including alternative parents
        '''
        if include_self:
            qs = self
        else:
            qs = self.none()
        for selection in self:
            qs = qs | selection.get_ancestors()
        for alt_parent in self.alternative_children():
            qs = qs | alt_parent.get_ancestors()
        return qs

    def alternative_children(self, include_self=True):
        '''
        Return alternative children that can claim a parent in this query
        '''
        qs = self.model.objects.filter(
            alternative_parents__in=self,
        )
        if include_self:
            qs = qs | self
        return qs


class ConceptManager(MP_NodeManager):
    def get_queryset(self):
        return ConceptQuerySet(self.model, using=self._db)


class InterestPageQueryset(models.QuerySet):
    def display(self):
        #we may want to display only published in the future...
        return self.published()

    def active(self):
        return self.exclude(state__in=[
            'new',
            'published',
        ])

    def published(self):
        '''
        Filter Catalog Records whose state is "published"
        '''
        return self.filter(state='published')

InterestPageManager = models.Manager.from_queryset(InterestPageQueryset)
