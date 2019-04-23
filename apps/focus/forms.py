from django import forms

from .models import FeaturedStory, FeaturedCatalogRecord


class FeaturedStoryForm(forms.ModelForm):
    class Meta:
        model = FeaturedStory
        fields = ('__all__')


class FeaturedCatalogRecordForm(forms.ModelForm):
    class Meta:
        model = FeaturedCatalogRecord
        fields = ('__all__')
