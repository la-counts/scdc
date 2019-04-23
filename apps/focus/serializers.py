from .models import Concept
from rest_framework import serializers


class ConceptSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Concept
        fields = ['title', 'definition', 'example',
            'alternative_parents', 'related_match', 'exact_match', 'close_match',
            'url_path']
