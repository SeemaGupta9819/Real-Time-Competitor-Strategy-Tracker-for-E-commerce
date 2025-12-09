import pandas as pd
 
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# -----------------------------------------
# Function to plot ACF & PACF for a dataset
# -----------------------------------------
def plot_acf_pacf(file_path, column_name, title_prefix):
    # Load dataset
    df = pd.read_csv(file_path)

    # Keep only numeric price column
    y = pd.to_numeric(df[column_name], errors="coerce").dropna()

    # Plot ACF & PACF
    plt.figure(figsize=(12,5))

    plt.subplot(1,2,1)
    plot_acf(y, lags=30, ax=plt.gca())
    plt.title(f"{title_prefix} ACF")

    plt.subplot(1,2,2)
    plot_pacf(y, lags=30, ax=plt.gca(), method="ywm")
    plt.title(f"{title_prefix} PACF")

    plt.tight_layout()
    plt.show()


# ---------------------------------------------------
# 1️⃣ ACF & PACF for AMAZON TRAIN
# ---------------------------------------------------
plot_acf_pacf(
    file_path="Forecasting_Model/amazon_train.csv",
    column_name="amazon_price",
    title_prefix="Amazon"
)

# ---------------------------------------------------
# 2️⃣ ACF & PACF for FLIPKART TRAIN
# ---------------------------------------------------
plot_acf_pacf(
    file_path="Forecasting_Model/flipkart_train.csv",
    column_name="flipkart_price",
    title_prefix="Flipkart"
)
