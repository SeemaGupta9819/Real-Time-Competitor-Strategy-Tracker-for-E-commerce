import pandas as pd
 
import matplotlib.pyplot as plt

# -----------------------------
# LOAD BOTH OUTPUT DATASETS
# -----------------------------
amazon_df   = pd.read_csv("Forecasting_Model/Amazon_output.csv")
flipkart_df = pd.read_csv("Forecasting_Model/flipkart_output.csv")

# Convert datetime to proper type
amazon_df["datetime"] = pd.to_datetime(amazon_df["datetime"])
flipkart_df["datetime"] = pd.to_datetime(flipkart_df["datetime"])

# -----------------------------
# RENAME COLUMNS FOR CLARITY
# -----------------------------
amazon_df = amazon_df.rename(columns={
    "actual_price": "amazon_actual",
    "predicted_price": "amazon_predicted"
})

flipkart_df = flipkart_df.rename(columns={
    "actual_price": "flipkart_actual",
    "predicted_price": "flipkart_predicted"
})

# -----------------------------
# MERGE BOTH USING datetime
# -----------------------------
combined = pd.merge(amazon_df, flipkart_df, on="datetime", how="inner")

pred = combined["amazon_predicted"]
actual = combined["amazon_actual"]

combined = combined.sort_values("datetime")
combined = combined.reset_index(drop=True)

# calculate confidence interval (simple)
residuals = actual - pred
std = residuals.std()

upper = pred + 1.96*std
lower = pred - 1.96*std

#---For Actual Prices-----
plt.figure(figsize=(12,6))

plt.plot(combined["datetime"], combined["amazon_actual"], 
         label="Amazon Actual Price", linewidth=2)

plt.plot(combined["datetime"], combined["flipkart_actual"], 
         label="Flipkart Actual Price", linewidth=2)

plt.title("Amazon vs Flipkart — Actual Price Comparison", fontsize=14)
plt.xlabel("Date")
plt.ylabel("Price")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

#----For Predicted Prices-----

plt.figure(figsize=(12,6))

plt.plot(combined["datetime"], combined["amazon_predicted"], 
         label="Amazon Predicted Price", linestyle="dashed", linewidth=2)

plt.plot(combined["datetime"], combined["flipkart_predicted"], 
         label="Flipkart Predicted Price", linestyle="dashed", linewidth=2)

plt.title("Amazon vs Flipkart — Predicted Price Comparison", fontsize=14)
plt.xlabel("Date")
plt.ylabel("Predicted Price")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()


