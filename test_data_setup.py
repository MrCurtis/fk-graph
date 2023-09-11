from unittest import TestCase
from data_setup import setup_data

class DataSetupTests(TestCase):
    def test_runs(self):
       setup_data()
