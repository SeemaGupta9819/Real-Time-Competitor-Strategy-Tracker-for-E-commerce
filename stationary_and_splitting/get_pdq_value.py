from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib
matplotlib.use("Agg")   
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, acf, pacf
import numpy as np
import pandas as pd


# ===================================================
# FUNCTION TO PROCESS ANY DATASET (AMAZON / FLIPKART)
# ===================================================
def analyze_series(file_path, price_column, title):
    print("\n======================================")
    print(f"📌 Analyzing: {title}")
    print("======================================")

    # --- Load Dataset ---
    df = pd.read_csv(file_path)

    # --- Convert datetime & set index ---
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df.dropna(subset=['datetime'], inplace=True)
    df.set_index('datetime', inplace=True)

    # --- Select price series ---
    y = pd.to_numeric(df[price_column], errors='coerce').dropna()

    # --- Differencing for stationarity ---
    y_diff = y.diff().dropna()

    # --- ACF & PACF values ---
    n = len(y_diff)
    acf_vals = acf(y_diff, nlags=15)
    pacf_vals = pacf(y_diff, nlags=15, method='ywm')
    conf = 1.96 / np.sqrt(n)

    # --- Find heuristic AR(p) ---
    try:
        p_candidate = next((lag for lag, val in enumerate(pacf_vals[1:], 1) if abs(val) <= conf))
    except StopIteration:
        p_candidate = 0

    # --- Find heuristic MA(q) ---
    try:
        q_candidate = next((lag for lag, val in enumerate(acf_vals[1:], 1) if abs(val) <= conf))
    except StopIteration:
        q_candidate = 0

    # --- ADF Test ---
    adf_p = adfuller(y)[1]
    print(f"ADF p-value: {adf_p}")

    if adf_p <= 0.05:
        print("✅ Stationary (d = 0)")
    else:
        print("⚠️ Non-stationary → recommend differencing (d = 1)")

    # --- Display p,q ---
    print(f"Suggested AR(p): {p_candidate}")
    print(f"Suggested MA(q): {q_candidate}")
    print(f"Confidence Limit ±{round(conf,4)}")

    # --- ACF + PACF Plots ---
    plt.figure(figsize=(12,5))

    plt.subplot(1,2,1)
    plot_acf(y_diff, lags=15, ax=plt.gca())
    plt.axhline(conf, color='red', linestyle='--')
    plt.axhline(-conf, color='red', linestyle='--')
    plt.title(f"{title} ACF")

    plt.subplot(1,2,2)
    plot_pacf(y_diff, lags=15, ax=plt.gca(), method='ywm')
    plt.axhline(conf, color='red', linestyle='--')
    plt.axhline(-conf, color='red', linestyle='--')
    plt.title(f"{title} PACF")

    plt.tight_layout()
    plt.show()



# ===================================================
# 1️⃣ AMAZON ANALYSIS
# ===================================================
analyze_series(
    file_path="Forecasting_Model/amazon_train.csv",
    price_column="amazon_price",
    title="Amazon Price"
)

# ===================================================
# 2️⃣ FLIPKART ANALYSIS
# ===================================================
analyze_series(
    file_path="Forecasting_Model/flipkart_train.csv",
    price_column="flipkart_price",
    title="Flipkart Price"
)
