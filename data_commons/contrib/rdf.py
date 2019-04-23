from rdflib import URIRef, BNode, Literal, Namespace, Graph, XSD
from rdflib.namespace import SKOS, RDFS, OWL, FOAF
from django.db.models import Model
from django.http import HttpResponse
import datetime


SKOSXL = Namespace("http://www.w3.org/2008/05/skos-xl#")
DCAT = Namespace('https://www.w3.org/ns/dcat#')
DCT = Namespace('http://purl.org/dc/terms/')

SUPPORTED_RDF_MIMETYPES = {
    'application/rdf+xml',
    'text/n3',
    'text/turtle',
}


class ModelInstanceRef(URIRef):
    __slots__ = ('instance',)

    def __new__(cls, value, base=None):
        if hasattr(value, 'get_rdf_url'):
            url = value.get_rdf_url()
        else:
            url = value.get_absolute_url()
        rt = URIRef.__new__(cls, url, base=base)
        rt.instance = value
        return rt


def DjRef(o):
    if isinstance(o, (Literal, URIRef)):
        return o
    elif isinstance(o, (datetime.datetime, datetime.date)):
        return Literal(o)
    elif isinstance(o, str):
        return Literal(o)
    elif isinstance(o, Model):
        return ModelInstanceRef(o)
    return o


def detect_rdf_request(request):
    '''
    Detects if the user requested rdf and returns a monad
    Returned function takes a callable that receives and rdf graph
    Monad returns an http response with the requested rdf representation
    '''
    mime_type = request.content_type
    rdf = False

    if 'rdf' in request.GET:
        mime_type = request.GET.get('rdf') or 'application/rdf+xml'
        rdf = True
    elif mime_type in SUPPORTED_RDF_MIMETYPES:
        rdf = True
    if rdf:
        def make_rdf_response(f):
            g = Graph()
            f(g)
            s = g.serialize(format=mime_type)
            return HttpResponse(s, content_type=mime_type)
        return make_rdf_response
    return False
