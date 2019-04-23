from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from apps.datasets.models import CatalogRecord



class Command(BaseCommand):
    help = "Syncs a catalog record(s) using the dataset's API."

    def add_arguments(self, parser):
        parser.add_argument('catalog_record', nargs='*', type=int)

    def handle(self, *args, **options):
        print(options)
        if len(options['catalog_record']):
            queryset = CatalogRecord.objects.filter(pk__in=options['catalog_record'])
        else:
            queryset = CatalogRecord.objects.exclude(sync_strategy='', state__in=['archived', 'rejected'])
        print(queryset)
        for cr in queryset:
            dupes = cr.check_if_duplicate()
            if dupes:
                self.stdout.write(self.style.WARNING("%s is a duplicate" % cr))
                #TODO now what?
            try:
                cr.run_sync_strategy()
            #TODO catch 404s? => flag broken
            except Exception as error:
                if cr.state == 'published':
                    cr.state = 'broken'
                    cr.save()
                self.stdout.write(self.style.ERROR(str(error)))
            else:
                if cr.state != 'published':
                    cr.state = 'published'
                    cr.save()
                self.stdout.write(self.style.SUCCESS('Successfully synced "%s"' % cr))
