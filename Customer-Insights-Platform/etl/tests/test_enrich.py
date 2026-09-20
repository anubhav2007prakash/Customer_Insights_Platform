from etl.enrich.enricher import enrich_record


def test_enrich_full_name_and_hash():
    r = {"first_name": "Jane", "last_name": "Roe", "email": "jane@example.com", "customer_id": "123"}
    out = enrich_record(r)
    assert out["full_name"] == "Jane Roe"
    assert "customer_hash" in out
