#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `py2neo_compat.py2neo_compat` package."""

from __future__ import absolute_import, print_function

import inspect
import operator
import os
import sys

import pytest
import py2neo
import six

from py2neo_compat.util import foremost
from py2neo_compat import (
    Node,
    Relationship,
    create_node,
    create_unique_rel,
    cypher_execute,
    cypher_stream,
    graph_metadata,
    node,
    py2neo_ver,
    rel,
    to_dict,
)
import py2neo_compat


def test_imported_symbols():
    """Test that some essential symbols exist."""

    assert py2neo_compat.Graph
    assert py2neo_compat.Node
    assert py2neo_compat.Relationship


@pytest.mark.parametrize(
    'symbol', [
        'Graph',
        'Node',
        'Relationship',
        # 'Record',
        'create_node',
        'create_node',
        'cypher_execute',
        'cypher_stream',
        # 'node',
        # 'rel',
        # 'ServerError',
        # 'ClientError',
        # 'URI',
    ]
)
def test_import_symbol__all__(symbol):
    """Test symbols in `__all__`."""
    # assert symbol in py2neo_compat.__all__
    assert getattr(py2neo_compat, symbol)
    # assert getattr(py2neo, symbol)


@pytest.mark.parametrize(
    ('klass', 'attr'), [
        ('Graph', 'delete_all'),
        ('Graph', 'uri'),
        ('Graph', 'find_one'),
        ('Node', 'push'),
        ('Node', 'pull'),
        ('Node', 'labels'),
        ('Relationship', 'push'),
        ('Relationship', 'pull'),
    ]
)
def test_monkey_patch_classes(klass, attr):
    """Test that monkey patch installs the expected symbols."""

    py2neo_compat.monkey_patch_py2neo()

    klass_in_py2neo = getattr(py2neo, klass)
    attr_in_py2neo = getattr(klass_in_py2neo, attr)
    klass_in_py2neo_compat = getattr(py2neo_compat, klass)
    attr_in_py2neo_compat = getattr(klass_in_py2neo_compat, attr)

    assert klass_in_py2neo is not None
    assert klass_in_py2neo_compat is not None
    assert klass_in_py2neo is klass_in_py2neo_compat
    assert attr_in_py2neo is not None
    assert attr_in_py2neo_compat is not None
    if six.PY2 and inspect.ismethod(attr_in_py2neo):
        assert repr(attr_in_py2neo) == repr(attr_in_py2neo_compat)
    else:
        assert attr_in_py2neo is attr_in_py2neo_compat

    assert attr_in_py2neo.__doc__ is attr_in_py2neo_compat.__doc__


@pytest.mark.todo_v2021
@pytest.mark.integration
def test_graph_metadata(neo4j_graph_object):
    """Test :func:`graph_metadata`."""
    assert len(graph_metadata(neo4j_graph_object)) > 0
    assert graph_metadata(neo4j_graph_object, 'indexes')\
        .endswith('/schema/index')


@pytest.mark.todo_v3
@pytest.mark.integration
def test_graph_delete_all(sample_graph):
    # type: (py2neo.Graph) -> None
    """Test :meth:`Graph.delete_all`."""

    py2neo_compat.monkey_patch_py2neo()

    g = sample_graph

    assert g.size > 0
    assert g.order > 0

    assert hasattr(g, 'delete_all')

    g.delete_all()

    assert g.size == 0
    assert g.order == 0


@pytest.mark.integration
@pytest.mark.parametrize(('labels', 'properties'), [
    (('restauranteur',), {'name': 'Alice'}),        # Label, property
    ((), {}),                                       # Empty iterable, empty map
    (None, None),                                   # Nada, Nada
    ({'person'}, {}),                               # Label, empty map
    ([], {'name': 'Alice'}),                        # Empty iterable, property
])
def test_create_node(neo4j_graph, labels, properties):
    """Test :func:`~py2neo_compat.create_node`."""

    node = create_node(graph=neo4j_graph, labels=labels, properties=properties)
    assert node is not None
    assert node.labels == (set(labels) if labels else set())
    assert to_dict(node) == (dict(properties) if properties else {})


@pytest.mark.integration
def test_graph_create_can_create_relationship(neo4j_graph):
    # type: (Graph) -> None

    def _assert_alice_knows_bob(alice, bob, knows):
        assert isinstance(alice, Node)
        assert isinstance(bob, Node)
        assert isinstance(knows, Relationship)

        # Remember Alice? This song's about Alice.
        assert alice['name'] == 'Alice'
        assert bob['name'] == 'Bob'
        assert knows.start_node == alice
        assert knows.end_node == bob
        assert knows['since'] == '2006'

    g = neo4j_graph
    alice = create_node(g, properties={'name': 'Alice'})
    bob = create_node(g, properties={'name': 'Bob'})

    knows_rel = py2neo.Relationship(alice, 'KNOWS', bob, **{'since': '2006'})
    create_result = g.create(knows_rel)
    assert create_result is not None

    _assert_alice_knows_bob(alice, bob, knows_rel)

    del alice, bob, knows_rel

    alice, knows, bob = foremost(cypher_execute(g, """
        MATCH (n1{name:"Alice"})-[r:KNOWS]->(n2{name:"Bob"})
        RETURN n1, r, n2
        """))

    _assert_alice_knows_bob(alice, bob, knows)


@pytest.mark.unit
def test_legacy_node_constructor(neo4j_graph):
    g = neo4j_graph
    orig_size, orig_order = (g.size, g.order)

    new_node0 = node()
    assert isinstance(new_node0, Node)
    assert new_node0.labels == set()
    assert new_node0.to_dict() == {}

    new_node1 = Node('foo', bar='baz')
    assert new_node1 is node(new_node1)
    assert new_node1.labels == {'foo'}
    assert new_node1.to_dict() == {'bar': 'baz'}

    new_node2 = node({'foo': 'bar'})
    assert isinstance(new_node2, Node)
    assert new_node2.to_dict()['foo'] == 'bar'
    assert new_node2.labels == set()

    new_node3 = node(foo='bar')
    assert isinstance(new_node3, Node)
    assert new_node3.to_dict()['foo'] == 'bar'
    assert new_node3.labels == set()

    # Ensure we didn't actually create anything
    assert (g.size, g.order) == (orig_size, orig_order)


@pytest.mark.unit
def test_legacy_rel_constructor(sample_graph_and_nodes):
    g, node_a, node_b = sample_graph_and_nodes

    orig_size, orig_order = (g.size, g.order)

    new_rel = rel(node_b, 'back_to', node_a)

    assert isinstance(new_rel, Relationship)

    # Ensure we didn't actually create anything
    assert (g.size, g.order) == (orig_size, orig_order)


@pytest.mark.integration
def test_graph_create_can_create_node(neo4j_graph):
    g = neo4j_graph
    orig_size, orig_order = (g.size, g.order)

    create_result = g.create(node({'foo': 'bar'}))
    new_node = foremost(create_result)
    assert isinstance(new_node, Node)
    assert new_node.labels == set()

    # Ensure new node in DB
    assert (g.order, g.size) == (orig_order+1, orig_size)


@pytest.mark.integration
def test_graph_create_can_create_relationship_tuple(sample_graph_and_nodes):
    """`Graph.create` can create relationship from tuple (Node, reltype, Node)"""
    g, node_a, node_b = sample_graph_and_nodes
    orig_size, orig_order = (g.size, g.order)

    hungry_for = foremost(g.create((node_a, 'hungry_for', node_b)))

    assert hungry_for.reltype == 'hungry_for'
    assert hungry_for.start_node == node_a
    assert hungry_for.end_node == node_b

    assert (g.order, g.size) == (orig_order, orig_size+1)


@pytest.mark.integration
def test_can_create_empty_node(neo4j_graph):
    """Test :func:`~py2neo_compat.create_node` with an empty node."""
    empty = create_node(graph=neo4j_graph)
    assert empty is not None
    assert empty.labels == set()
    assert empty.to_dict() == {}


@pytest.mark.integration
def test_can_get_graph_from_node(neo4j_graph):
    new_node = create_node(graph=neo4j_graph)
    assert new_node is not None
    assert new_node.graph == neo4j_graph


@pytest.mark.integration
def test_update_properties(sample_graph_and_nodes):
    """Ensure :func:`py2neo_compat.update_properties` works."""
    g, node_a, _ = sample_graph_and_nodes

    assert 'foo' not in node_a

    py2neo_compat.update_properties(node_a, {'foo': 'bar'})
    node_a.push()

    try:
        node_a.cache.clear()
    except AttributeError:
        pass
    node_a2 = foremost(cypher_execute(g, 'MATCH (n:thingy {name: "a"}) RETURN n'))['n']
    assert id(node_a) != id(node_a2)

    assert 'foo' in node_a2
    assert 'bar' == node_a2['foo']


@pytest.mark.integration
def test_graph_cypher_execute(sample_graph):
    # type: (py2neo.Graph) -> None
    """Ensure :meth:`Graph.cypher.execute` works."""

    r = cypher_execute(sample_graph, """
        MATCH (head)-[points_to:points_to]->(tail)
        RETURN head, points_to, tail
    """)

    assert 1 == len(r)


@pytest.mark.integration
def test_graph_cypher_stream(sample_graph):
    # type: (py2neo.Graph) -> None
    """Ensure :meth:`Graph.cypher.stream` works."""

    r = cypher_stream(sample_graph, """
        MATCH (head)-[points_to:points_to]->(tail)
        RETURN head, points_to, tail
    """)

    assert 1 == len(list(r))


@pytest.mark.integration
def test_create_unique_rel(sample_graph_and_nodes):
    g, node_a, node_b = sample_graph_and_nodes

    ur = create_unique_rel(g, node_a, 'new_rel', node_b)
    assert ur.start_node == node_a
    assert ur.end_node == node_b
    assert ur.reltype == 'new_rel'


@pytest.mark.integration
def test_create_unique_rel_dup_rel(sample_graph):
    g = sample_graph
    r = foremost(cypher_execute(g, """
        MATCH (head)-[points_to:points_to]->(tail)
        RETURN head, points_to, tail
    """))
    points_to1 = r['points_to']
    head = r['head']
    tail = r['tail']
    assert isinstance(points_to1, Relationship)
    assert points_to1._id is not None

    points_to2 = create_unique_rel(g, head, 'points_to', tail)

    assert points_to2 == points_to1

    points_to3 = create_unique_rel(g, head, 'points_to', tail)

    assert points_to3 == points_to1 == points_to2




