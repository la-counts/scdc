from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.contrib import admin
from .models import StoriesPluginModel, StoryDisplayPlugin
from .fields import StorySelectMultipleWidget, StorySelectWidget
from django.utils.translation import ugettext as _
from django.forms.models import modelform_factory


class StoryDisplayInline(admin.TabularInline):
    model = StoryDisplayPlugin
    form = modelform_factory(StoriesPluginModel,
        exclude = [],
        widgets = {
            'story': StorySelectWidget
        }
    )


class StoriesPluginPublisher(CMSPluginBase):
    model = StoriesPluginModel  # model where plugin data are saved
    module = _("Data Commons")
    name = _("Feature Stories")  # name of the plugin in the interface
    render_template = "stories/featured_stories.html"
    form = modelform_factory(StoriesPluginModel,
        exclude = [],
    )
    inlines = [StoryDisplayInline]

    def render(self, context, instance, placeholder):
        context.update({
            'display_cards': instance.display_cards,
            'stories': instance.get_stories(),
        })
        return context

plugin_pool.register_plugin(StoriesPluginPublisher)  # register the plugin


class StoriesListPluginPublisher(CMSPluginBase):
    model = StoriesPluginModel  # model where plugin data are saved
    module = _("Data Commons")
    name = _("Stories List")  # name of the plugin in the interface
    render_template = "stories/stories_list.html"
    form = modelform_factory(StoriesPluginModel,
        exclude = [],
    )
    inlines = [StoryDisplayInline]

    def render(self, context, instance, placeholder):
        context.update({
            'display_cards': instance.display_cards,
            'stories': instance.get_stories(),
        })
        return context

plugin_pool.register_plugin(StoriesListPluginPublisher)  # register the plugin