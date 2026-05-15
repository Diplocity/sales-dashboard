import pandas as pd
from datetime import datetime

df = pd.read_csv("data/eCommercePK.csv")

print("Dataset Loaded:")
print(df.head())

# Clean data
df = df.drop_duplicates()
df = df.dropna()

# FIXED revenue calculation (matches your dataset)
df["Revenue"] = df["quantity"] * df["sales"]

# Business insights
total_revenue = df["Revenue"].sum()

top_products = df.groupby("sku")["Revenue"].sum().sort_values(ascending=False)

top_categories = df.groupby("category")["Revenue"].sum()

top_cities = df.groupby("city")["Revenue"].sum()

print("\nTotal Revenue:", total_revenue)

# Export report
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"kaggle_sales_report_{timestamp}.xlsx"

with pd.ExcelWriter(filename, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Raw Data", index=False)
    top_products.to_excel(writer, sheet_name="Top Products")
    top_categories.to_excel(writer, sheet_name="Category Sales")
    top_cities.to_excel(writer, sheet_name="City Sales")

print(f"\nReport generated: {filename}")