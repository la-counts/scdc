from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^profile/$', views.view_self, name='view-self'),
    url(r'^u/(?P<username>[\w\d\-\@]+)/$', views.view_profile, name='view-profile'),
    url(r'^profile/saved-datasets/$', views.saved_datasets, name='saved-datasets'),
    url(r'^profile/saved-stories/$', views.saved_stories, name='saved-stories'),
    url(r'^profile/saved-searches/$', views.saved_searches, name='saved-searches'),
    url(r'^profile/recent-activity/$', views.recent_activity, name='recent-activity'),
    url(r'^profile/view-comments/$', views.view_comments, name='view-comments'),
    url(r'^ajax/follow-search/$', views.follow_search, name='follow-search'),
]
