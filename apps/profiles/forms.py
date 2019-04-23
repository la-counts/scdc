from django import forms
from django.contrib.auth import forms as authforms
from registration.forms import RegistrationForm as BaseRegistrationForm
from registration.validators import DUPLICATE_EMAIL

from apps.focus.fields import ConceptTagWidget, ConceptTagAdminWidget, ConceptTagField
from apps.datasets.fields import PublisherSelectWidget
from .models import User


class RegistrationForm(BaseRegistrationForm):
    # interests = ConceptTagField()

    class Meta:
        model = User
        fields = ['display_name', 'email']
        
    def clean(self):
        self.cleaned_data['username'] = self.cleaned_data['email']
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError(DUPLICATE_EMAIL, code='duplicate')
        return super(RegistrationForm, self).clean()

    def save(self, commit=True):
        instance = super(RegistrationForm, self).save(commit=False)
        instance.username = self.cleaned_data['email']
        instance.save()
        # tags = self['interests'].data
        # concepts = self.fields['interests'].concepts_from_tags(tags)
        # instance.interests.add(*tags)
        # instance.concepts.set(concepts)
        return instance


class ProfileForm(forms.ModelForm):
    interests = ConceptTagField()

    class Meta:
        model = User
        fields = ['display_name', 'email', 'title', 'organization', 'website', 'interests', 'avatar']
        widgets = {
            'interests': ConceptTagWidget, #TODO this widget will not load prior tags...
        }

    def save(self, commit=True):
        instance = super(ProfileForm, self).save(commit=commit)
        tags = self['interests'].data
        concepts = self.fields['interests'].concepts_from_tags(tags)
        instance.interests.set(*tags, clear=True) #TODO remove other tags
        instance.concepts.set(concepts)
        return instance


class UserCreationForm(authforms.UserCreationForm):
    class Meta:
        exclude = []
        model = User


class UserChangeForm(authforms.UserChangeForm):
    class Meta:
        exclude = []
        model = User
        widgets = {
            'concepts': ConceptTagAdminWidget,
            'publisher': PublisherSelectWidget,
        }
