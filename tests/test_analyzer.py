import pandas as pd
from querylens.analyzer import analyze, cost_summary, analyze_duckdb


def make_df():
    return pd.DataFrame(
        {
            "query": [
                "SELECT * FROM users WHERE id = 5",
                "SELECT * FROM users WHERE id = 99",
                "SELECT COUNT(*) FROM events WHERE month = 'Jan'",
            ],
            "scan_bytes": [1000, 1000, 50000],
            "latency_ms": [10, 12, 100],
        }
    )


def test_groups_same_shape():
    report = analyze(make_df())
    # two user queries collapse to one shape -> 2 shapes total
    assert len(report) == 2


def test_count_aggregation():
    report = analyze(make_df())
    users = report[report["example_query"].str.contains("users")].iloc[0]
    assert users["count"] == 2


def test_ranking_by_cost():
    report = analyze(make_df())
    # events shape (50k bytes) should rank above users (2k total)
    assert "events" in report.iloc[0]["example_query"]


def test_cost_summary_keys():
    summary = cost_summary(analyze(make_df()), top_n=1)
    assert set(summary) == {
        "total_shapes",
        "total_scan_bytes",
        "top_n",
        "top_n_pct_of_cost",
    }

def test_duckdb_matches_pandas():
    df = make_df()
    pdf = analyze(df).sort_values("fingerprint").reset_index(drop=True)
    ddf = analyze_duckdb(df).sort_values("fingerprint").reset_index(drop=True)
    assert len(pdf) == len(ddf)
    assert set(pdf["count"]) == set(ddf["count"])