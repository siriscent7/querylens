import streamlit as st
from querylens.loader import load_queries
from querylens.analyzer import analyze_duckdb, cost_summary

st.set_page_config(page_title="QueryLens", layout="wide")
st.title("🔍 QueryLens")
st.caption("Find your most expensive query patterns in seconds.")

uploaded = st.file_uploader("Upload a query log (CSV)", type="csv")
path = uploaded if uploaded else "sample_data/queries.csv"
if not uploaded:
    st.info("Showing sample data. Upload your own CSV (columns: query, scan_bytes, latency_ms).")

df = load_queries(path)
report = analyze_duckdb(df)
top_n = st.slider("Top N shapes to summarize", min_value=1, max_value=len(report), value=3)
summary = cost_summary(report, top_n=top_n)

c1, c2, c3 = st.columns(3)
c1.metric("Distinct query shapes", summary["total_shapes"])
c2.metric("Total scan bytes", f"{summary['total_scan_bytes']:,}")
c3.metric(f"Top {summary['top_n']} shapes =", f"{summary['top_n_pct_of_cost']}% of cost")

st.subheader("Query shapes ranked by scan cost")
st.dataframe(
    report[["example_query", "count", "total_scan_bytes", "avg_latency_ms", "cache_candidate"]],
    use_container_width=True,
)

st.subheader("💡 Cache candidates")
candidates = report[report["cache_candidate"]]
if len(candidates):
    st.write(f"**{len(candidates)} query shape(s)** are high-frequency + high-cost — cache these:")
    st.dataframe(candidates[["example_query", "count", "total_scan_bytes"]], use_container_width=True)
else:
    st.write("No strong cache candidates in this dataset.")