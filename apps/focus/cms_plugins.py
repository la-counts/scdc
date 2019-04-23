from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from apps.focus.fields import ConceptTagAdminWidget
from .models import ConceptsPluginModel, CallToActionPluginModel, WidgetPanelAnchorsModel, WidgetPanelModel, SearchWidgetModel, WidgetTitleModel, SimpleSlider, SimpleSlide, SimpleSlideAdminInline, PriorityAreaHeaderModel, ContentBoxModel, CollapsibleModel, SolidBoxModel
from django.forms.models import modelform_factory
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.translation import ugettext as _


class ConceptsPluginPublisher(CMSPluginBase):
    model = ConceptsPluginModel  # model where plugin data are saved
    module = _("Data Commons")
    name = _("Link Concepts")  # name of the plugin in the interface
    render_template = "focus/featured_concepts.html"
    form = modelform_factory(ConceptsPluginModel,
        exclude = [],
        widgets = {
            'concepts': ConceptTagAdminWidget,
        }
    )

    def render(self, context, instance, placeholder):
        context.update({'concepts': instance.concepts.all()})
        return context

plugin_pool.register_plugin(ConceptsPluginPublisher)  # register the plugin

#CONSIDE: recent datasets vs new datasets vs stories- concept level?
#TODO search form? publishers?
@plugin_pool.register_plugin
class CallToActionPluginPublisher(CMSPluginBase):
    model = CallToActionPluginModel
    module = _("Data Commons")
    name = _("Call To Action")
    render_template = "focus/call_to_action.html"

    def render(self, context, instance, placeholder):
        context.update({'widget': instance})
        return context


@plugin_pool.register_plugin
class WidgetPanelPublisher(CMSPluginBase):
    model = WidgetPanelModel
    module = _("Data Commons")
    name = _("Widget Panel")
    render_template = "focus/widget_panel.html"

    def render(self, context, instance, placeholder):
        context.update({'widget': instance})
        return context
    

@plugin_pool.register_plugin
class CollapsiblePublisher(CMSPluginBase):
    model = CollapsibleModel
    module = _("Data Commons")
    name = _("Collapsible Section")
    render_template = "collapsible/section.html"

    def render(self, context, instance, placeholder):
        context.update({'widget': instance})
        return context

@plugin_pool.register_plugin
class SolidBoxPublisher(CMSPluginBase):
    model = SolidBoxModel
    module = _("Data Commons")
    name = _("Solid Box Section")
    render_template = "solidbox/box.html"

    def render(self, context, instance, placeholder):
        context.update({'widget': instance})
        return context

@plugin_pool.register_plugin
class PriorityAreaHeaderPublisher(CMSPluginBase):
    model = PriorityAreaHeaderModel
    module = _("Data Commons")
    name = _("Priority Area Header")
    render_template = "priority_pages/priority_area_header.html"

    def render(self, context, instance, placeholder):
        context.update({'widget': instance})
        return context
    

@plugin_pool.register_plugin
class SliderImagePublisher(CMSPluginBase):
    admin_preview = False
    inlines = (SimpleSlideAdminInline,)
    model = SimpleSlider
    name = _('Simple Slider')
    render_template = "focus/slider_image_panel.html"

    def render(self, context, instance, placeholder):
        context = super(SliderImagePublisher, self).render(context, instance, placeholder)
        items = instance.simple_slide.all()
        context.update({
            'items': items,
        })
        return context


@plugin_pool.register_plugin
class WidgetPanelAnchorPublisher(CMSPluginBase):
    model = WidgetPanelAnchorsModel
    module = _("Data Commons")
    name = _("Widget Panel Anchor")
    render_template = "focus/widget_panel_anchor.html"

    def render(self, context, instance, placeholder):
        context.update({'widget': instance})
        return context


@plugin_pool.register_plugin
class SearchWidgetPublisher(CMSPluginBase):
    model = SearchWidgetModel
    module = _("Data Commons")
    name = _("Search Widget")
    render_template = "focus/search_widget.html"

    def render(self, context, instance, placeholder):
        context.update({'widget': instance})
        return context
    

@plugin_pool.register_plugin
class ContentBoxPublisher(CMSPluginBase):
    model = ContentBoxModel
    module = _("Data Commons")
    name = _("Colored Content Box")
    render_template = "focus/colored_content_box.html"

    def render(self, context, instance, placeholder):
        linkText = ""
        instanceLink = ""
        instanceText = instance.text
        if instance.link:
            if instance.link_text:
                linkText = instance.link_text
                
            instanceLink = ' <a class="widget-content-box-link" href="' + instance.link + '">' + linkText + ' <img src="' + static('images/link-arrow.svg') + '" class="svg-right-arrow"></a>'
        
        instance.text = '<p>' + instanceText.replace("\n", '</p><p>') + instanceLink + '</p>'
        context.update({'widget': instance})
        return context
    
    
@plugin_pool.register_plugin
class WidgetTitlePublisher(CMSPluginBase):
    model = WidgetTitleModel
    module = _("Data Commons")
    name = _("Widget Title")
    render_template = "focus/widget_title.html"

    def render(self, context, instance, placeholder):
        context.update({'widget': instance})
        return context