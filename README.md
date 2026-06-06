# 🔍 QueryLens

**A query observability plane that finds your most expensive query patterns in seconds.**

Point QueryLens at your SQL query logs. It fingerprints each query *shape*, ranks them by scan cost, and flags caching opportunities — the same problem data platforms like Snowflake solve at scale.

🔗 **Live demo:** https://querylens-xrdordlvnmdxddb75b9jv9.streamlit.app/

---

## The problem
Analysts run thousands of slightly-different queries. Two queries like `WHERE id = 5` and `WHERE id = 99` are the *same shape* but get counted
separately, so no one can see which query *patterns* actually drive cost.

## What it does
- **Fingerprinting** — normalizes literals so same-shape queries collapse into one (`WHERE id = 5` → `WHERE id = ?`), using AST parsing via `sqlglot`.
- **Cost ranking** — aggregates by shape and ranks by total scan bytes.
- **Cache detection** — flags high-frequency, high-cost shapes worth caching.
- **SQL-on-SQL** — analysis runs inside an embedded **DuckDB** engine.

## Results
On a synthetic workload of **10,000 queries**, QueryLens collapses them into **7 distinct shapes in ~694 ms**. A parse-caching optimization cut runtime from 1076 ms to 694 ms (**~1.55x speedup**) by avoiding redundant re-parsing of duplicate queries. The **top 3 shapes drive 80.6% of total scan cost** — a clear Pareto distribution that pinpoints exactly where to optimize

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

## Generating test data
QueryLens ships with a synthetic workload generator that produces realistic, skewed query logs (a few shapes dominate traffic, like real workloads):
```bash
python sample_data/generate.py   # writes sample_data/queries_large.csv (10k queries)
```

## Roadmap
- Snowflake `QUERY_HISTORY` connector for real workloads
- Query similarity clustering beyond exact shape match