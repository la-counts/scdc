from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'^search/$', views.search, name='search'),
    url(r'^submit-story/$', views.suggest_story, name='submit'),
    url(r'^(?P<slug>[\w\d\-]+)/$', views.detail, name='detail'),
]
