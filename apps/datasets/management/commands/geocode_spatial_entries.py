from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
from django.db.models import Q
from django.conf import settings
import time
from geopy.geocoders import Nominatim

from apps.datasets.models import CatalogRecord, SpatialEntity


#TODO policy on `,`

TITLED_ADDRESS = [
    ('City of ', 'city'),
    ('County of ', 'county'),
    ('State of ', 'state'),
]

all_and_true = lambda x: all(x) and len(x)

def isfloat(x):
    try:
        float(x)
    except:
        return False
    else:
        return True

class Command(BaseCommand):
    help = 'Creates spatial entities for catalog records that specify a spatial value'


    def handle(self, *args, **options):
        geolocator = Nominatim(country_bias='USA')
        qs = CatalogRecord.objects.exclude(Q(spatial='') | Q(spatial_entity__isnull=False) | Q(spatial_geometry__isnull=False))
        for ds in qs:
            name = ds.spatial
            print(name)
            geo_data = None
            if name.startswith('POLYGON'):
                try:
                    geo_data = GEOSGeometry(name)
                except Exception as error:
                    self.stdout.write(self.style.WARNING('bad geometry given.'))
                    print(error)
                    continue

            elif all_and_true(list(map(isfloat, name.split(',')))):
                numbers = list(map(float, name.split(',')))

                #TODO write to a geocode field
                #TODO also detect POLYGON entries
                if len(numbers) % 2:
                    self.stdout.write(self.style.WARNING('Catalog Record has uneven list of numbers for geolocation'))
                    continue

                points = list(zip(numbers[::2], numbers[1::2]))

                if len(points) == 1:
                    #point?
                    geo_data = Point(numbers)
                elif len(points) == 2:
                    #bounding box
                    geo_data = Polygon((
                        (numbers[0], numbers[1]),
                        (numbers[2], numbers[1]),
                        (numbers[2], numbers[3]),
                        (numbers[0], numbers[3]),
                        (numbers[0], numbers[1]),
                    ))
                else:
                    #all others: polygon
                    geo_data = Polygon(points)

            if geo_data:
                ds.spatial_geometry = geo_data
                ds.save()
                self.stdout.write(self.style.SUCCESS('Geoemtry field updated'))
                continue
            try:
                se = SpatialEntity.objects.get(name=name)
            except SpatialEntity.DoesNotExist:
                query = name

                #City of, County of, State of => parsed to dictionary for exact query
                for prefix, clevel in TITLED_ADDRESS:
                    if name.startswith(prefix):
                        query = {
                            clevel: name[len(prefix):]
                        }
                        break

                time.sleep(1) #rest a second so we dont get banned
                location = geolocator.geocode(query, geometry='geojson')
                if not location:
                    self.stdout.write(self.style.WARNING('No location found for: %s' % name))
                    continue
                geo_data = GEOSGeometry(str(location.raw.pop('geojson')))
                params = {
                    'name': name,
                    'geometry': geo_data,
                    'data': location.raw,
                }
                #print(name, params)
                se = SpatialEntity.objects.create(**params)
                self.stdout.write(self.style.SUCCESS('Spatial entity created: %s' % name))
            ds.spatial_entity = se
            ds.save()
