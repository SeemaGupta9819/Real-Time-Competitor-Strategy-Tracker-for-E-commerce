from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re, json, time, random
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# ====================== CONFIG ======================
API_KEY = os.getenv("GROQ_API_KEY")
INPUT_FILE = r"/content/Reviews.xlsx"
OUTPUT_FILE = INPUT_FILE.replace(".xlsx", "_Output.xlsx")

ENABLE_LOGS = False  # Set False for silent processing

# ====================== INIT =======================
client = Groq(api_key=API_KEY)
df = pd.read_excel(INPUT_FILE)

# ====================== MERGE TITLE + BODY =======================
TITLE_COLUMN = "Review_Title"
BODY_COLUMN = "Review_Body"

df[TITLE_COLUMN] = df[TITLE_COLUMN].fillna("").astype(str)
df[BODY_COLUMN] = df[BODY_COLUMN].fillna("").astype(str)

df["Merged_Review"] = (df[TITLE_COLUMN] + " " + df[BODY_COLUMN]).str.strip()

print(f"📌 Loaded {len(df)} rows")
print("🧩 Created column → Merged_Review")


# ====================== STRICT SENTIMENT MODEL =======================
def query_model(model_name, prompt):
    """Runs a Groq model with streaming enabled and returns text."""
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_completion_tokens=120,
            stream=True
        )
        response = "".join(chunk.choices[0].delta.content or "" for chunk in completion)
        return response.strip()
    except:
        return ""


def classify_sentiment(text: str):
    """Predict sentiment using cascade fallback system."""
    
    prompt = f"""
    SYSTEM:
You are a strict sentiment classifier for English, Hindi, Hinglish, and Emojis.

Your ONLY job:
Return valid JSON with fields:
{{
  "sentiment": "Positive|Neutral|Negative",
  "confidence": 0.xx
}}

RULES (STRICT + MINIMAL):
- Judge ONLY emotional tone.
- Mixed emotions → Negative.
- Unclear/weak/ambiguous → Neutral.
- Ignore filler words (e.g., yaar, bro, pls, btw, etc.).
- Emoji sentiment rules:
  Positive: 🙂😊😄❤️✨👍  
  Negative: 😡🤬😢😭💔👎  
  Neutral: 😐🤔😶
- No explanations. No extra text. JSON ONLY.

CLASSIFY:
"{text}"
    """

    models = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b"
    ]

    for model in models:
        if ENABLE_LOGS: print(f"⚡ Trying model → {model}")
        response_text = query_model(model, prompt)

        match = re.search(r"\{[^{}]*\}", response_text)

        if match:
            try:
                data = json.loads(match.group(0))
                sentiment = data.get("sentiment", "").capitalize()
                conf = float(data.get("confidence", 0.0))
                if sentiment in ["Positive", "Neutral", "Negative"]:
                    return sentiment, conf
            except:
                pass

    # FINAL FALLBACK: Rule-based
    review = text.lower()

    positives = ["good", "nice", "excellent", "love", "amazing", "great", "perfect","smooth","best"]
    negatives = ["bad", "slow", "refund", "poor", "worst", "terrible", "heating", "hang", "issue","horibble"]

    score = sum(word in review for word in positives) - sum(word in review for word in negatives)

    if score > 1: return "Positive", 0.75
    if score < -1: return "Negative", 0.75
    return "Neutral", 0.50


# ====================== RUN CLASSIFICATION =======================
sentiments, confidence_scores = [], []

print("\n⚙️ Processing sentiment...")
for idx, review in enumerate(df["Merged_Review"], start=1):
    s, c = classify_sentiment(review)
    sentiments.append(s)
    confidence_scores.append(round(c, 3))

    if ENABLE_LOGS and idx % 20 == 0:
        print(f"Processed {idx}/{len(df)}")

    time.sleep(random.uniform(0.5, 1.2))  # controlled pacing

df["Sentiment_Label"] = sentiments
df["Confidence"] = confidence_scores

print("🎯 Sentiment classification complete.\n")


# ====================== CATEGORY DETECTION =======================
CATEGORIES = {
    "Battery": ["battery", "charging", "backup", "drain", "heat"],
    "Camera": ["camera", "photo", "picture", "clarity"],
    "Performance": ["performance", "lag", "smooth", "hang", "speed", "processor", "slow"],
    "Display": ["screen", "brightness", "resolution"],
    "Value": ["price", "money", "worth", "value"],
    "Design": ["design", "look", "build", "color", "ui"],
    "Delivery": ["delivery", "packaging", "received", "delay","box"]
}

def detect_category(text):
    txt = text.lower()
    for category, keywords in CATEGORIES.items():
        if any(k in txt for k in keywords):
            return category
    return "General"

df["Category"] = df["Merged_Review"].apply(detect_category)


# ====================== PLOTS =======================
sns.set(style="whitegrid", font_scale=1.1)

plt.figure(figsize=(8,5))
sns.countplot(data=df, x="Sentiment_Label")
plt.title("Sentiment Distribution")
plt.show()

plt.figure(figsize=(8,5))
sns.barplot(data=df.groupby("Sentiment_Label")["Confidence"].mean().reset_index(),
            x="Sentiment_Label", y="Confidence")
plt.title("Average Confidence Score")
plt.show()


# ====================== EXPORT =======================
df.to_excel(OUTPUT_FILE, index=False)
print(f"💾 File saved → {OUTPUT_FILE}")
print("\n🎉 Processing Completed Successfully!")
