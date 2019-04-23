from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Q, F, QuerySet
from django.db.utils import IntegrityError
from django.utils.text import slugify
from mptt.exceptions import InvalidMove

from pprint import pprint
import rdflib
from rdflib.namespace import SKOS, RDFS, OWL, FOAF

from data_commons.contrib.rdf import DCT, DCAT, SKOSXL
from apps.focus.models import Concept, MappedUri, Label

#Problem: when importing it is often a higher level that implements Concept


TYPE = rdflib.RDF.type

RECOGNIZED_TYPES = [
    SKOS.Concept,
    SKOS.ConceptScheme,
    OWL.Class,
]


RECOGNIZED_SCHEMES = [
    SKOS,
    SKOSXL,
    DCAT,
    RDFS,
    OWL,
    FOAF,
]

#CONSIDER: it would be better to assume a list and optin for single column
LIST_FIELDS = [
    'label',
    'broader',
    'narrower',
    'prefLabel',
    'altLabel',
    'hiddenLabel',
    'scopeNote',
    'subClassOf',
]


class Command(BaseCommand):
    help = "Imports a W3C SKOS (Simple Knowledge Organization System) rdf vocabulary file."

    def add_arguments(self, parser):
        parser.add_argument('--format', dest='format', default=None,
                    help='rdflib format (use n3 for ttl)')
        parser.add_argument('--follow', dest='follow', #TODO does nothing now
                    action='store_const', const=True, default=False,
                    help='follow URIs for resolving concepts')
        parser.add_argument('--rebuild', dest='rebuild',
                    action='store_const', const=True, default=False,
                    help='do not rebuild concept tree')
        parser.add_argument('--allow-moves', dest='allow_moves',
                    action='store_const', const=True, default=False,
                    help='allow for concepts to be moved')
        parser.add_argument('--reset-alt', dest='reset_alt_parents',
                    action='store_const', const=True, default=False,
                    help='reset alternative parents')
        parser.add_argument('--datatype', dest='datatype',
                    action='store_const', const=True, default=False,
                    help='import datatatypes as concepts')
        parser.add_argument('path', type=str, nargs='+')


    def handle(self, *args, **options):
        follow = options['follow']
        g = rdflib.Graph()
        for filepath in options['path']:
            g.load(filepath, format=options.get('format', None))

        #Concept.objects.all().delete()
        if options['rebuild']:
            self.stdout.write(self.style.WARNING("Rebuilding concept tree"))
            try:
                Concept.fix_tree(destructive=True)
            except Exception as error:
                self.stdout.write(self.style.ERROR("Concept tree is unfixable"))
                self.stdout.write(self.style.ERROR(str(error)))
                #Concept.objects.all().delete()
                #QuerySet.delete(Concept.objects.all())
                return
            self.stdout.write(self.style.SUCCESS("Concept tree rebuilt"))
        else:
            check_fix_tree()

        concepts = dict()
        #subject predicate object
        #pprint(list(g))

        if options['datatype']:
            RECOGNIZED_TYPES.append(OWL.DatatypeProperty)

        #identify concepts
        for s, o in g.subject_objects(TYPE): #all type declaration
            if o not in RECOGNIZED_TYPES:
                continue
            if isinstance(s, rdflib.term.URIRef):
                obj = uri_to_dict(g, s)

                if not obj['title']:
                    print('Concept without a title:', s, obj)
                else:
                    concepts[s] = obj

        #compute depths
        def resolve_depth(obj, seen=None):
            if obj.get('parent'):
                if obj['parent'] not in concepts:
                    self.stdout.write(self.style.WARNING("Missing parent: %s" % obj['parent']))
                    obj['parent'] = None
                    return 1

                if seen is None:
                    seen = set()
                seen.add(str(obj))

                if str(concepts[obj['parent']]) in seen:
                    self.stdout.write(self.style.WARNING("Object has cyclic parent: %s" % obj))
                    obj['parent'] = None
                    return 1
                #print('resolve depth:', obj, concepts[obj['parent']])
                return resolve_depth(concepts[obj['parent']], seen) + 1
            else:
                return 1

        for key, val in concepts.items():
            val['depth'] = resolve_depth(val)

        concept_instances = dict()

        #uri -> instance
        def resolve_concept(uri):
            if uri in concept_instances:
                #dont return stale nodes?
                return Concept.objects.get(id=concept_instances[uri].id)
            if uri in RECOGNIZED_TYPES:
                return None #base type
            concept = Concept.objects.filter(mappeduri__uri=str(uri)).first()
            if not concept:
                if uri not in concepts: #implies another is a concept though it may not be stated
                    cobj = uri_to_dict(g, uri)
                    #if one of these failures happen it is usually because it isn't defined here
                    if not cobj:
                        self.stdout.write(self.style.WARNING("Parent not found: %s" % uri))
                        return None
                    if not cobj.get('title', None):
                        self.stdout.write(self.style.WARNING("Concept has no title: %s" % uri))
                        return None
                    concepts[uri] = cobj
                else:
                    cobj = concepts[uri]
                #this means cyclic parents!

                self.stdout.write(self.style.WARNING("Out of order update: %s" % cobj.get('title')))
                return None
                #assert False, "Out of order update"
                concept = mash_concept(uri, cobj)
                #dont return stale nodes?
                concept = Concept.objects.get(id=concept.id)
            return concept

        def mash_concept(uri, cobj):
            #check_fix_tree()
            print("Mash:", uri)
            pprint(cobj)
            #TODO real parent is the one with the most depth
            parent = cobj.get('parent', None)
            if parent:
                parent = resolve_concept(parent)
            mu = MappedUri.objects.filter(uri=str(uri)).first()
            new_concept = False
            if mu:
                concept = mu.concept
            else:
                params = {
                    'slug': slugify(cobj['title']),
                }

                try:
                    #a rose is a rose by any other name
                    if parent:
                        concept = Concept.objects.get(**params)
                    else:
                        concept = Concept.get_root_nodes().get(**params)
                except Concept.DoesNotExist:
                    params['title'] = cobj['title']
                    concept = Concept(**params)
                    new_concept = True

            if not concept.title or mu:
                concept.title = cobj['title']

            if options['reset_alt_parents'] and not new_concept:
                concept.alternative_parents.clear()

            if not new_concept:
                try:
                    concept.get_parent()
                except Concept.DoesNotExist as e:
                    #wtf treebeard?
                    print(e)
                    concept._cached_parent_obj = parent

            if new_concept:
                #check_fix_tree()
                if parent:
                    check_move(parent, concept)
                    #because we may have fixed parent after fetching it
                    parent = Concept.objects.get(id=parent.id)
                    self.stdout.write(self.style.WARNING("Adding concept to parent: '%s' > '%s'" % (parent, concept)))
                    parent.add_child(instance=concept)
                else:
                    self.stdout.write(self.style.WARNING("Adding concept to root '%s'" % concept))
                    Concept.add_root(instance=concept)
            elif parent != concept.get_parent():
                if options['allow_moves']:#TODO prefer the parent with more depth
                    if parent:
                        if concept.get_parent():
                            if parent.is_descendant_of(concept):
                                self.stdout.write(self.style.WARNING("Cannot move concept to parent because parent is a descendant: '%s' > '%s'" % (parent, concept)))
                            elif parent.depth > concept.get_parent().depth:
                                self.stdout.write(self.style.WARNING("Moving existing concept so that: '%s' > '%s'" % (parent, concept)))
                                self.stdout.write(self.style.WARNING("Was: %s" % concept.get_parent()))
                                #hack or else parent is stale/broken
                                #concept._cached_parent_obj = parent
                                #check_fix_tree()
                                check_move(parent, concept)
                                parent = Concept.objects.get(pk=parent.id)
                                concept = Concept.objects.get(pk=concept.id)
                                try:
                                    concept.move(parent, 'sorted-child')
                                except IntegrityError:
                                    check_fix_tree()
                                    concept.move(parent, 'sorted-child')
                                concept = Concept.objects.get(pk=concept.id)
                            else:
                                concept.alternative_parents.add(parent)
                        else:
                            self.stdout.write(self.style.WARNING("Moving existing concept so that: '%s' > '%s'" % (parent, concept)))
                            self.stdout.write(self.style.WARNING("Was: %s" % concept.get_parent()))
                            #check_fix_tree()
                            check_move(parent, concept)
                            parent = Concept.objects.get(pk=parent.id)
                            concept = Concept.objects.get(pk=concept.id)
                            try:
                                concept.move(parent, 'sorted-child')
                            except IntegrityError:
                                check_fix_tree()
                                concept.move(parent, 'sorted-child')
                            concept = Concept.objects.get(pk=concept.id)
                    else:
                        pass #TODO set as root?
                else: #don't move, add to alternative_parents
                    self.stdout.write(self.style.WARNING("%s already has a parent. Adding %s to alternative_parents" % (concept, parent)))
                    concept.alternative_parents.add(parent)
            if 'broader' in cobj:
                #aka alternative parents
                parents = list(filter(bool, map(resolve_concept, cobj['broader'])))
                if parents:
                    concept.alternative_parents.add(*parents)

            if not concept.definition:
                if 'definition' in cobj:
                    concept.definition = cobj['definition']
                elif 'scopeNote' in cobj:
                    #use scopeNote if no definition
                    for note in cobj['scopeNote']:
                        lang = getattr(note, 'language', None)
                        if lang in ('en', None):
                            concept.definition = str(note)
                            break
                elif 'comment' in cobj:
                    concept.definition = cobj['comment']

            if 'example' in cobj and not concept.example:
                concept.example = cobj['example']

            if 'topConceptOf' in cobj:
                #defines entry point
                pass

            #TODO owl:sameAs, skos:exactMatch, skos:closeMatch
            #TODO skos:relatedMatch, rdfs:seeAlso

            #cobj['disjointWith'] # is not of
            #TODO cobj['equivalentClass'] #exactMatch

            concept.save()
            #Concept.fix_tree() #wtf treebeard?
            #assert_tree()
            concept_instances[uri] = concept

            if not mu:
                mu = MappedUri(uri=str(uri), concept=concept)
                mu.save()
            if not mu.pk:
                mu.save()

            if new_concept:
                self.stdout.write(self.style.SUCCESS("Concept created: %s" % concept))
            else:
                self.stdout.write(self.style.SUCCESS("Concept synced: %s" % concept))
            return concept

        def mash_concept_labels(uri, cobj):
            concept = Concept.objects.get(pk=concept_instances[uri].pk)
            scheme = concept.get_root()

            def check_label(label):
                lc = getattr(label, 'language', 'en')
                #any label that exists in our scheme but does not belong to us
                return Label.objects.filter(
                    label=label, scheme=scheme, language_code=lc
                ).exclude(concept=concept).exists()

            def create_label(label, usage):
                if check_label(label):
                    self.stdout.write(self.style.WARNING("Duplicate label '%s' from: %s" % (label, uri)))
                    return
                lc = getattr(label, 'language', 'en') or 'en' #getattr may return None
                return Label.objects.get_or_create(label=label, concept=concept, language_code=lc, usage=usage)

            if 'narrower' in cobj:
                #add children
                for child in filter(bool, map(resolve_concept, cobj['narrower'])):
                    try:
                        child.move(concept, 'sorted-child')
                    except IntegrityError as error:
                        self.stdout.write(self.style.ERROR("Could not make %s child of %s" % (child, concept)))
                        self.stdout.write(self.style.ERROR(str(error)))

            if 'altLabel' in cobj:
                for al in cobj['altLabel']:
                    create_label(al, 'a')

            if 'hiddenLabel' in cobj:
                for al in cobj['hiddenLabel']:
                    create_label(al, 'h')

            if 'prefLabel' in cobj:
                for pl in cobj['prefLabel']:
                    create_label(pl, 'p')

            self.stdout.write(self.style.SUCCESS("Concept labels synced: %s" % concept))
            return concept


        print_concept_tree(concepts)
        #process top level concepts first
        breadth_first_concepts = sorted(list(concepts.items()), key=lambda kv: kv[1]['depth'])
        for k, c in breadth_first_concepts :
            try:
                mash_concept(k, c)
            except Exception as error:
                print(error)
                raise
                self.stdout.write(self.style.ERROR(str(error)))
                concepts.pop(k)

        list(map(lambda x: mash_concept_labels(*x), list(concepts.items())))

        if options['rebuild']:
            Concept.fix_tree(destructive=True)
        else:
            check_fix_tree()

        self.stdout.write(self.style.SUCCESS("Concepts synced"))


def uri_to_dict(g, uri):
    concept = g.resource(uri)

    obj = dict()
    obj['title'] = concept.value(FOAF.name)
    for p, o in concept.predicate_objects():
        if isinstance(o, rdflib.resource.Resource):
            o = o.identifier

        p = p.identifier
        #print(p,o)

        if any(map(lambda x: p.startswith(str(x)), RECOGNIZED_SCHEMES)):
            if isinstance(o, rdflib.term.Literal):
                o = o#._value
            if isinstance(o, rdflib.term.BNode):
                continue #ignore blank nodes
            if '#' in p:
                attr = p.split('#')[-1]
            else:
                attr = p.split('/')[-1]
            if attr in LIST_FIELDS:
                obj.setdefault(attr, []).append(o)
            else:
                obj[attr] = o

    #resolve parent uri
    if 'subClassOf' in obj:
        parents = obj.pop('subClassOf')
        if len(parents) > 1: #our picks must be deterministic
            parents.sort(key=str)
        if 'broader' in obj:
            obj['broader'] = parents + obj['broader']
        else:
            obj['broader'] = parents

    if 'broader' in obj:
        #select parent from broader
        obj['parent'] = obj['broader'].pop(0)

    #TODO if title > 50 chars, pick a smaller alt label for title

    if not obj['title']:
        if 'prefLabel' in obj:
            for pl in obj['prefLabel']:
                if len(pl) > 50:
                    continue
                lang = getattr(pl, 'language', None)
                if lang in ('en', 'en-US', None):
                    obj['title'] = pl
        elif 'label' in obj:
            for pl in obj['label']:
                if len(pl) > 50:
                    continue
                lang = getattr(pl, 'language', None)
                if lang in ('en', 'en-US', None):
                    obj['title'] = pl

    return obj


def print_concept_tree(concepts):
    concepts = {k: dict(v) for k, v in concepts.items()}
    tree = list()
    for k, v in concepts.items():
        if v.get('parent'):
            v['parent'] = concepts[v['parent']]
            v['parent'].setdefault('children', []).append(v)
        else:
            tree.append(v)
        v.pop('parent', None)
    pprint(tree)


def check_move(parent, child):
    parent = Concept.objects.get(id=parent.id)
    if not parent.is_leaf() and not parent.get_last_child():
        parent.numchild = parent.get_children().count()
        parent.save()
        #I hope there arent any orphans...
        #check_fix_tree()

def check_fix_tree():
    probs = Concept.find_problems()
    if probs[2]:
        fix_orphans(probs[2])
    if probs[4]:
        Concept.fix_tree()
    if any(probs):
        assert_tree()

def assert_tree():
    probs = Concept.find_problems()
    assert not any(probs), str(probs)


def fix_orphans(orphans):
    for orphan_id in orphans:
        concept = Concept.objects.get(id=orphan_id)
        print('Orphan:', concept)
        parent = None
        path = concept.path
        while not parent and path:
            path = path[:-4]
            parent = Concept.objects.filter(path=path).first()
        if parent:
            concept.move(parent, 'sorted-child')
        else:
            print('cannot resolve parent for', concept)
            pass
