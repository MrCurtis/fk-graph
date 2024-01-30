from argparse import ArgumentParser

from sqlalchemy import create_engine

from fk_graph import setup_data, get_graph
from fk_graph.plotly_functions import run_app

def main():
    args = _parse_args()
    if args.demo:
        engine = create_engine("sqlite+pysqlite:///:memory:")
        setup_data(engine)
    elif args.connection_string:
        engine = create_engine(args.connection_string)
    graph = get_graph(engine, args.table, args.primary_key)
    run_app(graph)

def _parse_args():
    parser = ArgumentParser(
        prog="fk-graph",
        description="Visualise the graphs hidden within relational databases.",

    )
    parser.add_argument("--demo", action="store_true", help="Run with the built-in demo database.")
    parser.add_argument("--connection-string")
    parser.add_argument("--table", required=True)
    parser.add_argument("--primary-key", required=True)
    args = parser.parse_args()
    if (
        (not args.demo and args.connection_string is None)
        or
        (args.demo and args.connection_string is not None)
    ):
        parser.error(
            "Exactly one of --demo and --connection-string should be used."
        )
    return args
