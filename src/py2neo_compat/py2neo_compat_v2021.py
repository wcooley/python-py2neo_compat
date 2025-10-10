"""
Compatibility layer for py2neo v2021
"""
from .util import foremost, SimpleNamespace

import py2neo
from py2neo import Graph
from py2neo import Node
from py2neo import Relationship
from py2neo import DatabaseError
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

# def _cast_rel(*args, **kwargs):
#     # Case 1: (Node, reltype, Node)
#     if len(args) in 3:


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

# Monkey-patching Graph

Graph.uri = property(lambda s: s.service.uri.uri)
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


def graph_find_one(self, label, property_key, property_value):
    return self.nodes.match(label, **{property_key: property_value}).first()

Graph.find_one = graph_find_one

Graph._orig_create = Graph.create

def graph_create(self, subgraph):
    if issubclass(type(subgraph), tuple):
        subgraph = Relationship(*subgraph)
    self._orig_create(subgraph)
    return (subgraph,)

Graph.create = graph_create


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
