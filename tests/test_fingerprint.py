from querylens.fingerprint import fingerprint


def test_same_shape_different_literals():
    a = fingerprint("SELECT * FROM users WHERE id = 5")
    b = fingerprint("SELECT * FROM users WHERE id = 99")
    assert a == b


def test_different_tables_differ():
    a = fingerprint("SELECT * FROM users WHERE id = 5")
    b = fingerprint("SELECT * FROM orders WHERE id = 5")
    assert a != b


def test_string_literals_normalized():
    a = fingerprint("SELECT COUNT(*) FROM events WHERE month = 'Jan'")
    b = fingerprint("SELECT COUNT(*) FROM events WHERE month = 'Feb'")
    assert a == b

def test_in_list_different_lengths_match():
    a = fingerprint("SELECT * FROM users WHERE id IN (1, 2, 3)")
    b = fingerprint("SELECT * FROM users WHERE id IN (1, 2)")
    assert a == b


def test_in_list_collapses_to_single_placeholder():
    fp = fingerprint("SELECT * FROM users WHERE id IN (1, 2, 3)")
    # should contain exactly one '?' inside the IN clause, not three
    assert fp.count("?") == 1


def test_dialect_parameter_works():
    # should not raise, and should still normalize
    fp = fingerprint("SELECT * FROM users WHERE id = 5", dialect="snowflake")
    assert "?" in fp