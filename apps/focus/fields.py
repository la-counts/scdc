from django.conf import settings
from django import forms
from django.db.models import Q, Count
from django.utils.encoding import force_text

from django_select2.forms import ModelSelect2TagWidget, ModelSelect2Widget, ModelSelect2MultipleWidget
from taggit.models import Tag, TaggedItem

from .models import Concept


class TokenSeperatorMixin(object):
    def build_attrs(self, extra_attrs=None, **kwargs):
        self.attrs.setdefault('data-token-separators', '[","]')
        return super(TokenSeperatorMixin, self).build_attrs(extra_attrs, **kwargs)


class TagWidget(TokenSeperatorMixin, ModelSelect2TagWidget):
    search_fields = [
        'name__icontains'
    ]
    model = Tag

    def render_options(self, *args):
        """
        Work around for rendering options with django-taggit.

        See: https://github.com/alex/django-taggit/issues/368
        """
        selected_choices, = args
        output = []
        print(type(selected_choices), getattr(selected_choices, 'model', None))
        if getattr(selected_choices, 'model', None) == TaggedItem:
            tags = Tag.objects.filter(taggit_taggeditem_items__in=selected_choices)
            #selected_choices = selected_choices.values_list('tag_id', flat=True)
        else:
            tags = selected_choices
        #assert tags.model == Tag
        for tag in tags:
            k, label = tag.id, force_text(tag.name)
            output.append('<option value="%s" selected="selected">%s</option>' % (k, label))
        return '\n'.join(output)

    def value_from_datadict(self, data, files, name):
        values = super(TagWidget, self).value_from_datadict(data, files, name)
        #values is a list of strings, but some values may be concept ids
        numbers_seen = list(filter(lambda x: x.isdigit(), values))
        qs = self.model.objects.all().filter(id__in=numbers_seen)
        tag_values = list(qs)
        pks = set(str(obj.id) for obj in tag_values)
        for val in values:
            if val not in pks:
                tag = Tag.objects.filter(name__iexact=val).first()
                if tag:
                    val = tag
                else:
                    val = Tag.objects.create(name=val)
                tag_values.append(val)
        return tag_values


class SortedTagWidget(TagWidget):
    '''
    Tag selection widget that favours concepts
    '''
    search_fields = [
        'name__icontains'
    ]
    model = Tag

    def get_queryset(self):
        #TODO can we join concept and tag by name?
        #sql alchemy?
        qs = Tag.objects.all().annotate(
            num_concepts=Count('concept'),
        )
        qs = qs.order_by('-num_concepts', 'name')
        return qs


class ConceptLookupMixin(object):
    search_fields = [
        'title__icontains'
    ]
    queryset = Concept.objects.all()
    model = Concept


class ConceptMultipleSelectWidget(TokenSeperatorMixin, ConceptLookupMixin, ModelSelect2MultipleWidget):
    '''
    Select multiple concepts
    '''
    pass


class ConceptTagWidget(SortedTagWidget):
    '''
    Tag selection widget that automaps to concepts as well as tags
    '''
    def concepts_from_tags(self, tag_values):
        return Concept.objects.all().from_tags(tag_values)


class ConceptTagAdminWidget(TokenSeperatorMixin, ConceptLookupMixin, ModelSelect2TagWidget):
    '''
    Staff only multi-select widget that can create concepts on the fly
    '''
    def value_from_datadict(self, data, files, name):
        values = super(ConceptTagAdminWidget, self).value_from_datadict(data, files, name)
        #values is a list of strings, but some values may be concept ids
        numbers_seen = list(filter(lambda x: x.isdigit(), values))
        qs = self.queryset.filter(id__in=numbers_seen)
        pks = set(map(str, qs.values_list('id', flat=True)))
        concept_values = []
        for val in values:
            if val not in pks:
                obj = self.model.objects.get_or_create(title=val)[0]
                obj.save() #trigger autoslugfield
                concept_values.append(obj.id)
            else:
                concept_values.append(val)
        return concept_values


class ConceptSelectWidget(TokenSeperatorMixin, ConceptLookupMixin, ModelSelect2Widget):
    '''
    Select a single concept
    '''
    pass


class ConceptTagField(forms.MultipleChoiceField):
    widget = ConceptTagWidget

    def validate(self, value):
        return True #any tags are accepted for now

    def concepts_from_tags(self, tag_values):
        return Concept.objects.all().from_tags(tag_values)


#TODO fancy tree widget for concepts
