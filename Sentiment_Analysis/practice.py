from groq import Groq
import pandas as pd
import matplotlib
matplotlib.use("Agg")   
import matplotlib.pyplot as plt
import seaborn as sns
import re, json, time, random
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, cohen_kappa_score, precision_score, recall_score, f1_score


# ----------------------- CONFIG -----------------------
API_KEY = "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"
INPUT_FILE = r"/content/Reviews.xlsx"
OUTPUT_FILE = INPUT_FILE.replace(".xlsx", "_Output.xlsx")
# ------------------------------------------------------

client = Groq(api_key=API_KEY)
df = pd.read_excel(INPUT_FILE)

# ----------------------- MERGE Review_Title + Riview_Body -----------------------
# Your exact column names:
title_col = "Review_Title"
body_col = "Review_Body"   # spelling exactly as in your dataset

# Validate columns
if title_col not in df.columns:
    raise ValueError("Column 'Review_Title' not found in dataset.")

if body_col not in df.columns:
    raise ValueError("Column 'Riview_Body' not found in dataset. Check spelling.")

# Clean & convert to text
df[title_col] = df[title_col].fillna("").astype(str)
df[body_col] = df[body_col].fillna("").astype(str)

# Create merged column
df["Merged_Review"] = df[title_col] + " " + df[body_col]

print(f"✅ Loaded {len(df)} reviews")
print("📌 Merged column created: Merged_Review\n")

sns.set(style="whitegrid", font_scale=1.1)
plt.rcParams["figure.figsize"] = (9, 5)


# ----------------------- ⭐ AUTO MAP RATINGS → TRUE SENTIMENT -----------------------
rating_columns = [c for c in df.columns if any(x in c.lower() for x in ["star", "rating", "rate", "stars"])]
true_sentiment_available = False

if rating_columns:
    rating_col = rating_columns[0]
    print(f"📌 Rating column detected: {rating_col}")

    def map_rating_to_sentiment(r):
        try:
            r = float(r)
        except:
            return None

        if r >= 4: return "Positive"
        elif r == 3: return "Neutral"
        elif r <= 2: return "Negative"
        return None

    df["True_Sentiment"] = df[rating_col].apply(map_rating_to_sentiment)
    true_sentiment_available = True
    print("⭐ True_Sentiment column auto-generated based on ratings.\n")
else:
    print("⚠ No rating column found, evaluation will be skipped.\n")


def classify_sentiment(text: str):
    text = str(text).strip()

    # ----- STRICT PROMPT -----
    prompt = f"""
You are an ULTRA-STRICT sentiment classifier for English, Hindi, Hinglish, Code-mixed text, and Emojis.

Follow EXACTLY these rules:

✔ Classify sentiment based ONLY on emotional tone.
✔ Ignore sarcasm unless very obvious.
✔ Ignore filler words like "acha", "theek", "mast", etc.
✔ If text is mixed (good + bad), classify as "Negative".
✔ If meaning is unclear, select "Neutral".

You MUST output ONLY valid JSON. NO text outside JSON.

JSON FORMAT (mandatory):
{{
  "sentiment": "<Positive|Neutral|Negative>",
  "confidence": 0.xx
}}

Text: "{text}"
"""

    # -------- MODEL RUN HELPER --------
    def run_model(model_name):
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_completion_tokens=120,
            stream=True
        )
        collected = ""
        for chunk in completion:
            collected += chunk.choices[0].delta.content or ""
        return collected.strip()

    # -------- TRY PRIMARY MODEL (120B) --------
    response_text = ""
    try:
        print("⚡ Using primary model → 120B")
        response_text = run_model("openai/gpt-oss-120b")
    except:
        response_text = ""

    # -------- TRY FALLBACK MODEL (20B) --------
    if not response_text:
        try:
            print("⚡ Using fallback model → 20B")
            response_text = run_model("openai/gpt-oss-20b")
        except:
            response_text = ""

    # -------- JSON PARSING --------
    try:
        match = re.search(r"\{[^{}]*\}", response_text)
        if match:
            data = json.loads(match.group(0))
            s = data.get("sentiment", "").capitalize()
            c = float(data.get("confidence", 0.0))
            if s in ["Positive", "Neutral", "Negative"]:
                return s, c
    except:
        pass

    # -------- ⭐ THIRD FALLBACK: YOUR OVERRIDE LOGIC ⭐ --------
    review_lower = text.lower()

    positive_keywords = {
        "amazing": 2, "love": 2, "excellent": 2, "awesome": 2, "perfect": 2,
        "good": 1, "nice": 1, "satisfied": 1, "happy": 1, "great": 1
    }

    negative_keywords = {
        "worst": 3, "pathetic": 3, "useless": 3, "refund": 3, "terrible": 3,
        "bad": 2, "poor": 2, "slow": 2, "hang": 2, "heating": 2, "issue": 2,
        "problem": 1, "disappointed": 1
    }

    neutral_cues = ["okay", "fine", "average", "not bad", "expected"]

    # Calculate score
    score = sum(weight for word, weight in positive_keywords.items() if word in review_lower)
    score -= sum(weight for word, weight in negative_keywords.items() if word in review_lower)

    # Final fallback sentiment logic
    if score <= -3:
        return "Negative", 0.90
    elif score < 0:
        return "Negative", 0.75
    elif score >= 3:
        return "Positive", 0.90
    elif score > 0:
        return "Positive", 0.70

    if any(x in review_lower for x in neutral_cues) and score == 0:
        return "Neutral", 0.60

    if ("but" in review_lower or "however" in review_lower) and score != 0:
        return "Neutral", 0.55

    # Default fallback
    return "Neutral", 0.50

# ----------------------- CLEAN SENTIMENT PROCESSING -----------------------
sentiments, confidences = [], []
print("\n⚙️ Processing merged reviews with improved logic...\n")

for i, review in enumerate(df["Merged_Review"], start=1):

    s, c = classify_sentiment(review)

    sentiments.append(s)
    confidences.append(round(c, 3))

    if i % 20 == 0 or i == len(df):
        print(f"Processed {i}/{len(df)}")

    time.sleep(random.uniform(0.8, 1.6))

df["Sentiment_Label"] = sentiments
df["Confidence"] = confidences

print("\n✅ Sentiment classification completed.")

# ----------------------- CATEGORY DETECTION -----------------------
CATEGORIES = {
    "Battery":     ["battery", "charging", "charge", "backup", "drain", "heat"],
    "Camera":      ["camera", "photo", "picture", "image", "clarity"],
    "Performance": ["performance", "lag", "smooth", "hang", "speed", "processor", "slow"],
    "Display":     ["display", "screen", "brightness", "resolution"],
    "Value":       ["price", "money", "worth", "value", "cost"],
    "Design":      ["design", "look", "build", "color", "finish"],
    "Delivery":    ["delivery", "packaging", "received", "delay"]
}

def detect_category(text: str) -> str:
    t = text.lower()
    for cat, keywords in CATEGORIES.items():
        for k in keywords:
            if k in t:
                return cat
    return "General"

df["Category"] = df["Merged_Review"].apply(detect_category)
# ----------------------- EVALUATION METRICS -----------------------
metrics_df = pd.DataFrame()

if true_sentiment_available:

    print("\n📊 Running Evaluation Using Star Ratings...\n")

    y_true = df["True_Sentiment"]
    y_pred = df["Sentiment_Label"]

    metrics_df = pd.DataFrame({
        "Accuracy": [accuracy_score(y_true, y_pred)],
        "Precision (Macro)": [precision_score(y_true, y_pred, average="macro", zero_division=0)],
        "Recall (Macro)": [recall_score(y_true, y_pred, average="macro", zero_division=0)],
        "F1 Score (Macro)": [f1_score(y_true, y_pred, average="macro", zero_division=0)],
        "Cohen Kappa": [cohen_kappa_score(y_true, y_pred)]
    })

    print(metrics_df)
    print("\n📌 Classification Report:\n")
    print(classification_report(y_true, y_pred))

    cm = confusion_matrix(y_true, y_pred, labels=["Positive", "Neutral", "Negative"])
    plt.figure(figsize=(6,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Positive", "Neutral", "Negative"],
                yticklabels=["Positive", "Neutral", "Negative"])
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

else:
    print("⚠ No valid rating → Meaningful evaluation cannot be performed.\n")



# ----------------------- 📊 Sentiment Distribution Graph -----------------------
plt.figure(figsize=(8,5))
sns.countplot(data=df, x="Sentiment_Label")
plt.title("Sentiment Distribution")
plt.xlabel("Sentiment Type")
plt.ylabel("Count")
plt.show()


# ----------------------- 📊 Average Confidence Graph -----------------------
avg_conf = df.groupby("Sentiment_Label")["Confidence"].mean().reset_index()

plt.figure(figsize=(8,5))
sns.barplot(data=avg_conf, x="Sentiment_Label", y="Confidence")
plt.title("Average Model Confidence per Sentiment")
plt.ylabel("Avg Confidence Score")
plt.show()



# ----------------------- SAVE OUTPUT -----------------------
with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Processed_Data", index=False)
    if not metrics_df.empty:
        metrics_df.to_excel(writer, sheet_name="Evaluation_Metrics", index=False)

print(f"\n💾 File saved → {OUTPUT_FILE}")
print("\n🎉 Done!\n")
