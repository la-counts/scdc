DCAT modeling:

spreadsheet: DCAT denormalized

* [internal] confirm dataset models are not to be dcat strict but spreadsheet.
* [yes] will the models be expected to export dcat strict representations? ie contactPoint
* [no] will we be supporting future spreadsheet syncing? resolve identifier issue, merge strategy
* [yes] add temporal coverage to search? parse temporal as date range?
* Recommend: Make use of Catalog Record?

Meta data population:

* [internal] will the system have tasks to sync metadata from machine readable api? yes because...
* [yes] will the system be expected to auto-populate download links & fields?
* What other facets should be captured? size? rows? SOCRATA: "Category & Attribution"
* Mention private datasets will not auto-populate, admin workflow. still public metadata
* Manual prioritized
* /dcat.json


Confirm Curated collection be used in focus topics/areas?
- or free topic
- currated collection tags
- still editorial, not tag for focus area
- feed into tags


Specs sheets
Missed fields from Spreadsheet but in data model spec (other fields):
* spatialGranularity
* reportsTo
* collectionProtocol
* isPartOf (data portal?)
* fundedBy


Add to model:
* describedByType


Stories -> django conforms_to
d3 blocks into cms pages
barebone cms
rich text editing
standard blog

see dataharmony (stanford) for search functionality
search across thesaurus (they want topology aware searches)
