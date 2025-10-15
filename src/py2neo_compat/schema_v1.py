#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""py2neo schema"""

from __future__ import absolute_import, print_function

import logging

from six.moves.urllib.parse import urljoin

try:
    # noinspection PyCompatibility,PyUnresolvedReferences
    from typing import (
        Dict,
        NamedTuple,
        Iterator,
        Iterable,
        Optional,
        Tuple,
        List,
        Union,
    )
    OptionalStrBool = Union[str, bool, None]
except ImportError:  # pragma: no cover
    "Module 'typing' is optional for 2.7-compatible types in comments"

# This works for 1.6, 2, 3.1 but not 4b2
from py2neo.packages.httpstream import Resource
from py2neo.packages.httpstream.http import URITemplate

from .py2neo_compat import Graph

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
log.addHandler(logging.NullHandler())


def schema_constraints(graph):
    # type: (Graph) -> Iterable[Tuple[str, List[str], str]]
    """Query iterable list of *all* schema constraints.

    This works around the fact that, in Neo4j 2.3 and :mod:`py2neo` 2.0.8 at
    least, `graph.node_labels` only returns labels used by extant nodes, whereas
    previously it returned all labels, which are needed for clearing the
    constraint schema by iterating over the labels.
    """

    constraint_resource = Resource(graph_metadata(graph, 'constraints'))

    return [(c['label'], c['property_keys'], c['type'])
            for c in constraint_resource.get().content]


def schema_indexes(graph):
    # type: (Graph) -> List[Tuple[str, List[str]]]
    """Query iterable list of *all* schema indexes.

    This works around the fact that, in Neo4j 2.3 and :mod:`py2neo` 2.0.8 at
    least, `graph.node_labels` only returns labels used by extant nodes, whereas
    previously it returned all labels, which are needed for clearing the
    constraint schema by iterating over the labels.
    """
    index_resource = Resource(graph_metadata(graph, 'indexes'))

    return [(n['label'], n['property_keys']) for n in
            index_resource.get().content]


def schema_template_subpath(label='', property_key='', constraint_type=''):
    # type: (OptionalStrBool, OptionalStrBool, OptionalStrBool) -> str
    """Get a string URI template by looking up in a map.

    The content of label and property_key do not matter, provided that `bool`
    accurately reflects the intended absence or presence in the resulting URI.

    Cases:
    * All indexes or constraints (GET):
        e.g., http://localhost:7474/db/data/schema/constraint
    * All indexes or constraints for a given label (GET, POST (index)):
        e.g., http://localhost:7474/db/data/schema/constraint/person
    * A particular index for a label and property key (DELETE (index))
        e.g., http://localhost:7474/db/data/schema/index/{label}/{key}
    * All constraints for a given label and constraint type (GET, POST):
        e.g., http://localhost:7474/db/data/schema/constraint/person/uniqueness
    * A particular constraint for a given label, constraint type and key (DELETE)
    """

    # noinspection PyPep8Naming
    CR = ConditionRecord = NamedTuple('ConditionRecord', [
        ('label', bool),
        ('property_key', bool),
        ('constraint_type', bool),
    ])

    condition_map = {
        CR(label=False, property_key=False, constraint_type=False): '',
        CR(True,        property_key=False, constraint_type=False): '{label}/',

        CR(True,        True,               constraint_type=False):
            '{label}/{property_key}',

        CR(True,        property_key=False, constraint_type=True):
            '{label}/%(constraint_type)s',

        CR(True,        True,               True):
            '{label}/%(constraint_type)s/{property_key}',

    }

    condition_key = CR(bool(label), bool(property_key), bool(constraint_type))

    try:
        template = condition_map[condition_key]
    except KeyError:
        raise ValueError('Invalid params for schema subpath condition_key="%s"'
                         % (condition_key,))

    template = template % {'constraint_type': constraint_type}

    return template


def _schema_template(graph, schema_type, label=None, property_key=None,
                     constraint_type=''):
    """Generate a URITemplate for schema."""

    subpath = schema_template_subpath(label=label,
                                      property_key=property_key,
                                      constraint_type=constraint_type)

    uri = graph_metadata(graph, schema_type)
    uri = urljoin(uri + '/', subpath)
    key_template = URITemplate(uri)

    return key_template


def drop_constraint(graph, constraint_type, label, property_key):
    # type: (Graph, str, str) -> None

    key_template = _schema_template(graph,
                                    schema_type='constraints',
                                    constraint_type=constraint_type,
                                    label=label,
                                    property_key=property_key)

    url_expanded = key_template.expand(label=label, property_key=property_key)
    resource = Resource(url_expanded)

    try:
        resource.delete()
    except Exception:
        log.exception('error deleting constraint'
                      ' type="%s" label="%s" property="%s"',
                      constraint_type, label, property_key)
        raise


def _create_constraint(graph, constraint_type, label, property_key):
    """Create a uniqueness constraint."""
    tpl = _schema_template(graph, 'constraints',
                           label=label, property_key=False,
                           constraint_type=constraint_type)
    resource = Resource(tpl.expand(label=label,
                                   property_key=property_key))
    resource.post({"property_keys": [property_key]})


def graph_metadata(graph, key=None):
    # type: (Graph, Optional[str]) -> Union[Dict, str]
    """Get graph metadata or a key in the metadata."""

    # v1.6 has Graph.__metadata__
    metadata = getattr(graph, '__metadata__', None)
    if metadata is not None:
        metadata = dict(metadata)
    elif hasattr(graph, 'resource'):
        # v2.0 has Graph.resource.metadata
        # noinspection PyUnresolvedReferences
        metadata = graph.resource.metadata
    elif hasattr(graph, '__remote__'):
        metadata = graph.__remote__.metadata

    if key is not None:
        return metadata[key]
    else:
        return metadata
