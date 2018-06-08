#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test fixtures & config."""

from __future__ import absolute_import, print_function

import os
import pytest  # noqa
import logging

from py2neo_compat import Graph, py2neo_ver, node
from py2neo_compat.util import foremost

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
log.addHandler(logging.NullHandler())

pytest.mark.todo_v3 = pytest.mark.xfail(py2neo_ver==3,
                                        reason='TODO py2neo v3',
                                        strict=True)


@pytest.fixture(scope='session', autouse=True)
def logging_config():
    logging.getLogger('py2neo').setLevel(logging.WARNING)


@pytest.fixture(scope='session')
def neo4j_uri():
    # type: () -> str
    """Neo4J URI.  Set env NEO4J_URI or override fixture to change."""
    return os.environ.get('NEO4J_URI', 'http://localhost:7474/db/data/')


# noinspection PyShadowingNames
@pytest.fixture
def neo4j_graph_object(neo4j_uri):
    # type: (str) -> Graph
    """Create a Graph object from a URI."""
    graph = Graph(neo4j_uri)
    # This forces communication with the server, so it serves as an
    # availability check so we can abort earlier.
    log.info('neo4j_uri="%s" version="%s"', neo4j_uri, graph.neo4j_version)
    return graph


# noinspection PyShadowingNames
@pytest.fixture
def neo4j_graph_schemaless(neo4j_graph_object):
    # type: (Graph) -> Graph
    """Graph instance cleared of all schema."""
    graph = neo4j_graph_object
    try:
        # noinspection PyUnresolvedReferences
        from py2neo_compat.schema import drop_schema
    except ImportError:
        pytest.fail('Unable to import `drop_schema`.')

    drop_schema(graph)
    return graph


# noinspection PyShadowingNames
@pytest.fixture
def neo4j_graph_empty(neo4j_graph_object):
    # type: (Graph) -> Graph
    """Graph instance with no nodes or relationships."""
    graph = neo4j_graph_object
    graph.delete_all()
    return graph


# noinspection PyShadowingNames,PyUnusedLocal
@pytest.fixture
def neo4j_graph(neo4j_graph_schemaless, neo4j_graph_empty):
    # type: (Graph, Graph) -> Graph
    """Test Neo4j graph fixture."""
    return neo4j_graph_schemaless


# noinspection PyShadowingNames
@pytest.fixture
def sample_graph(neo4j_graph):
    """Sample graph with some data."""
    g = neo4j_graph
    assert g.neo4j_version

    node_a = foremost(g.create(node({'name': 'a', 'py2neo_ver': py2neo_ver})))
    node_b = foremost(g.create(node({'name': 'b', 'py2neo_ver': py2neo_ver})))

    g.create((node_a, 'points_to', node_b))

    assert g.size > 0
    assert g.order > 0

    return g

