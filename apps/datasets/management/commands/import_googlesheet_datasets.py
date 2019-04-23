from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist

from apps.datasets.models import CatalogRecord, Publisher, DataPortal
from data_commons.contrib.autosave import AutoSave

import pytz
import httplib2
import datetime
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from stringcase import snakecase
from dateutil.parser import parse
from pprint import pprint


TZ_INFO = pytz.timezone(settings.TIME_ZONE)


def parseTime(astring):
    astring = astring.strip()
    if not astring:
        return None
    value = parse(astring)
    if not value.tzinfo:
        value = value.replace(tzinfo=pytz.UTC)#TZ_INFO)
    return value

def get_credentials(credential_path):
    scope = ['https://spreadsheets.google.com/feeds']

    return ServiceAccountCredentials.from_json_keyfile_name(credential_path, scope)


def worksheet_to_dictionary_list(service, spreadsheetId, worksheetName):
    def get_range(rangeStr):
        rangeName = '%s!%s' % (worksheetName, rangeStr)
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId, range=rangeName).execute()
        return result.get('values', [])

    titles = get_range('1:1')[0]
    print('titles:', worksheetName, titles)
    list_of_lists = get_range('A2:Z')
    print('length of results:', len(list_of_lists))

    rows = list()
    #chomp
    for proto_row in list_of_lists:
        row = dict()
        for col, val in zip(titles, proto_row):
            if col == '@type':
                continue
            row[col] = val
        rows.append(row)
    return rows

def write_obj(obj, dictionary):
    t = type(obj)
    for key, value in dictionary.items():
        if value in (None, ''): #skip empty values
            continue
        if key.endswith('URL'):
            key = key.replace('URL', 'Url')
        attr = snakecase(key)
        if not hasattr(t, attr) and not hasattr(obj, attr):
            raise AttributeError("unrecognized attribute: "+attr)
        try:
            field = t._meta.get_field(attr)
        except FieldDoesNotExist as error:
            pass
        else:
            value = field.to_python(value)
        setattr(obj, attr, value)
    return obj


def get_or_create_publisher(title):
    if ';' in title:
        last_part = title.split(';')[-1]
        obj = Publisher.objects.filter(slug=slugify(last_part)).first()
        if obj:
            return obj
        if len(title) > 100:
            title = last_part.strip()
    if len(title) > 100:
        print("Nope, title too long to be publisher")
        return None
    obj, created = Publisher.objects.get_or_create(
        slug=slugify(title),
        defaults={'name': title})
    return obj


class Command(BaseCommand):
    help = 'Imports datasets from a Regional Data Inventory google spreadsheet.'

    def add_arguments(self, parser):
        parser.add_argument('authjson', type=str)
        parser.add_argument('spreadsheetId', type=str)
        parser.add_argument('--rebuild', dest='rebuild',
                    action='store_const', const=True, default=False,
                    help='rebuild publisher tree')
        parser.add_argument('--publishers', dest='publishers',
                    action='store_const', const=True, default=False,
                    help='read publishers and dataportals tabs')

    def handle(self, *args, **options):
        print(options)
        self.updated_records = set()
        rebuild_publishers = options['rebuild']
        credentials = get_credentials(options['authjson'])
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)

        spreadsheetId = options['spreadsheetId']

        if rebuild_publishers:
            try:
                Publisher.fix_tree(destructive=True)
            except Exception as error:
                self.stdout.write(self.style.ERROR("Publisher tree is unfixable"))
                self.stdout.write(self.style.ERROR(str(error)))
                #Publisher.objects.all().delete()
                return

        rows_of_datasets = worksheet_to_dictionary_list(
            service, spreadsheetId, 'Datasets')
        if options['publishers']:
            rows_of_publishers = worksheet_to_dictionary_list(
                service, spreadsheetId, 'Publishers')
            rows_of_portals = worksheet_to_dictionary_list(
                service, spreadsheetId, 'Data Portals')

            print("publisher example:", rows_of_publishers[0])

        if options['publishers']:
            for publisher in rows_of_publishers:
                publisher['slug'] = slugify(publisher['name'])
                self.push_update(Publisher.objects.filter(slug=publisher['slug']), publisher)

            for portal in rows_of_portals:
                #match by slug or name?
                publisher = get_or_create_publisher(portal['publisher'])
                portal['publisher'] = publisher
                portal['datasets_estimate'] = portal.pop('datasets est', None) or None
                self.push_update(DataPortal.objects.filter(url=portal['url']), portal)

        ds_success = 0
        ds_error = 0
        ds_inc = 0
        for dataset in rows_of_datasets:
            try:
                ds_obj = self.update_dataset(dataset)
            except (KeyboardInterrupt, SystemError):
                raise
            except Exception as error:
                pprint(dataset)
                self.stdout.write(self.style.ERROR(str(error)))
                ds_error += 1
            else:
                if ds_obj:
                    ds_success += 1
                else:
                    ds_inc += 1

        if ds_error:
            self.stdout.write(self.style.ERROR('%s Datasets Errored out.' % ds_error))
        if ds_inc:
            self.stdout.write(self.style.WARNING('%s Datasets Incomplete and not imported.' % ds_inc))
        if ds_success:
            self.stdout.write(self.style.SUCCESS('%s Datasets Synced.' % ds_success))
        self.stdout.write(self.style.SUCCESS('Successfully synced spreadsheet "%s"' % spreadsheetId))

    def update_dataset(self, dataset):
        k = dataset.get('keyword', '')
        if k:
            if len(k) > 100 and len(k.split(',')) <= (len(k)/100):
                print(k)
                self.stdout.write(self.style.WARNING('Keyword doesnt look like tags'))
            else:
                dataset['tags'] = k.split(',')
        dataset.pop('describedByType', None) #TODO store this?
        dataset['distribution_fields'] = dataset.pop('distribution fields (url, etc)', None)
        dataset['notes'] = dataset.pop('notes (date/note)', None)
        modified = dataset.pop('modified', None)
        if modified:
            dataset['modified'] = parseTime(modified)
        else:
            dataset['modified'] = None
        issued = dataset.pop('issued', None)
        if issued:
            dataset['issued'] = parseTime(issued)
        else:
            dataset['issued'] = None

        match_by = dict()
        if dataset['distribution_fields']:
            match_by['distribution_fields'] = dataset['distribution_fields']
        if dataset.get('landingPage', None):
            match_by['landing_page'] = dataset['landingPage']

        if not match_by:
            pprint(dataset)
            self.stdout.write(self.style.WARNING('No unique identifier (distribution fields, landing page)'))
            return

        #convert publisher name into foreignkey
        if dataset.get('subpublisher', None):
            if len(dataset['subpublisher']) > 100: #name is too big
                #TODO if subpublisher is in publisher name, chomp?
                self.stdout.write(self.style.WARNING('Too long of a publisher name: %s' % dataset['subpublisher']))
            publisher = get_or_create_publisher(dataset['subpublisher'])
            dataset.pop('subpublisher', None)
        else:
            publisher = get_or_create_publisher(dataset['publisher'])

        dataset.pop('publisher type', None)
        tags = dataset.pop('tags', '')
        dataset['publisher'] = publisher

        queryset = CatalogRecord.objects.filter(**match_by).exclude(id__in=self.updated_records)

        new_obj, autosaver = self.push_update(queryset, dataset)
        self.updated_records.add(new_obj.id)

        if 'keyword' in autosaver.changed_fields:
            tags = list(filter(bool, map(lambda x: x.strip(), tags)))
            if tags:
                try:
                    new_obj.tags.add(*tags)
                except (KeyboardInterrupt, SystemError):
                    raise
                except Exception as error:
                    pprint(tags)
                    self.stdout.write(self.style.WARNING("Could not set tags"))
                    self.stdout.write(self.style.ERROR(str(error)))
        return new_obj

    def push_update(self, qs, instance_data):
        update = True
        model_class = qs.model
        obj = qs.first()
        if not obj:
            update = False
            obj = model_class()

        autosaver = AutoSave(obj)
        with autosaver:
            write_obj(obj, instance_data)
        #obj.save() #handled by autosaver
        if autosaver.saved:
            m_name = model_class._meta.verbose_name
            if update:
                self.stdout.write(self.style.SUCCESS('Updated %s: %s' % (m_name, obj)))
                pprint(autosaver.changed_fields)
            else:
                self.stdout.write(self.style.SUCCESS('New %s: %s' % (m_name, obj)))
        return obj, autosaver

    def push_publisher(self, instance_data):
        update = True
        obj = Publisher.objects.filter(slug=instance_data['slug']).first()
        if not obj:
            update = False
            obj = Publisher()

        autosaver = AutoSave(obj)
        autosaver.snapshot()
        write_obj(obj, instance_data)

        if instance_data['sub_organization_of']:
            parent = Publisher.objects.filter(slug=slugify(instance_data['sub_organization_of'])).first()
            if not parent:
                parent = Publisher.add_root(slug=slugify(instance_data['sub_organization_of']), name=instance_data['sub_organization_of'])
        else:
            parent = None
        m_name = obj._meta.verbose_name

        if update:
            autosaver.autocommit() #obj.save()
            if parent:
                obj.move(parent, 'sorted-child')
            else:
                pass
                #TODO check if we're root?
        else:
            if parent:
                parent.add_child(instance=obj)
            else:
                Publisher.add_root(instance=obj)
            autosaver.saved = True

        if autosaver.saved:
            if update:
                self.stdout.write(self.style.SUCCESS('Updated %s: %s' % (m_name, obj)))
            else:
                self.stdout.write(self.style.SUCCESS('New %s: %s' % (m_name, obj)))
        return obj, autosaver
