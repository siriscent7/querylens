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
- **IN-list normalization** — `IN (1,2,3)` and `IN (1,2)` collapse to the same
  shape, so variable-length lists don't fragment your patterns.
- **Dialect-aware parsing** — supports Snowflake, BigQuery, Postgres, etc. via sqlglot.

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

## Limitations
- **Semantic equivalence** — queries that are logically identical but written differently (e.g., reordered JOINs, subquery vs JOIN) produce different fingerprints.
- **Cost metadata is supplied, not measured** — `scan_bytes` and `latency_ms` come from the input log, as they would from a warehouse's query history in production. QueryLens analyzes the metadata; it does not execute queries.
- **Exact structural matching** — fingerprinting groups queries by AST shape, so two patterns that are semantically equivalent but structurally different are not yet merged.

## Future Work
- **Snowflake `QUERY_HISTORY` connector** — analyze real production workloads directly instead of CSV logs.
- **JOIN-order normalization** — canonicalize reordered JOINs. Deferred because it is semantically risky (JOIN conditions are tied to specific table pairs), and naive reordering could create false matches.
- **Query similarity clustering** — group near-identical patterns beyond exact AST matching (e.g., subquery vs JOIN forms).
- **Streaming ingestion** — process query logs continuously for larger-than-memory and real-time analysis.