# -*- coding: utf-8 -*-

"""Main module."""

from __future__ import absolute_import, print_function

import logging

try:
    # noinspection PyUnresolvedReferences
    from typing import (
        Any, Dict, List, Mapping, NamedTuple, Optional,
        Union, Tuple, Iterable,  # noqa
    )
except ImportError:  # pragma: no cover
    """Module :mod:`typing` not required for Py27-compatible type comments."""


import py2neo

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
log.addHandler(logging.NullHandler())


if py2neo.__version__.startswith('1.6'):
    py2neo_ver = 1
    from .py2neo_compat_v1 import *

elif py2neo.__version__.startswith('2.0'):
    py2neo_ver = 2
    from .py2neo_compat_v2 import *

elif py2neo.__version__.startswith('2021'):  # pragma: no cover
    py2neo_ver = 2021
    from .py2neo_compat_v2021 import *

else:  # pragma: no cover
    raise NotImplementedError("py2neo %s not supported" % py2neo.__version__)


if False:  # Trick PyCharm into believing that these exist
    Graph = py2neo.Graph
    Node = py2neo.Node
    Relationship = py2neo.Relationship
    Resource = py2neo.Resource
    rel = py2neo.rel
    node = py2neo.node


def monkey_patch_py2neo():
    # type: () -> None
    pass


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


def py2neo_entity_to_dict(entity):
    # type: (Union[Node,Relationship,PropertySet]) -> Dict[str, Any]
    """Convert an "entity" to a `dict`.

    All three major versions are incompatible with how to get a dict
    from the properties of an entity:

    * 1.6 only needs get_properties() (but dict() doesn't hurt)
    * 2 requires both get_properties and dict()
    * 3 only needs dict() and has no get_properties

    Catching :class:`AttributeError` also allows this to work a PropertySet,
    which is the output of `get_properties()` on 2.
    """
    assert isinstance(entity, py2neo_property_classes)

    try:
        # noinspection PyUnresolvedReferences
        entity = entity.get_properties()
    except AttributeError:
        pass
    finally:
        entity = dict(entity)
    return entity

to_dict = py2neo_entity_to_dict

# Attach `to_dict` to base classes for Node/Relationship
for cls in py2neo_property_classes:
    cls.to_dict = to_dict


def create_unique_rel(
    graph, start_node, rel_type, end_node, prop_key=None, prop_val=None
):
    # type: (Graph, Node, str, Node, Optional[str], Optional[Any]) -> Relationship
    """Get or create a unique relationship.

    py2neo 1.6 has similar functionality but not 2.0

    :param graph: Graph session/connection.
    :type graph: py2neo.Graph
    :param start_node: Head node of relationship.
    :type start_node: py2neo.Node
    :param rel_type: Relationship type.
    :type rel_type: str
    :param end_node: Tail node of relationship.
    :type end_node: py2neo.Node
    :param prop_key: (optional) Property key to identify relationship.
    :type prop_key: str
    :param prop_val: (optional) Property value to identify relationship.
    :type prop_val: str

    :return: The pre-existing or newly-created Relationship object.
    :rtype: py2neo.Relationship
    """
    params = {'start_id': start_node._id, 'end_id': end_node._id}

    if prop_key and prop_val is not None:
        # language=cypher
        query = """
            MATCH (start_node), (end_node)
            WHERE ID(start_node)={start_id}
              AND ID(end_node)={end_id}
            CREATE UNIQUE (start_node)-[r:`%s` {`%s`: {prop_val}}]->(end_node)
            RETURN r
        """ % (rel_type, prop_key)
        params['prop_val'] = prop_val

    else:
        # language=cypher
        query = (
            """
            MATCH (start_node), (end_node)
            WHERE ID(start_node)={start_id}
              AND ID(end_node)={end_id}
            CREATE UNIQUE (start_node)-[r:`%s`]->(end_node)
            RETURN r
        """
            % rel_type
        )

    for row in cypher_stream(graph, query, **params):
        return row['r']
