from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^concept/$', views.concept_index, name='concept_index'),
    url(r'^concept/(?P<path>.+)/stories/$', views.concept_stories, name='concept_stories'),
    url(r'^concept/(?P<path>.+)/datasets/$', views.concept_datasets, name='concept_datasets'),
    url(r'^concept/(?P<path>.+)/$', views.concept_detail, name='concept_detail'),
    url(r'^interest/(?P<slug>[\w\d\-]+)/$', views.page_detail, name='page_detail'),
]
