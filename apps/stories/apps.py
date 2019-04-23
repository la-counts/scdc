from django.apps import AppConfig


class StoriesConfig(AppConfig):
    name = 'apps.stories'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Story'))
