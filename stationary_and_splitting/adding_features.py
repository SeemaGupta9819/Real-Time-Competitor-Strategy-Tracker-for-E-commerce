

# -------------------------------------------------------
# 📌 IMPORTS
# -------------------------------------------------------
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


df = pd.read_csv("processed_dataset/daily_price_dataset.csv")

# --- Lags for Amazon ---
df["amazon_lag1"] = df["amazon_price"].shift(1)
df["amazon_lag2"] = df["amazon_price"].shift(2)

# --- Lags for Flipkart ---
df["flipkart_lag1"] = df["flipkart_price"].shift(1)
df["flipkart_lag2"] = df["flipkart_price"].shift(2)