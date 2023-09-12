from unittest import TestCase

from data_setup import setup_data

from graph import get_graph

from sqlalchemy import create_engine, text

from plot_graph import plot

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

class DataSetupTests(TestCase):
    def test_integration(self):
        setup_data(engine)
        graph = get_graph( engine, 'table_a', 1 )
        plot(graph)

