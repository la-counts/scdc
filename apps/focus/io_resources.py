from import_export import resources, fields, widgets
from .models import Concept


class ConceptResource(resources.ModelResource):
    parent = fields.Field(widget=widgets.ForeignKeyWidget(Concept))

    class Meta:
        model = Concept
        fields = ['id', 'title', 'slug', 'definition',
            'example', 'parent', 'alternative_parents',
            'related_match', 'exact_match', 'close_match']
