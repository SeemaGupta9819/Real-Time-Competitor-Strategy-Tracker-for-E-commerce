import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------------------
# 1️⃣ LOAD DATA
# ----------------------------
amazon = pd.read_csv("raw/amazon_dataset")
flipkart = pd.read_csv("raw/flipkart_dataset.csv")   # CHANGE THIS

flipkart = flipkart.rename(columns={
    "Price": "price",
    "Date": "date"
})

# ----------------------------
# 2️⃣ CLEAN DATE COLUMNS
# ----------------------------
amazon['date'] = pd.to_datetime(amazon['date'], errors='coerce').dt.tz_localize(None)
flipkart['date'] = pd.to_datetime(flipkart['date'], errors='coerce').dt.tz_localize(None)

amazon = amazon.dropna(subset=['date']).sort_values('date')
flipkart = flipkart.dropna(subset=['date']).sort_values('date')

# Convert date to pure date (remove time)
amazon['date'] = amazon['date'].dt.date
flipkart['date'] = flipkart['date'].dt.date

# # ----------------------------
# # 3️⃣ FEATURE EXTRACTION
# # ----------------------------
# amazon['hour'] = pd.to_datetime(amazon['date']).dt.hour
# amazon['weekday'] = pd.to_datetime(amazon['date']).dt.weekday
# amazon['month'] = pd.to_datetime(amazon['date']).dt.month

# flipkart['hour'] = pd.to_datetime(flipkart['date']).dt.hour
# flipkart['weekday'] = pd.to_datetime(flipkart['date']).dt.weekday
# flipkart['month'] = pd.to_datetime(flipkart['date']).dt.month

# ----------------------------
# 4️⃣ TIME SERIES PLOT
# ----------------------------
plt.figure(figsize=(14,5))
plt.plot(amazon['date'], amazon['price'], label='Amazon Price', linewidth=2)
plt.plot(flipkart['date'], flipkart['price'], label='Flipkart Price', linewidth=2)

plt.title("Price Comparison: Amazon vs Flipkart")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.show()

# ----------------------------
# 5️⃣ PRICE DISTRIBUTION (Amazon vs Flipkart)
# ----------------------------
plt.figure(figsize=(10,4))
sns.histplot(flipkart['price'], kde=True, bins=50, color='skyblue')
plt.title("Flipkart price Distribution")
plt.xlabel("Price")
plt.ylabel("Frequency")
plt.show()

plt.figure(figsize=(10,4))
sns.histplot(amazon['price'], kde=True, bins=50, color='lightpink')
plt.title("Flipkart Price Distribution")
plt.xlabel("Price")
plt.ylabel("Frequency")
plt.show()


# ----------------------------
# 6️⃣ BOXPLOT (Amazon + Flipkart)
# ----------------------------
combined = pd.DataFrame({
    "price": pd.concat([amazon['price'], flipkart['price']]),
    "platform": ["Amazon"] * len(amazon) + ["Flipkart"] * len(flipkart)
})

plt.figure(figsize=(10,6))
sns.boxplot(data=combined, x="platform", y="price", palette="Set2")
plt.title("Price Comparison Boxplot - Amazon vs Flipkart")
plt.xlabel("Platform")
plt.ylabel("Price")
plt.show()
