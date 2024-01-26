from unittest import TestCase
from networkx import Graph, is_isomorphic
from sqlalchemy import Column, create_engine, ForeignKey, insert, Integer, MetaData, String, Table

from fk_graph.data_setup import setup_data

from fk_graph.graph import (
    get_graph,
    Node,
    PrimaryKeyDoesNotExist,
    TableDoesNotExist,
)


class GetGraphTests(TestCase):

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")

    def test_can_build_with_single_table_no_relation(self):
        self._create_single_table_no_relations(self.engine)
        node_1 = Node(table="table_a", primary_key=1)
        expected_graph = Graph()
        expected_graph.add_node(node_1)

        graph = get_graph(self.engine, "table_a", 1)

        with self.subTest():
            self.assertCountEqual(_to_table_primary_keys(graph.nodes), _to_table_primary_keys(expected_graph.nodes))

        with self.subTest():
            self.assertTrue(is_isomorphic(graph, expected_graph))

    def test_can_build_from_reverse_foreign_key_relations(self):
        self._create_db_with_reverse_foreign_key_relations(self.engine)
        node_1 = Node(table="table_a", primary_key=1)
        node_2 = Node(table="table_b", primary_key=1)
        node_3 = Node(table="table_b", primary_key=2)
        expected_graph = Graph()
        expected_graph.add_edge(node_1, node_2)
        expected_graph.add_edge(node_1, node_3)

        graph = get_graph(self.engine, "table_a", 1)

        with self.subTest():
            self.assertCountEqual(_to_table_primary_keys(graph.nodes), _to_table_primary_keys(expected_graph.nodes))

        with self.subTest():
            self.assertTrue(is_isomorphic(graph, expected_graph))

    def test_can_build_from_triple_row_linear_foreign_key_relations(self):
        self._create_three_entries_with_linear_foreign_key_relations(self.engine)
        node_1 = Node(table="table_c", primary_key=1)
        node_2 = Node(table="table_b", primary_key=1)
        node_3 = Node(table="table_a", primary_key=1)
        expected_graph = Graph()
        expected_graph.add_edge(node_1, node_2)
        expected_graph.add_edge(node_2, node_3)

        graph = get_graph(self.engine, "table_c", 1)

        with self.subTest():
            self.assertCountEqual(_to_table_primary_keys(graph.nodes), _to_table_primary_keys(expected_graph.nodes))

        with self.subTest():
            self.assertTrue(is_isomorphic(graph, expected_graph))

    def test_can_build_from_triple_row_linear_reverse_foreign_key_relations(self):
        self._create_three_entries_with_linear_foreign_key_relations(self.engine)
        node_1 = Node(table="table_a", primary_key=1)
        node_2 = Node(table="table_b", primary_key=1)
        node_3 = Node(table="table_c", primary_key=1)
        expected_graph = Graph()
        expected_graph.add_edge(node_1, node_2)
        expected_graph.add_edge(node_2, node_3)

        graph = get_graph(self.engine, "table_a", 1)

        with self.subTest():
            self.assertCountEqual(_to_table_primary_keys(graph.nodes), _to_table_primary_keys(expected_graph.nodes))

        with self.subTest():
            self.assertTrue(is_isomorphic(graph, expected_graph))

    def test_can_build_from_data_with_circular_relations(self):
        self._create_data_with_circular_realtionships(self.engine)
        node_1 = Node(table="table_a", primary_key=1)
        node_2 = Node(table="table_b", primary_key=1)
        node_3 = Node(table="table_c", primary_key=1)
        expected_graph = Graph()
        expected_graph.add_edge(node_1, node_2)
        expected_graph.add_edge(node_2, node_3)
        expected_graph.add_edge(node_3, node_1)

        graph = get_graph(self.engine, "table_a", 1)

        with self.subTest():
            self.assertCountEqual(_to_table_primary_keys(graph.nodes), _to_table_primary_keys(expected_graph.nodes))

        with self.subTest():
            self.assertTrue(is_isomorphic(graph, expected_graph))

    def test_adds_data_attribute(self):
        self._create_data_with_non_primary_key_non_foreign_kay_fields(self.engine)
        expected_data = (
            ("id", 1),
            ("string_field", "some_text"),
            ("integer_field", 123),
            ("b_id", 1),
        )

        graph = get_graph(self.engine, "table_a", 1)

        table_a_node = [
            n for n in graph.nodes if n.table == "table_a" and n.primary_key == 1
        ][0]

        self.assertCountEqual(table_a_node.data, expected_data)

    def test_raises_table_does_not_exist_exception_when_no_table_with_name(self):
        self._create_single_table_no_relations(self.engine)

        with self.assertRaisesRegex(
            TableDoesNotExist,
            f"Table 'non_existent_table' not present in '{self.engine.url.database}'",
        ):
            get_graph(self.engine, "non_existent_table", 1)

    def test_raises_primary_key_does_not_exist_when_no_key_in_table(self):
        self._create_single_table_no_relations(self.engine)

        with self.assertRaisesRegex(
            PrimaryKeyDoesNotExist,
            f"Primary key '9876' not present in 'table_a'",
        ):
            get_graph(self.engine, "table_a", "9876")

    def test_can_restrict_to_selected_tables__reverse_foreign_key_case(self):
        self._create_three_entries_with_linear_foreign_key_relations(self.engine)

        graph = get_graph(self.engine, "table_a", "1", only_tables=["table_a", "table_b"])

        with self.subTest("includes selected tables"):
            self.assertTrue(
                any([n.table == "table_a" for n in graph.nodes])
                and
                any([n.table == "table_b" for n in graph.nodes])
            )
        with self.subTest("excludes non-selected tables"):
            self.assertFalse(
                any([n.table == "table_c" for n in graph.nodes])
            )

    def test_can_restrict_to_selected_tables__forward_foreign_key_case(self):
        self._create_three_entries_with_linear_foreign_key_relations(self.engine)

        graph = get_graph(self.engine, "table_c", "1", only_tables=["table_c", "table_b"])

        with self.subTest("includes selected tables"):
            self.assertTrue(
                any([n.table == "table_c" for n in graph.nodes])
                and
                any([n.table == "table_b" for n in graph.nodes])
            )
        with self.subTest("excludes non-selected tables"):
            self.assertFalse(
                any([n.table == "table_a" for n in graph.nodes])
            )

    def test_can_create_graph_when_some_rows_have_null_foreign_keys(self):
        self._create_entries_with_null_foreign_key(self.engine)

        graph = get_graph(self.engine, "table_a", "1")

        # Check does not add null nodes to graph.
        self.assertEqual(len(graph.nodes), 1)

    def _create_single_table_no_relations(self, engine):
        metadata_object = MetaData()
        table_a = Table(
            "table_a",
            metadata_object,
            Column("id", Integer, primary_key=True),
        )
        metadata_object.create_all(engine)
        with engine.connect() as conn:
            conn.execute(
                insert(table_a),
                [
                    {"id": 1},
                ]
            )
            conn.commit()

    def _create_db_with_reverse_foreign_key_relations(self, engine):
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

    def _create_three_entries_with_linear_foreign_key_relations(self, engine):
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
        table_c = Table(
            "table_c",
            metadata_object,
            Column("id", Integer, primary_key=True),
            Column("b_id", ForeignKey("table_b.id"), nullable=False),
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
                ]
            )
            conn.execute(
                insert(table_c),
                [
                    {"id": 1, "b_id": 1},
                ]
            )
            conn.commit()

    def _create_data_with_circular_realtionships(self, engine):
        metadata_object = MetaData()
        table_a = Table(
            "table_a",
            metadata_object,
            Column("id", Integer, primary_key=True),
            Column("c_id", ForeignKey("table_c.id"), nullable=False),
        )
        table_b = Table(
            "table_b",
            metadata_object,
            Column("id", Integer, primary_key=True),
            Column("a_id", ForeignKey("table_a.id"), nullable=False),
        )
        table_c = Table(
            "table_c",
            metadata_object,
            Column("id", Integer, primary_key=True),
            Column("b_id", ForeignKey("table_b.id"), nullable=False),
        )
        metadata_object.create_all(engine)
        with engine.connect() as conn:
            conn.execute(
                insert(table_a),
                [
                    {"id": 1, "c_id": 1},
                ]
            )
            conn.execute(
                insert(table_b),
                [
                    {"id": 1, "a_id": 1},
                ]
            )
            conn.execute(
                insert(table_c),
                [
                    {"id": 1, "b_id": 1},
                ]
            )
            conn.commit()

    def _create_data_with_non_primary_key_non_foreign_kay_fields(self, engine):
        metadata_object = MetaData()
        table_a = Table(
            "table_a",
            metadata_object,
            Column("id", Integer, primary_key=True),
            Column("b_id", ForeignKey("table_b.id"), nullable=False),
            Column("string_field", String),
            Column("integer_field", Integer),
        )
        table_b = Table(
            "table_b",
            metadata_object,
            Column("id", Integer, primary_key=True),
        )
        metadata_object.create_all(engine)
        with engine.connect() as conn:
            conn.execute(
                insert(table_a),
                [
                    {"id": 1, "b_id": 1, "string_field": "some_text", "integer_field": 123},
                ]
            )
            conn.execute(
                insert(table_b),
                [
                    {"id": 1},
                ]
            )
            conn.commit()

    def _create_entries_with_null_foreign_key(self, engine):
        metadata_object = MetaData()
        table_a = Table(
            "table_a",
            metadata_object,
            Column("id", Integer, primary_key=True),
            Column("b_id", ForeignKey("table_b.id"), nullable=True),
        )
        table_b = Table(
            "table_b",
            metadata_object,
            Column("id", Integer, primary_key=True),
        )
        metadata_object.create_all(engine)
        with engine.connect() as conn:
            conn.execute(
                insert(table_a),
                [
                    {"id": 1, "b_id": None},
                ]
            )
            conn.commit()


def _to_table_primary_keys(nodes):
    return [
        (n.table, n.primary_key) for n in nodes
    ]
