#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `py2neo_compat.py2neo_compat` package."""

from __future__ import absolute_import, print_function

import operator
import os
import sys

import pytest
import py2neo

from py2neo_compat.util import foremost
from py2neo_compat.py2neo_compat import py2neo_ver


def test_imported_symbols():
    """Test that some essential symbols exist."""
    import py2neo_compat.py2neo_compat as p2n

    assert p2n.Graph
    assert p2n.Node
    assert p2n.Relationship


@pytest.mark.parametrize(
    'symbol', [
        'Graph',
        'Node',
        'Relationship',
        'Record',
        'node',
        'rel',
        'ServerError',
        'ClientError',
        'URI',
    ]
)
def test_import_symbol__all__(symbol):
    """Test symbols in `__all__`."""
    import py2neo_compat.py2neo_compat as p2n

    assert symbol in p2n.__all__
    assert hasattr(p2n, symbol)


@pytest.mark.parametrize(
    ('klass', 'attr'), [
        ('Graph', 'delete_all'),
        ('Graph', 'uri'),
        ('Graph', 'find_one'),
        pytest.param('Graph', 'legacy', marks=pytest.mark.todo_v3),
        pytest.param('Graph', 'resource', marks=pytest.mark.todo_v3),
        pytest.param('Graph', 'cypher', marks=pytest.mark.todo_v3),
        pytest.param('Graph', 'create_unique', marks=pytest.mark.todo_v3),
        ('Node', 'push'),
        ('Node', 'pull'),
        ('Node', 'labels'),
        ('Relationship', 'push'),
        ('Relationship', 'pull'),
    ]
)
def test_monkey_patch(klass, attr):
    """Test that monkey patch installs the expected symbols."""
    import py2neo_compat.py2neo_compat as p2n
    import py2neo

    p2n.monkey_patch_py2neo()

    klass_attr = operator.attrgetter(klass)

    assert klass_attr(py2neo) is not None
    assert klass_attr(p2n) is not None
    assert klass_attr(py2neo) == klass_attr(p2n)
    assert getattr(klass_attr(py2neo), attr) is not None
    assert getattr(klass_attr(p2n), attr) is not None
    assert getattr(klass_attr(py2neo), attr).__doc__ is \
           getattr(klass_attr(p2n), attr).__doc__


@pytest.mark.integration
def test_graph_metadata(neo4j_graph_object):
    """Test :func:`graph_metadata`."""

    from py2neo_compat.py2neo_compat import graph_metadata

    assert len(graph_metadata(neo4j_graph_object)) > 0
    assert graph_metadata(neo4j_graph_object, 'indexes')\
        .endswith('/schema/index')


@pytest.mark.todo_v3
@pytest.mark.integration
def test_graph_delete_all(neo4j_uri):
    # type: (py2neo.Graph) -> None
    """Test :meth:`Graph.delete_all`."""
    import py2neo_compat.py2neo_compat as p2n
    from py2neo_compat.py2neo_compat import Graph, rel, node

    p2n.monkey_patch_py2neo()

    neo4j_graph_object = Graph(neo4j_uri)
    g = neo4j_graph_object
    assert g.neo4j_version

    node_a = foremost(g.create(node({'name': 'a', 'py2neo_ver': py2neo_ver})))
    node_b = foremost(g.create(node({'name': 'b', 'py2neo_ver': py2neo_ver})))

    g.create((node_a, 'points_to', node_b))

    assert g.size > 0
    assert g.order > 0

    assert hasattr(g, 'delete_all')
    g.delete_all()
    assert g.size == 0
    assert g.order == 0
