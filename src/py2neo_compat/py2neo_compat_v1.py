"""
Compatibility layer for py2neo v1
"""
from .util import foremost

import py2neo
from py2neo.neo4j import GraphDatabaseService as Graph
from py2neo.neo4j import Node
from py2neo.neo4j import Relationship
from py2neo.neo4j import ServerError as DatabaseError
py2neo.DatabaseError = DatabaseError

from py2neo.neo4j import CypherQuery as _CypherQuery

from py2neo import node
from py2neo import rel

py2neo_property_classes = (Node, Relationship)

# py2neo 1.6 did everything eagerly; 2.0 requires explicit sync
Node.push = Node.refresh
Node.pull = Node.refresh
# noinspection PyPropertyAccess
Node.labels = property(lambda s: s.get_labels())
Relationship.push = Relationship.refresh
Relationship.pull = Relationship.refresh

Graph.find_one = lambda s, *args, **kws: foremost(s.find(*args, **kws))
Graph.delete_all = Graph.clear
Graph.uri = Graph.__uri__
Graph.resource = property(lambda s: s._resource)


def create_node(
    graph=None,  # type: Optional[py2neo.Graph]
    labels=None,  # type: Optional[Iterable[str]]
    properties=None,  # type: Optional[Mapping[str, Any]]
):
    # type: (...) -> Node
    """Cross-version function to create a node."""
    properties = properties or {}

    if labels and graph is None:
        raise TypeError('Parameter "graph" is required for py2neo v1 with'
                        ' labels')

    new_node = node(properties)
    if graph is not None:
        new_node = foremost(graph.create(new_node))
    if labels:
        new_node.add_labels(*labels)
    return node


def cypher_execute(graph, query, **params):
    return _CypherQuery(graph, query).execute(**params)

def cypher_stream(graph, query, **params):
    return _CypherQuery(graph, query).stream(**params)

def update_properties(entity, properties):
    entity.update_properties(properties)

def set_properties(entity, properties):
    entity.set_properties(properties)
