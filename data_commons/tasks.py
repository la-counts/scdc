from django.core.management import call_command
from django_rq import job, get_connection
from rq_scheduler import Scheduler
from datetime import timedelta


SCHEDULER = Scheduler(connection=get_connection('default'))


@job
def update_search_index():
    call_command('update_index')

@job
def update_catalog_records():
    call_command('detect_dataset_sync_strategy')
    call_command('sync_catalog_record')
    call_command('map_story_dataset_urls')


SCHEDULER.cron(
    "0 1 * * *",
    func=update_search_index,
    repeat=None, #forever
)

SCHEDULER.cron(
    "0 0 * * *",
    func=update_catalog_records,
    repeat=None, #forever
)
