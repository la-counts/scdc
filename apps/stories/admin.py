from django.contrib import admin
from django.utils.timezone import datetime
from django.forms.models import modelform_factory

from fsm_admin.mixins import FSMTransitionMixin

from .models import Story, StoryImage
from apps.focus.fields import ConceptTagAdminWidget
from apps.datasets.fields import PublisherSelectWidget, CatalogRecordSelectMultipleWidget
from data_commons.contrib.admin_utils import ImproveRawIdFieldsFormMixin
from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from image_cropping import ImageCroppingMixin


class StoryImageInline(admin.StackedInline):
    model = StoryImage
    extra = 1


class StoryAdmin(FrontendEditableAdminMixin, ImageCroppingMixin, FSMTransitionMixin, ImproveRawIdFieldsFormMixin, admin.ModelAdmin):
    frontend_editable_fields = ['title', 'body']
    list_display = ['title', 'state']
    list_filter = ['state']
    raw_id_fields = ['posted_by', 'approved_by']
    inlines = [StoryImageInline]
    actions = ['publish', 'map_datasource_urls']
    fsm_field = ['state']
    form = modelform_factory(Story,
        exclude = [],
        widgets = {
            'concepts': ConceptTagAdminWidget,
            'organization': PublisherSelectWidget,
            'datasets': CatalogRecordSelectMultipleWidget,
        }
    )
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'author',
                'published_at',
                'subheader',
                'repostPermissionLine',
                'bodyFeaturedText',
                'body'),
        }),
        ('Display', {
            'fields': (
                'highlight',
                'featured_image',
                ('card_image', 'wide_card_image'),
                'featured_image_caption'),
        }),
        ('Catalog', {
            'fields': (
                'concepts',
                'datasets',
                'organization',
                'datasource_urls',
                'tags'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': (
                'approved_by',
                'posted_by',
                'state'),
        }),
    )

    def publish(self, request, queryset):
        user = request.user
        now = datetime.now()
        queryset.filter(approved_by__isnull=True).update(approved_by=user)
        queryset.filter(published_at__isnull=True).update(published_at=now)
        queryset.update(state='published')
        self.message_user(request, "Stories published")
    publish.short_description = "Publish stories"

    def map_datasource_urls(self, request, queryset):
        count = 0
        for story in queryset:
            count += len(story.map_datasource_urls())
        self.message_user(request, "Newly associated %s datasets" % count)
    map_datasource_urls.short_description = "Map datasource urls to catalog records/datasets"


admin.site.register(Story, StoryAdmin)
