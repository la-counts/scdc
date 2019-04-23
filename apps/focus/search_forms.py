from django import forms
from haystack.forms import FacetedSearchForm
from haystack.inputs import Raw, Exact

from apps.focus.models import Concept


as_ids = lambda x: list(x.values_list('pk', flat=True))

class TopicSearchForm(FacetedSearchForm):
    #feild `q` => full text search
    concept = forms.ModelMultipleChoiceField(Concept.objects.all(), required=False)
    keywords = forms.CharField(required=False)


    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        sqs = self.searchqueryset

        if self.cleaned_data['q']:
            sqs = sqs.auto_query(self.cleaned_data['q'])

        if self.cleaned_data['concept']:
            #TODO does not span across exactMatch, relatedMatch & closeMatch
            #expand concept selection to include children concepts
            m_concepts = Concept.objects.get_queryset_descendants(self.cleaned_data['concept'], include_self=True)
            sqs = sqs.filter(concepts__in=as_ids(m_concepts))

        if self.load_all:
            sqs = sqs.load_all()

        return sqs
