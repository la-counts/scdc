SCDC


=======
Running
=======

Configured & tested for postgresql, easticsearch & redis.


Docker
======

Initialize your override file::

  cp docker-compose.dev.yml docker-compose.override.yml
  touch .env


Create our containers::

  docker-compose up


Create database & account::

  docker-compose run cli migrate
  docker-compose run cli createsuperuser


`docker-compose run cli` pipes to a `python manage.py` in a container


Python
======

Install requirements::

  pip3 install -r requirements.txt


Set environment variables:

* DATABASE_URL
* SEARCH_URL
* CACHE_URL


Create database & account::

  python manage.py migrate
  python manage.py createsuperuser



AWS EC2
=======


Create ec2 instance and deploy::

  docker-machine create --driver amazonec2 --amazonec2-region us-west-2 --amazonec2-instance-type "t2.medium" scdc01
  eval $(docker-machine env scdc01)
  docker-compose -f docker-compose.yml -f docker-compose.prod.yml up


Production configuration includes a varnish service.


=========
Importing
=========

Recommended way to export catalog (without stories or CMS)::

  docker-compose run cli dumpdata --indent 2 --format xml datasets.SpatialEntity datasets.Publisher datasets.DataPortal datasets.CatalogRecord datasets.RecordColumn datasets.Dataset datasets.Distribution focus.Concept focus.Label focus.MappedUri > datasets.xml


import_googlesheet_datasets
===========================

You will need a json auth file from Google API to run this command.
Consult `google-api-python-client` docs to obtain a copy.

Example import of datasets from a google spreadsheet::

  python manage.py import_googlesheet_datasets ./scdc-5b861566cbdc.json 1uNtA4GbBwky8PPdNUvmXXZCI1GLtH5cGF-Q0FqD90w0


`import_googlesheet_datasets` takes two arguments:

* path to JSON auth file from Google
* spreadsheet id


The command will sync the following tabs to the database:

* Datasets
* Publishers
* Data Portals


For best results the spreadsheet should be modeled after:
https://docs.google.com/spreadsheets/d/1uNtA4GbBwky8PPdNUvmXXZCI1GLtH5cGF-Q0FqD90w0


geocode_spatial_entries
=======================

This will iterate through all datasets that specify a `spatial` value but are not currently mapped to geojson.
For each new value of `spatial`, a geocode lookup is done against open street maps and all datasets with that value are mapped to the new geocoded spatial entity.


import_skos_vocabulary
======================

Imports a W3C SKOS (Simple Knowledge Organization System) vocabulary file.
Each entry is mapped to a `Concept` instance and if a prior field is blank the value will be updated.

The command requires a path to a file to import::

  python manage.py import_skos_vocabulary https://www.seegrid.csiro.au/subversion/CGI_CDTGVocabulary/tags/SKOSVocabularies/EnvironmentalImpactValue201401.rdf


Test vocabularies:

- http://eulersharp.sourceforge.net/2003/03swap/countries
- http://id.loc.gov/vocabulary/subjectSchemes.rdf
- http://www.gesis.org/en/services/research/tools/social-science-thesaurus/
- https://www.w3.org/2006/07/SWD/SKOS/reference/20090315/implementation.html
- http://s3.amazonaws.com/jestaticd2l/purl/scheme/GEM-S
- http://metadataregistry.org/vocabulary/list.html?filters%5Bagent_id%5D=&filters%5Bstatus_id%5D=1&filter=filter
- http://www.omg.org/spec/EDMC-FIBO/FND/1.0/index.htm
- http://lov.okfn.org/dataset/lov/vocabs
- http://sw-portal.deri.org/ontologies/swportal


detect_dataset_sync_strategy
============================

Goes through Catalog Records that don't have an associated sync strategy and tests a variety of methods.
If a sync strategy matches and works then the catalog record will be updated to use that strategy in the future.


sync_catalog_record
===================

This will sync `Catalog Record` with their selected `sync_strategy`.

You may provide a list of ids to sync, or just do a default sync::

  python manage.py sync_catalog_record 1268 1269


create_concepts_from_collections
================================

Generates Concepts from `curated_collection` and adds the concept to the Catalog Record.

Run this after populating catalog records::

  python manage.py create_concepts_from_collections


populate_tags_from_concepts
===========================

All concepts will generate a tag and associate itself to any tags matching its various names.
Datasets with tags associated to concepts will have their concept associations updated.


======
Layout
======

- **apps** folder contains custom django applications for this project
- **data_commons** is the django entry point and app loader
- **specs** contains notes and aims to document requirements and implementation negotiation
- **static** holds css, js and other assets to be served on the website for styling purposes
- **templates** defines the HTML to be rendered in the Django templating language
- **vue-components** ui/js components
