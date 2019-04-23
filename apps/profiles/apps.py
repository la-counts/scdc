from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    name = 'apps.profiles'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('User'))
        registry.register(self.get_model('SavedSearch'))
