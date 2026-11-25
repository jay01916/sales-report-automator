"""Create a deliberately messy fake sales file for demos and tests."""
import random

import pandas as pd

random.seed(42)
products = {"Laptop": 55000, "Phone": 22000, "Headphones": 2500, "Monitor": 12000, "Keyboard": 1500}
regions = ["north", "South", " East ", "WEST"]

rows = []
for _ in range(400):
    p = random.choice(list(products))
    rows.append(
        {
            "Date": pd.Timestamp("2025-01-01") + pd.Timedelta(days=random.randint(0, 330)),
            "Product": random.choice([p, p.lower(), f" {p} "]),
            "Region": random.choice(regions),
            "Quantity": random.randint(1, 8),
            "Unit Price": products[p] * random.choice([1, 1, 1, 0.9, 1.05]),
        }
    )

df = pd.DataFrame(rows)
# add realistic mess: blanks, bad values, duplicates
df["Unit Price"] = df["Unit Price"].astype(object)
df.loc[random.sample(range(len(df)), 6), "Quantity"] = None
df.loc[random.sample(range(len(df)), 4), "Unit Price"] = "N/A"
df.loc[random.sample(range(len(df)), 3), "Quantity"] = -2
df = pd.concat([df, df.sample(10, random_state=1)], ignore_index=True)

df.to_csv("sample_sales.csv", index=False)
print(f"Wrote sample_sales.csv with {len(df)} rows")
