#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for :mod:`py2neo_compat.schema`."""

from __future__ import absolute_import, print_function

import pytest  # noqa

# noinspection PyUnresolvedReferences,PyProtectedMember
from py2neo_compat import Graph
from py2neo_compat.schema import \
    create_uniqueness_constraint, \
    create_schema, \
    drop_schema, \
    schema_constraints, \
    schema_indexes, \
    SchemaItem


def test_schema_indexes(sample_graph):
    g = sample_graph
    create_schema(g, schema_map={
        'indexes': [
            SchemaItem(label='thingy', property_key='name')
        ]
    })

    assert [('thingy', ['name'])] == schema_indexes(g)


@pytest.mark.integration
def test_drop_schema(sample_graph):
    """Test the :func:`drop_schema` works."""
    g = sample_graph

    create_schema(g, schema_map={
        'uniqueness_constraints': [
            SchemaItem(label='person', property_key='username'),
            SchemaItem(label='thingy', property_key='name'),
        ],
        'indexes': [
            SchemaItem(label='thingy', property_key='py2neo_ver')
        ]
    })

    # Ensure we're testing a graph with constraints & indexes
    assert len(list(schema_constraints(g))) > 0
    assert len(list(schema_indexes(g))) > 0

    drop_schema(g)

    assert len(list(schema_constraints(g))) == 0
    assert len(list(schema_indexes(g))) == 0


@pytest.mark.integration
def test_create_uniqness_constraint(neo4j_graph):
    g = neo4j_graph

    assert len(list(schema_constraints(g))) == 0
    assert len(list(schema_indexes(g))) == 0

    create_uniqueness_constraint(g, 'person', 'username')

    assert len(list(schema_constraints(g))) == 1
    assert len(list(schema_indexes(g))) == 1


@pytest.mark.integration
def test_create_null_schema(neo4j_graph):
    g = neo4j_graph

    assert len(list(schema_constraints(g))) == 0
    assert len(list(schema_indexes(g))) == 0

    create_schema(g, schema_map={})

    assert len(list(schema_constraints(g))) == 0
    assert len(list(schema_indexes(g))) == 0


@pytest.mark.integration
def test_create_schema(neo4j_graph):
    g = neo4j_graph

    assert len(list(schema_constraints(g))) == 0
    assert len(list(schema_indexes(g))) == 0

    create_schema(g, schema_map={
        'uniqueness_constraints': [
            SchemaItem(label='person', property_key='username'),
            SchemaItem(label='thingy', property_key='name'),
        ],
        'indexes': [
            SchemaItem(label='thingy', property_key='py2neo_ver')
        ]
    })

    assert len(list(schema_constraints(g))) > 0
    assert len(list(schema_indexes(g))) > 0


uniqueness_map = {
        'uniqueness_constraints': [
            SchemaItem(label='thingy', property_key='name'),
        ],
    }

indexes_map = {
        'indexes': [
            SchemaItem(label='thingy', property_key='name'),
        ]
    }


@pytest.mark.parametrize(
    ('schema1', 'schema2'), [
        (indexes_map, indexes_map),
        (indexes_map, uniqueness_map),
        (uniqueness_map, uniqueness_map),
        (uniqueness_map, indexes_map),
    ]
)
@pytest.mark.integration
def test_create_schema_dup_indexes(neo4j_graph, schema1, schema2):
    # type: (Graph, Graph) -> None
    """Creating the same schema twice works as expected."""
    g = neo4j_graph

    create_schema(g, schema_map=schema1)
    create_schema(g, schema_map=schema2)
