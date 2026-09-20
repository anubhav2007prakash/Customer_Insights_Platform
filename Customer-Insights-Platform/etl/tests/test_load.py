import tempfile
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, text
import os
from etl.load.loader import LoadEngine


def test_load_engine_sqlite():
    # create sqlite in-memory engine and a table
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    path = tmp.name
    url = f"sqlite+pysqlite:///{path}"
    engine = create_engine(url, future=True)
    metadata = MetaData()
    t = Table("customers", metadata, Column("id", Integer, primary_key=True), Column("name", String), Column("email", String))
    metadata.create_all(engine)

    rows = [{"id": 1, "name": "A", "email": "a@x.com"}, {"id": 2, "name": "B", "email": "b@x.com"}]

    loader = LoadEngine(url)
    loader.load_table("customers", rows, batch_size=1)

    # verify rows inserted
    with engine.connect() as conn:
        res = conn.execute(text("SELECT COUNT(*) FROM customers"))
        cnt = res.scalar()
        assert cnt == 2

    # dispose engines before removing temp file
    engine.dispose()
    loader.connector.engine.dispose()
    os.unlink(path)
