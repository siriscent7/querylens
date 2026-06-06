# 🔍 QueryLens

**A query observability plane that finds your most expensive query patterns in seconds.**

Point QueryLens at your SQL query logs. It fingerprints each query *shape*,
ranks them by scan cost, and flags caching opportunities — the same problem
data platforms like Snowflake solve at scale.

🔗 **Live demo:** https://querylens-xrdordlvnmdxddb75b9jv9.streamlit.app/

---

## The problem
Analysts run thousands of slightly-different queries. Two queries like
`WHERE id = 5` and `WHERE id = 99` are the *same shape* but get counted
separately, so no one can see which query *patterns* actually drive cost.

## What it does
- **Fingerprinting** — normalizes literals so same-shape queries collapse into one
  (`WHERE id = 5` → `WHERE id = ?`), using AST parsing via `sqlglot`.
- **Cost ranking** — aggregates by shape and ranks by total scan bytes.
- **Cache detection** — flags high-frequency, high-cost shapes worth caching.
- **SQL-on-SQL** — analysis runs inside an embedded **DuckDB** engine.

## Results
On a sample workload of 8 queries, QueryLens collapsed them into
**4 distinct shapes** and found the **top 2 shapes account for
85.7% of total scan cost.**  *(numbers from the live demo)*

## Architecture
```
query log (CSV)
│
▼
fingerprint.py ── AST parse + literal normalization (sqlglot)
│
▼
analyzer.py ── group by shape, cost ranking, cache flags (DuckDB)
│
▼
app.py ── Streamlit dashboard
```

## Run locally
```bash
git clone https://github.com/siriscent7/querylens.git
cd querylens
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

## Tests
```bash
pytest -v   # 8 tests: fingerprinting + analytics
```

## Roadmap
- Snowflake `QUERY_HISTORY` connector for real workloads
- Query similarity clustering beyond exact shape match