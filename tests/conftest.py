
"""Test fixtures & config for :mod:`py2neo_compat`."""

import logging
import os
from pathlib import Path

import py2neo
import pytest

from py2neo_compat import Graph, Node, create_node, py2neo_ver
from py2neo_compat.util import foremost

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
log.addHandler(logging.NullHandler())


def pytest_report_header(config, start_path: Path):
    """Add versions & config info to test output on terminal."""
    lines = []

    if 'NEO4J_URI' in os.environ:
        lines.append(f'Neo4J URI: {os.environ["NEO4J_URI"]}')

    lines.append(f'py2neo: {py2neo.__version__}')

    return lines


@pytest.fixture(scope='session', autouse=True)
def logging_config():
    logging.getLogger('py2neo').setLevel(logging.WARNING)


@pytest.fixture(scope='session')
def neo4j_uri() -> str:
    """Neo4J URI.  Set env NEO4J_URI or override fixture to change."""
    return os.environ.get('NEO4J_URI', 'http://localhost:7474/db/data/')


# noinspection PyShadowingNames
@pytest.fixture
def neo4j_graph_object(neo4j_uri: str) -> Graph:
    """Create a Graph object from a URI."""
    graph = Graph(neo4j_uri)
    # This forces communication with the server, so it serves as an
    # availability check so we can abort earlier.
    log.info('neo4j_uri="%s" version="%s"', neo4j_uri, graph.neo4j_version)
    return graph


# noinspection PyShadowingNames
@pytest.fixture
def neo4j_graph_schemaless(neo4j_graph_object: Graph) -> Graph:
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
def neo4j_graph_empty(neo4j_graph_object: Graph) -> Graph:
    """Graph instance with no nodes or relationships."""
    graph = neo4j_graph_object
    graph.delete_all()
    return graph


# noinspection PyShadowingNames,PyUnusedLocal
@pytest.fixture
def neo4j_graph(neo4j_graph_schemaless: Graph, neo4j_graph_empty: Graph) -> Graph:
    """Test Neo4j graph fixture."""
    return neo4j_graph_schemaless


# noinspection PyShadowingNames
@pytest.fixture
def sample_graph_and_nodes(neo4j_graph: Graph) -> tuple[Graph, Node, Node]:
    """Sample graph with some nodes."""
    g = neo4j_graph
    assert g.neo4j_version

    node_a = create_node(
        graph=g,
        labels=['thingy'],
        properties={'name': 'a', 'py2neo_ver': py2neo_ver},
    )
    node_b = create_node(
        graph=g,
        labels=['thingy'],
        properties={'name': 'b', 'py2neo_ver': py2neo_ver},
    )

    assert None is not node_a
    assert None is not node_b

    rel = foremost(g.create((node_a, 'points_to', node_b)))
    rel['sample'] = 'property'
    rel.push()

    assert g.size > 0
    assert g.order > 0

    return g, node_a, node_b


@pytest.fixture
def sample_graph(sample_graph_and_nodes: tuple[Graph, Node, Node]) -> Graph:
    """Sample graph only."""
    return foremost(sample_graph_and_nodes)
