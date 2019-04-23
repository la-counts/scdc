========
Services
========

Web
===

Django 1.10 with additional community libraries:

* django-haystack
* django-taggit
* django-imagekit
* django-registration
* django-rq
* django-mptt
* django-ckeditor
* django-comments-xtd
* django-activity-stream
* django_select2


Database
========

Recommended: Postgresql

Any RDBMS supported by Django may also work but may reduce querying capacity across meta data.


Search
======

Elasticsearch provides advanced searching functionality and reduces database load for search operations.

Features that will be used in this project:

* Faceting
* Geospatial searching
* Fulltext search & language stemming
* Pre-rendered item result

Other django-haystack backends may be used but may result in reduced performance.


Cache
=====

Redis is used as a cache layer and for sending messages to other worker processes in the cluster.
