"""End-to-end smoke test for ingestion service (in-memory small file)."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ingestion.services.ingestion_service import IngestionService
from ingestion.repositories.repository import IngestionRepository
from database.base import Base



def test_import_csv_preview_and_import():
    # create in-memory sqlite for repository to avoid external DB dependency
    engine = create_engine("sqlite:///:memory:", future=True)
    # Create a minimal organizations table to satisfy TenantModel foreign keys during tests
    from sqlalchemy import Table, Column, String

    metadata = Base.metadata
    if "organizations" not in metadata.tables:
        Table("organizations", metadata, Column("id", String(64), primary_key=True))
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    session = TestSession()

    repo = IngestionRepository(session=session)
    svc = IngestionService(repo=repo)
    csv_bytes = b"name,email\nAlice,alice@example.com\nBob,bob@example.com\n"
    preview = svc.preview(csv_bytes, "test.csv")
    assert preview.file_name == "test.csv"
    assert len(preview.preview) == 2

    import uuid

    report = svc.import_file(organization_id=uuid.UUID("00000000-0000-0000-0000-000000000000"), user_id="tester", file_bytes=csv_bytes, filename="test.csv", required=["email"])
    assert report.total == 2
