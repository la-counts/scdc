from django.contrib import admin
from django.contrib.gis import admin as geoadmin
from django.forms.models import modelform_factory

from fsm_admin.mixins import FSMTransitionMixin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from taggit_helpers.admin import TaggitListFilter, TaggitCounter
from import_export.admin import ImportExportMixin

from apps.focus.fields import ConceptTagAdminWidget, ConceptSelectWidget
from apps.datasets.fields import PublisherSelectWidget, SpatialEntitySelectWidget
from .models import (SpatialEntity, Publisher, CatalogRecord, RecordColumn,
    DataPortal, Dataset, Distribution, DatasourceSuggestion)
from .io_resources import PublisherResource, CatalogRecordResource, DataPortalResource
from data_commons.contrib.admin_utils import ImproveRawIdFieldsFormMixin


class SpatialEntityAdmin(geoadmin.OSMGeoAdmin):
    pass
admin.site.register(SpatialEntity, SpatialEntityAdmin)


class PublisherAdmin(ImportExportMixin, TreeAdmin):
    change_list_template = 'admin/tree_change_list.html'
    list_display = ['name', 'agency_type']
    list_filter = ['agency_type']
    search_fields = ['name']
    prepopulated_fields = {"slug": ("name",)}
    resource_class = PublisherResource
    form = movenodeform_factory(Publisher)
admin.site.register(Publisher, PublisherAdmin)


class DataPortalAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['name', 'vendor', 'status']
    list_filter = ['vendor', 'status']
    #search_fields = ['name', 'publisher__name']
    raw_id_fields = ['publisher']
    resource_class = DataPortalResource
admin.site.register(DataPortal, DataPortalAdmin)


class DatasetInline(admin.StackedInline):
    model = Dataset


class RecordColumnInline(admin.StackedInline):
    model = RecordColumn
    extra = 0
    form = modelform_factory(RecordColumn,
        exclude = [],
        widgets = {
            'concept': ConceptSelectWidget,
        }
    )


class CatalogRecordAdmin(ImportExportMixin, FSMTransitionMixin, ImproveRawIdFieldsFormMixin, admin.ModelAdmin):
    list_display = ['title', 'curated_collection', 'publisher', 'state',
                    'distribution', 'access_level', '_percentage_complete']
    list_filter = ['curated_collection', 'access_level', 'sync_strategy', 'state']
    raw_id_fields = ['submitted_by', 'approved_by']
    search_fields = ['title', 'urls__url']
    date_hierarchy = 'modified'
    inlines = [
        RecordColumnInline,
        DatasetInline,
    ]
    fieldsets = (
        (None, {
            'fields': ('title', 'curated_collection', 'publisher', '_percentage_complete',
                'description',
                'keyword', 'concepts',
                'contact_point',
                'identifier', 'access_level', 'landing_page')
        }),
        ('Publishing', {
            'fields': ('state', ('submitted_by', 'approved_by'))
        }),
        ('Time & Place', {
            'classes': ('collapse',),
            'fields': (('spatial', 'spatial_granularity'), 'spatial_entity',
                ('temporal', 'accrual_periodicity')),
        }),
        ('Legal', {
            'classes': ('collapse',),
            'fields': ('license', 'rights', 'reports_to', 'funded_by'),
        }),
        ('Technical', {
            'classes': ('collapse',),
            'fields': ('distribution', 'distribution_fields', 'sync_strategy',
                'collection_protocol',
                'conforms_to', 'described_by', 'described_by_type', 'is_part_of',
                'notes', 'language'),
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('issued', 'modified'),
        }),
    )
    save_on_top = True
    form = modelform_factory(CatalogRecord,
        exclude = [],
        widgets = {
            'publisher': PublisherSelectWidget,
            'concepts': ConceptTagAdminWidget,
            'spatial_entity': SpatialEntitySelectWidget,
        }
    )
    resource_class = CatalogRecordResource

    actions = ['sync_metadata', 'publish']

    def sync_metadata(self, request, queryset):
        #TODO if count > 1, do in a task and return a task id
        for cr in queryset:
            cr.run_sync_strategy()
        cr_updated = len(queryset)
        if cr_updated == 1:
            message_bit = "1 record was"
        else:
            message_bit = "%s records were" % cr_updated
        self.message_user(request, "%s successfully synced." % message_bit)
    sync_metadata.short_description = "Sync selected records with their metadata"

    def publish(self, request, queryset):
        user = request.user
        queryset.filter(approved_by__isnull=True).update(approved_by=user)
        #TODO: queryset.filter(published_at__isnull=True).update(published_at=now)
        queryset.update(state='published')
        self.message_user(request, "Catalog Record(s) published")
    publish.short_description = "Publish records"

admin.site.register(CatalogRecord, CatalogRecordAdmin)


class DistributionInline(admin.StackedInline):
    model = Distribution
    extra = 0


class DatasetAdmin(admin.ModelAdmin):
    list_display = ['title', 'publisher',
                    'modified']
    #list_filter = ['curated_collection', 'access_level']
    raw_id_fields = ['catalog_record']
    search_fields = ['title']
    date_hierarchy = 'modified'
    inlines = [
        DistributionInline
    ]
admin.site.register(Dataset, DatasetAdmin)


class DatasourceSuggestionAdmin(FSMTransitionMixin, admin.ModelAdmin):
    list_dislay = ['submitted_by', 'state']
    raw_id_fields = ['submitted_by']
admin.site.register(DatasourceSuggestion, DatasourceSuggestionAdmin)
