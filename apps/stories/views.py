from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from .models import Story
from .forms import SuggestStoryForm, PublishStoryForm
from .jobs import map_story_datasource_urls_job


class StoryListView(ListView):
    model = Story
    queryset = Story.objects.published().select_related()
    template_name = 'stories/index.html'
    paginate_by = 12
    #TODO if first page, page size is 11?
    

index = StoryListView.as_view()

def detail(request, slug):
    story = get_object_or_404(Story, slug=slug)
    context = {
        'story': story
    }
    if hasattr(request, 'toolbar'):
        request.toolbar.set_object(story)
    return render(request, 'stories/detail.html', context)


class SuggestStoryView(CreateView):
    '''
    Creates an unpublished story for review
    '''
    template_name = 'stories/suggest_story.html'
    model = Story
    form_class = SuggestStoryForm
    success_url = '/pages/story-submitted/'

    def get_form_kwargs(self, **kwargs):
        kwargs = CreateView.get_form_kwargs(self, **kwargs)
        kwargs['posted_by'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = CreateView.form_valid(self, form)
        map_story_datasource_urls_job.delay(self.object.id)
        return response

suggest_story = SuggestStoryView.as_view()
