from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.urlresolvers import reverse
from urllib.parse import urlencode
from taggit.managers import TaggableManager
import json


#username == email
class User(AbstractUser):
    display_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255, blank=True)
    publisher = models.ForeignKey('datasets.Publisher', blank=True, null=True) #set by an admin
    website = models.URLField(blank=True, help_text='Include the protocol, example: https://www.lacity.org')

    avatar = models.ImageField(upload_to='avatars/', blank=True)
    interests = TaggableManager(blank=True) #form provides any graphical sauce ontop, but translates to a list of words
    concepts = models.ManyToManyField('focus.Concept', blank=True)

    def __str__(self):
        return self.display_name or self.username


class SavedSearch(models.Model):
    #CONSIDER: json field uniqueness?
    params = models.TextField(unique=True) #search form fields

    @classmethod
    def from_search_form(cls, form):
        data = form.data
        #json antipattern? (queryset values blow up)
        params = json.dumps(data, sort_keys=True, ensure_ascii=False)
        obj = cls.objects.get_or_create(params=params)[0]
        return obj

    def get_absolute_url(self):
        return '%s?%s' % (
            reverse('datasets:dataset_search'),
            self.get_urlencoded_params()
        )

    @property
    def form_data(self):
        return json.loads(self.params)

    def get_urlencoded_params(self):
        return urlencode(self.form_data)

    def __str__(self):
        return ' + '.join('%s:%s' % (key, val) if key != 'q' else str(val)
            for key, val in self.form_data.items() if val and key != 'facet_display')
