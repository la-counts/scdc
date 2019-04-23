from django.conf import settings

from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget

from .models import Story


class StorySelectWidget(ModelSelect2Widget):
    model = Story
    search_fields = [
        'title__icontains'
    ]


class StorySelectMultipleWidget(ModelSelect2MultipleWidget):
    model = Story
    search_fields = [
        'title__icontains'
    ]
