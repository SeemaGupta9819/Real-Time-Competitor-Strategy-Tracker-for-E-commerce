import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression

# ----------------------
# LOAD DATA
# ----------------------
train = pd.read_csv("Forecasting_Model/amazon_train.csv")
test  = pd.read_csv("Forecasting_Model/amazon_test.csv")

# -----------------------------
# FIX STRING PERCENT COLUMNS
# -----------------------------
for df in [train, test]:
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].replace('%', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors="ignore")

# ----------------------
# TARGET
# ----------------------
target = "amazon_price"

drop_cols = ["datetime", "date"]
train = train.drop(columns=drop_cols, errors='ignore')
test = test.drop(columns=drop_cols, errors='ignore')

X_train = train.drop(columns=[target])
y_train = train[target]

X_test = test.drop(columns=[target])
y_test = test[target]

# ----------------------
# METRICS
# ----------------------
def evaluate(true, pred):
    rmse = np.sqrt(mean_squared_error(true, pred))
    mae = mean_absolute_error(true, pred)
    mape = np.mean(np.abs((true - pred) / true)) * 100
    return rmse, mae, mape

# ----------------------
# MODEL — ONLY LINEAR REGRESSION
# ----------------------
model = LinearRegression()

print("\n==============================")
print("Training & Evaluating: Linear Regression")
print("==============================")

model.fit(X_train, y_train)
preds = model.predict(X_test)

# Metrics
rmse, mae, mape = evaluate(y_test, preds)

print("\nLinear Regression Performance:")
print(f"RMSE: {rmse}")
print(f"MAE : {mae}")
print(f"MAPE: {mape}%")
# -----------------------------
# PLOT — Actual vs Predicted
# -----------------------------

# Load datetime column separately (because we dropped it before training)
plot_data = pd.read_csv("Forecasting_Model/amazon_test.csv")
plot_data["datetime"] = pd.to_datetime(plot_data["datetime"])

plt.figure(figsize=(14,6))
plt.plot(plot_data["datetime"], y_test.values, label="Actual Price")
plt.plot(plot_data["datetime"], preds, label="Linear Regression Predicted", linestyle="dashed")

plt.title("Actual vs Predicted Price — Linear Regression")
plt.xlabel("Date")
plt.ylabel("Price")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# -----------------------------
# SAVE OUTPUT AS CSV
# -----------------------------

output_df = pd.DataFrame({
    "datetime": plot_data["datetime"],
    "actual_price": y_test.values,
    "predicted_price": preds
})

output_df.to_csv("Forecasting_Model/Amazon_output.csv", index=False)

print("\nSaved CSV: Forecasting_Model/linear_regression_output.csv")