from collections import namedtuple

from networkx import Graph
from sqlalchemy import inspect, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from dataclasses import dataclass

import typing

@dataclass(frozen=True)
class Node:
    table:str
    primary_key:typing.Any

    data:tuple[tuple[typing.Any, typing.Any]] = ()

    def str(self):
        """table.primary_key"""
        return f"{self.table}.{str(self.primary_key)}"

    def str_data(self, max_row_length=25, max_rows=7):
        """Convert addtional data to string for plotly, using <br> for newlines."""
        if self.data is None:
            return "<br>(no data)"
        s = '<br>'.join([f"{k}:{str(v)[:max_row_length]}"
                         for k, v in self.data[:max_rows]])
        if len(self.data) > max_rows:
            s += f"<br>...{len(self.data)-max_rows} rows omitted."
        return s


    def __repr__(self):
        return self.str()

    def __str__(self):
        return self.str()


def get_graph(engine, table, primary_key) -> Graph:
    """Construct the graph for a specified data-point

    Args:
        engine: An sql-alchemy engine instance, used to connect to the database.
        table: Name of the table.
        primary_key: The primary key for the row.

    Returns:
        A graph of relations for the row.
    """
    metadata = MetaData()
    metadata.reflect(engine)
    Base = automap_base(metadata=metadata)
    Base.prepare()
    _table = Base.classes[table]
    graph = Graph()
    with Session(engine) as session:
        row = session.query(_table).get(primary_key)
        row_node = Node(
            table=_get_table_name_from_row(row),
            primary_key=_get_primary_key_from_row(row),
            data=_get_data(row),
        )
        graph.add_node(row_node)
        _add_related_rows_to_graph(row, row_node, graph)

    return graph


def _add_related_rows_to_graph(row, row_node, graph):
    related = []
    relationships = row.__mapper__.relationships
    for relationship in relationships:
        # This is a bit hacky - but they don't call it a hackathon for nothing.
        relationship_name = str(relationship).split(".")[-1]
        related_rows = getattr(row, relationship_name)
        try:
            # This path for reverse foreign keys
            for related_row in related_rows:
                related_node = Node(
                    table=_get_table_name_from_row(related_row),
                    primary_key=_get_primary_key_from_row(related_row),
                    data=_get_data(related_row),
                )
                related.append((related_row, related_node))
        except TypeError:
            # This path for foreign keys.
            related_row = related_rows
            related_node = Node(
                table=_get_table_name_from_row(related_row),
                primary_key=_get_primary_key_from_row(related_row),
                data=_get_data(related_row),
            )
            related.append((related_row, related_node))
    unvisited = [
        (row, node) for (row, node) in related
        if node not in graph.nodes
    ]
    for _, related_node in related:
        graph.add_edge(row_node, related_node)
    for unvisited_row, unvisited_node in unvisited:
        _add_related_rows_to_graph(unvisited_row, unvisited_node, graph)


def _get_table_name_from_row(row):
    return row.__table__.name

def _get_primary_key_from_row(row):
    primary_key_columns = row.__mapper__.primary_key
    primary_key_values = [getattr(row, column.name) for column in primary_key_columns]
    if len(primary_key_values) != 1:
        raise NotImplementedError("We just consider cases with single column pk for the time being")
    return primary_key_values[0]

def _get_data(row):
    return tuple( 
            (column.name, getattr(row, column.name))
            for column in row.__table__.columns
        )
