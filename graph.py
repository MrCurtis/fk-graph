from collections import namedtuple

from networkx import Graph
from sqlalchemy import inspect, MetaData
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from dataclasses import dataclass

import typing


class FKGraphException(Exception):
    """Base class for fk-graph exceptions."""


class TableDoesNotExist(FKGraphException):
    """Indicates the specified table does not exist."""


class PrimaryKeyDoesNotExist(FKGraphException):
    """Indicates a table does not have an entry for the specified primary key."""


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


def get_graph(engine, table, primary_key, only_tables=None) -> Graph:
    """Construct the graph for a specified data-point

    Args:
        engine: An sql-alchemy engine instance, used to connect to the database.
        table: Name of the table.
        primary_key: The primary key for the row.
        only_tables: (Optional) A list of table names. Any rows for tables not
          in the list will not be included in the graph.

    Raises:
        TableDoesNotExist - when the specified table does not exist.
        PrimaryKeyDoesNotExist - when the table does not have an entry for the
            specified primary key.

    Returns:
        A graph of relations for the row.
    """
    metadata = MetaData()
    metadata.reflect(engine, only=only_tables)
    Base = automap_base(metadata=metadata)
    Base.prepare()
    _table = _get_table(engine, Base, table)
    graph = Graph()
    with Session(engine) as session:
        row = _get_row(session, _table, primary_key)
        row_node = Node(
            table=_get_table_name_from_row(row),
            primary_key=_get_primary_key_from_row(row),
            data=_get_data(row),
        )
        graph.add_node(row_node)
        _add_related_rows_to_graph(row, row_node, graph, only_tables)

    return graph


def _get_table(engine, Base, table):
    try:
        return Base.classes[table]
    except KeyError:
        raise TableDoesNotExist(
            f"Table '{table}' not present in '{engine.url.database}'"
        )


def _get_row(session, table, primary_key):
    try:
        return session.get_one(table, primary_key)
    except NoResultFound:
        raise PrimaryKeyDoesNotExist(
            f"Primary key '{primary_key}' not present in '{table.__table__.name}'"
        )


def _add_related_rows_to_graph(row, row_node, graph, only_tables):
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
            # Ignore null foreign-keys.
            if related_row is not None and (only_tables is None or related_row.__table__.name in only_tables):
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
        _add_related_rows_to_graph(unvisited_row, unvisited_node, graph, only_tables)


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
