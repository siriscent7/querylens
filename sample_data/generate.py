import csv
import random

# Query templates with realistic cost profiles (scan_bytes ranges)
TEMPLATES = [
    ("SELECT * FROM users WHERE id = {int}", 800_000, 1_200_000),
    ("SELECT name, email FROM users WHERE signup_date > '{date}'", 2_000_000, 4_000_000),
    ("SELECT * FROM orders WHERE total > {int}", 4_000_000, 6_000_000),
    ("SELECT COUNT(*) FROM events WHERE month = '{month}'", 9_000_000, 12_000_000),
    ("SELECT * FROM products WHERE category = '{cat}'", 1_500_000, 2_500_000),
    ("SELECT user_id, SUM(total) FROM orders WHERE region = '{cat}' GROUP BY user_id", 7_000_000, 10_000_000),
    ("SELECT * FROM sessions WHERE duration > {int}", 3_000_000, 5_000_000),
    ("SELECT * FROM users WHERE id IN ({in_list})", 1_000_000, 1_500_000),
    ("SELECT * FROM orders WHERE status IN ({in_list_str})", 2_000_000, 3_000_000),
]

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
CATS = ["electronics", "books", "toys", "garden", "auto"]
DATES = ["2025-01-01", "2025-03-15", "2025-06-20", "2025-09-10"]

# Skewed frequency: a few query shapes dominate (realistic workload)
WEIGHTS = [40, 5, 25, 15, 8, 4, 3, 6, 4]

N = 10_000

def fill(template):
    # random-length integer IN-list, e.g. (3, 17, 42)
    int_list = ", ".join(
        str(random.randint(1, 1000)) for _ in range(random.randint(1, 5))
    )
    # random-length string IN-list, e.g. ('shipped', 'pending')
    statuses = ["shipped", "pending", "cancelled", "delivered", "returned"]
    str_list = ", ".join(
        f"'{random.choice(statuses)}'" for _ in range(random.randint(1, 4))
    )
    return (
        template
        .replace("{int}", str(random.randint(1, 100_000)))
        .replace("{month}", random.choice(MONTHS))
        .replace("{cat}", random.choice(CATS))
        .replace("{date}", random.choice(DATES))
        .replace("{in_list_str}", str_list)
        .replace("{in_list}", int_list)
    )

with open("sample_data/queries_large.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["query", "scan_bytes", "latency_ms"])
    for _ in range(N):
        template, lo, hi = random.choices(TEMPLATES, weights=WEIGHTS, k=1)[0]
        query = fill(template)
        scan_bytes = random.randint(lo, hi)
        # latency loosely correlates with scan size
        latency = int(scan_bytes / 100_000 + random.randint(-5, 15))
        w.writerow([query, scan_bytes, max(latency, 1)])

print(f"Wrote {N} queries to sample_data/queries_large.csv")