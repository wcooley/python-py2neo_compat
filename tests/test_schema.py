#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for :mod:`py2neo_compat.schema`."""

from __future__ import absolute_import, print_function

import itertools
import pytest  # noqa

from boltons.typeutils import issubclass

# noinspection PyUnresolvedReferences,PyProtectedMember
from py2neo_compat import Graph
from py2neo_compat.schema import \
    _create_constraint, \
    _schema_template, \
    create_schema, \
    drop_schema, \
    schema_constraints, \
    schema_indexes, \
    schema_template_subpath, \
    SchemaItem


@pytest.mark.integration
def test__schema_template(neo4j_graph_object):
    graph = neo4j_graph_object

    t = _schema_template(graph, schema_type='constraints', label='LEBAL',
                         property_key='YEK', constraint_type='uniqueness')

    assert str(t).endswith('/schema/constraint/{label}/uniqueness/{property_key}')

    assert str(t.expand(label='LEBAL', property_key='YEK')).endswith('/schema/constraint/LEBAL/uniqueness/YEK')


@pytest.mark.parametrize(
    ('given', 'expected'), [
        ({}, ''),
        ({'label': True}, '{label}/'),
        ({'label': 'person',
          'property_key': 'username'},
                '{label}/{property_key}'),

        ({'label': 'person',
          'constraint_type': 'uniqueness'},
                '{label}/uniqueness'),

        ({'label': 'person',
          'property_key': 'username',
          'constraint_type': 'uniqueness'},
                '{label}/uniqueness/{property_key}'),

        ({'property_key': 'foo'}, ValueError),

        ({'constraint_type': 'bar'}, ValueError)
    ]
)
@pytest.mark.unit
def test_schema_template_subpath(given, expected):
    """Ensure schema_template_subpath makes the right URIs."""

    if isinstance(expected, Exception) or issubclass(expected, Exception):
        with pytest.raises(expected):
            schema_template_subpath(**given)
    else:
        assert schema_template_subpath(**given) == expected


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
def test_create_constraint(neo4j_graph):
    g = neo4j_graph

    assert len(list(schema_constraints(g))) == 0
    assert len(list(schema_indexes(g))) == 0

    _create_constraint(g, 'uniqueness', 'person', 'username')

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
