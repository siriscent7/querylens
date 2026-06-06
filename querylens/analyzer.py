import pandas as pd
from querylens.fingerprint import fingerprint


def analyze(df: pd.DataFrame) -> pd.DataFrame:
    """Group queries by fingerprint and compute cost metrics.

    Returns one row per query shape, ranked by total scan cost
    (count * scan_bytes), with a cache-candidate flag.
    """
    df = df.copy()
    df["fingerprint"] = df["query"].apply(fingerprint)

    grouped = (
        df.groupby("fingerprint")
        .agg(
            count=("query", "size"),
            total_scan_bytes=("scan_bytes", "sum"),
            avg_latency_ms=("latency_ms", "mean"),
            example_query=("query", "first"),
        )
        .reset_index()
    )

    # Cost score: how much total scanning this shape is responsible for
    grouped["cost_score"] = grouped["total_scan_bytes"]

    # Cache candidate: runs frequently AND scans a lot -> worth caching
    median_count = grouped["count"].median()
    grouped["cache_candidate"] = (grouped["count"] > median_count) & (
        grouped["total_scan_bytes"] >= grouped["total_scan_bytes"].median()
    )

    grouped = grouped.sort_values("cost_score", ascending=False).reset_index(drop=True)
    return grouped


def cost_summary(report: pd.DataFrame, top_n: int = 5) -> dict:
    """Headline numbers for the README/dashboard."""
    total_cost = report["cost_score"].sum()
    top = report.head(top_n)
    top_cost = top["cost_score"].sum()
    pct = (top_cost / total_cost * 100) if total_cost else 0
    return {
        "total_shapes": len(report),
        "total_scan_bytes": int(total_cost),
        "top_n": min(top_n, len(report)),
        "top_n_pct_of_cost": round(pct, 1),
    }