# scripts/regenerate_charts.py
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "data" / "sales.csv"
CHARTS = PROJECT / "outputs" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

print("Project:", PROJECT)
print("Data file:", DATA)
print("Charts folder:", CHARTS)
print()

# 1) show existing chart files
existing = sorted([p.name for p in CHARTS.glob("*.png")])
print("Existing PNGs in outputs/charts:")
for name in existing:
    print(" -", name)
if not existing:
    print(" (none found)")

# 2) load data and inspect columns and a few rows
if not DATA.exists():
    print("\nERROR: data/sales.csv not found. Put your CSV at:", DATA)
    sys.exit(1)

df = pd.read_csv(DATA)
print("\nCSV columns:", list(df.columns))
print("First 5 rows:\n", df.head().to_string(index=False))

# 3) try to detect key columns
def detect(cols, candidates):
    for c in candidates:
        if c in cols:
            return c
    for c in cols:
        if c.lower() in [x.lower() for x in candidates]:
            return c
    return None

cols = list(df.columns)
date_col = detect(cols, ['date','Date','sale_date','SaleDate','day'])
sales_col = detect(cols, ['sales','Sales','amount','Amount','value','Value'])
cat_col = detect(cols, ['category','Category','cat','Cat','product_category'])

print("\nDetected columns -> date:", date_col, " sales:", sales_col, " category:", cat_col)

# 4) coerce and prepare
if date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
else:
    print("No date column detected. Aborting.")
    sys.exit(1)

if sales_col:
    df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce')
else:
    print("No numeric sales column detected. Aborting.")
    sys.exit(1)

df = df.dropna(subset=[date_col, sales_col]).rename(columns={date_col:'date', sales_col:'sales'})
if cat_col:
    df = df.rename(columns={cat_col:'category'})
else:
    df['category'] = 'All'

print("\nAfter cleaning: rows =", len(df))
if df.empty:
    print("No valid rows after cleaning. Check your CSV data.")
    sys.exit(1)

# 5) generate the commonly missing charts (weekly, quarterly, pie, grouped)
try:
    # weekly
    weekly = df.set_index('date').resample('W')['sales'].sum()
    fig = plt.figure(figsize=(10,4))
    plt.plot(weekly.index, weekly.values)
    plt.title("Weekly Sales")
    plt.tight_layout()
    path = CHARTS / "weekly_sales.png"
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("Saved:", path)

    # quarterly
    quarterly = df.set_index('date').resample('Q')['sales'].sum()
    fig = plt.figure(figsize=(9,4))
    plt.plot(quarterly.index, quarterly.values, marker='s')
    plt.title("Quarterly Sales")
    plt.tight_layout()
    path = CHARTS / "quarterly_sales.png"
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("Saved:", path)

    # pie (category share)
    cat_totals = df.groupby('category')['sales'].sum().sort_values(ascending=False)
    if not cat_totals.empty:
        fig = plt.figure(figsize=(6,6))
        plt.pie(cat_totals.values, labels=cat_totals.index, autopct='%1.1f%%', startangle=140)
        plt.title("Category Share (Overall)")
        path = CHARTS / "category_share_pie.png"
        fig.savefig(path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print("Saved:", path)
    else:
        print("Skipping pie chart — no category totals")

    # grouped monthly x category (last 6 months)
    monthly_cat = df.set_index('date').groupby([pd.Grouper(freq='ME'), 'category'])['sales'].sum().unstack(fill_value=0)
    last6 = monthly_cat.tail(6)
    if not last6.empty:
        fig = last6.plot(kind='bar', figsize=(12,6)).get_figure()
        path = CHARTS / "monthly_by_category_grouped.png"
        fig.savefig(path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print("Saved:", path)
    else:
        print("Skipping grouped monthly-by-category — not enough monthly data")

except Exception as e:
    print("Error while generating additional charts:", repr(e))
    sys.exit(1)

print("\nDone. Check outputs/charts/ for the newly created images.")
