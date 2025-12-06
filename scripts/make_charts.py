import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Paths
data_path = Path("data/sales.csv")
output_path = Path("outputs")
charts_path = output_path / "charts"
charts_path.mkdir(parents=True, exist_ok=True)

# ---------------------------
# 1) LOAD DATA
# ---------------------------
df = pd.read_csv(data_path, parse_dates=['date'])
df = df.sort_values('date')

# ---------------------------
# 2) DAILY SALES LINE CHART
# ---------------------------
daily = df.groupby('date')['sales'].sum()

plt.figure(figsize=(10,4))
plt.plot(daily.index, daily.values)
plt.title("Daily Sales")
plt.xlabel("date")
plt.ylabel("sales")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(charts_path / "daily_sales.png", dpi=300)
plt.close()

# ---------------------------
# 3) MONTHLY SALES LINE CHART
# ---------------------------
monthly = df.set_index('date').resample('M')['sales'].sum()

plt.figure(figsize=(10,4))
plt.plot(monthly.index, monthly.values, marker='o')
plt.title("Monthly Sales")
plt.xlabel("Month")
plt.ylabel("sales")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(charts_path / "monthly_sales.png", dpi=300)
plt.close()

# ---------------------------
# 4) CATEGORY BAR CHART
# ---------------------------
cat_totals = df.groupby('category')['sales'].sum()

plt.figure(figsize=(8,5))
plt.bar(cat_totals.index, cat_totals.values)
plt.title("Sales by Category")
plt.xlabel("category")
plt.ylabel("sales")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(charts_path / "category_sales_bar.png", dpi=300)
plt.close()

print("All charts generated successfully!")
