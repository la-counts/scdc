from django.test import TestCase
from datetime import date

from .models import CatalogRecord


def test_parse_human_temporal_range():
    assert CatalogRecord.parse_human_temporal_range("2004") == (
        date(2004), date(2005)
    )
