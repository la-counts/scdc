from django import forms
from django.forms import widgets
from haystack.forms import FacetedSearchForm
from haystack.inputs import AutoQuery, Clean
from haystack.utils.geo import Point, D
from haystack.constants import DJANGO_CT
import datetime
import json
from collections import OrderedDict, defaultdict

from .models import Publisher, SpatialEntity, CatalogRecord
from apps.focus.models import Concept, InterestPage
from apps.stories.models import Story

from .fields import PublisherSelectMulitpleWidget, SpatialEntitySelectMultipleWidget
from .constants import ACCESS_LEVEL_CHOICES
from apps.focus.fields import ConceptMultipleSelectWidget


as_ids = lambda x: list(x.values_list('pk', flat=True))


SORT_CHOICES = [
    ('', 'Best Match'),
    #('-percentage_complete', 'Percentage Complete'),
    ('-temporal_start', 'Last Created'),
    ('temporal_start', 'First Created'),
    ('-modified', 'Last Modified'),
    ('-issued', 'Last Published'),
    ('issued', 'First Published'),
    ('title_s', 'Title'),
    ('-download_count', 'Downloads'),
    ('-duration', 'Duration'),
]

MODEL_CHOICES = [
    ('Story', 'Stories'),
    ('CatalogRecord', 'Datasets'),
    ('InterestPage', 'Focus Areas'),
]

model_choice_to_model = lambda x: {
    'Story': Story,
    'CatalogRecord': CatalogRecord,
    'InterestPage': InterestPage,
}[x]


#TODO on initial search we should store active facets into a hidden field
class AdvancedDatasetSearchForm(FacetedSearchForm):
    #feild `q` => full text search
    #CONSIDER: should the model keu values be the title of these entitity?
    title = forms.CharField(required=False)
    license = forms.CharField(required=False)
    spatial = forms.CharField(required=False)
    funded_by = forms.CharField(required=False)
    exclude = forms.CharField(required=False)
    domain = forms.CharField(required=False)
    result_types = forms.MultipleChoiceField(choices=MODEL_CHOICES,
        widget=widgets.CheckboxSelectMultiple, required=False, initial=[])#'Story', 'CatalogRecord'])
    concept = forms.ModelMultipleChoiceField(Concept.objects.all(),
        widget=ConceptMultipleSelectWidget, required=False)
    publisher = forms.ModelMultipleChoiceField(Publisher.objects.all(),
        widget=PublisherSelectMulitpleWidget, required=False)
    access_level = forms.MultipleChoiceField(choices=ACCESS_LEVEL_CHOICES,
        widget=widgets.CheckboxSelectMultiple, required=False)
    spatial_entity = forms.ModelMultipleChoiceField(SpatialEntity.objects.all(),
        widget=SpatialEntitySelectMultipleWidget, required=False)
    language = forms.CharField(required=False)
    location_lat = forms.FloatField(required=False)
    location_lng = forms.FloatField(required=False)

    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False)
    no_q = forms.BooleanField(required=False)

    facet_display = forms.CharField(required=False, widget=widgets.HiddenInput)

    def is_valid(self):
        super(AdvancedDatasetSearchForm, self).is_valid()
        if self.data.get('no_q'):
            self.errors.pop('q', None)
        elif not self.data.get('q'):
            self.errors['q']= forms.ValidationError('Query is required')
        return not bool(self.errors)

    def read_facets(self, facets, formdata=None):
        if not formdata:
            formdata = self.cleaned_data or self.data

        def build_temporal_map(ids):
            timestamps = [int(sid) for sid in ids if sid != 'None']
            mapping = OrderedDict( (t, datetime.datetime.fromtimestamp(t/1000 + 24*60*60) )
                for t in timestamps )
            if 'None' in ids:
                mapping[None] = None
            return mapping

        def build_map(ids, Model):
            model_ids = [int(sid) for sid in ids if sid != 'None']
            qs = Model.objects.all().filter(id__in=model_ids)
            mapping = OrderedDict( (c.id, c) for c in qs )
            if 'None' in ids:
                mapping[None] = None
            return mapping

        def build_count_map(prefix, facet_results_entry):
            return { '%s-%s' % (prefix, sid): cnt for sid, cnt in facet_results_entry }

        self.facets = defaultdict(OrderedDict) #id => obj
        self.facet_counts = dict()

        #facets from prior search
        if formdata.get('facet_display', None):
            visible_facets = json.loads(formdata['facet_display'])

            for key, ids in visible_facets.items():
                if key == 'concepts':
                    self.facets['concepts'] = build_map(ids, Concept)
                elif key == 'publisher':
                    self.facets['publisher'] = build_map(ids, Publisher)
                elif key == 'temporal_start':
                    self.facets['temporal_start'] = build_temporal_map(ids)
                else:
                    self.facets[key] = OrderedDict( (sid, sid) for sid in ids )

        #facets from this search result
        if 'fields' in facets:
            for key, facet_results in facets['fields'].items():
                self.facet_counts.update(build_count_map(key, facet_results))
                ids = [sid for sid, cnt in facet_results]
                if key == 'concepts':
                    self.facets['concepts'].update(build_map(ids, Concept))
                elif key == 'publisher':
                    self.facets['publisher'].update(build_map(ids, Publisher))
                elif key == 'temporal_start':
                    self.facets['temporal_start'].update(build_temporal_map(ids))
                else:
                    self.facets[key].update(OrderedDict( (sid, sid) for sid in ids ))

        #stash initial facets
        if self.facets and not formdata.get('facet_display', None):
            #store visible facets
            #print(dir(self.fields['facet_display']))
            self.data = self.data.copy()
            self.data['facet_display'] = json.dumps({
                key: list(obj_count.keys())
                for key, obj_count in self.facets.items() if len(obj_count)
            })
            #self.initial['facet_display'] = json.dumps(facets['fields'])

        def generate_facet_chocies_with_count(key, labels=None):
            choices = []
            for sid, obj in self.facets[key].items():
                count = self.facet_counts.get('%s-%s' % (key, sid), None)
                if labels and str(obj) in labels:
                    obj = labels[obj]
                if count:
                    label = "%s (%s)" % (obj, count)
                else:
                    label = str(obj)
                choices.append((sid, label))
            return choices

        def generate_facet_multiple_choice_field(key, labels=None):
            choices = generate_facet_chocies_with_count(key, labels=labels)
            default = list(self.facets[key].keys())
            return forms.MultipleChoiceField(choices=choices, initial=default,
                widget=widgets.CheckboxSelectMultiple, required=False,
            )

        #facet_fields = ['concepts', 'publisher', 'web_domains', 'funded_by', 'temporal_start']
        #with self.facets, construct a multiple choice field with checkboxes
        if self.facets.get('concepts', None):
            self.fields['concept'] = generate_facet_multiple_choice_field('concepts')
        if self.facets.get('publisher', None):
            self.fields['publisher'] = generate_facet_multiple_choice_field('publisher')
        if self.facets.get('web_domains', None):
            self.fields['domain'] = generate_facet_multiple_choice_field('web_domains')
        if self.facets.get('funded_by', None):
            self.fields['funded_by'] = generate_facet_multiple_choice_field('funded_by')
        #if self.facets.get('temporal_start', None):
        #    self.fields['temporal_start'] = generate_facet_multiple_choice_field('temporal_start')
        if self.facets.get('access_level', None):
            self.fields['access_level'] = generate_facet_multiple_choice_field('access_level')
        if self.facets.get(DJANGO_CT, None):
            labels = {
                'stories.story': 'Story',
                'datasets.catalogrecord': 'CatalogRecord',
                'focus.interestpage': 'InterestPage',
            }
            self.fields['result_types'] = generate_facet_multiple_choice_field(DJANGO_CT, labels={
                'stories.story': 'Stories',
                'datasets.catalogrecord': 'Datasets',
                'focus.interestpage': 'Focus Areas',
            })
            self.fields['result_types'].choices = [ (labels[val], label) for val, label in self.fields['result_types'].choices]

        return None

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        sqs = self.searchqueryset

        for facet in self.selected_facets:
            if ":" not in facet:
                continue

            field, value = facet.split(":", 1)

            if value:
                sqs = sqs.narrow(u'%s:%s' % (field, value))
                
        #print(self.cleaned_data)

        if self.cleaned_data['q']:
            sqs = sqs.auto_query(self.cleaned_data['q'])
        
        if self.cleaned_data['title']:
            sqs = sqs.filter(title=AutoQuery(self.cleaned_data['title']))

        if self.cleaned_data['license']:
            sqs = sqs.filter(license=AutoQuery(self.cleaned_data['license']))

        if self.cleaned_data['funded_by']:
            sqs = sqs.filter(funded_by=AutoQuery(self.cleaned_data['funded_by']))

        if self.cleaned_data['domain']:
            sqs = sqs.filter(web_domains__in=AutoQuery(self.cleaned_data['domain']))

        if self.cleaned_data['exclude']:
            sqs = sqs.exclude(content=Clean(self.cleaned_data['exclude']))

        if self.cleaned_data['concept']:
            #expand concept selection as wide as we can
            m_concepts = self.cleaned_data['concept'].search_matched().alternative_children().get_descendants(include_self=True)
            sqs = sqs.filter(concepts__in=as_ids(m_concepts.distinct()))
            #TODO use keywords to search meta data (dataset's own reported keywords)?

        if self.cleaned_data['publisher']:
            #TODO expand publisher selection to include subpublishers
            m_publishers = self.cleaned_data['publisher']
            sqs = sqs.filter(publisher__in=as_ids(m_publishers))

        if self.cleaned_data['spatial_entity']:
            sqs = sqs.filter(spatial_entity__in=as_ids(self.cleaned_data['spatial_entity']))

        if self.cleaned_data['location_lng'] and self.cleaned_data['location_lat']:
            point = Point(self.cleaned_data['location_lat'], self.cleaned_data['location_lng'])
            sqs = sqs.dwithin('location', point, D(mi=2))

        if self.cleaned_data['language']:
            sqs = sqs.filter(language=self.cleaned_data['language'])

        if self.cleaned_data['access_level']:
            sqs = sqs.filter(access_level__in=self.cleaned_data['access_level'])

        if self.cleaned_data['sort_by']:
            sqs = sqs.order_by(self.cleaned_data['sort_by'])

        if self.cleaned_data['result_types']:
            models = map(model_choice_to_model, self.cleaned_data['result_types'])
            sqs = sqs.models(*models)
        else:
            sqs = sqs.models(Story, CatalogRecord)
        
        return sqs
