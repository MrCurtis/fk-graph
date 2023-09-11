from collections import namedtuple


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
    pass
