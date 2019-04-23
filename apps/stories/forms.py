from django import forms
from django.utils.timezone import datetime

from apps.focus.fields import ConceptTagWidget, ConceptTagField
from apps.datasets.fields import PublisherSelectWidget, CatalogRecordSelectMultipleWidget
from .models import Story


class SuggestStoryForm(forms.ModelForm):
    tags = ConceptTagField()

    class Meta:
        model = Story
        fields = ['title', 'subheader', 'author', 'organization', 'datasets', 'datasource_urls',
            'body', 'featured_image', 'featured_image_caption', 'tags']
        widgets = {
            'tags': ConceptTagWidget,
            'organization': PublisherSelectWidget,
            'datasets': CatalogRecordSelectMultipleWidget,
        }

    def __init__(self, posted_by, **kwargs):
        self.posted_by = posted_by
        super(SuggestStoryForm, self).__init__(**kwargs)

    def save(self):
        instance = super(SuggestStoryForm, self).save(commit=False)
        instance.posted_by = self.posted_by
        instance.save()
        tags = self['tags'].data
        concepts = self.fields['tags'].concepts_from_tags(tags)
        instance.tags.add(*tags)
        instance.concepts.add(*concepts)
        if self.cleaned_data['datasets']:
            instance.datasets.add(*self.cleaned_data['datasets'])
        return instance


class PublishStoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['title', 'subheader', 'organization', 'datasets',
            'tags', 'concepts', 'body', 'featured_image']

    def __init__(self, approved_by, **kwargs):
        self.approved_by = approved_by
        super(PublishStoryForm, self).__init__(**kwargs)

    def save(self):
        instance = super(PublishStoryForm, self).save(commit=False)
        instance.approved_by = self.approved_by
        instance.publish()
        instance.save()
        return instance
