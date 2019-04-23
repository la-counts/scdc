'''
Catalog Record Sync Routines

exposes a dictionary whose values are monads, and keys are strings.

A sync routine:

- takes one argument: a catalog record
- updates the dataset associated
- updates distributions (purges old ones)
- update record columns if none exist
- assumes a public API or at least credentials are loaded from environ


Sync routines:

- static_link
- socrata
- arcgis
'''
from urllib.parse import urlparse
from sodapy import Socrata, _format_new_api_request, _raise_for_status
from apps.datasets.models import Dataset, Distribution, RecordColumn
from django.utils.timezone import datetime
from requests.exceptions import HTTPError
import requests
import json
import stringcase


def static_link(catalog_record, url=None):
    dataset = Dataset.objects.get_or_create(catalog_record=catalog_record)[0]
    for col in ['title', 'description', 'identifier', 'language',
                'spatial', 'temporal', 'accrual_periodicity',
                'landing_page', 'theme', 'contact_point']:
        setattr(dataset, col, getattr(catalog_record, col))
    dataset.temporal_coverage = catalog_record.temporal
    dataset.save()
    dist = Distribution.objects.get_or_create(dataset=dataset)[0]
    dist.download_url = catalog_record.identifier or catalog_record.distribution_fields
    dist.access_url = url or catalog_record.landing_page
    dist.license = catalog_record.license
    #TODO dist.byte_size , media_type , format
    dist.save()


class ModdedSocrata(Socrata):
    def get_columns(self, identifier):
        resource = _format_new_api_request(dataid=identifier, content_type="json")
        uri = "{0}{1}{2}?$limit=0".format(self.uri_prefix, self.domain, resource)

        response = getattr(self.session, "head")(uri, timeout=self.timeout)

        # handle errors
        if response.status_code not in (200, 202):
            _raise_for_status(response)

        # when responses have no content body (ie. delete, set_permission),
        # simply return the whole response
        if not response.text:
            return response

        fields = response.headers.get('X-SODA2-Fields') or '[]'
        types = response.headers.get('X-SODA2-Types') or '[]'

        fields = json.loads(fields)
        types = json.loads(types)

        return fields, types


def socrata(catalog_record, url):
    o = urlparse(url)
    client = ModdedSocrata(o.netloc, None)
    uparts = o.path.split('/')
    looks_like_ids = list(filter(lambda x: '-' in x, uparts))
    if looks_like_ids:
        identifier = looks_like_ids[-1]
    else:
        identifier = uparts[-1]
    md = client.get_metadata(identifier)
    from pprint import pprint
    pprint(md.keys())

    assert 'columns' in md, 'columns not found in json response'
    assert 'name' in md, 'name not found in json response'

    if not catalog_record.id:
        catalog_record.save()

    for column in md['columns']:
        rc = RecordColumn.objects.get_or_create(
            catalog_record=catalog_record,
            field_name=column['fieldName'])[0]
        rc.data_type = column['dataTypeName']
        rc.label = column['name']
        #rc.position = column['position']
        rc.catalog_record_order = column['position']
        rc.render_type = column['renderTypeName']
        rc.save()

    dataset = Dataset.objects.get_or_create(catalog_record=catalog_record)[0]
    dataset.last_sync = datetime.now()
    dataset.sourced_meta_data = md
    dataset.title = md['name']
    dataset.description = md.get('description', '')
    dataset.issued = datetime.utcfromtimestamp(md['publicationDate'])
    dataset.modified = datetime.utcfromtimestamp(md['indexUpdatedAt'])
    dataset.identifier = md['id']
    if 'tags' in md:
        dataset.keyword = ', '.join(md['tags'])
    dataset.theme = md.get('category', '')
    dataset.save()

    #only record one distriubtion: JSON
    dist = Distribution.objects.get_or_create(dataset=dataset)[0]
    dist.license = md.get('license', '')
    #dist.rights = md['rights'] #wrong kind of rights
    dist.download_url = url
    dist.access_url = catalog_record.landing_page or catalog_record.distribution_fields
    dist.media_type = 'application/json'
    dist.format = 'json'
    if 'blobFileSize' in md:
        dist.byte_size = md['blobFileSize']
    if 'blobMimeType' in md:
        dist.media_type = md['blobMimeType']
    #blobFilename?
    dist.save()

    #Sometimes the API doesn't report the columns fields with an old api request
    if not md['columns'] and not md.get('blobId'):
        try:
            fields, types = client.get_columns(identifier)
        except HTTPError: #may not be available
            pass
        else:
            for field_name, field_type in zip(fields, types):
                rc = RecordColumn.objects.get_or_create(
                    catalog_record=catalog_record,
                    field_name=field_name)[0]
                rc.data_type = field_type
                if not rc.label:
                    rc.label = field_name
                rc.save()


def arcgis(catalog_record, url):
    if 'FeatureServer' in url:
        service_name = url.split('/services/')[-1].split('/FeatureServer')[0]
    else:
        service_name = url.split('/services/')[-1].split('/MapServer')[0]

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    response = requests.get(url+"?f=pjson", headers=headers)
    md = response.json()

    from pprint import pprint
    pprint(md.keys())

    assert 'currentVersion' in md, 'currentVersion not found in json response'

    if not catalog_record.id:
        catalog_record.save()

    for index, column in enumerate(md.get('fields', [])):
        rc = RecordColumn.objects.get_or_create(
            catalog_record=catalog_record,
            field_name=column['name'])[0]
        rc.data_type = column['type']
        rc.label = column['alias']
        rc.catalog_record_order = index
        #rc.render_type = column['domain'] ? length?
        rc.save()

    dataset = Dataset.objects.get_or_create(catalog_record=catalog_record)[0]
    dataset.last_sync = datetime.now()
    dataset.sourced_meta_data = md
    dataset.title = md.get('name', stringcase.titlecase(service_name))
    dataset.description = md.get('description', '') or md.get('serviceDescription', '')
    #dataset.issued = datetime.utcfromtimestamp(md['publicationDate'])
    #dataset.modified = datetime.utcfromtimestamp(md['indexUpdatedAt'])
    dataset.identifier = md.get('id', service_name)
    #if 'tags' in md:
    #    dataset.keyword = ', '.join(md['tags'])
    dataset.theme = md.get('category', '')
    dataset.save()

    #only record one distriubtion: ARCGIS
    dist = Distribution.objects.get_or_create(dataset=dataset)[0]
    dist.license = md.get('license', '')
    dist.rights = md.get('copyrightText', '')
    dist.download_url = url
    dist.access_url = catalog_record.landing_page or catalog_record.distribution_fields
    dist.media_type = 'application/json'
    dist.format = 'arcgis'
    #blobFilename?
    dist.save()
