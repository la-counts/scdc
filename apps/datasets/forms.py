from django import forms
from django.core.mail import mail_managers
from cms.utils.urlutils import admin_reverse
import json

from apps.focus.fields import ConceptTagWidget
from .models import CatalogRecord, DatasourceSuggestion


class SuggestDatasetForm(forms.ModelForm):
    class Meta:
        model = CatalogRecord
        fields = ['title', 'distribution_fields', 'description', 'tags']
        widgets = {
            'tags': ConceptTagWidget,
        }

    def __init__(self, submitted_by, **kwargs):
        self.submitted_by = submitted_by
        super(SuggestDatasetForm, self).__init__(**kwargs)

    def save(self):
        instance = super(SuggestDatasetForm, self).save(commit=False)
        instance.submitted_by = self.submitted_by
        instance.save()
        concepts, tags = self['tags'].data
        instance.tags.add(*tags)
        instance.concepts.add(*concepts)
        url = admin_reverse('datasets_dataset_change', args=[instance.pk])
        #TODO prepend site url
        message = 'A user has submitted a dataset: %s' % url
        mail_managers('New Dataset suggestion', message, fail_silently=True)
        return instance


class SubmitDataSourcesForm(forms.Form):
    url = forms.URLField() #supports multiple getlist though
    message = forms.CharField(widget=forms.Textarea)

    def __init__(self, submitted_by, instance=None, **kwargs):
        self.submitted_by = submitted_by
        self.instance = instance
        super(SubmitDataSourcesForm, self).__init__(**kwargs)

    def clean_url(self):
        #TODO validate
        return self.data.getlist('url')

    def save(self):
        submission = json.dumps(dict(self.cleaned_data))
        instance = DatasourceSuggestion(submitted_by=self.submitted_by, submission=submission)
        instance.save()
        return instance
