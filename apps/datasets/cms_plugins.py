from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import DatasetsPluginModel, DatasetsGroupPluginModel, DatasetsCustomPluginModel
from .fields import CatalogRecordSelectMultipleWidget
from django.forms.models import modelform_factory
from django.utils.translation import ugettext as _


class DatasetsPluginPublisher(CMSPluginBase):
    model = DatasetsPluginModel  # model where plugin data are saved
    module = _("Data Commons")
    name = _("Link Datasets")  # name of the plugin in the interface
    render_template = "datasets/featured_datasets.html"
    form = modelform_factory(DatasetsPluginModel,
        exclude = [],
        widgets = {
            'datasets': CatalogRecordSelectMultipleWidget,
        }
    )

    def render(self, context, instance, placeholder):
        context.update({'datasets': instance.datasets.all()})
        return context

plugin_pool.register_plugin(DatasetsPluginPublisher)  # register the plugin


class DatasetCustomPluginPublisher(CMSPluginBase):
    model = DatasetsCustomPluginModel  # model where plugin data are saved
    module = _("Data Commons")
    name = _("Link Datasets - Custom Title")  # name of the plugin in the interface
    render_template = "datasets/featured_datasets_custom.html"
    form = modelform_factory(DatasetsPluginModel,
        exclude = [],
        widgets = {
            'datasets': CatalogRecordSelectMultipleWidget,
        }
    )

    def render(self, context, instance, placeholder):
        context.update({'datasets': instance.datasets.all(), 'widget': instance})
        return context

plugin_pool.register_plugin(DatasetCustomPluginPublisher)  # register the plugin

class DatasetOfDayPublisher(CMSPluginBase):
    model = DatasetsPluginModel  # model where plugin data are saved
    module = _("Data Commons")
    name = _("Datasets of the Day")  # name of the plugin in the interface
    render_template = "datasets/dataset_of_the_day.html"
    form = modelform_factory(DatasetsPluginModel,
        exclude = [],
        widgets = {
            'datasets': CatalogRecordSelectMultipleWidget,
        }
    )

    def render(self, context, instance, placeholder):
        context.update({'datasets': instance.datasets.all()})
        return context

plugin_pool.register_plugin(DatasetOfDayPublisher)  # register the plugin


class DatasetGroupPublisher(CMSPluginBase):
    model = DatasetsGroupPluginModel  # model where plugin data are saved
    module = _("Data Commons")
    name = _("Dataset Group")  # name of the plugin in the interface
    render_template = "datasets/dataset_group.html"
    form = modelform_factory(DatasetsGroupPluginModel,
        exclude = [],
        widgets = {
            'datasets': CatalogRecordSelectMultipleWidget,
        }
    )

    def render(self, context, instance, placeholder):
        context.update({'datasets': instance.datasets.all(), 'widget': instance})
        return context

plugin_pool.register_plugin(DatasetGroupPublisher)  # register the plugin

#TODO search form? publishers? concepts?
