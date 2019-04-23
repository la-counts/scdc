from django.utils.translation import ugettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cms.utils.urlutils import admin_reverse
from .models import Story


class StoriesToolbar(CMSToolbar):
    supported_apps = (
        'apps.stories',
    )

    watch_models = [Story]

    def populate(self):
        user = getattr(self.request, 'user', None)
        try:
            view_name = self.request.resolver_match.view_name
        except AttributeError:
            view_name = None

        if not user or not view_name:
            return

        change_story_perm = user.has_perm(
            'stories.change_story')
        delete_story_perm = user.has_perm(
            'stories.delete_story')
        add_story_perm = user.has_perm('stories.add_story')

        menu = self.toolbar.get_or_create_menu('stories-app', _('Stories'))

        if change_story_perm:
            menu.add_sideframe_item(
                name=_('Story submissions'),
                url=admin_reverse('stories_story_changelist') + "?state__exact=new",
            )

        if add_story_perm:
            menu.add_modal_item(
                name=_('Add new story'),
                url=admin_reverse('stories_story_add'),
            )

        if self.is_current_app and change_story_perm and self.toolbar.obj:
            obj = self.toolbar.obj
            url = admin_reverse('stories_story_change', args=[obj.pk])
            menu.add_modal_item(
                name=_('Edit this story'),
                url = url,
                active = True,
            )


toolbar_pool.register(StoriesToolbar)  # register the toolbar
