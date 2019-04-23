from django.apps import AppConfig


class DatasetsConfig(AppConfig):
    name = 'apps.datasets'
    verbose_name = 'Data Inventory'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('CatalogRecord'))
