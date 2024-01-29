from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    Session,
)

from fk_graph.edge_excluders import input_row_is_in_tables

class TestInputRowIsInTable(TestCase):

    def setUp(self):
        class Base(DeclarativeBase):
            pass

        class TableA(Base):
            __tablename__ = "table_a"
            id: Mapped[int] = mapped_column(primary_key=True)

        class TableB(Base):
            __tablename__ = "table_b"
            id: Mapped[int] = mapped_column(primary_key=True)

        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.TableA, self.TableB = TableA, TableB

    def test_function_returns_true_if_input_row_from_table(self):
        with Session(self.engine) as session:
            table_a_row = self.TableA(id=1)
            table_b_row = self.TableB(id=1)
            session.add_all([table_a_row, table_b_row])
            session.commit()

        with Session(self.engine) as session:
            table_a_row = session.get_one(self.TableA, 1)
            table_b_row = session.get_one(self.TableB, 1)

            self.assertTrue(
                input_row_is_in_tables(["table_a"])(table_a_row, table_b_row)
            )

    def test_function_returns_false_if_input_row_not_from_table(self):
        with Session(self.engine) as session:
            table_a_row = self.TableA(id=1)
            table_b_row = self.TableB(id=1)
            session.add_all([table_a_row, table_b_row])
            session.commit()

        with Session(self.engine) as session:
            table_a_row = session.get_one(self.TableA, 1)
            table_b_row = session.get_one(self.TableB, 1)

            self.assertFalse(
                input_row_is_in_tables(["table_b"])(table_a_row, table_b_row)
            )
