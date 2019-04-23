import uuid
from functools import lru_cache

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.timezone import datetime

from cms.models import CMSPlugin
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django_fsm import FSMField, transition
from taggit.managers import TaggableManager
from autoslug import AutoSlugField
from image_cropping import ImageRatioField
from cms.models.fields import PlaceholderField

from .managers import StoryManager


STATE_CHOICES = [
    ('new', 'New', 'Story'),
    ('published', 'Published', 'Story'),
    ('rejected', 'Rejected', 'Story'),
]

class Story(models.Model):
    title = models.CharField('Headline', max_length=255)
    slug = AutoSlugField(populate_from='title', unique=True)
    subheader = models.CharField('Subheader', max_length=255, blank=True)
    state = FSMField(default='new', protected=False, db_index=True, state_choices=STATE_CHOICES)
    highlight = models.BooleanField(default=False, db_index=True,
        help_text='If checked, this story will be listed towards the top')

    organization = models.ForeignKey('datasets.Publisher', blank=True, null=True)

    datasets = models.ManyToManyField('datasets.CatalogRecord', blank=True, related_name='linked_stories')
    datasource_urls = models.TextField(blank=True, help_text='''
    Extra datasource urls
    ''')
    #related is spanned through concepts
    #related = models.ManyToManyField('self', blank=True)
    tags = TaggableManager('User tags', blank=True)
    concepts = models.ManyToManyField('focus.Concept', blank=True)
    repostPermissionLine = models.CharField(verbose_name='Reposted with Permission Text', max_length=255, blank=True)
    
    bodyFeaturedText = RichTextField(verbose_name='Body Featured Text', blank=True)
    
    body = RichTextUploadingField()

    author = models.CharField(max_length=255, blank=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='posted_stories')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='approved_stories')
    published_at = models.DateTimeField(null=True, blank=True) #TODO url based on this or author?
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    featured_image = models.ImageField(upload_to='stories', blank=True)
    card_image = ImageRatioField('featured_image', '400x400')
    wide_card_image = ImageRatioField('featured_image', '800x400')
    featured_image_caption = models.TextField(blank=True)

    objects = StoryManager()

    def __str__(self):
        if len(self.title) > 53:
            return self.title[:50] + '...'
        return self.title

    class Meta:
        verbose_name_plural = 'stories'
        ordering = ['-highlight', '-published_at']

    @property
    def authored_by(self):
        return self.author or self.posted_by

    def get_absolute_url(self):
        return reverse('stories:detail', args=(self.slug,))

    @transition(field=state, source=['new', 'rejected'], target='published')
    def publish(self):
        if not self.published_at:
            self.published_at = datetime.now()

    @transition(field=state, source='new', target='rejected')
    def reject(self):
        pass

    @lru_cache()
    def related_concepts(self):
        return self.concepts.all().get_descendants(include_self=True).search_matched()

    def related_stories(self):
        concepts = self.related_concepts()
        stories = Story.objects.published().filter(concepts__in=concepts).exclude(pk=self.pk).distinct()
        
        return stories

    def related_datasets(self):
        from apps.datasets.models import CatalogRecord
        concepts = self.related_concepts()
        return CatalogRecord.objects.published().filter(concepts__in=concepts)

    def map_datasource_urls(self):
        #TODO datasource is more broad then datasets, handle those as suggestions
        from apps.datasets.models import DatasetURL
        unmapped_urls = list()
        new_datasets = list()
        for ds_url in self.datasource_urls.split():
            if '://' not in ds_url:
                continue
            print('Story datasource:', ds_url)
            du = DatasetURL.objects.get_or_create(url=ds_url)[0]
            if du.catalog_record:
                self.datasets.add(du.catalog_record)
                new_datasets.append(du.catalog_record)
            else:
                cr = du.attempt_catalog_record_sync()
                if cr:
                    self.datasets.add(cr)
                    new_datasets.append(cr)
                else:
                    unmapped_urls.append(du)
        self.datasource_urls = '\n'.join((du.url for du in unmapped_urls))
        self.save()
        return new_datasets



class StoryImage(models.Model):
    story = models.ForeignKey(Story, related_name='images')
    image = models.ImageField(upload_to='stories')
    caption = models.TextField(blank=True)

    class Meta:
        order_with_respect_to = 'story'


#for featuring stories on a page
class StoriesPluginModel(CMSPlugin):
    stories = models.ManyToManyField(Story, through='StoryDisplayPlugin')
    display_cards = models.BooleanField(default=False,
        help_text='Render linked stories as cards')

    def copy_relations(self, oldinstance):
        for sdp in oldinstance.story_display_set.all():
            StoryDisplayPlugin.objects.update_or_create(plugin=self, story=sdp.story, defaults={'order': sdp.order})

    def get_stories(self):
        return self.stories.all().order_by('story_display_set')

    def __str__(self):
        stories = self.get_stories()
        count = len(stories)
        stories_repr = None
        if count == 0:
            stories_repr = "(Empty)"
        elif count == 1:
            stories_repr = str(stories[0])
        elif count < 3:
            stories_repr = str(list(stories))
        else:
            stories_repr = "%s Stories" % count
        return stories_repr

class StoryDisplayPlugin(models.Model):
    plugin = models.ForeignKey(StoriesPluginModel, related_name='story_display_set')
    order = models.IntegerField(default=0, help_text='lower values are displayed first')
    story = models.ForeignKey(Story, related_name='story_display_set')
    sidebar_placeholder = PlaceholderField('story_index_sidebar')

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return str(self.story)
