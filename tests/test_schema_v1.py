from __future__ import absolute_import, print_function

import pytest
from boltons.typeutils import issubclass

pytest.importorskip('py2neo_compat.schema_v1',
                    reason='py2neo v1/v2 only')

from py2neo_compat.schema_v1 import (
    _create_constraint,
    _schema_template,
    graph_metadata, schema_constraints,
    schema_indexes, schema_template_subpath,
)


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
def test_create_constraint(neo4j_graph):
    g = neo4j_graph

    assert len(list(schema_constraints(g))) == 0
    assert len(list(schema_indexes(g))) == 0

    _create_constraint(g, 'uniqueness', 'person', 'username')

    assert len(list(schema_constraints(g))) == 1
    assert len(list(schema_indexes(g))) == 1


@pytest.mark.integration
def test_graph_metadata(neo4j_graph_object):
    """Test :func:`graph_metadata`."""
    assert len(graph_metadata(neo4j_graph_object)) > 0
    assert graph_metadata(neo4j_graph_object, 'indexes')\
        .endswith('/schema/index')
