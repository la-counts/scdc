

====
Apps
====

Datasets
========

Also see: `catalog.rst`

Can track other machine readable APIs or wrap flat urls into a DCAT compatible system.

Internal models are templated after https://github.com/compilerla/los-angeles-data-sources

Exports a searchable index for use with django-haystack.
Index can be filtered geo-spatially or tagged with other semantics.

App label: Data Inventory


Sync
----

`apps.datasets.sync` is a submodule for syncing datasets with various strategies.

Sync strategies should not modify the catalog record but will modify or delete associated Metadata/DCAT models:

- Dataset
- RecordColumn
- Distribution


The following sync strategies exist:

- apps.datasets.sync.socrata
- apps.datasets.sync.static_link
- apps.datasets.sync.arcgis


Each `CatalogRecord` has a field `sync_strategy` to specify which function to use.


Moderation
==========

Also see: `moderation.rst`

Funnels for collecting user & automated feedback.

Examples:

* User suggests tag for catalog record or other modification
* System flags catalog record as broken url
* story submission
* suggest dataset
* suggest concept
* contact form


Focus
=====

Also see: `catalog.rst`

Organize datasets into Focus Areas & Topics.

* datasets are manually assigned
* curated display
* areas & topics are manually created

Represents a limited W3C Simple Knowledge Organization System:
https://www.w3.org/TR/skos-primer/

Includes management command to import vocabularies from other rdf systems.

Reviews
=======

Will be using "disqus".
See: http://django-disqus.readthedocs.io/en/latest/
other options to be found at: https://djangopackages.org/grids/g/forums/

However, it seems there are additional features to be delivered through API calls.

- Recent comments
- Followed conversations

These API calls will need to be cached and properly sandboxed to not hang up rendering.

Due to the number of parts and relative use of this feature, the advance API integration will be saved for last.
Comments themselves will be integrated early on.


Stories
=======

Custom blog that allows users to post stories (from the front end, permission based).

Allows for links to publisher, datasets, stories, tags.

Multiple images may be attached and body is a rich text editor (CKeditor).

A secondary moderation system is used to move stories to published.


Profiles
========

Defines a custom user model. Stores the following fields:

- Display name
- title?
- organization (text field and optional fk entity to publisher model)
- url/website
- marked interests
- picture (moderate this?)

Allows users to save or track recent views of:

- searches
- datasets
- stories

Provides template tags for displaying recent activity.

Additionally, per topic ranking may be associated to each profile.
Stackoverflow reputation system?

django-activity-stream for tracking views and saves
