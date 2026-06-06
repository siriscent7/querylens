import sqlglot
from sqlglot import exp


def fingerprint(sql: str) -> str:
    """Normalize a SQL query into its 'shape' by replacing literals.

    Two queries differing only in literal values produce the same
    fingerprint:
        SELECT * FROM users WHERE id = 5
        SELECT * FROM users WHERE id = 99
    both -> SELECT * FROM users WHERE id = ?
    """
    tree = sqlglot.parse_one(sql)
    for lit in tree.find_all(exp.Literal):
        lit.replace(exp.Placeholder())
    return tree.sql()