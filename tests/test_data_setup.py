from unittest import TestCase

from sqlalchemy import create_engine, text

from fk_graph.data_setup import setup_data

from fk_graph.plotly_functions import basic_test

class DataSetupTests(TestCase):

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

    def test_runs(self):
       setup_data(self.engine)

    def test_has_some_data(self):
       setup_data(self.engine)
       with self.engine.connect() as conn:
           with self.subTest():
               rs = conn.execute(text("SELECT * FROM table_a"))
               self.assertTrue(len(rs.all()) > 0)
           with self.subTest():
               rs = conn.execute(text("SELECT * FROM table_b"))
               self.assertTrue(len(rs.all()) > 0)


class PlotlyFunctionsTests(TestCase):
    def test_basic(self):
        basic_test()
