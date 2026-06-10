# -*- coding: utf-8 -*-
"""
Healthcare Data Engineering Project
Dataiku Python Recipe: Inventory Reorder Recommendations
Automates data transformation to identify reorder needs
"""

import dataiku
from datetime import datetime

# Read input dataset
inventory_prepared = dataiku.Dataset("inventory_status_prepared")
df = inventory_prepared.get_dataframe()

# Transform: Calculate reorder recommendations
print(f"Processing {len(df)} stockout records...")

# Calculate days of stock remaining
df["days_of_stock_remaining"] = (
    df["QUANTITY_ON_HAND"] /
    df["UNITS_SOLD_30D"].replace(0, 1)
)

# Calculate recommended reorder quantity
# Rule: reorder 30 days worth of supply
df["recommended_reorder_qty"] = (
    df["UNITS_SOLD_30D"] * 30
).astype(int)

# Assign priority level


def get_priority(row):
    if row["STOCKOUT_FLAG"] == "Y":
        return "CRITICAL"
    elif row["LOW_STOCK_FLAG"] == "Y":
        return "HIGH"
    else:
        return "NORMAL"


df["reorder_priority"] = df.apply(get_priority, axis=1)

# Add processing timestamp
df["processed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Add recommendation message
df["recommendation"] = df.apply(
    lambda r: f"Order {r['recommended_reorder_qty']} units of {r['PRODUCT_NAME']} for {r['STORE_NAME']}",
    axis=1
)

# Select final columns
output_df = df[[
    "STORE_NAME",
    "REGION",
    "PRODUCT_NAME",
    "CATEGORY",
    "QUANTITY_ON_HAND",
    "UNITS_SOLD_30D",
    "REORDER_POINT",
    "days_of_stock_remaining",
    "recommended_reorder_qty",
    "reorder_priority",
    "recommendation",
    "processed_at"
]]

print(f"Generated {len(output_df)} reorder recommendations")
print(output_df[["STORE_NAME", "PRODUCT_NAME", "reorder_priority", "recommended_reorder_qty"]].to_string())

#  Write output dataset
reorder_output = dataiku.Dataset("inventory_reorder_recommendations")
reorder_output.write_with_schema(output_df)

print("✓ Reorder recommendations written successfully!")
