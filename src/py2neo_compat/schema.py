from __future__ import absolute_import, print_function

import logging
from functools import partial

from typing import NamedTuple

from . import Graph, py2neo_compat, py2neo_ver

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
log.addHandler(logging.NullHandler())


if py2neo_ver == 2021:
    from .schema_v2021 import drop_constraint
    from py2neo_compat.schema_v2021 import *
elif py2neo_ver == 2:
    from py2neo_compat.schema_v2 import *
elif py2neo_ver == 1:
    from .schema_v1 import drop_constraint, \
        _create_constraint
    from py2neo_compat.schema_v1 import *

SchemaItem = NamedTuple('SchemaItem', [
    ('label', str),
    ('property_key', str),
])



def create_uniqueness_constraint(graph, label, property_key):
    """Create uniqueness constraint."""
    # type: (Graph, str, str) -> None
    if hasattr(graph.schema, 'create_uniqueness_constraint'):
        graph.schema.create_uniqueness_constraint(label, property_key)
    else:
        _create_constraint(graph, 'uniqueness', label, property_key)


def create_schema(graph, schema_map, ignoredups=True):
    # type: (Graph) -> None
    """Create constraints and indexes.

    :param Graph graph: Instance of :class:`py2neo.Graph`.
    :param dict schema_map: Mapping describing schema where the key is the
        name of the schema type (corresponding with the keys of the `creators`
        dict below), and the values a list of :class:`SchemaItem` instances.

    e.g.:
        'uniqueness_constraints'|'indexes': [
            SchemaItem(label=..., property_key=...),
            ...
        ]
    """

    creators = {
        'uniqueness_constraints': partial(create_uniqueness_constraint, graph),
        'indexes': graph.schema.create_index
    }

    for schema_type, schema_items in schema_map.items():
        schema_creator = creators[schema_type]

        for item in schema_items:
            log.debug('creating schema_type="%s" for label="%s"'
                      ' property_key="%s"',
                      schema_type,
                      item.label,
                      item.property_key)

            try:
                schema_creator(item.label, item.property_key)
            except Exception as excp:
                if not ignoredups:
                    raise

                # We could be more specific with the exception but then we'd
                # have to deal with yet more symbol compatibility, so instead
                # we catch everything and match on the message.
                msg = excp.args[0]

                flag = False
                # import sys
                # print('Comparing msg="%s"' % msg, file=sys.stderr)
                for m in dup_schema_exception_messages:
                    # print('with m="%s"' % m, file=sys.stderr)
                    if m in msg:
                        flag = True
                        break

                if not flag:
                    raise

dup_schema_exception_messages = [
    'Property key already indexed',
    'an index is already created',
    'There already exists an index for label',
    'Conflict',
    'Constraint already exists',
]


def drop_schema(graph):
    # type: (Graph) -> None
    """Drop all constraints and indexes."""
    drop_constraints(graph)
    drop_indexes(graph)


def drop_constraints(graph):
    # type: (Graph) -> None
    """Drop all constraints."""
    constraint_dispatch = {
        'UNIQUENESS': getattr(graph.schema,
                              'drop_uniqueness_constraint',
                              partial(drop_constraint, graph, 'uniqueness')),
    }

    for label, property_keys, type_ in schema_constraints(graph):
        log.debug('dropping schema constraint for label="%s" properties="%s",'
                  ' type="%s"', label, ','.join(property_keys), type_)
        for propkey in property_keys:
            constraint_dispatch[type_](label, propkey)


def drop_indexes(graph):
    # type: (Graph) -> None
    """Drop all schema indexes."""
    for label, property_keys in schema_indexes(graph):
        log.debug('dropping schema index for label="%s" properties="%s"',
                  label, ','.join(property_keys))
        try:
            for property_key in property_keys:
                graph.schema.drop_index(label, property_key)
        except py2neo_compat.ServerError:
            # Usually means it doesn't have the index or
            # otherwise can't do it (e.g., py2neo v1.6)
            log.exception('dropping index label="%s" properties="%s"',
                          label, ','.join(property_keys))
        except Exception:  # FIXME more specific
            log.exception('dropping index label="%s" properties="%s"',
                          label, ','.join(property_keys))
            raise
