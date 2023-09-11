from sqlalchemy import Column, create_engine, ForeignKey, insert, Integer, MetaData, Table
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

def setup_data(engine=engine):
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
