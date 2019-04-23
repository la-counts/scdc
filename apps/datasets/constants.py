ACCESS_LEVEL_CHOICES = [
    ('public', 'public'),
    ('restricted public', 'restricted public'),
    ('non-public', 'non-public')
]

SYNC_STRATEGY_CHOICES = [
    ('apps.datasets.sync.static_link', 'Static Link'),
    ('apps.datasets.sync.socrata', 'Socrata'),
    ('apps.datasets.sync.arcgis', 'ArcGIS'),
]

RECORD_STATE_CHOICES = [
    ('new', 'New', 'CatalogRecord'),
    ('published', 'Published', 'CatalogRecord'),
    ('rejected', 'Rejected', 'CatalogRecord'),
    ('broken', 'Broken', 'CatalogRecord'),
    ('in_progress', 'In Progress', 'CatalogRecord'),
    ('archived', 'Archived', 'CatalogRecord'),
]

DATASOURCE_STATE_CHOICES = [
    ('new', 'New', 'DatasourceSuggestion'),
    ('processed', 'Processed', 'DatasourceSuggestion'),
]

METADATA_FIELDS = [
    'theme',
    'title',
    'description',
    'modified',
    'publisher',
    'contactPoint',
    'identifier',
    'accessLevel',
    'license',
    'rights',
    'spatial',
    'spatialGranularity',
    'temporal',
    'distribution',
    'distributionFields',
    'accrualPeriodicity',
    'reportsTo',
    'collectionProtocol',
    'conformsTo',
    'describedBy',
    'describedByType',
    'isPartOf',
    'issued',
    'language',
    'landingPage',
    'fundedBy',
]

MINIMUM_METADATA_FIELDS = [
    'title',
    'description',
    'modified',
    'publisher',
    'contactPoint',
    'identifier',
    'accessLevel',
    'license',
    'spatial',
    'temporal',
    'distribution',
    'distributionFields',
    'accrualPeriodicity',
    'language',
    'landingPage',
]

#fields computed towards completion
PROGRESS_METADATA_FIELDS = MINIMUM_METADATA_FIELDS[1:]

DISPLAY_METADATA_FIELDS = METADATA_FIELDS[2:]
#display pulisher first
DISPLAY_METADATA_FIELDS.remove('publisher')
DISPLAY_METADATA_FIELDS.insert(0, 'publisher')
