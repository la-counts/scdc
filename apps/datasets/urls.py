from django.conf.urls import url
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^$', RedirectView.as_view(url='/catalog/datasets/'), name='index'),
    url(r'^search/$', views.dataset_search, name='dataset_search'),
    url(r'^suggest/$', views.suggest_dataset, name='suggest_dataset'),
    url(r'^submit-datasources/$', views.submit_datasources, name='submit_datasources'),
    url(r'^publisher/(?P<slug>[\w\d\-]+)/$', views.publisher_detail, name='publisher_detail'),
    url(r'^publisher/(?P<slug>[\w\d\-]+)/datasets/$', views.publisher_datasets, name='publisher_datasets'),
    url(r'^publisher/(?P<slug>[\w\d\-]+)/stories/$', views.publisher_stories, name='publisher_stories'),
    url(r'^datasets/$', views.dataset_list, name='dataset_list'),
    url(r'^(?P<object_id>\d+)/$', views.dataset_detail, name='dataset_detail'),
    url(r'^(?P<object_id>\d+)/related-datasets/$', views.related_datasets, name='related_datasets'),
    url(r'^(?P<object_id>\d+)/related-stories/$', views.related_stories, name='related_stories'),
    url(r'^(?P<object_id>\d+)/linked-stories/$', views.linked_stories, name='linked_stories'),
]
