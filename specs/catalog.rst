This document deals with the cataloging, and indexing of datasets.

Note: dataset in the client wireframes is CatalogRecord in the backend.

====
Apps
====

Each target RDF domain/spec will tend to be represented by its own application with a content management / editorial twist.
These apps will support importing & exporting within their own domain constraints.
While RDF aims to be consistent the application will likely encounter invalid associations (ie duplicate labels in a concept scheme)
or unsupported fields that will result in lower resolution (ie additional schema fields not defined in our models)

datasets
========

Can track other machine readable APIs or wrap flat urls into a DCAT compatible system.

Internal models are templated after https://github.com/compilerla/los-angeles-data-sources


* Exports a searchable index for use with django-haystack.
* Index can be filtered geo-spatially or structured using SKOS (see DCAT theme category field)
* Can sync against various backends (Socrata, ArcGIS) to populate meta data fields
* Tracks column definitions
* Support RDF DCAT serialization
* Additional fields for user submissions, allow for crowd-sourcing


Informal Data Model Specification: https://github.com/compilerla/los-angeles-data-sources
Referenced spreadsheet for modeling: https://docs.google.com/spreadsheets/d/1uNtA4GbBwky8PPdNUvmXXZCI1GLtH5cGF-Q0FqD90w0/edit#gid=612549376

ALSO see:
* https://project-open-data.cio.gov/v1.1/schema/
* https://www.w3.org/TR/vocab-dcat/




focus
=====

Represents a limited W3C Simple Knowledge Organization System

https://www.w3.org/TR/skos-primer/


* `ConceptModel` is a SKOS concept with defined labels.
* `FeaturedInterest` is a page calling attention to a concept(s)
* Concepts may be ordered in a tree view (django-mptt).
* other models in the site may be associated to concepts for enhanced searching
* Support RDF SKOS serialization
* Imports SKOS & OWL
* Search engine may span special concept relationships to expand searches
