"""
Compatibility layer for py2neo v2
"""
from .util import foremost, SimpleNamespace

import py2neo
from py2neo import Graph
from py2neo import Node
from py2neo import Relationship
from py2neo.core import ServerError as DatabaseError
py2neo.DatabaseError = DatabaseError


from py2neo import node
from py2neo import rel

from py2neo import PropertySet, PropertyContainer

py2neo_property_classes = (Node, Relationship, PropertySet, PropertyContainer)

def rel_types(self: py2neo.Relationship):
    return frozenset({self.type})
Relationship.types = rel_types
Relationship.reltype = property(lambda s: s.type)

Relationship.identity = property(lambda s: s._id)
Node.identity = property(lambda s: s._id)

def create_node(
    graph=None,  # type: Optional[py2neo.Graph]
    labels=None,  # type: Optional[Iterable[str]]
    properties=None,  # type: Optional[Mapping[str, Any]]
):
    # type: (...) -> Node
    """Cross-version function to create a node."""
    properties = properties or {}
    labels = labels or []

    new_node = node(*labels, **properties)
    if graph is not None:
        new_node = foremost(graph.create(new_node))
    return new_node

def cypher_stream(graph, query, **params):
    return graph.cypher.stream(query, **params)

def cypher_execute(graph, query, **params):
    return graph.cypher.execute(query, **params)

def update_properties(entity, properties):
    entity.properties.update(properties)

def set_properties(entity, properties):
    entity.properties.replace(properties)
