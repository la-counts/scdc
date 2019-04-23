'''
Represents a limited W3C Simple Knowledge Organization System

https://www.w3.org/TR/skos-primer/

DCAT conveys themes/topics with Concept & ConceptScheme objects

A Concept is a unit in the system with defined labels.
A ConceptScheme is a top level for concepts with additional fields

Consider in the admin we want a ConceptScheme to be a top level concept?
- easier drag & drop if same tree
- easier semantics
- may duplicate fields (ConceptScheme has no labels)
'''
from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.postgres.fields import JSONField

from functools import lru_cache
from cms.models import CMSPlugin
from rdflib.namespace import SKOS, RDFS, RDF
from rdflib import URIRef, Literal
from autoslug import AutoSlugField
from treebeard.mp_tree import MP_Node
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
from django_fsm import FSMField, transition
from django.contrib.admin import StackedInline
from django.utils.text import slugify

from data_commons.contrib.rdf import DjRef
from apps.datasets.models import CatalogRecord
from .managers import ConceptManager, InterestPageManager


PAGE_STATE_CHOICES = [
    ('new', 'New', 'InterestPage'),
    ('published', 'Published', 'InterestPage'),
    ('archived', 'Archived', 'InterestPage'),
]

#CONSIDER: within a concept scheme, a label may only be used once, even among alternates
class Concept(MP_Node):
    '''
    A W3C SKOS Concept
    '''
    title = models.CharField(max_length=60)
    slug = AutoSlugField(populate_from='title', unique=True)
    definition = models.TextField(blank=True)
    example = models.TextField(blank=True)
    alternative_parents = models.ManyToManyField('self', blank=True, related_name='alternative_children')

    #CONSIDER would this be bidirectional many2many?
    #skos:relatedMatch
    related_match = models.ManyToManyField('self', blank=True, related_name='related_from')
    #skos:exactMatch
    exact_match = models.ManyToManyField('self', blank=True, related_name='exact_from')
    #skos:closeMatch
    close_match = models.ManyToManyField('self', blank=True, related_name='close_from')

    #CONSIDER: we may want an autopopulate action
    tags = TaggableManager(blank=True, related_name='concepts',
        help_text='these tags will automatically be mapped to this concept')

    url_path = models.CharField(max_length=512, unique=True, editable=False)

    objects = ConceptManager()
    node_order_by = ['slug']

    class Meta:
        ordering = ['path']

    def __str__(self):
        return self.title

    @property
    def rdf_type(self):
        if self.depth == 1:
            return 'skos:ConceptScheme'
        return 'skos:Concept'

    @property
    def as_rdf_ref(self):
        return self.slug

    def to_rdf_concept_scheme(self):
        return {
            'rdf:type': 'skos:ConceptScheme',
            'dct:title': self.title,
            'skos:definition': self.definition,
            'skos:example': self.example,
        }

    @classmethod
    def add_rdf_scheme(cls, g):
        concepts = cls.get_root_nodes()
        uri = URIRef(reverse('focus:index'))
        for concept in concepts:
            o = DjRef(concept)
            g.add( (uri, SKOS.topConceptOf, o) )

    def add_rdf_concept(self, g, ref_children=True):
        uri = URIRef(self.get_absolute_url())
        for p, o in [
            (RDF.type, SKOS.Concept),
            (SKOS.definition, self.definition),
            (SKOS.example, self.example),
            (SKOS.broaderTransitive, self.get_parent()),
            (SKOS.inScheme, URIRef(reverse('focus:index'))),
        ]:
            if o:
                g.add( (uri, p, DjRef(o)) )

        has_preferred = False
        for l in self.labels.all():
            o = Literal(l.label, lang=l.language_code)
            p = l.rdf_predicate
            g.add( (uri, p, o) )
            if l.usage == 'p':
                has_preferred = True

        if not has_preferred:
            g.add( (uri, SKOS.prefLabel, Literal(self.title)) )

        for p in self.alternative_parents.all():
            #CONSIDER: broaderTransitive instead?
            g.add( (uri, SKOS.broadMatch, DjRef(p)) )

        for m in self.related_match.all():
            g.add( (uri, SKOS.relatedMatch, DjRef(m)) )

        for m in self.exact_match.all():
            g.add( (uri, SKOS.exactMatch, DjRef(m)) )

        for m in self.close_match.all():
            g.add( (uri, SKOS.closeMatch, DjRef(m)) )

        for equiv in self.mappeduri_set.all():
            g.add( (uri, SKOS.closeMatch, URIRef(equiv.uri)) )

        if ref_children:
            for child in self.get_children():
                g.add( (uri, SKOS.narrowerTransitive, DjRef(child)))

    def to_rdf(self):
        if self.depth == 1:
            return self.to_rdf_concept_scheme()
        return self.to_rdf_concept()

    def update_url_path(self):
        ancestors = self.get_ancestors()
        parts = [k.slug for k in ancestors]
        parts.append(self.slug)
        self.url_path = '/'.join(parts)

    def save(self, *args, **kwargs):
        if not self.slug: #trigger slug generation before updating url path
            self._meta.get_field('slug').pre_save(self, not self.pk)
        self.update_url_path() #may fail if we are updating our path?
        return super(Concept, self).save(*args, **kwargs)

    def get_all_the_catalog_records(self):
        '''
        Get all datasets belonging to this tag, and tags of descendents
        '''
        all_tag_names = list(self.get_descendants().values_list('title', flat=True))
        all_tag_names += self.title
        return CatalogRecord.objects.filter(keyword__name__in=all_tag_names)

    def get_catalog_records(self):
        return CatalogRecord.objects.filter(keyword__name=self.title)

    def our_search_labels(self):
        p_label = None
        all_labels = list()
        for label_instance in self.labels.all():
            all_labels.append(label_instance.label)
            if label_instance.usage == 'p':
                p_label = label_instance.label
        if not p_label:
            p_label = self.title
            all_labels.append(self.title)
        return all_labels

    def search_related(self):
        return (self.related_match.all() | self.exact_match.all() | self.close_match.all()).distinct()

    def get_all_search_related(self):
        return self.get_family().search_matched()

    @lru_cache()
    def preferred_label(self):
        label = self.labels.filter(usage='p').first()
        if label:
            return label.label
        return self.title

    @lru_cache()
    def parents(self):
        all_parents = []
        parent = self.get_parent()
        if parent:
            all_parents.append(parent)
            all_parents.extend(self.alternative_parents.all())
        return all_parents

    def get_absolute_url(self):
        return reverse('focus:concept_detail', args=(self.url_path,))

#With this model, title would be for admin purposes
#Could auto create label if none is defined and is not scheme (top level)
#CONSIDER: only one preferred label for concept, must be validated
class Label(models.Model):
    '''
    A label in a concept scheme
    '''
    concept = models.ForeignKey(Concept, related_name='labels')
    label = models.CharField(max_length=100)
    language_code = models.CharField(max_length=10)
    usage = models.CharField(max_length=1, choices=[
        ('p', 'preferred'),
        ('a', 'alternative'),
        ('h', 'hidden'),
    ])
    scheme = models.ForeignKey(Concept, editable=False, related_name='scheme_labels',
        help_text='Automatically set to the root of the concept')

    def populate_scheme(self):
        if self.concept.depth == 1:
            self.scheme = self.concept
        else:
            self.scheme = self.concept.get_root()

    @property
    def rdf_predicate(self):
        return {
            'p': SKOS.prefLabel,
            'a': SKOS.altLabel,
            'h': SKOS.hiddenLabel,
        }[self.usage]

    def save(self, *args, **kwargs):
        self.populate_scheme()
        return super(Label, self).save(*args, **kwargs)

    class Meta:
        unique_together = [('label', 'language_code', 'scheme')]


class MappedUri(models.Model):
    '''
    Represents an rdf subject or url that maps to a concept in the system
    '''
    concept = models.ForeignKey(Concept)
    uri = models.CharField(max_length=500, unique=True)
    sourced_meta_data = JSONField(null=True, blank=True, editable=False)

    def __str__(self):
        return 'URI:%s' % self.uri


class InterestPage(models.Model):
    title = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from='title', unique=True)
    state = FSMField(default='new', protected=False, db_index=True, state_choices=PAGE_STATE_CHOICES)
    order = models.IntegerField(default=0,
        help_text='Sets the order in which to display the page in a listing')
    body = RichTextUploadingField()
    link_image = models.ImageField(upload_to='images', blank=True,
        help_text='Image to link to this page')

    concepts = models.ManyToManyField(Concept, blank=True)

    featured_catalog_records = models.ManyToManyField(
        'datasets.CatalogRecord',
        through='FeaturedCatalogRecord',
        through_fields=('page', 'catalog_record'),
        related_name='featured_interests',
        blank=True,
    )

    featured_stories = models.ManyToManyField(
        'stories.Story',
        through='FeaturedStory',
        through_fields=('page', 'story'),
        related_name='featured_interests',
        blank=True,
    )

    objects = InterestPageManager()

    class Meta:
        ordering = ['order']

    def get_absolute_url(self):
        return reverse('focus:page_detail', args=(self.slug,))

    @transition(field=state, source=['new', 'archived'], target='published')
    def publish(self):
        pass

    @transition(field=state, source='new', target='archived')
    def archive(self):
        pass

    def __str__(self):
        return self.title


class FeaturedCatalogRecord(models.Model):
    page = models.ForeignKey(InterestPage)
    catalog_record = models.ForeignKey('datasets.CatalogRecord')

    class Meta:
        unique_together = [('page', 'catalog_record')]
        order_with_respect_to = 'page'


class FeaturedStory(models.Model):
    page = models.ForeignKey(InterestPage)
    story = models.ForeignKey('stories.Story')

    class Meta:
        unique_together = [('page', 'story')]
        order_with_respect_to = 'page'
        verbose_name_plural = 'Featured Stories'


#for featuring concepts on a page
class ConceptsPluginModel(CMSPlugin):
    concepts = models.ManyToManyField(Concept)

    def copy_relations(self, oldinstance):
        self.concepts = oldinstance.concepts.all()

    def __str__(self):
        qs = self.concepts.all()
        count = len(qs)
        s_repr = None
        if count == 0:
            s_repr = "(Empty)"
        elif count == 1:
            s_repr = str(qs[0])
        elif count < 3:
            s_repr = str(qs)
        else:
            s_repr = "%s Concepts" % count
        return s_repr


#TODO ask client for parameters
#class SearchPluginModel(CMSPlugin):
#    pass


class CallToActionPluginModel(CMSPlugin):
    title = models.CharField(max_length=50)
    link = models.CharField(blank=True, max_length=200)
    widget_type = models.CharField(max_length=15)
    text = models.TextField()

    def __str__(self):
        return self.title


class WidgetPanelModel(CMSPlugin):
    text = models.CharField(max_length=250)
    link = models.CharField(blank=True, max_length=200)
    icon = models.FileField(upload_to='uploads/icons')
    image = models.ImageField(upload_to='images')

    def __str__(self):
        return self.text
    

class ContentBoxModel(CMSPlugin):
    title = models.CharField(max_length=250)
    text = models.TextField()
    box_type = models.CharField(max_length=100)
    link_text = models.CharField(max_length=250, null=True, blank=True, help_text='If set, will be added to the end of the text field')
    link = models.CharField(max_length=250, null=True, blank=True)
    
    def __str__(self):
        return self.title


class PriorityAreaHeaderModel(CMSPlugin):
    text = models.CharField(max_length=250)
    icon = models.FileField(upload_to='uploads/icons')
    image = models.ImageField(upload_to='images')

    def __str__(self):
        return self.text
    

class WidgetPanelAnchorsModel(CMSPlugin):
    link = models.CharField(blank=True, max_length=200)
    image = models.ImageField(upload_to='images')
    alignment = models.CharField(max_length=8, choices=(
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
    ))
    body = RichTextUploadingField()

    def __str__(self):
        return self.link
    
class CollapsibleModel(CMSPlugin):
    title = models.CharField(max_length=250)
    body = RichTextUploadingField()

    def __str__(self):
        return self.title
    
class SolidBoxModel(CMSPlugin):
    title = models.CharField(max_length=250)
    body = RichTextUploadingField()
    color = models.CharField(max_length=12, choices=(
        ('yellow', 'Yellow'),
        ('grey', 'Grey'),
        ('blue', 'Blue'),
        ('orange', 'Orange'),
        ('green', 'Green'),
        ('red', 'Red'),
        ('yelloworange', 'Yellow Orange'),
        ('darkblue', 'Dark Blue'),
        ('white', 'White'),
        ('black', 'Black'),
        ('lightgrey', 'Light Grey'),
    ))

    def __str__(self):
        return self.color + ": " + self.title
    

class SimpleSlider(CMSPlugin):
    """ A model that serves as a container for images """

    title = models.CharField(max_length=50, help_text='For reference only')

    def copy_relations(self, oldinstance):
        for slide in oldinstance.simple_slide.all():
            slide.pk = None
            slide.slider = self
            slide.save()

    def __str__(self):
        qs = self.simple_slide.all()
        count = len(qs)
        s_repr = None
        if count == 0:
            s_repr = "(Empty)"
        elif count == 1:
            s_repr = str(qs[0])
        else:
            s_repr = "%s Slides" % count
        return self.title + ": " + s_repr
    

class SimpleSlide(models.Model):
    def get_upload_to(instance, filename):
        return 'slides/{slug}/{filename}'.format(
            slug=slugify(instance.slider.title), filename=filename)

    text = models.CharField(max_length=250)
    link = models.CharField(blank=True, max_length=200)
    icon = models.FileField(upload_to='uploads/icons')
    image = models.ImageField(upload_to=get_upload_to)
    slider = models.ForeignKey(SimpleSlider, related_name="simple_slide")

    def __str__(self):
        return self.text


class SimpleSlideAdminInline(StackedInline):
    model = SimpleSlide
    
    
class SearchWidgetModel(CMSPlugin):
    title = models.CharField(max_length=250)
    placeholdertext = models.CharField(max_length=250)
    endpoint = models.CharField(blank=True, max_length=200)

    def __str__(self):
        return self.title
    
class WidgetTitleModel(CMSPlugin):
    title = models.CharField(max_length=250)
    tag = models.CharField(default='h2', max_length=12, choices=(
        ('h1', 'H1'),
        ('h2', 'H2'),
        ('h3', 'H3'),
        ('h4', 'H4'),
        ('h5', 'H5'),
        ('h6', 'H6'),
    ))

    def __str__(self):
        return self.tag + ":" + self.title