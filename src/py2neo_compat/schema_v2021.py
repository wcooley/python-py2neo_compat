from typing import Any

from . import Graph


def schema_constraints(graph: Graph) -> list[tuple[str, list[str], list[Any]]]:
    return [
        (l, graph.schema.get_uniqueness_constraints(l), 'UNIQUENESS')
        for l in graph.schema.node_labels
        if graph.schema.get_uniqueness_constraints(l)
    ]


def schema_indexes(graph: Graph) -> list[tuple[str, list[str]]]:
    return [
        (labels, list(properties))
        for labels in graph.schema.node_labels
        for properties in graph.schema.get_indexes(labels)
    ]


def drop_constraint(
    graph: Graph, constraint_type: str, label: str, property_key: str
) -> None:
    dispatch = {
        'uniqueness': graph.schema.drop_uniqueness_constraint,
    }
    dispatch[constraint_type](label, property_key)
