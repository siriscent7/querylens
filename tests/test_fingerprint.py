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