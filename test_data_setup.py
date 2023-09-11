from unittest import TestCase

from sqlalchemy import create_engine

from data_setup import setup_data

class DataSetupTests(TestCase):

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

    def test_runs(self):
       setup_data(self.engine)
