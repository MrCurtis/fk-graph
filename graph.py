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

    data:dict[str, typing.Any] = None

    def str(self):
        """table.primary_key"""
        return f"{self.table}.{str(self.primary_key)}"

    def str_data(self, max_length=25):
        """Convert addtional data to string for plotly, using <br> for newlines."""
        s = '<br>'.join([f"{k}:{str(v)[:max_length]}"
                         for k, v in self.data])
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
        )
        graph.add_node(row_node)
        relationships = row.__mapper__.relationships
        for relationship in relationships:
            # This is a bit hacky - but they don't call it a hackathon for nothing.
            relationship_name = str(relationship).split(".")[-1]
            related_rows = getattr(row, relationship_name)
            for related_row in related_rows:
                related_row_node = Node(
                    table=_get_table_name_from_row(related_row),
                    primary_key=_get_primary_key_from_row(related_row),
                )
                graph.add_node(related_row_node)
                graph.add_edge(row_node, related_row_node)

    return graph


def _get_table_name_from_row(row):
    return row.__table__.name

def _get_primary_key_from_row(row):
    primary_key_columns = row.__mapper__.primary_key
    primary_key_values = [getattr(row, column.name) for column in primary_key_columns]
    if len(primary_key_values) != 1:
        raise NotImplementedError("We just consider cases with single column pk for the time being")
    return primary_key_values[0]
