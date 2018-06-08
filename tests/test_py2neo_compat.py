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
    create_node,
    graph_metadata,
    Node,
    py2neo_ver,
    Relationship,
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
    # assert symbol in py2neo_compat.__all__
    assert getattr(py2neo_compat, symbol)
    # assert getattr(py2neo, symbol)


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


def test_monkey_patch_modules():
    """Test that monkey patch makes expected symbols available."""

    py2neo_compat.monkey_patch_py2neo()

    assert sys.modules['py2neo.legacy']
    assert py2neo.legacy is not None
    assert py2neo.legacy.Index is not None

    assert sys.modules['py2neo.batch']
    assert py2neo.batch is not None
    assert py2neo.batch.WriteBatch is not None


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


@pytest.mark.todo_v3
@pytest.mark.integration
def test_graph_cypher_execute(sample_graph):
    # type: (py2neo.Graph) -> None
    """Ensure :meth:`Graph.cypher.execute` works."""
    g = sample_graph

    r = g.cypher.execute("""
        MATCH (head)-[points_to:points_to]->(tail)
        RETURN head, points_to, tail 
    """)

    assert 1 == len(r)


@pytest.mark.todo_v3
@pytest.mark.integration
def test_graph_cypher_stream(sample_graph):
    # type: (py2neo.Graph) -> None
    """Ensure :meth:`Graph.cypher.stream` works."""
    g = sample_graph

    r = g.cypher.stream("""
        MATCH (head)-[points_to:points_to]->(tail)
        RETURN head, points_to, tail 
    """)

    assert 1 == len(list(r))
