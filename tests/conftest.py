#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test fixtures & config."""

from __future__ import absolute_import, print_function

import os
import pytest  # noqa
import logging

import py2neo_compat
from py2neo_compat import Graph, py2neo_ver, node, create_node
from py2neo_compat.util import foremost

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
log.addHandler(logging.NullHandler())

pytest.mark.todo = pytest.mark.xfail(reason='TODO', strict=True)

pytest.mark.todo_v1 = pytest.mark.xfail(py2neo_ver==1,
                                        reason='TODO py2neo v1',
                                        strict=True)
pytest.mark.todo_v2 = pytest.mark.xfail(py2neo_ver==2,
                                        reason='TODO py2neo v2',
                                        strict=True)
pytest.mark.todo_v3 = pytest.mark.xfail(py2neo_ver==3,
                                        reason='TODO py2neo v3',
                                        strict=True)
pytest.mark.todo_v4 = pytest.mark.xfail(py2neo_ver==4,
                                        reason='TODO py2neo v4',
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
    py2neo_compat.monkey_patch_py2neo()
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
def sample_graph_and_nodes(neo4j_graph):
    """Sample graph with some nodes."""
    g = neo4j_graph
    assert g.neo4j_version

    node_a = create_node(graph=g, labels=['thingy'],
                         properties={'name': 'a', 'py2neo_ver': py2neo_ver})
    node_b = create_node(graph=g, labels=['thingy'],
                         properties={'name': 'b', 'py2neo_ver': py2neo_ver})

    assert None is not node_a
    assert None is not node_b

    g.create((node_a, 'points_to', node_b))

    assert g.size > 0
    assert g.order > 0

    return g, node_a, node_b


@pytest.fixture
def sample_graph(sample_graph_and_nodes):
    """Sample graph only."""
    return foremost(sample_graph_and_nodes)
