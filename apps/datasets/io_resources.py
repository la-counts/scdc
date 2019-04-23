from import_export import resources, fields, widgets
from .models import CatalogRecord, Publisher, DataPortal


class PublisherResource(resources.ModelResource):
    parent = fields.Field(widget=widgets.ForeignKeyWidget(Publisher))

    class Meta:
        model = Publisher
        fields = ['id', 'name', 'slug', 'parent',
            'agency_type', 'agency_url', 'primary_data_portal',
            'body', 'description']


class CatalogRecordResource(resources.ModelResource):
    class Meta:
        model = CatalogRecord


class DataPortalResource(resources.ModelResource):
    class Meta:
        model = DataPortal
