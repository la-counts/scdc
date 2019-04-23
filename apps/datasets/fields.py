from django.conf import settings

from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget

from .models import SpatialEntity, Publisher, CatalogRecord, DataPortal

#these widgets are to power search and user form submissions


class SpatialEntitySelectWidget(ModelSelect2Widget):
    model = SpatialEntity
    search_fields = [
        'name__icontains'
    ]


class SpatialEntitySelectMultipleWidget(ModelSelect2MultipleWidget):
    model = SpatialEntity
    search_fields = [
        'name__icontains'
    ]


class PublisherSelectWidget(ModelSelect2Widget):
    model = Publisher
    search_fields = [
        'name__icontains'
    ]

class PublisherSelectMulitpleWidget(ModelSelect2MultipleWidget):
    model = Publisher
    search_fields = [
        'name__icontains'
    ]


class CatalogRecordSelectWidget(ModelSelect2Widget):
    model = CatalogRecord
    search_fields = [
        'title__icontains',
    ]


class CatalogRecordSelectMultipleWidget(ModelSelect2MultipleWidget):
    model = CatalogRecord
    search_fields = [
        'title__icontains',
    ]


class DataPortalSelectWidget(ModelSelect2Widget):
    model = DataPortal
    search_fields = [
        'title__icontains',
        'publisher__name__icontains',
    ]


class DataPortalSelectMultipleWidget(ModelSelect2MultipleWidget):
    model = DataPortal
    search_fields = [
        'title__icontains',
        'publisher__name__icontains',
    ]
