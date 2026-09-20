from etl.dedup.deduplicator import deduplicate


def test_dedup_keep_first():
    rows = [
        {"email": "a@x.com", "name": "A"},
        {"email": "b@x.com", "name": "B"},
        {"email": "a@x.com", "name": "A2"},
    ]
    deduped, dups = deduplicate(rows, ["email"], strategy="keep_first")
    assert len(deduped) == 2
    assert len(dups) == 1
