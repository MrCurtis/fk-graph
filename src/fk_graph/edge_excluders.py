"""Edge Excluders.

Functions to pass in as an `exclude_edge` argument to `get_graph`.

The functions in this module that do not take any arguments can be passed in
directly to `get_graph`. Those that do take arguments should be called with the
required arguments, and the returned function passed to `get_graph`.
"""

def input_row_is_in_tables(table_names):
    """Checks whether input row-node is in list of tables.

    This is typically used in cases where one wishes to include rows from a
    table as nodes in the graph, but *not* include the subsequent rows which
    can only be reached via these nodes.
    For example, if there is a `user` table with f-k relation to a `country`
    table, one might want to include the country that a user is from, but not
    also include all the other users that are from that country.

    Args:
      table_names: A list of table names.

    Returns:
      A function of the form (input_row, output_row) -> bool. The function will
      return `True` if and only if `input_row` is from a table with one of the
      names in `table_name`.
    """
    def f(input_row, output_row):
        return _get_table_name_from_row(input_row) in table_names

    return f

def _get_table_name_from_row(row):
    return row.__table__.name
