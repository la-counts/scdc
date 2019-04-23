from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.conf import settings

from apps.stories.models import Story



class Command(BaseCommand):
    help = """
    Map user supplied dataset urls from stories to existing catalog records.
    Make a record of any newly mentioned dataset urls.
    """

    def add_arguments(self, parser):
        parser.add_argument('story', nargs='*', type=int)

    def handle(self, *args, **options):
        print(options)
        if len(options['story']):
            queryset = Story.objects.filter(pk__in=options['story'])
        else:
            queryset = Story.objects.exclude(Q(state__in=['archived', 'rejected']) | Q(datasource_urls=''))
        print(queryset)
        for story in queryset:
            story.map_datasource_urls()
        self.stdout.write(self.style.SUCCESS('Successfully mapped story urls'))
