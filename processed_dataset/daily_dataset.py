import pandas as pd

# ---------------------------
# 1️⃣ Load datasets
# ---------------------------
amazon = pd.read_csv("raw/amazon_dataset")
flipkart = pd.read_csv("raw/flipkart_dataset.csv")


# ---------------------------
# 2️⃣ Convert date + time
# ---------------------------
amazon["date"] = pd.to_datetime(amazon["date"], errors="coerce")
flipkart["Date"] = pd.to_datetime(flipkart["Date"], errors="coerce")

amazon["date"] = amazon["date"].dt.date
flipkart["Date"] = flipkart["Date"].dt.date

amazon["date"] = pd.to_datetime(amazon["date"])
flipkart["Date"] = pd.to_datetime(flipkart["Date"])

# ---------------------------
# 3️⃣ CREATE DISCOUNT FOR AMAZON
# ---------------------------
base_price_amazon = amazon["price"].max()
amazon["amazon_discount"] = ((base_price_amazon - amazon["price"]) / base_price_amazon) * 100

# ---------------------------
# 4️⃣ CREATE DISCOUNT FOR FLIPKART
# ---------------------------
base_price_flipkart = flipkart["Price"].max()
flipkart["flipkart_discount"] = ((base_price_flipkart - flipkart["Price"]) / base_price_flipkart) * 100

amazon["amazon_discount"] = amazon["amazon_discount"].round(2).astype(str) + "%"
flipkart["flipkart_discount"] = flipkart["flipkart_discount"].round(2).astype(str) + "%"

# Rename Flipkart date column for merging
flipkart = flipkart.rename(columns={"Date": "date"})

# ---------------------------
# 5️⃣ Create FULL daily date range
# ---------------------------
full_dates = pd.DataFrame({"date": pd.date_range("2024-01-01", "2025-09-22")})

# ---------------------------
# 6️⃣ Merge each dataset with full calendar
# ---------------------------
amazon_daily = full_dates.merge(amazon, on="date", how="left")
flipkart_daily = full_dates.merge(flipkart, on="date", how="left")

# ---------------------------
# 7️⃣ Forward fill missing values
# ---------------------------
amazon_daily = amazon_daily.ffill()
flipkart_daily = flipkart_daily.ffill()

amazon_daily = amazon_daily.ffill().bfill()
flipkart_daily = flipkart_daily.ffill().bfill()

# ---------------------------
# 8️⃣ Rename price columns
# ---------------------------
amazon_daily = amazon_daily.rename(columns={
    "price": "amazon_price"
})

flipkart_daily = flipkart_daily.rename(columns={
    "Price": "flipkart_price"
})

# ---------------------------
# 9️⃣ Combine into final dataset
# ---------------------------
final = (
    full_dates
    .merge(amazon_daily[["date", "amazon_price", "amazon_discount"]], on="date", how="left")
    .merge(flipkart_daily[["date", "flipkart_price", "flipkart_discount"]], on="date", how="left")
)

# ---------------------------
# 🔟 Add date features + fixed time
# ---------------------------
final["day"] = final["date"].dt.day
final["month"] = final["date"].dt.month
final["year"] = final["date"].dt.year
final["weekend"] = final["date"].dt.weekday >= 5

final["datetime"] = pd.to_datetime(final["date"].astype(str) + " 19:26:37")

# ---------------------------
# 1️⃣1️⃣ Save final dataset
# ---------------------------
final.to_csv("processed_dataset/daily_price_dataset.csv", index=False)

print("Dataset created successfully!")
print(final.head())
