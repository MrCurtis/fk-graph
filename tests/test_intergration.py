from unittest import TestCase

from sqlalchemy import create_engine, text

from fk_graph.graph import get_graph
from fk_graph.data_setup import setup_data
from fk_graph.plot_graph import plot

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

class DataSetupTests(TestCase):
    def test_integration(self):
        setup_data(engine)
        graph = get_graph( engine, 'table_a', 1 )
        plot(graph)

