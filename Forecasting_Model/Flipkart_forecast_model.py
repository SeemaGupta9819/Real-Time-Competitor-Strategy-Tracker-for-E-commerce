import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
train = pd.read_csv("Forecasting_Model/flipkart_train.csv")
test = pd.read_csv("Forecasting_Model/flipkart_test.csv")

# Convert date column
train['date'] = pd.to_datetime(train['date'])
test['date'] = pd.to_datetime(test['date'])

# Sort for safety
train = train.sort_values("date").reset_index(drop=True)
test = test.sort_values("date").reset_index(drop=True)

# Convert % columns
for df in [train, test]:
    df["flipkart_discount"] = df["flipkart_discount"].astype(str).str.replace("%","", regex=False)
    df["flipkart_discount"] = pd.to_numeric(df["flipkart_discount"], errors="coerce").fillna(0)

# -------------------------------------------------
# FEATURE ENGINEERING (Apply on train+test)
# -------------------------------------------------
full = pd.concat([train, test]).reset_index(drop=True)

full["price_lag_1"] = full["flipkart_price"].shift(1)
full["price_lag_7"] = full["flipkart_price"].shift(7)

full["roll_mean_7"] = full["flipkart_price"].shift(1).rolling(7).mean()
full["roll_std_7"] = full["flipkart_price"].shift(1).rolling(7).std()

full["price_diff"] = full["flipkart_price"].diff()

# Date Features
full["month"] = full["date"].dt.month
full["dayofweek"] = full["date"].dt.dayofweek
full["quarter"] = full["date"].dt.quarter
full["is_weekend"] = (full["dayofweek"] >= 5).astype(int)

# Remove NAN rows introduced by lag/rolling
full = full.dropna().reset_index(drop=True)

# Re-split into train/test exact size
train_final = full.iloc[:len(train)]
test_final = full.iloc[len(train):]

# -------------------------------------------------
# TRAIN TEST SPLIT
# -------------------------------------------------
target = "flipkart_price"

X_train = train_final.drop(columns=["flipkart_price", "date"])
y_train = train_final[target]

X_test = test_final.drop(columns=["flipkart_price", "date"])
y_test = test_final[target]

# -------------------------------------------------
# MODEL
# -------------------------------------------------
model = XGBRegressor(
    n_estimators=400,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    random_state=42
)

model.fit(X_train, y_train)

# Predict
pred = model.predict(X_test)

# -------------------------------------------------
# METRICS
# -------------------------------------------------
rmse = np.sqrt(mean_squared_error(y_test, pred))
mae = mean_absolute_error(y_test, pred)
mape = np.mean(np.abs((y_test - pred) / y_test)) * 100

print("\n📌 XGBoost Performance:\n")
print(f"RMSE: {rmse:.2f}")
print(f"MAE : {mae:.2f}")
print(f"MAPE: {mape:.2f}%")

# -------------------------------------------------
# PLOT
# -------------------------------------------------
plt.figure(figsize=(14,6))
plt.plot(test_final["date"], y_test, label="Actual Price")
plt.plot(test_final["date"], pred, label="Predicted Price", linestyle="dashed")
plt.title("XGBoost Forecasting - Flipkart Price")
plt.xticks(rotation=45)
plt.legend()
plt.grid()
plt.show()

# -------------------------------------------------
# SAVE OUTPUT
# -------------------------------------------------
output_df = pd.DataFrame({
    "date": test_final["date"],
    "actual": y_test,
    "predicted": pred
})

output_df.to_csv("Forecasting_Model/flipkart_output.csv", index=False)

print("\n📁 Saved: Forecasting_Model/flipkart_output.csv")
