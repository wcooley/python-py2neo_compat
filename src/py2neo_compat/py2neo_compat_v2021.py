"""
Compatibility layer for py2neo v2021
"""
from typing import Optional

from .util import foremost

import py2neo
from py2neo import Graph as Graph
from py2neo import Node as Node
from py2neo import Relationship as Relationship
from py2neo import DatabaseError as DatabaseError
from py2neo import Entity as _Entity

# Monkey-patch py2neo
def _cast_node(*args, **kwargs):
    """Minimally reproduce staticmethod Node.cast

    Reimplement only what we are actually using, for now.
    """
    # Case 0: No args
    if len(args) == 0 and len(kwargs) == 0:
        return Node()
    if len(args) > 0:
        # Case 1: Already a Node
        if isinstance(args[0], Node):
            return args[0]
        # Case 2: Single dictionary
        if isinstance(args[0], dict):
            kwargs = kwargs or {}
            new_args = dict.copy(args[0])
            new_args.update(kwargs)
            return Node(**new_args)
    # Case 3: kwargs only
    else:
        return Node(**kwargs)
node = _cast_node
py2neo.node = _cast_node


rel = Relationship
py2neo.rel = rel

Relationship.reltype = property(lambda s: foremost(s.types()))

from py2neo.data import PropertyDict
py2neo_property_classes = (Node, Relationship, PropertyDict)

from py2neo.cypher import Record
py2neo.Record = Record

# Monkey-patching Entity (parent class of Node & Relationship)

_Entity._id = property(lambda s: s.identity)
_Entity.push = lambda s: s.graph.push(s)
_Entity.pull = lambda s: s.graph.pull(s)
_Entity.exists = lambda s: s.identity is not None

# Monkey-patching Node
def _node_add_labels(node, *args):
    for label in args:
        node.add_label(label)
Node.add_labels = _node_add_labels

def _node_match_outgoing(self, rel_type=None, end_node=None, limit=None):
    return self.graph.match(start_node=self, rel_type=rel_type, end_node=end_node, limit=limit)
Node.match_outgoing = _node_match_outgoing

# Monkey-patching Graph

def _graph_service_uri(self):
    uri = self.service.uri
    if uri.startswith("http") and not uri.endswith("/db/data/"):
        uri += "/db/data/"
    return uri
Graph.uri = property(_graph_service_uri)
Graph.neo4j_version = property(lambda s: s.service.kernel_version)
Graph.node_labels = property(lambda s: s.schema.node_labels)


def _size(graph) -> int:
    """Number of relationships in graph"""
    return foremost(foremost(r.values() for r in
                             cypher_execute(graph,
                                 'START r=rel(*) RETURN count(r)')))
Graph.size = property(_size)


def _order(graph) -> int:
    """Number of nodes in graph"""
    return foremost(foremost(r.values() for r in
                             cypher_execute(graph,
                                 'START n=node(*) RETURN count(n)')))
Graph.order = property(_order)

def graph_find(self, label=None, property_key=None, property_value=None):
    properties = {property_key: property_value} if property_key else {}
    return self.nodes.match(label, **properties)
Graph.find = graph_find

def graph_find_one(self, label=None, property_key=None, property_value=None):
    return self.find(label, property_key, property_value).first()
Graph.find_one = graph_find_one

Graph._orig_create = Graph.create

def graph_create(self, subgraph):
    properties = {}
    if issubclass(type(subgraph), tuple):
        if type(subgraph[-1]) is dict:
            subgraph, properties = subgraph[:-1], subgraph[-1]
        subgraph = Relationship(*subgraph, **properties)
    self._orig_create(subgraph)
    return (subgraph,)

Graph.create = graph_create

Graph._orig_match = Graph.match
def graph_match(
    graph: Graph,
    start_node: Optional[Node] = None,
    rel_type: Optional[str] = None,
    end_node: Optional[Node] = None,
    limit: Optional[int] = None
):
    """Match relationships between two nodes."""
    return graph._orig_match((start_node, end_node), r_type=rel_type, limit=limit)
Graph.match = graph_match


Graph._orig_match_one = Graph.match_one
def graph_match_one(
    graph: Graph,
    start_node: Optional[Node] = None,
    rel_type: Optional[str] = None,
    end_node: Optional[Node] = None
):
    """Match one relationship between two nodes."""
    return foremost(graph.match(start_node=start_node, rel_type=rel_type, end_node=end_node))
Graph.match_one = graph_match_one


# Stand-alone functions


def create_node(
    graph=None,  # type: Optional[py2neo.Graph]
    labels=None,  # type: Optional[Iterable[str]]
    properties=None,  # type: Optional[Mapping[str, Any]]
) -> Node:
    properties = properties or {}
    labels = labels or []
    node = Node(*labels, **properties)
    if graph is not None:
        graph.create(node)
    return node

def cypher_stream(graph, query, **ps):
    return graph.run(query, **ps)

def cypher_execute(graph, query, **ps):
    return list(graph.run(query, **ps))

def update_properties(entity, properties):
    entity.update(properties)

def set_properties(entity, properties):
    entity.clear()
    entity.update(properties)

def delete_rel(rel):
    if rel.graph is None:
        return

    rel.graph.separate(rel)
