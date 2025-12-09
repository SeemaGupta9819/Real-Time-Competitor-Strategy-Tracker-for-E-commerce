import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt


train = pd.read_csv("Forecasting_Model/amazon_train.csv")
test = pd.read_csv("Forecasting_Model/amazon_test.csv")


# ----------- FEATURE ENGINEERING FUNCTION (Reusable for Train + Test) -----------

def add_features(df):
    df = df.copy()

    # Date handling
    df['date'] = pd.to_datetime(df['date'])

    # Clean and convert discount column
    if 'amazon_discount' in df.columns:
        df['amazon_discount'] = df['amazon_discount'].astype(str).str.replace('%', '', regex=False)
        df['amazon_discount'] = pd.to_numeric(df['amazon_discount'], errors='coerce').fillna(0.0)

    # Ensure price numeric
    df['amazon_price'] = pd.to_numeric(df['amazon_price'], errors='coerce')

    # Lags
    df['lag_1'] = df['amazon_price'].shift(1)
    df['lag_7'] = df['amazon_price'].shift(7)

    # Rolling mean features
    df['roll_mean_14'] = df['amazon_price'].shift(1).rolling(14).mean()
    df['roll_mean_30'] = df['amazon_price'].shift(1).rolling(30).mean()
    df['roll_std_30'] = df['amazon_price'].shift(1).rolling(30).std()
    df['momentum_14'] = df['amazon_price'] - df['amazon_price'].shift(14)

    


    # Time features
    df['month'] = df['date'].dt.month
    df['dayofweek'] = df['date'].dt.dayofweek

    # Remove rows with missing engineered features
    df = df.dropna().reset_index(drop=True)

    return df


# ---------------- APPLY FEATURE ENGINEERING ----------------

train_fe = add_features(train)
test_fe = add_features(test)


# ---------------- SELECT FEATURES AND TARGET ----------------

features = ['lag_1', 'lag_7', 'month', 'roll_mean_30', 'roll_mean_14',"roll_std_30","momentum_14"]


X_train = train_fe[features]
y_train = train_fe['amazon_price']

X_test = test_fe[features]
y_test = test_fe['amazon_price']


# ---------------- TRAIN MODEL ----------------

model = LinearRegression()
model.fit(X_train, y_train)


# ---------------- PREDICT ----------------

pred = model.predict(X_test)


# -------------------------------------------------
# PLOT
# -------------------------------------------------
plt.figure(figsize=(14,6))
plt.plot(test_fe["date"], y_test, label="Actual Price")
plt.plot(test_fe["date"], pred, label="Predicted Price", linestyle="dashed")
plt.title("Linear Regression - Amazon Price")
plt.xticks(rotation=45)
plt.legend()
plt.grid()
plt.show()

# ---------------- METRICS ----------------

rmse = np.sqrt(mean_squared_error(y_test, pred))
mae = mean_absolute_error(y_test, pred)
mape = np.mean(np.abs((y_test - pred) / (y_test + 1e-9))) * 100

print("====== MODEL PERFORMANCE ======")
print(f"RMSE : {rmse:.2f}")
print(f"MAE  : {mae:.2f}")
print(f"MAPE : {mape:.2f}%")



output_df = pd.DataFrame({
    "date": test_fe["date"],
    "actual": y_test,
    "predicted": pred
})

output_df.to_csv("Forecasting_Model/amazon_output.csv", index=False)

print("\n📁 Saved: Forecasting_Model/amazon_output.csv")
