from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from apps.datasets.models import CatalogRecord, SYNC_STRATEGY_CHOICES


SOCRATA = 'apps.datasets.sync.socrata'
STATIC_LINK = 'apps.datasets.sync.static_link'
ARCGIS = 'apps.datasets.sync.arcgis'


class Command(BaseCommand):
    help = "Automatically detects which sync strategy to use on unassigned catalog records."

    def add_arguments(self, parser):
        parser.add_argument('catalog_record', nargs='*', type=int)

    def handle(self, *args, **options):
        print(options)
        if len(options['catalog_record']):
            queryset = CatalogRecord.objects.filter(pk__in=options['catalog_record'])
        else:
            queryset = CatalogRecord.objects.filter(sync_strategy='')
        for cr in queryset:
            self.stdout.write(self.style.SUCCESS('Testing %s' % cr))
            dist = cr.distribution.lower()
            if 'arcgis' in dist or 'shapefile' in dist:
                if self.test_sync_and_set(cr, ARCGIS):
                    self.stdout.write(self.style.SUCCESS('%s set to Arcgis' % cr))
                    continue
            if 'socrata' in dist:
                if self.test_sync_and_set(cr, SOCRATA):
                    self.stdout.write(self.style.SUCCESS('%s set to Socrata' % cr))
                    continue
            if 'github.com' in cr.landing_page:
                cr.run_sync_strategy(sync_strategy, cr.landing_page)
                self.stdout.write(self.style.SUCCESS('%s set to Static' % cr))
                continue
            self.stdout.write(self.style.WARNING('Could not resolve stategy'))


    def test_sync_and_set(self, cr, sync_strategy):
        urls = filter(lambda x: x and '://' in x, [cr.identifier, cr.distribution_fields, cr.landing_page])
        for url in set(urls):
            try:
                result = cr.run_sync_strategy(sync_strategy, url)
            except Exception as error:
                self.stdout.write(self.style.NOTICE('Nope: %s (%s)' % (sync_strategy, url)))
                self.stdout.write(self.style.NOTICE(str(error)))
            else:
                cr.sync_strategy = sync_strategy
                cr.sync_url = url
                if cr.state == 'new':
                    cr.state = 'published'
                cr.save()
                return True
        return False
