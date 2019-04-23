from django import template
from django.db.models import F, Count
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
import json
import html

from actstream.models import Follow

from apps.datasets.models import CatalogRecord, Publisher
from apps.stories.models import Story
from apps.profiles.models import SavedSearch
from apps.focus.models import InterestPage


register = template.Library()

@register.inclusion_tag('tags/recent_datasets.html')
def recent_datasets(datasets=None, limit=10, concepts=None):
    datasets = CatalogRecord.objects.display()
    if concepts is not None:
        datasets = datasets.select_concepts(concepts)
    datasets = datasets.distinct().order_by('-created_at')[:limit]
    return {
        'datasets': datasets
    }

@register.inclusion_tag('tags/updated_datasets.html')
def updated_datasets(datasets=None, limit=10, concepts=None):
    datasets = CatalogRecord.objects.display()
    if concepts is not None:
        datasets = datasets.select_concepts(concepts)
    datasets = datasets.distinct().order_by('-updated_at')[:limit]
    return {
        'datasets': datasets
    }


@register.inclusion_tag('tags/dataset_headline.html')
def dataset_headline(dataset, width=12):
    '''
    Renders a column cell call to action to the dataset
    '''
    return {
        'dataset': dataset,
        'width': width,
    }


@register.inclusion_tag('tags/dataset_list_item.html')
def dataset_list_item(dataset, width=12):
    '''
    Renders a column cell call to action to the dataset
    '''
    return {
        'dataset': dataset,
        'width': width,
    }


@register.inclusion_tag('tags/recent_stories.html')
def recent_stories(stories=None, limit=10, concepts=None):
    stories = Story.objects.published()
    if concepts is not None:
        stories = stories.select_concepts(concepts)
    stories = stories.distinct().order_by('-published_at')[:limit]
    return {
        'stories': stories,
    }

@register.inclusion_tag('tags/story_card.html')
def story_card(story, width=3):
    return {
        'story': story,
        'width': width,
    }

@register.inclusion_tag('tags/story_headline.html')
def story_headline(story, width=12):
    return {
        'story': story,
        'width': width,
    }

@register.inclusion_tag('tags/word_bubble.html')
def word_bubble(data):
    #[{id, title, package , value}]
    rows_json = json.dumps(data)
    return {
        'rows_json': rows_json
    }

@register.inclusion_tag('tags/word_bubble.html')
def pulisher_dataset_bubble():
    qs = Publisher.objects.all().annotate(
        title=F('name'),
        value=Count('catalogrecord'),
        package=F('agency_type'),
    )
    qs = qs.values('id', 'title', 'package', 'value', 'slug')
    #[{id, title, package , value}]
    qs = list(qs)
    for x in qs:
        x['url'] = reverse('datasets:publisher_detail', args=(x['slug'],))
    rows_json = json.dumps(qs)
    return {
        'rows_json': rows_json
    }

@register.inclusion_tag('tags/publisher_list.html')
def publisher_list():
    publishers = Publisher.objects.root_nodes()
    agencyTypes = []
    groups = {}
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for letter in alphabet:
        groups[letter] = []
        
    for publisher in publishers:
        alphaGroup = publisher.get_alpha_group().upper()
        if alphaGroup in groups:
            groups[alphaGroup].append(publisher)
        else:
            groups[alphaGroup] = [publisher]
        
        agencyType = publisher.agency_type.strip()
        if agencyType == "":
            agencyType = "Uncategorized"
            
        if agencyType != "" and agencyType not in agencyTypes:
            agencyTypes.append(agencyType)
    
    agencyTypes.sort()
    
    agencyGroupCounter = 0
    agencyGroups = []
    agencyGroup = []
    for agency in agencyTypes:
        agencySlug = slugify(agency)
        agencyLen = len(agency)
        agencyGroup.append(agency)
        if agencyLen > 20:
            agencyGroupCounter += 1
        agencyGroupCounter += 1
        if agencyGroupCounter >= 3:
            agencyGroupCounter = 0
            agencyGroups.append(agencyGroup)
            agencyGroup = []
        
    
    ctx = {
        'filters': agencyGroups,
        'groups': groups
    }
    return ctx

@register.inclusion_tag('tags/display_tags.html')
def display_tags(tagset):
    return {
        'tags': tagset
    }

@register.inclusion_tag('tags/saved_datasets.html', takes_context=True)
def saved_datasets(context):
    user = context['user']
    if user.is_authenticated:
        records = Follow.objects.following(user, CatalogRecord)
    else:
        records = []
    return {
        'records': records
    }

@register.inclusion_tag('tags/saved_searches.html', takes_context=True)
def saved_searches(context):
    user = context['user']
    if user.is_authenticated:
        seaches = Follow.objects.following(user, SavedSearch)
    else:
        searches = []
    return {
        'searches': searches
    }

@register.inclusion_tag('tags/saved_stories.html', takes_context=True)
def saved_stories(context):
    user = context['user']
    if user.is_authenticated:
        stories = Follow.objects.following(user, Story)
    else:
        stories = []
    return {
        'stories': stories
    }

@register.inclusion_tag('tags/saved_status.html', takes_context=True)
def saved_status(context, obj):
    '''
    Render whether the current user is following the object
    '''
    user = context['user']
    is_following = False
    url = '#'
    if user.is_authenticated:
        content_type = ContentType.objects.get_for_model(obj).pk
        is_following = Follow.objects.is_following(user, obj)

        if is_following:
            url = reverse('actstream_unfollow', kwargs={
                'content_type_id': content_type, 'object_id': obj.pk})
        else:
            url = reverse('actstream_follow', kwargs={
                'content_type_id': content_type, 'object_id': obj.pk})

    return {
        'user': user,
        'is_following': is_following,
        'url': url,
        'obj': obj,
    }

@register.inclusion_tag('tags/interest_pages.html')
def interest_pages():
    '''
    Call to Action that features interest areas
    '''
    pages = InterestPage.objects.all()
    return {
        'pages': pages,
    }

@register.filter()
def html_unescape(value):
    return html.unescape(value)

@register.inclusion_tag('tags/imgbox.html')
def imgbox(img, size):
    width, height = size.split('x', 1)
    return {
        'width': width,
        'height': height,
        'image': img,
        'size': size
    }
