Define how content is indexed and filtered.

===============
Filter Controls
===============


Concept Tree
============

Taxonomic trees can be defined in the admin and a CatalogRecord may be associated to multiple concepts.
`RecordColumn` may also be associated to a single taxonomic concept.

The `Concept Tree` filter can be display in either:

- drop-down selector (select2)
- collapsible tree selector (fancytree)

Given a selected concept, the search engine will also include all datasets mapped to any of its subconcepts.

Stories may also be mapped to a concept and may optionally be included in results.


Widget
------

jQuery Francy Tree has some django integrations:

- https://github.com/xrmx/django-fancytree
- https://pypi.python.org/pypi/django-mptt-autocomplete/0.1.3
- http://wwwendt.de/tech/fancytree/demo/#sample-configurator.html



Full Text
=========

Browser displays a one line text input field.

The following fields are included in a full text search:

- title
- description
- keyword
- concepts (including aliased names)
- spatial location name
- theme
- field descriptions

Stories will also be included in full text search.


Categorical
===========

Browser may display either:

- a drop-down of all known values
- a table of known values with multi-select checkboxes

The following columns will be indexed separately:

- publisher
- language
- spatial entity
- accrual periodicity


Keywords
========

CONSIDER: keywords are redundant to concepts, this is describing a one line interface

Browser displays a one line input field that autocompletes into known keywords.

Fallback: User enters in keywords separated by commas.

Keywords (non-taxonomic slug assignments) are sourced from the catalog record's meta data.
Dataset source keywords are also included.


Scalar
======

Browser displays a one line number input field and a comparative operator for the following scalar columns:

- duration (in years)
- download count (if reported)
- percentage complete

Available comparative operators:

- greater and equal
- lesser and equal


Date Searches
=============

Browser displays a one line date input field and a comparative operator for the following columns:

- issued
- modified

Available comparative operators:

- after date
- before date
