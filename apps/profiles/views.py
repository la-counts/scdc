from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, View
from django.views.generic.edit import UpdateView
from django.http import HttpResponse, QueryDict
from django.contrib.auth.decorators import login_required

from actstream.models import Follow
from actstream.actions import follow, unfollow
from rest_framework import viewsets

from apps.stories.models import Story
from apps.datasets.models import CatalogRecord
from apps.profiles.models import User
#TODO should be configurable in settings
from apps.focus.search_forms import TopicSearchForm
from .models import SavedSearch
from .forms import ProfileForm
from .serializers import UserSerializer


class SavedDatasetsView(ListView):
    model = CatalogRecord
    template_name = 'profiles/saved_datasets.html'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.following(user, CatalogRecord)

saved_datasets = login_required(SavedDatasetsView.as_view())


class SavedSearchesView(ListView):
    model = SavedSearch
    template_name = 'profiles/saved_searches.html'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.following(user, SavedSearch)

saved_searches = login_required(SavedSearchesView.as_view())


class SavedStoriesView(ListView):
    model = Story
    template_name = 'profiles/saved_stories.html'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.following(user, Story)

saved_stories = login_required(SavedStoriesView.as_view())


#TODO rate limit actions
class FollowSearchView(View):
    search_form_class = TopicSearchForm

    def post(self, request):
        '''
        Post a search form to follow
        '''
        form = self.search_form_class(request.POST)
        if form.is_valid():
            ss = SavedSearch.from_search_form(form)
            follow(request.user, ss)
            return HttpResponse(status=201)
        return HttpResponse(status=403)

    #are we allowed to delete with post data?
    def delete(self, request):
        '''
        Delete a search form to unfollow
        '''
        body = QueryDict(request.body)
        form = self.search_form_class(body)
        if form.is_valid():
            ss = SavedSearch.from_search_form(form)
            unfollow(request.user, ss)
            return HttpResponse(status=204)
        return HttpResponse(status=403)
follow_search = login_required(FollowSearchView.as_view())


def view_profile(request, username):
    user = get_object_or_404(User, username=username)
    ctx = {
        'profile': user
    }
    return render(request, 'profiles/view_profile.html', ctx)


class ProfileView(UpdateView):
    template_name = 'profiles/view_self.html'
    success_url = '/accounts/profile/'
    model = User
    form_class = ProfileForm

    def get_object(self, queryset=None):
        return self.request.user

view_self = login_required(ProfileView.as_view())


def recent_activity(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    #CONSIDER this display actions by user, slighty different then comps but more practical
    '''
    from actstream.models import actor_stream
    actor_stream(user)
    '''
    ctx = {
        #'activities': user.actor_actions.all()[:10], #TODO list view?
        'profile': user,
    }
    return render(request, 'profiles/recent_activity.html', ctx)


def view_comments(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    ctx = {
        'comments': user.comment_comments.all(),
        'profile': user
    }
    return render(request, 'profiles/view_comments.html', ctx)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
