from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.core.paginator import Paginator
from haystack.generic_views import FacetedSearchView
from haystack.constants import DJANGO_CT

from .models import CatalogRecord, Publisher, DatasourceSuggestion
from .search_forms import AdvancedDatasetSearchForm
from .forms import SuggestDatasetForm, SubmitDataSourcesForm
from apps.stories.models import Story
from apps.focus.models import Concept
from data_commons.contrib.rdf import detect_rdf_request
import datetime


def index(request):
    items = Publisher.objects.root_nodes()
    ctx = {
        'publishers': items

    }
    return render(request, 'datasets/index.html', ctx)

def dataset_detail(request, object_id):
    '''
    Render the details of a dataset/record
    '''
    dataset = get_object_or_404(CatalogRecord, pk=object_id)
    rdfer = detect_rdf_request(request)
    if rdfer:
        return rdfer(dataset.add_rdf_catalog_record)
    ctx = {
        'dataset': dataset #TODO obj merged with lookup()
    }
    if hasattr(request, 'toolbar'):
        request.toolbar.set_object(dataset)
    return render(request, 'datasets/dataset_detail.html', ctx)

def publisher_detail(request, slug):
    publisher = get_object_or_404(Publisher, slug=slug)
    ctx = {
        'publisher': publisher
    }
    if hasattr(request, 'toolbar'):
        request.toolbar.set_object(publisher)
    return render(request, 'datasets/publisher_detail.html', ctx)


class DatasetSearchView(FacetedSearchView):
    facet_fields = ['concepts', 'publisher', 'access_level', DJANGO_CT]
    template_name = 'datasets/search.html'
    form_class = AdvancedDatasetSearchForm

    def get_context_data(self, **kwargs):
        extra = super(DatasetSearchView, self).get_context_data(**kwargs)
        #extra['facets']['fields']['concepts'] = [(id, count)]
        #populate a concept tree based on faceted results
        facets = extra['facets']

        extra['selected_facets'] = self.request.GET.getlist('selected_facets')

        #print('facets:', facets)

        if extra['form'].is_valid():
            extra['form'].read_facets(facets)
        return extra

dataset_search = DatasetSearchView.as_view()


class SuggestDatasetView(CreateView):
    '''
    Creates an unpublished dataset for review
    '''
    template_name = 'datasets/suggest_dataset.html'
    model = CatalogRecord
    form_class = SuggestDatasetForm
    success_url = '/catalog/dataset-submitted/'

    def get_form_kwargs(self, **kwargs):
        kwargs = CreateView.get_form_kwargs(self, **kwargs)
        kwargs['submitted_by'] = self.request.user
        return kwargs

suggest_dataset = SuggestDatasetView.as_view()


class SubmitDatasourcesView(CreateView):
    '''
    Submits datasouce urls for review
    '''
    template_name = 'datasets/suggest_datasources.html'
    model = DatasourceSuggestion
    form_class = SubmitDataSourcesForm
    success_url = '/catalog/datasources-submitted/'

    def get_form_kwargs(self, **kwargs):
        kwargs = CreateView.get_form_kwargs(self, **kwargs)
        kwargs['submitted_by'] = self.request.user
        return kwargs

submit_datasources = SubmitDatasourcesView.as_view()


class RelatedDatasetsView(ListView):
    model = CatalogRecord
    template_name = 'datasets/related_datasets.html'
    paginate_by = 20

    def get_queryset(self):
        self.catalog_record = CatalogRecord.objects.get(pk=self.kwargs['object_id'])
        return self.catalog_record.related_records()

    def get_context_data(self, **kwargs):
        ctx = ListView.get_context_data(self, **kwargs)
        ctx['dataset'] = self.catalog_record
        return ctx

related_datasets = RelatedDatasetsView.as_view()

class RelatedStoriesView(ListView):
    model = Story
    template_name = 'datasets/related_stories.html'
    paginate_by = 20

    def get_queryset(self):
        self.catalog_record = CatalogRecord.objects.get(pk=self.kwargs['object_id'])
        return self.catalog_record.related_stories()

    def get_context_data(self, **kwargs):
        ctx = ListView.get_context_data(self, **kwargs)
        ctx['dataset'] = self.catalog_record
        return ctx

related_stories = RelatedStoriesView.as_view()

class LinkedStoriesView(ListView):
    model = Story
    template_name = 'datasets/linked_stories.html'
    paginate_by = 20

    def get_queryset(self):
        self.catalog_record = CatalogRecord.objects.get(pk=self.kwargs['object_id'])
        return self.catalog_record.linked_stories.all()

    def get_context_data(self, **kwargs):
        ctx = ListView.get_context_data(self, **kwargs)
        ctx['dataset'] = self.catalog_record
        return ctx

linked_stories = LinkedStoriesView.as_view()


class PublisherDatasetsView(ListView):
    model = CatalogRecord
    template_name = 'datasets/publisher_datasets.html'
    paginate_by = 20

    def get_queryset(self):
        self.publisher = Publisher.objects.get(slug=self.kwargs['slug'])
        return self.publisher.catalogrecord_set.all()

    def get_context_data(self, **kwargs):
        ctx = ListView.get_context_data(self, **kwargs)
        ctx['publisher'] = self.publisher
        return ctx

publisher_datasets = PublisherDatasetsView.as_view()


class PublisherStoriesView(ListView):
    model = Story
    template_name = 'datasets/publisher_stories.html'
    paginate_by = 20

    def get_queryset(self):
        self.publisher = Publisher.objects.get(slug=self.kwargs['slug'])
        return self.publisher.story_set.all()

    def get_context_data(self, **kwargs):
        ctx = ListView.get_context_data(self, **kwargs)
        ctx['publisher'] = self.publisher
        return ctx

publisher_stories = PublisherStoriesView.as_view()


class DatasetListView(ListView):
    model = CatalogRecord
    template_name = 'datasets/dataset_list.html'
    paginate_by = 20

    def get_queryset(self):
        return self.model.objects.published().order_by('title').select_related()

dataset_list = DatasetListView.as_view()
