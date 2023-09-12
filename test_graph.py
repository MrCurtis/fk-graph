from unittest import TestCase

from networkx import Graph, is_isomorphic
from sqlalchemy import create_engine, text

from data_setup import setup_data

from graph import get_graph, Node


class GetGraphTests(TestCase):

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        setup_data(self.engine)

    def test_can_build_from_reverse_foreign_key_relations(self):
        node_1 = Node(table="table_a", primary_key=1)
        node_2 = Node(table="table_b", primary_key=1)
        node_3 = Node(table="table_b", primary_key=2)
        expected_graph = Graph()
        expected_graph.add_edge(node_1, node_2)
        expected_graph.add_edge(node_1, node_3)

        graph = get_graph(self.engine, "table_a", 1)

        with self.subTest():
            self.assertCountEqual(graph.nodes, expected_graph.nodes)

        with self.subTest():
            self.assertTrue(is_isomorphic(graph, expected_graph))
