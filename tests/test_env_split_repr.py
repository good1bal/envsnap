from envsnap.env_split import SplitResult, split_by_prefix, split_by_keys


def _env():
    return {"APP_X": "1", "DB_Y": "2", "OTHER": "3"}


def test_repr_contains_split_result():
    r = split_by_prefix(_env(), ["APP_"])
    assert "SplitResult" in repr(r)


def test_repr_shows_key_counts():
    r = split_by_prefix(_env(), ["APP_", "DB_"])
    rep = repr(r)
    assert "1keys" in rep


def test_split_result_parts_is_dict():
    r = split_by_prefix(_env(), ["APP_"])
    assert isinstance(r.parts, dict)


def test_split_result_remainder_is_dict():
    r = split_by_prefix(_env(), ["APP_"])
    assert isinstance(r.remainder, dict)


def test_split_by_keys_result_type():
    r = split_by_keys(_env(), {"g": ["APP_X"]})
    assert isinstance(r, SplitResult)


def test_split_empty_env():
    r = split_by_prefix({}, ["APP_"])
    assert r.parts["APP_"] == {}
    assert r.remainder == {}
