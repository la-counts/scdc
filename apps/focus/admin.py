from django.contrib import admin
from django.forms.models import modelform_factory

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from import_export.admin import ImportExportMixin
from fsm_admin.mixins import FSMTransitionMixin

from .models import Concept, Label, FeaturedStory, FeaturedCatalogRecord, \
    MappedUri, InterestPage
from .io_resources import ConceptResource
from .fields import ConceptTagAdminWidget, ConceptSelectWidget, TagWidget
from data_commons.contrib.admin_utils import ImproveRawIdFieldsFormMixin


class LabelInline(admin.TabularInline):
    model = Label
    fk_name = 'concept'


class FeaturedStoryInline(admin.TabularInline):
    model = FeaturedStory
    raw_id_fields = ['story']
    #TODO select2


class FeaturedCatalogRecordInline(admin.TabularInline):
    model = FeaturedCatalogRecord
    raw_id_fields = ['catalog_record']
    #TODO select2


class MappedUriInline(admin.TabularInline):
    model = MappedUri


class ConceptAdmin(ImportExportMixin, ImproveRawIdFieldsFormMixin, TreeAdmin):
    change_list_template = 'admin/tree_change_list.html'
    search_fields = ['title']
    inlines = [LabelInline, MappedUriInline]
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'definition',
                'example',
                'tags',
                '_position', '_ref_node_id'),
        }),
        ('Search', {
            'classes': ('collapse',),
            'fields': ('alternative_parents', 'related_match',
                       'exact_match', 'close_match'),
        }),
    )
    resource_class = ConceptResource
    form = movenodeform_factory(Concept,
        exclude = [],
        widgets = {
            #'parent': ConceptSelectWidget,
            #'tags': TagWidget,
            'alternative_parents': ConceptTagAdminWidget,
            'related_match': ConceptTagAdminWidget,
            'exact_match': ConceptTagAdminWidget,
            'close_match': ConceptTagAdminWidget,
        }
    )

admin.site.register(Concept, ConceptAdmin)


class InterestPageAdmin(FSMTransitionMixin, admin.ModelAdmin):
    inlines = [FeaturedStoryInline, FeaturedCatalogRecordInline]
    form = modelform_factory(InterestPage,
        exclude = [],
        widgets = {
            'concepts': ConceptTagAdminWidget,
        }
    )
    fsm_field = ['state']

admin.site.register(InterestPage, InterestPageAdmin)
