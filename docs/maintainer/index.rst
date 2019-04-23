
====
Apps
====

Datasets
========

Track other machine readable APIs or wrap flat urls into a DCAT compatible system.

Provides a performant text search index backed with elasticsearch.
Searches can be filtered geo-spatially, by tags, by date, or by scalar values (ie duration, completion %).

Internal models are adapted from https://github.com/compilerla/los-angeles-data-sources and are harmonized with the DCAT standard.


--------------
Catalog Record
--------------

Referred to as "dataset" in design but W3C DCAT disambiguates `CatalogRecord` from `Dataset`. https://www.w3.org/TR/vocab-dcat/
From the spec itself:

  Notice that while dcat:Dataset represents the dataset itself, dcat:CatalogRecord represents the record that describes a dataset in the catalog. The use of the CatalogRecord is considered optional. It is used to capture provenance information about dataset entries in a catalog.


By introducing `CatalogRecord` the system is able to differentiate between self-reported metadata (provided from Sync) and curated metadata.
`CatalogRecord` is the curated source of truth and is required for inclusion into the catalog.

Records also have a `state` which can control their visibility in the catalog. Only a `CatalogRecord` with a state of PUBLISHED is displayed and indexed!


-----------
Detail View
-----------

1. Title - The given title of the CatalogRecord
2. Tags - A list of SKOS Concepts
3. Selected Metadata - Displays field values associated to the CatalogRecord. If no value is provided, the associated Dataset is consulted.
4. [DISABLED] Columns - Displays the known dataset columns
5. [DISABLED] Definitions - Displays the definitions of concepts associated through tags and columns
6. Access Original Data Source - The first non-empty value from:  `distribution_fields`, `identifier` or `landing_page`
7. Metadata completion rate - A percentage value of the completion, computed by default but may be overridden with `percentage_complete`
8. Related Datasets - PUBLISHED Datasets within the same Tag structure / sharing SKOS Concepts; Or shared spatial entity; Or Shared publisher depending upon quantity.
9. Related Stories - PUBLISHED Stories within the same Tag structure / sharing SKOS Concepts
10. [DISABLED] Linked Stories - Lists stories explicitly linked to this CatalogRecord

.. image:: /_static/dataset_detail.jpg


--------
Commands
--------

:detect_dataset_sync_stategy:
  Automatically detects which sync strategy to use on unassigned catalog records.
:geocode_spatial_entries:
  Creates spatial entities for catalog records that specify a spatial value
:import_googlesheet_datasets:
  Imports datasets from a Regional Data Inventory google spreadsheet.
:sync_catalog_record:
  Syncs a catalog record(s) using the dataset's API. Upon successful synchronization the `CatalogRecord` is PUBLISHED.


detect_dataset_sync_stategy & sync_catalog_record run nightly.


----
Sync
----

`apps.datasets.sync` is a submodule for syncing datasets with various strategies.

Sync strategies should not modify the `CatalogRecord` but will modify or delete associated Metadata/DCAT models:

- Dataset
- RecordColumn
- Distribution


Populating `Dataset` provides the detail page with metadata values if the `CatalogRecord` has none.

The following sync strategies exist:

- apps.datasets.sync.socrata
- apps.datasets.sync.static_link
- apps.datasets.sync.arcgis


Each `CatalogRecord` has a field `sync_strategy` to specify which function to use.

Focus
=====

Provides a topic-based view of the catalog by providing a Simple Knowledge Organization System:
https://www.w3.org/TR/skos-primer/

Related datasets & stories is done by including all descendant concepts to include items that are conceptually related.


`CatalogRecord` s can be organized into Focus Areas & Concepts.

* stories & records are manually assigned to concepts
* focus areas are a curated display of stories & records with a primary linked concept

-------
Concept
-------

A Directed Acyclic Graph (DAG) representing linked concepts.
The DAG structure allows for efficient querying of concept descendants.


--------
Commands
--------

:create_concepts_from_collections: Create a concept entry for each curated collection and add the datasets.
:import_skos_vocabulary: Imports a W3C SKOS (Simple Knowledge Organization System) rdf vocabulary file.
:populate_tags_from_concepts: All concepts will generate a tag and associate itself to any tags matching its various names. Datasets with tags associated to concepts will have their concept associations updated.


Commenting
==========

Using django-comments-xtd


Stories
=======

Custom blog that allows users to post stories (from the front end, permission based).

Allows for links to publisher, datasets, stories, tags.

Multiple images may be attached and body is a rich text editor (CKeditor).

Stories also have a `state` which can control their visibility in the catalog. Only a `Story` with a state of PUBLISHED is displayed and indexed!



Profiles
========

Defines a custom user model. Stores the following fields:

- Display name
- title
- organization (text)
- publisher (foreign key to a registered publisher)
- url/website
- marked interests
- avatar

Allows users to save or track recent views of:

- searches
- datasets
- stories

django-activity-stream for tracking views and saves
