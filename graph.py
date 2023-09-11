from collections import namedtuple

from networkx import Graph
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


Node = namedtuple("Node", ["table", "primary_key"])


def get_graph(engine, table, primary_key):
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
    with Session(engine) as session:
        row = session.query(_table).get(primary_key)
        graph = Graph()
        graph.add_node(Node(table=table, primary_key=primary_key))

    return graph
