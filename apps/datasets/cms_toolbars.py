from django.utils.translation import ugettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cms.utils.urlutils import admin_reverse
from .models import CatalogRecord, Publisher


class DatasetsToolbar(CMSToolbar):
    supported_apps = (
        'apps.datasets',
    )

    watch_models = [CatalogRecord, Publisher]

    def populate(self):
        user = getattr(self.request, 'user', None)
        try:
            view_name = self.request.resolver_match.view_name
        except AttributeError:
            view_name = None

        if not user or not view_name:
            return

        change_ds_perm = user.has_perm(
            'datasets.change_catalogrecord')
        add_ds_perm = user.has_perm('datasets.add_catalogrecord')
        change_pub_perm = user.has_perm(
            'datasets.change_publisher')
        add_pub_perm = user.has_perm('datasets.add_publisher')

        menu = self.toolbar.get_or_create_menu('datasets-app', _('Datasets'))

        if change_ds_perm:
            menu.add_sideframe_item(
                name=_('Dataset list'),
                url=admin_reverse('datasets_catalogrecord_changelist'),
            )

        if add_ds_perm:
            menu.add_modal_item(
                name=_('Add new dataset'),
                url=admin_reverse('datasets_catalogrecord_add'),
            )

        if change_pub_perm:
            menu.add_sideframe_item(
                name=_('Publisher list'),
                url=admin_reverse('datasets_publisher_changelist'),
            )

        if add_pub_perm:
            menu.add_modal_item(
                name=_('Add new publisher'),
                url=admin_reverse('datasets_publisher_add'),
            )

        if self.is_current_app and self.toolbar.obj:
            obj = self.toolbar.obj
            if isinstance(obj, CatalogRecord) and change_ds_perm:
                url = admin_reverse('datasets_catalogrecord_change', args=[obj.pk])
                menu.add_modal_item(
                    name=_('Edit this dataset'),
                    url = url,
                    active = True,
                )
            if isinstance(obj, Publisher) and change_pub_perm:
                url = admin_reverse('datasets_publisher_change', args=[obj.pk])
                menu.add_modal_item(
                    name=_('Edit this publisher'),
                    url = url,
                    active = True,
                )


toolbar_pool.register(DatasetsToolbar)  # register the toolbar
