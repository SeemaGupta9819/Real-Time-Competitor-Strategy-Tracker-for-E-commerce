import pandas as pd

# ---- Load Dataset ----
df = pd.read_csv("processed_dataset/daily_price_dataset.csv")  # If already loaded, ignore reading step
df['date'] = pd.to_datetime(df['date'])

# ---- Sort by date to keep forecasting realistic ----
df = df.sort_values('date').reset_index(drop=True)

# ---- Create Amazon-only dataset ----
amazon_df = df[['date', 'amazon_price', 'amazon_discount']]
amazon_df = amazon_df.dropna(subset=['amazon_price']).reset_index(drop=True)

# ---- Create Flipkart-only dataset ----
flipkart_df = df[['date', 'flipkart_price', 'flipkart_discount']]
flipkart_df = flipkart_df.dropna(subset=['flipkart_price']).reset_index(drop=True)

# ---- 80–20 Time Split ----
amazon_split = int(len(amazon_df) * 0.8)
flipkart_split = int(len(flipkart_df) * 0.8)

# Amazon Train/Test
amazon_train = amazon_df.iloc[:amazon_split].reset_index(drop=True)
amazon_test = amazon_df.iloc[amazon_split:].reset_index(drop=True)

# Flipkart Train/Test
flipkart_train = flipkart_df.iloc[:flipkart_split].reset_index(drop=True)
flipkart_test = flipkart_df.iloc[flipkart_split:].reset_index(drop=True)

# ---- Save Output (Optional) ----
amazon_train.to_csv("Forecasting_Model/amazon_train.csv", index=False)
amazon_test.to_csv("Forecasting_Model/amazon_test.csv", index=False)
flipkart_train.to_csv("Forecasting_Model/flipkart_train.csv", index=False)
flipkart_test.to_csv("Forecasting_Model/flipkart_test.csv", index=False)

# ---- Summary ----
print("Split Completed Successfully!")
print(f"Amazon: Train = {len(amazon_train)}, Test = {len(amazon_test)}")
print(f"Flipkart: Train = {len(flipkart_train)}, Test = {len(flipkart_test)}")
