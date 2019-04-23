from django.forms.models import model_to_dict


class AutoSave(object):
    '''
    with AutoSave(user):
        user.name = 'John'

    #will save if any fields changed
    '''
    def __init__(self, instance):
        self.instance = instance

    def _dict(self, instance):
        return model_to_dict(instance, fields=[field.name for field in
                             instance._meta.fields])

    def _diff(self, other):
        d1 = self.state
        d2 = other
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    def get_state(self):
        return self._dict(self.instance)

    def snapshot(self):
        self.state = self.get_state()
        self.saved = False

    @property
    def changed_fields(self):
        return self._diff(self.get_state())

    @property
    def has_changed(self):
        return bool(self.changed_fields)

    def commit(self):
        self.instance.save()
        self.saved = True

    def autocommit(self):
        if self.has_changed or not self.instance.pk:
            self.commit()

    def __enter__(self):
        self.snapshot()

    def __exit__(self, *args):
        self.autocommit()
