from django_rq import job

from .models import Story


@job
def map_story_datasource_urls_job(id):
    story = Story.objects.get(id=id)
    story.map_story_datasource_urls()
