from unittest import TestCase

from networkx import Graph, is_isomorphic
from sqlalchemy import Column, create_engine, ForeignKey, insert, Integer, MetaData, Table

from data_setup import setup_data

from graph import get_graph, Node


class GetGraphTests(TestCase):

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        setup_data(self.engine)

    def test_can_build_from_reverse_foreign_key_relations(self):
        self._create_db_with_foreign_key_relations(self.engine)
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

    def _create_db_with_foreign_key_relations(self, engine):
        metadata_object = MetaData()
        table_a = Table(
            "table_a",
            metadata_object,
            Column("id", Integer, primary_key=True),
        )
        table_b = Table(
            "table_b",
            metadata_object,
            Column("id", Integer, primary_key=True),
            Column("a_id", ForeignKey("table_a.id"), nullable=False),
        )
        metadata_object.create_all(engine)
        with engine.connect() as conn:
            conn.execute(
                insert(table_a),
                [
                    {"id": 1},
                ]
            )
            conn.execute(
                insert(table_b),
                [
                    {"id": 1, "a_id": 1},
                    {"id": 2, "a_id": 1},
                ]
            )
            conn.commit()
