import pandas as pd


def load_queries(path: str) -> pd.DataFrame:
    """Load a query log CSV with columns: query, scan_bytes, latency_ms."""
    df = pd.read_csv(path)
    required = {"query", "scan_bytes", "latency_ms"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return df