import numpy as np
import pandas as pd

np.random.seed(42)
GRID_SIZE = 40
rows = []

for x in range(GRID_SIZE):
    for y in range(GRID_SIZE):
        dist = ((x-20)**2 + (y-20)**2) ** 0.5
        rows.append({
            "x": x,
            "y": y,
            "dist_center": dist,
            "temperature": 32 + np.random.normal(0,1.5) + dist*0.05,
            "pm25": 40 + np.random.normal(0,10) + (abs(x-20)<3)*60,
            "traffic": np.random.randint(100,400) + (abs(x-20)<3)*1500,
            "encroachment_index": min(2, np.random.rand() + (y<5)*1.2),
        })

df = pd.DataFrame(rows)

df["green_cover"] = (
    np.random.uniform(5,40,len(df)) - df["traffic"]/200
).clip(0,50)

import os
os.makedirs("data/raw", exist_ok=True)

df.to_csv("data/raw/city_grid_raw.csv", index=False)
print("✅ Synthetic city data generated")
