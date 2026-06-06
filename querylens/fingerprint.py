import sqlglot
from sqlglot import exp


def fingerprint(sql: str, dialect: str | None = None) -> str:
    """Normalize a SQL query into its 'shape' by replacing literals.
    
    Two queries differing only in literal values produce the same
    fingerprint:
        SELECT * FROM users WHERE id = 5
        SELECT * FROM users WHERE id = 99
    both -> SELECT * FROM users WHERE id = ?

    - Replaces literal values with placeholders (5, 'Jan' -> ?)
    - Collapses variable-length IN-lists so IN (1,2,3) and IN (1,2)
      fingerprint identically -> IN (?)
    """
    tree = sqlglot.parse_one(sql, dialect=dialect)

    # 1. Collapse IN-lists to a single placeholder
    for in_expr in tree.find_all(exp.In):
        if in_expr.expressions:  # the list of values inside IN (...)
            in_expr.set("expressions", [exp.Placeholder()])

    # 2. Replace all remaining literals with placeholders
    for lit in tree.find_all(exp.Literal):
        lit.replace(exp.Placeholder())

    return tree.sql(dialect=dialect)