from django import forms

from apps.focus.fields import ConceptTagWidget #CONSIDER move to data commons


class ConceptTagField(forms.MultipleChoiceField):
    widget = ConceptTagWidget

    def validate(self, value):
        return True #any tags are accepted for now
