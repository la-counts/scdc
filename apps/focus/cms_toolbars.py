from django.utils.translation import ugettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cms.utils.urlutils import admin_reverse
from .models import Concept, InterestPage


class FocusToolbar(CMSToolbar):
    supported_apps = (
        'apps.focus',
    )

    watch_models = [Concept, InterestPage]

    def populate(self):
        user = getattr(self.request, 'user', None)
        try:
            view_name = self.request.resolver_match.view_name
        except AttributeError:
            view_name = None

        if not user or not view_name:
            return

        change_concept_perm = user.has_perm(
            'focus.change_concept')
        add_concept_perm = user.has_perm('focus.add_concept')
        change_ip_perm = user.has_perm(
            'focus.change_interestpage')
        add_ip_perm = user.has_perm('focus.add_interestpage')

        menu = self.toolbar.get_or_create_menu('focus-app', _('Concepts'))

        if change_concept_perm:
            menu.add_sideframe_item(
                name=_('Concept list'),
                url=admin_reverse('focus_concept_changelist'),
            )

        if add_concept_perm:
            menu.add_modal_item(
                name=_('Add new concept'),
                url=admin_reverse('focus_concept_add'),
            )

        if change_ip_perm:
            menu.add_sideframe_item(
                name=_('Interest page list'),
                url=admin_reverse('focus_interestpage_changelist'),
            )

        if add_ip_perm:
            menu.add_modal_item(
                name=_('Add new interest page'),
                url=admin_reverse('focus_interestpage_add'),
            )

        if self.is_current_app and self.toolbar.obj:
            obj = self.toolbar.obj
            if isinstance(obj, Concept) and change_concept_perm:
                url = admin_reverse('focus_concept_change', args=[obj.pk])
                menu.add_modal_item(
                    name=_('Edit this concept'),
                    url = url,
                    active = True,
                )
            if isinstance(obj, InterestPage) and change_ip_perm:
                url = admin_reverse('focus_interestpage_change', args=[obj.pk])
                menu.add_modal_item(
                    name=_('Edit this interest page'),
                    url = url,
                    active = True,
                )


toolbar_pool.register(FocusToolbar)  # register the toolbar
