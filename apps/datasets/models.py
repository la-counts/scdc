'''
Data Model Specification: https://github.com/compilerla/los-angeles-data-sources
Referenced spreadsheet for modeling: https://docs.google.com/spreadsheets/d/1uNtA4GbBwky8PPdNUvmXXZCI1GLtH5cGF-Q0FqD90w0/edit#gid=612549376

ALSO see:
* https://project-open-data.cio.gov/v1.1/schema/
* https://www.w3.org/TR/vocab-dcat/


Notes:

The spreadsheet and DCAT standard are not one to one but can be adapted and detected.
Major discrepency is over the flatening of distributions into a url and descriptor.
The system may be configured to use the dataset's portal's vendor field to load a driver.
A driver would be responsible for populating distribution instances. Default is a direct link driver.
'''
import uuid
import logging

from functools import lru_cache
from importlib import import_module
from django.db import models
from django.db.models import Q, F
from django.contrib.gis.db import models as geomodels
from django.conf import settings
from django.contrib.postgres.fields import HStoreField, JSONField
from django.core.urlresolvers import reverse
from django.utils.text import slugify

from data_commons.contrib.rdf import DCT, DCAT, DjRef
from data_commons.contrib.meta_display import MetaTag
from rdflib.namespace import SKOS, RDFS, RDF, FOAF
from rdflib import URIRef, Literal
from collections import OrderedDict
import stringcase
from dateutil.parser import parse as parse_datetime
from dateutil.relativedelta import relativedelta
from datetime import date
import itertools
from urllib.parse import urlparse

from cms.models import CMSPlugin
from treebeard.mp_tree import MP_Node
from django_fsm import FSMField, transition
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField

from .managers import CatalogRecordManager, PublisherManager
from .constants import (PROGRESS_METADATA_FIELDS, DISPLAY_METADATA_FIELDS,
                        ACCESS_LEVEL_CHOICES, SYNC_STRATEGY_CHOICES, RECORD_STATE_CHOICES, DATASOURCE_STATE_CHOICES)


logger = logging.getLogger(__name__)


class SpatialEntity(geomodels.Model):
    name = geomodels.CharField(max_length=255)
    geometry = geomodels.GeometryField()
    granularity = geomodels.TextField(blank=True)
    data = HStoreField(blank=True, default=dict) #raw geocode response: {type: city, class: place}

    class Meta:
        verbose_name_plural = 'spatial entities'

    def __str__(self):
        return self.name


class Publisher(MP_Node):
    '''
    Fields scraped from spreadsheet `Publishers`

    aka Content Contributor
    shows up as `dct:publisher`
    must be able to export: http://xmlns.com/foaf/spec/#term_Person
    '''
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, help_text='appears in the url')
    agency_type = models.CharField(max_length=50, blank=True)
    agency_url = models.URLField(blank=True)

    primary_data_portal = models.URLField(blank=True)

    body = RichTextUploadingField(blank=True)
    description = models.TextField(blank=True)

    #TODO users may be associated to publisher, are they automatically editors?
    objects = PublisherManager()

    node_order_by = ['name']

    class Meta:
        ordering = ['path']

    def __str__(self):
        return self.name

    #TODO fully deprecate
    def set_sub_organization_of(self, name):
        '''
        Sets the organizational parent by name
        '''
        return

    def get_sub_organization_of(self):
        if self.get_parent():
            return self.get_parent().name
        else:
            if self.name.find(';') > 0:
                #split it and use the first instance as the group, last part as the name
                publisherNameSet = publisherName.split(';', 1)
                publisherNameParent = publisherNameSet[0]
                parentName = publisherNameParent[1].strip()
                return parentName
            
        return ''

    sub_organization_of = property(get_sub_organization_of, set_sub_organization_of)

    def get_absolute_url(self):
        return reverse('datasets:publisher_detail', args=(self.slug,))

    def save(self, **kwargs):
        if self.depth is None:
            if hasattr(self, 'parent'):
                self.parent.add_child(instance=self)
            else:
                Publisher.add_root(instance=self)
        else:
            super(Publisher, self).save(**kwargs)

    def all_catalog_records(self):
        return CatalogRecord.objects.filter(publisher__in=self.get_tree(self))

    def get_display_name(self):
        publisherName = self.name
        
        if publisherName.find(';') > 0:
            #split it and use the first instance as the group, last part as the name
            publisherNameSet = publisherName.split(';', 1)
            publisherNameParent = publisherNameSet[0]
            publisherName = publisherNameSet[1].strip()
            
            #return publisherName
        
        #Some cheezy exceptions...
        if publisherName.find('City of Industry') >= 0:
            return publisherName
        
        if publisherName.find('City of') >= 0:
            publisherName = publisherName.replace('City of', '')
            publisherName += ', City of'
        elif publisherName.find('State of') >= 0:
            publisherName = publisherName.replace('State of', '')
            publisherName += ', State of'
        
        publisherName = publisherName.strip();
        
        return publisherName
    
    def child_get_display_name(self):
        publisherName = self.name
        if self.get_parent():
            parentName = self.get_parent().name
        
            if publisherName.find(parentName+";") >= 0:
                publisherName = self.name.replace(parentName+";", '')
                
            if publisherName.find(parentName+";") > 0:
                parentNameSet = parentName.split(';', 1)
                publisherNameParent = parentNameSet[0]
                publisherName = parentNameSet[1].strip()
        
        #if publisherName.find(';') == 0:
        #    return publisherName
        
        if publisherName.find('City of') >= 0:
            publisherName = self.name.replace('City of', '')
            publisherName += ', City of'
        elif publisherName.find('State of') >= 0:
            publisherName = self.name.replace('State of', '')
            publisherName += ', State of'
        
        publisherName = publisherName.strip();
        
        return publisherName

    def get_alpha_group(self):
        publisherName = self.get_display_name().strip()
        return publisherName[:1].lower()

    def agency_filter(self):
        agencyType = self.agency_type
        if agencyType == "":
            publisherName = self.name
            if publisherName.find('Federal') >= 0:
                agencyType = "Federal"
            else:
                agencyType = "uncategorized"
                
        return slugify(agencyType)


#TODO this gets allot of overlap fields with dataset (language, etc)
class DataPortal(models.Model):
    '''
    Fields scraped from spreadsheet `Data Portals`

    dcat:Catalog

    Typically, a web-based data catalog is represented as a single instance of this class.
    '''
    status = models.CharField(max_length=50, blank=True)
    publisher = models.ForeignKey(Publisher)
    url = models.URLField(unique=True)

    title = models.CharField(max_length=255, blank=True)
    vendor = models.CharField(max_length=50, blank=True)
    datasets_estimate = models.IntegerField(blank=True, null=True)

    license = models.TextField(blank=True)
    spatial_entity = models.ForeignKey(SpatialEntity, blank=True, null=True, on_delete=models.SET_NULL)

    #TODO language, issued, modified

    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.title or self.publisher.name

    def to_rdf(self):
        return {
            'rdf:type': 'dcat:Catalog',
            'dct:title': self.name,
            'dct:description': self.publisher.description,
            'rdfs:label': self.title,
            'dct:publisher': self.publisher,
            #'dct:language': None,
            'dct:license': self.license,
            'dct:spatial': self.spatial_entity and self.spatial_entity.name or None,
            #dcat-dataset??
        }


class CatalogRecord(models.Model):
    '''
    Populated from SCDC data requirements doc.
    Additional context from fields scraped from speadsheet `Datasets`

    https://asset1.basecamp.com/2345560/projects/13740930/attachments/275923420/44a8dc7c4f5133ba3e56252eb2e4400f0010/original/SCDC%20Presentation%20+%20data%20requirements%202-27-2017.pdf

    This is the data maintained by humans.
    It represents a linkage to an external dataset.

    dcat:CatalogRecord
    '''
    title = models.CharField(max_length=255,
        help_text='A name given to the dataset.')
    state = FSMField(default='new', protected=False, db_index=True, state_choices=RECORD_STATE_CHOICES)

    #CONSIDER: this should map to concepts
    curated_collection = models.CharField('primary topic', max_length=50, blank=True,
        help_text='Collections were developed for CCF, following requested thematic topics and existing focus areas. Note: At a future data this field will meet requirements for optional “theme” adopted by USPRO and DCAT.')
    description = models.TextField(blank=True,
        help_text='free-text account of the dataset.')
    keyword = models.TextField('keyword/tag', blank=True,
        help_text='A keyword or tag describing the dataset.')
    tags = TaggableManager('User tags', blank=True) #to be mapped to concepts by curator

    concepts = models.ManyToManyField('focus.Concept', blank=True,
        help_text='The main category of the dataset. A dataset can have multiple themes.')

    modified = models.DateTimeField('update/modification date', null=True, blank=True,
        help_text='Most recent date on which the dataset was changed, updated or modified.')

    publisher = models.ForeignKey(Publisher, null=True, blank=True, on_delete=models.SET_NULL,
        help_text='''An entity responsible for making the dataset available (may not be responsible for collecting the data).''')

    #dcat range: vcard:Kind
    contact_point = models.TextField(blank=True,
        help_text='All relevant contact information (including name and email) for the person(s) to whom questions about the dataset should be sent.')

    identifier = models.CharField(max_length=255, blank=True,
        help_text='A unique identifier of the dataset.')

    access_level = models.CharField(max_length=20, blank=True, choices=ACCESS_LEVEL_CHOICES,
        help_text='''
        The degree to which this dataset could be made publicly-available, regardless of whether it has been made available. Choices:
        public (Data asset is or could be made publicly available to all without restrictions),
        restricted public (Data asset is available under certain use restrictions), or
        non-public (Data asset is not available to members of the public).
        ''')

    license = models.TextField(blank=True,
        help_text='This links to the license document under which the distribution is made available.')

    rights = models.CharField(max_length=255, blank=True,
        help_text='Information about rights held in and over the distribution.')

    spatial = models.TextField('spatial/geographical coverage', blank=True,
        help_text='Spatial coverage of the dataset.')
    spatial_granularity = models.TextField(blank=True,
        help_text='Sub field of spatial coverage, required where applicable.')
    spatial_entity = models.ForeignKey(SpatialEntity, blank=True, null=True, on_delete=models.SET_NULL)
    spatial_geometry = geomodels.GeometryField(blank=True, null=True,
        help_text='Spatial geometry describing the coverage of the dataset.')

    temporal = models.TextField('temporal coverage', blank=True,
        help_text='The temporal period that the dataset covers.')

    sync_strategy = models.CharField(max_length=50, blank=True,
        choices=SYNC_STRATEGY_CHOICES,
        help_text='Plugin for automatically syncing metadata')
    sync_url = models.CharField(max_length=255, blank=True,
        help_text='Detected sync strategy url')

    #RDF: A container for the array of Distribution objects.
    #for us this is an indicator of how to treat the url (next field)
    distribution = models.CharField(max_length=255, blank=True,
        help_text='Available distributions, or specific data formats (ex: csv, Socrata API); type(s) of format(s)')

    #often becomes accessURL, or downloadURL
    distribution_fields = models.CharField(max_length=255, blank=True,
        help_text='URL of most commonly accessed distribution')

    accrual_periodicity = models.TextField(blank=True,
        help_text='The frequency at which dataset is published.')

    reports_to = models.TextField(blank=True,
        help_text='All legislation that requires or informs the collection and reporting of these data points.')

    collection_protocol = models.TextField(blank=True,
        help_text='''Description of the frequency and mode of data collection
        (different from periodicity of dataset publication).
        Links to original data collection plan or proposals may also be added here.''')

    conforms_to = models.TextField(blank=True,
        help_text='Data standard dataset meets.')
    described_by = models.CharField(max_length=255, blank=True,
        help_text='Machine readable documentation (typically used for APIs)')
    described_by_type = models.CharField(max_length=255, blank=True,
        help_text='Machine readable documentation type (typically used for APIs)')
    #TODO is this to become a foreignkey? to publisher or itself?
    is_part_of = models.TextField(blank=True,
        help_text='The collection of which the dataset is a subset')
    issued = models.DateTimeField('listing date', null=True, blank=True,
        help_text='Date of formal issuance (e.g., publication) of the dataset.')
    language = models.CharField(max_length=20, blank=True)
    landing_page = models.URLField(blank=True,
        help_text='A Web page that can be navigated to in a Web browser to gain access to the dataset, its distributions and/or additional information.')
    funded_by = models.TextField(blank=True,
        help_text='''All groups and/or individuals that financially support the collection of this dataset.
These entities may be the same or different from the dataset’s publisher''')
    notes = models.TextField(blank=True,
        help_text='For use by SCDC project only')

    #for updating content
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='submitted_catalog_records')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='approved_catalog_records')

    _percentage_complete = models.FloatField('% complete', default=0.0, db_column='percentage_complete')

    objects = CatalogRecordManager()


    def __str__(self):
        return self.title

    def add_rdf_catalog_record(self, g):
        uri = URIRef(self.get_absolute_url())
        for p, o in [
            (RDF.type, DCAT.CatalogRecord),
            (DCT.title, self.title),
            (DCT.description, self.lookup('description')),
            (DCAT.theme, self.curated_collection),
            (DCT.issued, self.lookup('issued')),
            (DCT.modified, self.lookup('modified')),
            (DCT.identifier, self.identifier),
            (DCAT.keyword, self.keyword),
            (DCT.language, self.lookup('language')),
            (DCAT.contactPoint, self.lookup('contact_point')),
            (DCT.temporal, self.lookup('temporal')),
            (DCT.spatial, self.lookup('spatial')),
            (DCT.accrualPeriodicity, self.lookup('accrual_periodicity')),
            (DCAT.landingPage, self.lookup('landing_page')),

            #extended, not part of DCAT at this level
            (DCT.license, self.lookup('license')),
            (DCT.rights, self.lookup('rights')),
            (FOAF.fundedBy, self.lookup('funded_by')),
            #TODO these dont map to any RDF standard, maybe add our own
            #isPartOf described_by described_by_type reportsTo collectionProtocol, accessLevel
        ]:
            if o:
                g.add( (uri, p, DjRef(o)) )

        if self.publisher:
            g.add( (uri, DCT.publisher, DjRef(self.publisher)))

        if hasattr(self, 'dataset'):
            for dist in self.dataset.distributions.all():
                dist.add_rdf_distribution(g)
                g.add( (uri, DCAT.distribution, DjRef(dist)) )


    @property
    def theme(self):
        return self.curated_collection

    @property
    def dataportal(self):
        domain = self.identifier or self.distribution_fields
        domain = domain.split('/')[2]
        return self.publisher.dataportal_set.filter(url__contains=domain).first()

    @property
    def geometry(self):
        if self.spatial_entity:
            return self.spatial_entity.geometry
        return None

    def run_sync_strategy(self, sync_strategy=None, url=None):
        '''
        Load & run the associated sync strategy

        Simply returns if none is defined.
        '''
        if sync_strategy is None:
            sync_strategy = self.sync_strategy
        if not sync_strategy:
            return
        url = url or self.sync_url
        strategy_path, strategy_attr = sync_strategy.rsplit('.', 1)
        strategy = getattr(import_module(strategy_path), strategy_attr)

        if not url:
            print('Warning: No sync url specified, detecting...')
            urls = filter(lambda x: x and '://' in x, [
                self.identifier,
                self.distribution_fields,
                self.landing_page
            ])
            for can_url in urls:
                try:
                    strategy(self, can_url)
                except Exception as error:
                    print(error)
                else:
                    print('Success:', can_url)
                    self.sync_url = can_url
                    self.save()
                    return
            raise RuntimeError('No sync url specified')
        else:
            return strategy(self, url)

    def lookup(self, local_name, dset_name=None):
        '''
        Lookup a single value accross the catalog record and it's dataset.
        The dataset provides any defaults the catalog record does not.
        '''
        local_name = stringcase.snakecase(local_name) # describedBy => described_by
        if dset_name is None:
            dset_name = local_name
        value = getattr(self, local_name, None)
        try:
            dset = self.dataset
        except Dataset.DoesNotExist:
            dset = None
        if dset and value in (None, ''):
            value = getattr(dset, dset_name, value)
        return value

    def get_absolute_url(self):
        return reverse('datasets:dataset_detail', args=(self.pk,))

    def get_external_access_url(self):
        #TODO the first two are not guaranteed to be urls
        return self.distribution_fields or self.identifier or self.landing_page

    @lru_cache()
    def all_concepts(self):
        from apps.focus.models import Concept
        return Concept.objects.filter(
            Q(recordcolumn__catalog_record=self) |
            Q(catalogrecord=self)
        ).distinct()

    @lru_cache()
    def related_concepts(self):
        '''
        The intent is to query all related concepts,
        But "related" seems to work inverse of search?
        Right now we query descendant concepts instead of ancestors.
        Meaning a dataset tagged with "Health an Human Services" will relate to a story about water.
        In all likliehood we may want to query both descendant and ancestors for related but prefer a particular direction.
        '''
        return self.all_concepts().get_descendants(include_self=True)#.search_matched()

    @lru_cache()
    def match_concepts(self):
        '''
        Concepts that should match during search.
        Does not select child concepts.

        Expands concepts in the following order:

        * alternative ancestors (ancestors, ancestors alt parents)
        * search matched

        Search expansion is ordering is limited by performace.
        '''
        return self.concepts.all().alternative_ancestors()#.search_matched()

    def related_stories(self):
        #TODO search accross spatial entity
        from apps.stories.models import Story
        concepts = self.related_concepts()
        return Story.objects.filter(concepts__in=concepts).published().select_related()

    def related_records(self):
        #include spatial entities or publisher if no match by concept
        concepts = self.related_concepts()
        if concepts:
            qs = CatalogRecord.objects.filter(concepts__in=concepts)
        elif self.spatial_entity:
            qs = CatalogRecord.objects.filter(spatial_entity=self.spatial_entity)
        elif self.publisher:
            qs = CatalogRecord.objects.filter(publisher=self.publisher)
        else:
            qs = CatalogRecord.objects.none()
        return qs.display().exclude(pk=self.pk).select_related()

    def meta_tags(self):
        required = set(PROGRESS_METADATA_FIELDS)
        tags = list()

        for key in DISPLAY_METADATA_FIELDS:
            mt = MetaTag(key, self.lookup(key))
            if key in required:
                mt.label = mt.label() + "*"
            tags.append(mt)

        return tags

    @lru_cache()
    def all_definitions(self):
        return self.all_concepts().exclude(definition='')

    @property
    @lru_cache()
    def percentage_complete(self):
        if self._percentage_complete:
            return self._percentage_complete

        count = 0
        for key in PROGRESS_METADATA_FIELDS:
            if self.lookup(key):
                count += 1

        return count*100/len(PROGRESS_METADATA_FIELDS)

    @transition(field=state, source=['in_progress', 'broken', 'archived'], target='published')
    def publish(self):
        pass

    @transition(field=state, source=['new'], target='rejected')
    def reject(self):
        pass

    @transition(field=state, source=['published', 'broken'], target='archived')
    def archive(self):
        pass

    @transition(field=state, source=['new', 'rejected'], target='in_progress')
    def start_work(self):
        pass

    @transition(field=state, source=['published'], target='broken')
    def flag(self):
        pass

    def scrape_url_aliases(self):
        return set(filter(lambda x: x and '://' in x, [
            self.identifier,
            self.distribution_fields,
            self.landing_page
        ]))

    def web_domains(self):
        return set(urlparse(url).hostname for url in self.scrape_url_aliases())

    def populate_url_mappings(self):
        urls = self.scrape_url_aliases()
        dus = list()
        for url in urls:
            du = DatasetURL.objects.get_or_create(url=url, defaults={'catalog_record': self})[0]
            if not du.catalog_record_id: #url has been seen before but not mapped
                du.catalog_record = self
                du.save()
            dus.append(du)
        return dus

    def check_if_duplicate(self):
        dupes = filter(lambda x: x.catalog_record_id != self.id, self.populate_url_mappings())
        return list(dupes)

    @lru_cache()
    def temporal_range(self):
        try:
            return self.parse_human_temporal_range(self.temporal)
        except Exception as error:
            logger.exception(error)
            return None

    @staticmethod
    def parse_human_temporal_range(temporal):
        def safe_parse_datetime(val):
            try:
                return parse_datetime(val).date()
            except ValueError:
                return None

        def parse_datetime_duration(val):
            if val.startswith('CY'):
                val = val.split('CY', 1)[-1].strip()
                start = safe_parse_datetime(val)
                if not start:
                    return None, None
                start += relativedelta(month=1, day=1)
                duration = relativedelta(years=1)
                return start, start + duration
            else:
                #detect precision and offset by one
                prec_count = val.count('/')
                prec, duration = {
                    0: (relativedelta(month=1, day=1), relativedelta(years=1)),
                    1: (relativedelta(day=1), relativedelta(months=1)),
                    2: (relativedelta(), relativedelta(days=1))
                }.get(prec_count, (relativedelta(), relativedelta()))
                start = safe_parse_datetime(val)
                if not start:
                    return None, None
                start += prec
                return start, start + duration

        def parse_frag(tfrag):
            '''
            Time fragments should indicate a period of time, returning a tuple of start and stop
            '''
            tfrag = tfrag.strip()
            start, end = None, None
            if tfrag.count('-') == 1:
                l = list(map(parse_datetime_duration, tfrag.split('-')))
                start, end = l[0][0], l[1][0]
            else:
                start, end = parse_datetime_duration(tfrag)
            return (start, end)

        if temporal:
            t_tuples = list(filter(bool, map(parse_frag, temporal.split(','))))
            t_dates = set(filter(bool, itertools.chain.from_iterable(
                t_tuples
            )))
            if not t_dates:
                return (None, None)
            start = min(t_dates)
            end = max(t_dates)

            if start == end:
                return (start, None)
            return (start, end)
        return (None, None)

    @property
    def temporal_start(self):
        return self.temporal_range()[0]

    @property
    def temporal_end(self):
        return self.temporal_range()[1]


class RecordColumn(models.Model):
    '''
    Describes a column belonging to a dataset
    '''
    catalog_record = models.ForeignKey(CatalogRecord)
    field_name = models.CharField(max_length=255)
    label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    data_type = models.CharField(max_length=255)
    render_type = models.CharField(max_length=255, blank=True)

    concept = models.ForeignKey('focus.Concept', null=True, blank=True)

    class Meta:
        order_with_respect_to = 'catalog_record'
        unique_together = [('catalog_record', 'field_name')]


class Dataset(models.Model):
    '''
    This class represents the actual dataset as published by the dataset publisher.
    In cases where a distinction between the actual dataset and its entry in the catalog is necessary
    (because metadata such as modification date and maintainer might differ),
    the catalog record class can be used for the latter.

    dcat:Dataset + api meta data

    https://www.w3.org/TR/2013/WD-vocab-dcat-20130312/

    This is where we sync metadata with external APIs
    '''
    catalog_record = models.OneToOneField(
        CatalogRecord,
        on_delete=models.SET_NULL,
        null=True, blank=True #If null then this was scraped but has to be approved
    )
    title = models.CharField(max_length=255,
        help_text='A name given to the dataset.')
    description = models.TextField(blank=True,
        help_text='free-text account of the dataset.')

    issued = models.DateTimeField('release date', null=True, blank=True,
        help_text='Date of formal issuance (e.g., publication) of the dataset.')

    modified = models.DateTimeField('update/modification date', null=True, blank=True,
        help_text='Most recent date on which the dataset was changed, updated or modified.')
    identifier = models.CharField(max_length=255, blank=True,
        help_text='A unique identifier of the dataset.')
    keyword = models.TextField('keyword/tag', blank=True,
        help_text='A keyword or tag describing the dataset.')
    language = models.CharField(max_length=20, blank=True,
        help_text='The language of the dataset.')
    temporal = models.TextField('temporal coverage', blank=True,
        help_text='The temporal period that the dataset covers.')
    spatial = models.TextField('spatial/geographical coverage', blank=True,
        help_text='Spatial coverage of the dataset.')
    accrual_periodicity = models.TextField('frequency', blank=True,
        help_text='The frequency at which dataset is published.')
    landing_page = models.URLField(blank=True,
        help_text='A Web page that can be navigated to in a Web browser to gain access to the dataset, its distributions and/or additional information.')

    theme = models.TextField('theme/category', blank=True,
        help_text='The main category of the dataset. A dataset can have multiple themes.')
    publisher = models.TextField(blank=True,
        help_text='An entity responsible for making the dataset available.')
    contact_point = models.TextField(blank=True)

    #for updating content
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    last_sync = models.DateTimeField(null=True, editable=False,
        help_text='Last time the data automatically synced')

    sourced_meta_data = JSONField(null=True, blank=True)#, editable=False)


    def to_rdf(self):
        return {
            'rdf:type': 'dcat:Dataset',
            'dct:title': self.title,
            'dct:description': self.description,
            'dcat:theme': self.theme,
            'dct:issued': self.issued,
            'dct:modified': self.modified,
            'dct:identifier': self.identifier,
            'dcat:keyword': self.keyword,
            'dct:language': self.language,
            'dcat:contactPoint': self.contact_point,
            'dct:temporal': self.temporal,
            'dct:spatial': self.spatial,
            'dct:accrualPeriodicity': self.accrual_periodicity,
            'dcat:landingPage': self.landing_page,
            'dcat:distribution': list(map(
                lambda x: x.to_rdf(),
                self.distributions.all()
            ))
        }

    @property
    def linked_publisher(self):
        return self.catalog_record.publisher

    def __str__(self):
        return self.title


class Distribution(models.Model):
    '''
    Fields defined from: https://www.w3.org/TR/vocab-dcat/#class-distribution

    This model should be autopopulated by a sync task

    dcat:Distribution
    '''
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    issued = models.DateTimeField('release date', null=True, blank=True,
        help_text='Date of formal issuance (e.g., publication) of the distribution.')
    modified = models.DateTimeField('update/modification date', null=True, blank=True,
        help_text='Most recent date on which the distribution was changed, updated or modified.')
    license = models.TextField(blank=True,
        help_text='This links to the license document under which the distribution is made available.')
    rights = models.TextField(blank=True,
        help_text='Information about rights held in and over the distribution.')
    access_url = models.URLField(blank=True,
        help_text='A landing page, feed, SPARQL endpoint or other type of resource that gives access to the distribution of the dataset')
    download_url = models.URLField(blank=True,
        help_text='A file that contains the distribution of the dataset in a given format')
    byte_size = models.PositiveIntegerField(null=True, blank=True,
        help_text='The size of a distribution in bytes.')
    media_type = models.CharField(max_length=50, blank=True,
        help_text='The media type of the distribution as defined by IANA.')
    format = models.CharField(max_length=50, blank=True,
        help_text='The file format of the distribution.')

    dataset = models.ForeignKey(Dataset, related_name='distributions')

    def get_rdf_url(self):
        url = self.dataset.catalog_record.get_absolute_url()
        return '#distribution-'.join((url, str(self.id)))

    def add_rdf_distribution(self, g):
        uri = URIRef(self.get_rdf_url())
        for p, o in [
            (RDF.type, DCAT.Distribution),
            (DCT.title, self.title),
            (DCT.description, self.description),
            (DCT.issued, self.issued),
            (DCT.modified, self.modified),
            (DCT.license, self.license),
            (DCT.rights, self.rights),
            (DCAT.accessURL, self.access_url),
            (DCAT.downloadURL, self.download_url),
            (DCAT.media_type, self.media_type),
            (DCT['format'], self.format),
            (DCAT.byteSize, self.byte_size),
        ]:
            if o:
                g.add( (uri, p, DjRef(o)) )


class DatasetURL(models.Model):
    '''
    Keeps track of dataset urls in the system.

        * associate datasets not yet registered in the system
        * track old urls
        * search & dedupe catalog records
    '''
    catalog_record = models.ForeignKey(CatalogRecord, null=True, blank=True, related_name='urls')
    url = models.URLField(unique=True)

    def __str__(self):
        return self.url

    def attempt_catalog_record_sync(self):
        '''
        Attempts to create a catalog record for this url.
        The record will be saved if the sync is successfull.
        None will be returned if no successfull sync took place.
        '''
        assert not self.catalog_record
        url = self.url
        cr = CatalogRecord(identifier=url)
        #TODO detect publisher
        for sync_strategy in ['apps.datasets.sync.socrata', 'apps.datasets.sync.arcgis']:
            try:
                result = cr.run_sync_strategy(sync_strategy, url)
            except Exception as error:
                pass
                print('nope:', error, sync_strategy)
                #self.stdout.write(self.style.NOTICE('Nope: %s (%s)' % (sync_strategy, url)))
                #self.stdout.write(self.style.NOTICE(str(error)))
            else:
                cr.title = cr.dataset.title
                cr.description = cr.dataset.description
                cr.sync_strategy = sync_strategy
                cr.sync_url = url
                if cr.state == 'new':
                    cr.state = 'published'
                cr.save()

                self.catalog_record = cr
                self.save()
                return cr


#TODO make models folder?
#for featuring datasets on a page
class DatasetsPluginModel(CMSPlugin):
    datasets = models.ManyToManyField(CatalogRecord)

    def copy_relations(self, oldinstance):
        self.datasets = oldinstance.datasets.all()

    def __str__(self):
        qs = self.datasets.all()
        count = len(qs)
        s_repr = None
        if count == 0:
            s_repr = "(Empty)"
        elif count == 1:
            s_repr = str(qs[0])
        elif count < 3:
            s_repr = str(list(qs))
        else:
            s_repr = "%s Datasets" % count
        return s_repr


class DatasetsCustomPluginModel(CMSPlugin):
    title = models.CharField(max_length=250)
    datasets = models.ManyToManyField(CatalogRecord)
    show_title = models.BooleanField(default=True)

    def copy_relations(self, oldinstance):
        self.datasets = oldinstance.datasets.all()

    def __str__(self):
        qs = self.datasets.all()
        count = len(qs)
        s_repr = None
        if count == 0:
            s_repr = "(Empty)"
        elif count == 1:
            s_repr = str(qs[0])
        else:
            s_repr = "%s Datasets" % count

        s_repr = self.title + ': ' + s_repr
        return s_repr

class DatasetsGroupPluginModel(CMSPlugin):
    title = models.CharField(max_length=250)
    link = models.CharField(blank=True, max_length=200)
    datasets = models.ManyToManyField(CatalogRecord)
    show_title = models.BooleanField(default=True)

    def copy_relations(self, oldinstance):
        self.datasets = oldinstance.datasets.all()

    def __str__(self):
        qs = self.datasets.all()
        count = len(qs)
        s_repr = None
        if count == 0:
            s_repr = "(Empty)"
        elif count == 1:
            s_repr = str(qs[0])
        else:
            s_repr = "%s Datasets" % count

        s_repr = self.title + ': ' + s_repr
        return s_repr


class DatasourceSuggestion(models.Model):
    state = FSMField(default='new', protected=False, db_index=True, state_choices=DATASOURCE_STATE_CHOICES)
    submission = models.TextField() #json
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='submitted_datasources')
