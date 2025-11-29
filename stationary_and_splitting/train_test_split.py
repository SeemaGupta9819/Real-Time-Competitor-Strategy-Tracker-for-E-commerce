import pandas as pd
import numpy as np
import os

# Load dataset
df = pd.read_csv("processed_dataset/daily_price_dataset.csv")

# Ensure datetime
df["datetime"] = pd.to_datetime(df["datetime"])
df = df.sort_values("datetime")
df = df.set_index("datetime")

# Convert numeric columns
df["amazon_price"] = pd.to_numeric(df["amazon_price"], errors="coerce")
df["flipkart_price"] = pd.to_numeric(df["flipkart_price"], errors="coerce")

# ============================
# DATE FEATURES
# ============================
df["day"] = df.index.day
df["month"] = df.index.month
df["year"] = df.index.year
df["dayofweek"] = df.index.dayofweek
df["weekofyear"] = df.index.isocalendar().week.astype(int)
df["quarter"] = df.index.quarter
df["weekend"] = df["dayofweek"].isin([5, 6]).astype(int)
df["is_month_start"] = df.index.is_month_start
df["is_month_end"] = df.index.is_month_end

# ============================
# FUNCTION: Create Lags & Rollings
# ============================
def create_features(data, price_col, discount_col):
    data = data.copy()

    # LAG features
    lags = [1,2,3,7,14,30]
    for lag in lags:
        data[f"{price_col}_lag_{lag}"] = data[price_col].shift(lag)

    # ROLLING features
    windows = [3,7,14,30]
    for w in windows:
        data[f"{price_col}_roll_mean_{w}"] = data[price_col].rolling(w).mean()
        data[f"{price_col}_roll_std_{w}"] = data[price_col].rolling(w).std()

    # Price & discount changes
    data[f"{price_col}_change_1d"] = data[price_col].diff()
    data[f"{discount_col}_change_1d"] = (
        data[discount_col].astype(str).str.rstrip("%").astype(float).diff()
    )

    return data

# Create features for AMAZON and FLIPKART
df_amz = create_features(df, "amazon_price", "amazon_discount")
df_fkp = create_features(df, "flipkart_price", "flipkart_discount")

# Drop NA (lag & rolling introduced them)
df_amz = df_amz.dropna()
df_fkp = df_fkp.dropna()

# ============================
# SELECT IMPORTANT FEATURES
# ============================
amazon_feature_cols = [
    # Lags
    "amazon_price_lag_1","amazon_price_lag_2","amazon_price_lag_3",
    "amazon_price_lag_7","amazon_price_lag_14","amazon_price_lag_30",

    # Rolling statistics
    "amazon_price_roll_mean_3","amazon_price_roll_mean_7",
    "amazon_price_roll_mean_14","amazon_price_roll_mean_30",
    "amazon_price_roll_std_7","amazon_price_roll_std_30",

    # Changes
    "amazon_price_change_1d","amazon_discount_change_1d",

    # Date features
    "day","month","year","dayofweek","weekend","weekofyear","quarter"
]

flipkart_feature_cols = [
    # Lags
    "flipkart_price_lag_1","flipkart_price_lag_2","flipkart_price_lag_3",
    "flipkart_price_lag_7","flipkart_price_lag_14","flipkart_price_lag_30",

    # Rolling statistics
    "flipkart_price_roll_mean_3","flipkart_price_roll_mean_7",
    "flipkart_price_roll_mean_14","flipkart_price_roll_mean_30",
    "flipkart_price_roll_std_7","flipkart_price_roll_std_30",

    # Changes
    "flipkart_price_change_1d","flipkart_discount_change_1d",

    # Date features
    "day","month","year","dayofweek","weekend","weekofyear","quarter"
]

# ============================
# TRAIN–TEST SPLIT
# ============================
def time_split(data, features, target_col):
    train_size = int(len(data) * 0.8)

    train = data.iloc[:train_size]
    test = data.iloc[train_size:]

    X_train = train[features]
    y_train = train[target_col]

    X_test = test[features]
    y_test = test[target_col]

    return X_train, X_test, y_train, y_test, train, test

# AMAZON SPLIT
X_train_amz, X_test_amz, y_train_amz, y_test_amz, amz_train_df, amz_test_df = time_split(
    df_amz, amazon_feature_cols, "amazon_price"
)

# FLIPKART SPLIT
X_train_fkp, X_test_fkp, y_train_fkp, y_test_fkp, fkp_train_df, fkp_test_df = time_split(
    df_fkp, flipkart_feature_cols, "flipkart_price"
)

# ============================
# SAVE OUTPUT FILES
# ============================
os.makedirs("Forecasting_Model", exist_ok=True)

amz_train_df.to_csv("Forecasting_Model/amazon_train.csv")
amz_test_df.to_csv("Forecasting_Model/amazon_test.csv")
fkp_train_df.to_csv("Forecasting_Model/flipkart_train.csv")
fkp_test_df.to_csv("Forecasting_Model/flipkart_test.csv")

print("FILES SAVED SUCCESSFULLY:")
print(" - amazon_train.csv") 
print(" - amazon_test.csv")
print(" - flipkart_train.csv")
print(" - flipkart_test.csv")
