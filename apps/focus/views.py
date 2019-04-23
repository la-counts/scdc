from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import ListView
from haystack.generic_views import SearchView
from rest_framework import viewsets

from .models import Concept, InterestPage
from .search_forms import TopicSearchForm
from .serializers import ConceptSerializer
from apps.datasets.models import CatalogRecord
from apps.stories.models import Story
from data_commons.contrib.rdf import detect_rdf_request


def index(request):
    ctx = {
        'pages': InterestPage.objects.published(),
    }
    return render(request, 'focus/index.html', ctx)


class FocusSearchView(SearchView):
    template_name = 'focus/search.html'
    form_class = TopicSearchForm

search = FocusSearchView.as_view()


class ConceptListView(ListView):
    '''
    Renders a page listing of concepts, but also supports RDF
    '''
    model = Concept
    queryset = Concept.objects.all()
    template_name = 'focus/concept_index.html'
    paginate_by = 50

    def get(self, *args, **kwargs):
        request = self.request
        rdfer = detect_rdf_request(request)
        if rdfer:
            return rdfer(Concept.add_rdf_scheme)
        return super(ConceptListView, self).get(*args, **kwargs)

concept_index = ConceptListView.as_view()


def concept_detail(request, path):
    concept = get_object_or_404(Concept, url_path=path)
    rdfer = detect_rdf_request(request)
    if rdfer:
        return rdfer(concept.add_rdf_concept)
    else:
        ctx = {
            'concept': concept
        }
        if hasattr(request, 'toolbar'):
            request.toolbar.set_object(concept)
        return render(request, 'focus/concept_detail.html', ctx)


class ConceptDatasetsView(ListView):
    model = CatalogRecord
    template_name = 'focus/concept_datasets.html'
    paginate_by = 20

    def get_queryset(self):
        self.concept = Concept.objects.get(url_path=self.kwargs['path'])
        return CatalogRecord.objects.filter(concepts=self.concept)

    def get_context_data(self, **kwargs):
        ctx = ListView.get_context_data(self, **kwargs)
        ctx['concept'] = self.concept
        return ctx

concept_datasets = ConceptDatasetsView.as_view()

class ConceptStoriesView(ListView):
    model = Story
    template_name = 'focus/concept_stories.html'
    paginate_by = 20

    def get_queryset(self):
        self.concept = Concept.objects.get(url_path=self.kwargs['path'])
        return Story.objects.filter(concepts=self.concept)

    def get_context_data(self, **kwargs):
        ctx = ListView.get_context_data(self, **kwargs)
        ctx['concept'] = self.concept
        return ctx

concept_stories = ConceptStoriesView.as_view()


def page_detail(request, slug):
    page = get_object_or_404(InterestPage, slug=slug)
    ctx = {
        'page': page
    }
    if hasattr(request, 'toolbar'):
        request.toolbar.set_object(page)
    return render(request, 'focus/page_detail.html', ctx)


class ConceptViewSet(viewsets.ModelViewSet):
    queryset = Concept.objects.all()
    serializer_class = ConceptSerializer
