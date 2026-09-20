from etl.transform.transformer import Transformer


def test_rename_and_merge():
    spec = [
        {"action": "rename", "from": "fname", "to": "first_name"},
        {"action": "merge", "into": "full_name", "cols": ["first_name", "last_name"], "sep": " "},
    ]
    t = Transformer(spec)
    row = {"fname": "John", "last_name": "Doe"}
    out = t.apply(row)
    assert out["first_name"] == "John"
    assert out["full_name"] == "John Doe"
