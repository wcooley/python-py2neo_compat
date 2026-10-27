"""Main module."""

import logging
from collections.abc import Iterable, Mapping
from typing import Any

import py2neo
from py2neo import (
    Graph as Graph,
)
from py2neo import (
    Node as Node,
)
from py2neo import (
    Relationship as Relationship,
)

if py2neo.__version__.startswith('2021'):
    py2neo_ver = 2021
    from .py2neo_compat_v2021 import *

else:
    raise NotImplementedError('py2neo %s not supported' % py2neo.__version__)


log = logging.getLogger(__name__)  # pylint: disable=invalid-name
log.addHandler(logging.NullHandler())


def monkey_patch_py2neo() -> None:
    raise DeprecationWarning('monkey_patch_py2neo')


def py2neo_entity_to_dict(
    self: Node | Relationship,
) -> dict[str, Any]:
    """Convert an "entity" to a `dict`.
    """
    assert isinstance(self, py2neo_property_classes)
    return dict(self)

to_dict = py2neo_entity_to_dict

# Attach `to_dict` to base classes for Node/Relationship
for cls in py2neo_property_classes:
    cls.to_dict = to_dict


def create_unique_rel(
    graph: Graph,
    start_node: Node,
    rel_type: str,
    end_node: Node,
    prop_key: str | None = None,
    prop_val: Any | None = None,
):
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
