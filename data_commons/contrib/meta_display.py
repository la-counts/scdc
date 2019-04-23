import stringcase
import html
from django.utils.html import format_html, strip_tags
from django.db.models import Model
from rdflib.term import Literal, URIRef
from rdflib import XSD

from .rdf import ModelInstanceRef


class MetaTag(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def label(self):
        return stringcase.titlecase(self.key)

    def html_value(self):
        if not self.value:
            return self._render_empty()
        if isinstance(self.value, Model) and hasattr(self.value, 'get_absolute_url'):
            return self._render_link(self.value.get_absolute_url(), str(self.value))
        if isinstance(self.value, ModelInstanceRef):
            return self._render_link(self.value, str(self.value.instance))
        #if isinstance(self.value, URIRef):
        #    if self.value[0] == '/':
        #        return self._render_link(self.value)
        if isinstance(self.value, str):
            if '://' in self.value:
                return self._render_link(self.value)
        if isinstance(self.value, Literal):
            if self.value.datatype == XSD.date:
                return self._render_date(self.value.value)
            if self.value.datatype == XSD.dateTime:
                return self._render_datetime(self.value.value)
        return strip_tags(html.unescape(str(self.value)))

    def _render_empty(self):
        return ' - '

    def _render_link(self, value, link_name=None):
        #TODO render from template
        if link_name is None:
            link_name = value
        return format_html('<a href="{}">{}</a>',
            value,
            link_name,
        )

    def _render_date(self, value):
        return value.strftime("%m/%d/%Y")

    def _render_datetime(self, value):
        return value.strftime("%m/%d/%Y")# %H:%M")
