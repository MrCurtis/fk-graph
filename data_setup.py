from sqlalchemy import Column, create_engine, Integer, MetaData, Table
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

def setup_data():
    metadata_object = MetaData()
    table_a = Table(
        "table_a",
        metadata_object,
        Column("id", Integer, primary_key=True),
    )
    metadata_object.create_all(engine)
