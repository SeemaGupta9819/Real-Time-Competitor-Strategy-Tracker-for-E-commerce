# --------------------------
# IMPORTS
# --------------------------
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose


# --------------------------
# LOAD YOUR DATASET
# --------------------------
df = pd.read_csv("processed_dataset/daily_price_dataset.csv")

# ensure datetime is proper timestamp
df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
df = df.sort_values("datetime")

# filter from 2024 only
df = df[df["datetime"] >= "2024-01-01"].reset_index(drop=True)

print("Records available:", len(df))

# --- Preprocess ---
df["datetime"] = pd.to_datetime(df["datetime"])

# Add weekday name
df["weekday"] = df["datetime"].dt.day_name()

# Add price difference (Amazon - Flipkart)
df["price_diff"] = df["amazon_price"] - df["flipkart_price"]


# --------------------------
# CREATE MA7, MA30, EMA
# --------------------------
df["MA_7_Amazon"] = df["amazon_price"].rolling(window=7).mean()
df["MA_30_Amazon"] = df["amazon_price"].rolling(window=30).mean()
df["EMA_14_Amazon"] = df["amazon_price"].ewm(span=14, adjust=False).mean()

df["MA_7_Flipkart"] = df["flipkart_price"].rolling(window=7).mean()
df["MA_30_Flipkart"] = df["flipkart_price"].rolling(window=30).mean()
df["EMA_14_Flipkart"] = df["flipkart_price"].ewm(span=14, adjust=False).mean()

# Save the DataFrame to CSV
df.to_csv("Trend_Analysis/trend_analysis.csv", index=False)

print("CSV saved successfully!")


# ============================================
# 📌 1️⃣ TREND + MA7 + MA30 — SIDE BY SIDE
# ============================================
fig, ax = plt.subplots(1, 2, figsize=(18,6))

# Amazon
ax[0].plot(df["datetime"], df["amazon_price"], alpha=0.5, label="Amazon Price")
ax[0].plot(df["datetime"], df["MA_7_Amazon"], label="MA 7")
ax[0].plot(df["datetime"], df["MA_30_Amazon"], label="MA 30")
ax[0].set_title("Amazon Price Trend")
ax[0].set_xlabel("Date"); ax[0].set_ylabel("Price")
ax[0].grid(True); ax[0].legend()

# Flipkart
ax[1].plot(df["datetime"], df["flipkart_price"], alpha=0.5, label="Flipkart Price")
ax[1].plot(df["datetime"], df["MA_7_Flipkart"], label="MA 7")
ax[1].plot(df["datetime"], df["MA_30_Flipkart"], label="MA 30")
ax[1].set_title("Flipkart Price Trend")
ax[1].set_xlabel("Date"); ax[1].set_ylabel("Price")
ax[1].grid(True); ax[1].legend()

plt.tight_layout()
plt.show()


# ============================================
# 📌 2️⃣ SEASONAL DECOMPOSITION — SIDE BY SIDE
# ============================================
decomp_A = seasonal_decompose(df["amazon_price"], model="additive", period=30)
decomp_F = seasonal_decompose(df["flipkart_price"], model="additive", period=30)

# -------- TREND --------
fig, ax = plt.subplots(1, 2, figsize=(18,6))

decomp_A.trend.plot(ax=ax[0], title="Amazon Trend")
decomp_F.trend.plot(ax=ax[1], title="Flipkart Trend")

plt.tight_layout()
plt.show()

# -------- SEASONAL --------
fig, ax = plt.subplots(1, 2, figsize=(18,6))

decomp_A.seasonal.plot(ax=ax[0], title="Amazon Seasonal")
decomp_F.seasonal.plot(ax=ax[1], title="Flipkart Seasonal")

plt.tight_layout()
plt.show()

# ============================================
# 📌 3️⃣ WEEKDAY BOXPLOTS — SIDE BY SIDE
# ============================================
fig, ax = plt.subplots(1, 2, figsize=(18,7))

sns.boxplot(
    x="weekday", y="amazon_price", data=df,
    order=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    ax=ax[0]
)
ax[0].set_title("Amazon Weekday Price Distribution")
ax[0].tick_params(axis='x', rotation=45)

sns.boxplot(
    x="weekday", y="flipkart_price", data=df,
    order=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    ax=ax[1]
)
ax[1].set_title("Flipkart Weekday Price Distribution")
ax[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()


# ================================
# 📌 5️⃣ COMPARISON GRAPH (VERY IMPORTANT)
# ================================
plt.figure(figsize=(16,7))
plt.plot(df["datetime"], df["amazon_price"], label="Amazon Price", color="blue")
plt.plot(df["datetime"], df["flipkart_price"], label="Flipkart Price", color="orange")
plt.title("Amazon vs Flipkart: Price Comparison")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.show()



print(df.head())