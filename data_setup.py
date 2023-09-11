from sqlalchemy import Column, create_engine, ForeignKey, Integer, MetaData, Table
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
