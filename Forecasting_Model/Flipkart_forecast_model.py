import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
import matplotlib.pyplot as plt

# -----------------------------
# LOAD DATA
# -----------------------------
train = pd.read_csv("Forecasting_Model/flipkart_train.csv")
test  = pd.read_csv("Forecasting_Model/flipkart_test.csv")

# -----------------------------
# FIX STRING PERCENT COLUMNS
# -----------------------------
for df in [train, test]:
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].replace('%', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors="ignore")

# -----------------------------
# TARGET
# -----------------------------
target = "flipkart_price"

# Keep a copy for plotting (contains datetime)
test_plot = test.copy()

# Remove unwanted columns ONLY from model input
drop_cols = ["date"]   # KEEP datetime here
train = train.drop(columns=[c for c in drop_cols if c in train.columns])
test  = test.drop(columns=[c for c in drop_cols if c in test.columns])

# Split
X_train = train.drop(columns=[target, "datetime"])
y_train = train[target]

X_test = test.drop(columns=[target, "datetime"])
y_test = test[target]

# -----------------------------
# METRIC FUNCTION
# -----------------------------
def evaluate(true, pred):
    rmse = np.sqrt(mean_squared_error(true, pred))
    mae = mean_absolute_error(true, pred)
    mape = np.mean(np.abs((true - pred) / true)) * 100
    return rmse, mae, mape

# -----------------------------
# XGBOOST MODEL
# -----------------------------
model = XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    random_state=42
)

# Train
model.fit(X_train, y_train)

# Predict
preds = model.predict(X_test)

# -----------------------------
# RESULTS
# -----------------------------
rmse, mae, mape = evaluate(y_test, preds)
print("\nXGBoost Model Performance:\n")
print(f"RMSE: {rmse}")
print(f"MAE : {mae}")
print(f"MAPE: {mape}%")

# -----------------------------
# PLOT
# -----------------------------
test_plot["datetime"] = pd.to_datetime(test_plot["datetime"])

plt.figure(figsize=(14,6))
plt.plot(test_plot["datetime"], y_test.values, label="Actual Price")
plt.plot(test_plot["datetime"], preds, label="XGBoost Predicted Price", linestyle="dashed")
plt.title("Actual vs Predicted Price — XGBoost")
plt.xlabel("Date")
plt.ylabel("Price")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

output_df = pd.DataFrame({
    "datetime": test_plot["datetime"],
    "actual_price": y_test.values,
    "predicted_price": preds
})

output_df.to_csv("Forecasting_Model/flipkart_output.csv", index=False)

print("\nSaved CSV: Forecasting_Model/flipkart_xgboost_output.csv")
