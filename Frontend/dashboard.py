import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
import yagmail
import datetime
from datetime import datetime

if "sent_alerts_log" not in st.session_state:
    st.session_state.sent_alerts_log = []

EMAIL_SENDER = "seemag7738@gmail.com"

EMAIL_PASSWORD = "jjfvmoetuuzpzndt"    # 16-character Gmail app password
EMAIL_RECEIVER = "seemag7738@gmail.com"


st.set_page_config(page_title="Real-Time Competitor Strategy Tracker for E-commerce", layout="wide")

# Add main header
st.markdown(
    """
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <h1 style="margin: 0; font-size: 2.5rem; background: linear-gradient(120deg, #6366F1, #2DD4BF); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   background-clip: text;">
            Real-Time Competitor Strategy Tracker for E-commerce
        </h1>
        <p style="color: #475467; margin: 0.5rem 0 0 0; font-size: 1rem;">
            Amazon & Flipkart Intelligence Dashboard
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

THEME = {
    "primary": "#6366F1",        # Luminous indigo
    "secondary": "#2DD4BF",      # Aqua mint
    "accent": "#F43F5E",         # Coral pop
    "neutral_light": "#0F172A",  # Headline / text
    "neutral_mid": "#475467",    # Subtext
    "neutral_dark": "#F5F7FB",   # Page background
    "surface": "#FFFFFF",        # Cards / charts
    "surface_alt": "#EEF2FF",    # Highlight panels
}

TYPOGRAPHY = {
    "display": "Space Grotesk, 'Space Grotesk', sans-serif",
    "body": "Inter, 'Inter', sans-serif",
}

midnight_template = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(family=TYPOGRAPHY["body"], color=THEME["neutral_light"], size=13),
        xaxis=dict(
            gridcolor="rgba(71,84,103,0.16)",
            zeroline=False,
            showspikes=True,
            spikethickness=1,
            spikedash="dot",
            spikecolor=THEME["secondary"],
        ),
        yaxis=dict(
            gridcolor="rgba(71,84,103,0.16)",
            zeroline=False,
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(15,23,42,0.06)",
            borderwidth=1,
        ),
        margin=dict(l=50, r=40, t=60, b=45),
    )
)

pio.templates["midnight_pulse"] = midnight_template
px.defaults.template = "midnight_pulse"
px.defaults.color_discrete_sequence = [
    THEME["primary"],
    THEME["secondary"],
    THEME["accent"],
    "#22D3EE",
    "#A855F7",
]


def style_figure(fig: go.Figure, title: str | None = None) -> go.Figure:
    """Apply dashboard styling to Plotly figures."""
    fig.update_layout(
        paper_bgcolor=THEME["neutral_dark"],
        plot_bgcolor=THEME["neutral_dark"],
        margin=dict(l=40, r=30, t=55 if title else 35, b=45),
        title=dict(
            text=title,
            font=dict(family=TYPOGRAPHY["display"], size=20, color=THEME["neutral_light"]),
            x=0.02,
            pad=dict(t=20),
        )
        if title
        else None,
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(99,102,241,0.12)",
        zeroline=False,
        ticks="outside",
        tickcolor="rgba(71,84,103,0.25)",
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(99,102,241,0.12)",
        zeroline=False,
        ticks="outside",
        tickcolor="rgba(71,84,103,0.25)",
    )
    return fig

st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

        :root {{
            --color-primary: {THEME["primary"]};
            --color-secondary: {THEME["secondary"]};
            --color-accent: {THEME["accent"]};
            --color-light: {THEME["neutral_light"]};
            --color-mid: {THEME["neutral_mid"]};
            --color-dark: {THEME["neutral_dark"]};
            --color-surface: {THEME["surface"]};
            --color-surface-alt: {THEME["surface_alt"]};
            --radius-lg: 22px;
            --radius-md: 14px;
            --radius-sm: 10px;
            --shadow-soft: 0 24px 50px rgba(15, 23, 42, 0.12);
            --shadow-card: 0 35px 80px rgba(15, 23, 42, 0.12);
            --font-display: {TYPOGRAPHY["display"]};
            --font-body: {TYPOGRAPHY["body"]};
        }}

        html, body, [data-testid="stAppViewContainer"] {{
            background: radial-gradient(circle at 15% 20%, rgba(99,102,241,0.15), transparent 40%),
                        radial-gradient(circle at 85% 5%, rgba(45,212,191,0.18), transparent 45%),
                        var(--color-dark) !important;
            color: var(--color-light) !important;
            font-family: var(--font-body);
        }}

        .block-container {{
            padding: 1.5rem 2.75rem 3rem 2.75rem;
        }}

        h1, h2, h3, h4 {{
            font-family: var(--font-display);
            letter-spacing: -0.02em;
            color: var(--color-light);
        }}

        h1 {{
            font-size: 2.35rem;
            font-weight: 600;
        }}

        h2 {{
            font-size: 1.55rem;
            margin-top: 2rem;
        }}

        .stMarkdown p, .stMarkdown li {{
            color: var(--color-mid);
            line-height: 1.6;
        }}

        .glass-card {{
            background: linear-gradient(145deg, rgba(255,255,255,0.95), rgba(238,242,255,0.95));
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            border: 1px solid rgba(148, 163, 184, 0.25);
            box-shadow: var(--shadow-card);
        }}

        div[data-testid="stMetric"] {{
            background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(45,212,191,0.12));
            border-radius: var(--radius-md);
            padding: 1rem 1.25rem;
            border: 1px solid rgba(99,102,241,0.2);
            box-shadow: var(--shadow-soft);
        }}

        div[data-testid="stMetric"] label {{
            color: var(--color-mid);
            font-size: 0.85rem;
        }}

        div[data-testid="stMetric"] div {{
            color: var(--color-light);
            font-size: 1.4rem;
            font-weight: 600;
        }}

        .stButton>button {{
            border-radius: var(--radius-md);
            font-weight: 600;
            padding: 0.75rem 1.4rem;
            border: none;
            background: linear-gradient(120deg, var(--color-primary), var(--color-secondary));
            color: white;
            transition: all 0.2s ease;
            box-shadow: 0 18px 35px rgba(99,102,241,0.25);
        }}

        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 20px 40px rgba(45,212,191,0.25);
        }}

        .stButton>button[data-baseweb="button"][class*="secondary"] {{
            background: var(--color-surface);
            border: 1px solid rgba(15, 23, 42, 0.08);
            color: var(--color-light);
            box-shadow: none;
        }}

        input, textarea, select, .stTextInput>div>div>input {{
            border-radius: var(--radius-sm) !important;
            border: 1px solid rgba(148, 163, 184, 0.4) !important;
            background-color: var(--color-surface) !important;
            color: var(--color-light) !important;
            box-shadow: inset 0 2px 6px rgba(15, 23, 42, 0.03);
        }}

        .stSelectbox label, .stTextInput label {{
            color: var(--color-mid) !important;
            font-weight: 500;
            letter-spacing: 0.01em;
        }}

        .stDataFrame, .stTable {{
            background: var(--color-surface);
            border-radius: var(--radius-lg);
            padding: 1rem;
            box-shadow: var(--shadow-card);
            border: 1px solid rgba(148, 163, 184, 0.18);
        }}

        .stPlotlyChart {{
            background: transparent;
            border: none;
            border-radius: 0;
            padding: 0;
            box-shadow: none;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
        }}

        .stTabs [data-baseweb="tab"] {{
            padding: 0.75rem 1.25rem;
            border-radius: var(--radius-md);
            background-color: var(--color-surface);
            border: 1px solid rgba(148, 163, 184, 0.4);
            color: var(--color-mid);
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(120deg, rgba(99,102,241,0.22), rgba(45,212,191,0.2));
            border-color: rgba(99,102,241,0.35);
            color: var(--color-light);
        }}

        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(71,84,103,0.25), transparent);
            margin: 2rem 0;
        }}

        .stAlert {{
            background: linear-gradient(120deg, rgba(244,63,94,0.12), rgba(249,115,22,0.12));
            border-radius: var(--radius-md);
            border: 1px solid rgba(244,63,94,0.35);
            color: var(--color-light);
        }}

        footer, .viewerBadge_container__1QSob {{
            display: none;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_SOURCES = {
    "trend": BASE_DIR / "Trend_Analysis" / "trend_analysis.csv",
    "daily": BASE_DIR / "processed_dataset" / "daily_price_dataset.csv",
    "amazon_forecast": BASE_DIR / "Forecasting_Model" / "amazon_output.csv",
    "flipkart_forecast": BASE_DIR / "Forecasting_Model" / "flipkart_output.csv",
    "reviews": BASE_DIR / "Sentiment_Analysis" / "Reviews_Output (5).xlsx",
}


@st.cache_data(ttl=600)
def load_table(path: Path, kind: str = "csv") -> pd.DataFrame:
    try:
        if kind == "excel":
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path)
    except FileNotFoundError:
        st.error(f"File not found: {path}")
        return pd.DataFrame()
    except Exception as exc:
        st.error(f"Unable to load {path.name}: {exc}")
        return pd.DataFrame()
    return df


def ensure_datetime(df: pd.DataFrame, column: str) -> pd.DataFrame:
    if column in df.columns:
        df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


def parse_percentage(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace("%", "", regex=False), errors="coerce")

def render_product_header():
    st.markdown("## 🛍️ Product Details")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image("imge.jpg", use_container_width=True)  # put product.jpg in your folder

    with col2:
        st.markdown("""
            ### Apple iPhone 15 (256GB)
            - **Brand:** Apple  
            - **Category:** Smartphone  
            - **Rating:** ⭐ 4.6  
            - **Platforms:** Amazon & Flipkart
            - Description
                    Experience the iPhone 15 – your dynamic companion. Dynamic I
                    sland ensures you stay 
                    connected, bubbling up alerts seamlessly while you're busy. Its 
                    durable design features infused glass and aerospace-grade aluminum, 
                    making it dependable and resistant to water and dust. Capture life 
                    with precision using the 48 MP Main Camera, perfect for any shot. 
                    Powered by the A16 Bionic Processor, it excels in computational 
                    photography and more, all while conserving battery life. Plus, it's USB-C compatible, 
                    simplifying your charging needs. Elevate your tech game with the 
                    iPhone 15 – innovation at your fingertips. Goodbye cable clutter, 
                    hello convenience.
        """)

def send_alert_email(subject, body, receiver_email):

    sender_email = "seemag7738@gmail.com"
    app_password = "jjfvmoetuuzpzndt"  # Gmail App Password

    print("\n===== EMAIL DEBUG START =====")
    print(f"📧 Sending to: {receiver_email}")
    print(f"📌 Subject: {subject}")
    print(f"📄 Body: {body}")
    print("=============================\n")

    try:
        yag = yagmail.SMTP(sender_email, app_password)

        yag.send(
            to=receiver_email,
            subject=subject,
            contents=body
        )

        print("🎉 SUCCESS: Email sent!\n")

        # Logging
        st.session_state.sent_alerts_log.append(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | SENT → {receiver_email} | {subject}"
        )

        return True

    except Exception as e:
        print(f"❌ ERROR SENDING EMAIL → {e}\n")

        st.session_state.sent_alerts_log.append(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | FAILED → {receiver_email} | {subject} | Error: {e}"
        )

        return False



def render_trend_page(trend_df: pd.DataFrame, daily_df: pd.DataFrame) -> None:
    render_product_header()   # ← ADD THIS LINE
    
    st.title("Trend Analysis")
    if trend_df.empty:
        st.info("Trend analysis data is not available.")
        return

    df = trend_df.copy()
    df = ensure_datetime(df, "date").sort_values("date")

    price_cols = ["date", "amazon_price", "flipkart_price"]
    price_data = df[price_cols].dropna()
    if not price_data.empty:
        trend_long = price_data.melt("date", var_name="Platform", value_name="Price")
        fig = px.line(trend_long, x="date", y="Price", color="Platform", markers=True)
        fig = style_figure(fig, "Amazon vs Flipkart Price Trajectory")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Price columns are missing from the trend dataset.")

    # Use discounts from daily_dataset
    if not daily_df.empty:
        daily_copy = ensure_datetime(daily_df.copy(), "date").sort_values("date")
        discount_cols = ["date", "amazon_discount", "flipkart_discount"]
        discount_data = daily_copy[discount_cols].dropna()
        if not discount_data.empty:
            # Parse percentage values
            discount_data["amazon_discount_pct"] = parse_percentage(discount_data["amazon_discount"])
            discount_data["flipkart_discount_pct"] = parse_percentage(discount_data["flipkart_discount"])
            discount_display = discount_data[["date", "amazon_discount_pct", "flipkart_discount_pct"]].dropna()
            if not discount_display.empty:
                discount_long = discount_display.melt("date", var_name="Platform", value_name="Discount %")
                disc_fig = px.area(discount_long, x="date", y="Discount %", color="Platform", groupnorm="")
                disc_fig = style_figure(disc_fig, "Discount Movement")
                st.plotly_chart(disc_fig, use_container_width=True)

    if "price_diff" in df.columns:
        diff_fig = px.bar(df.tail(60), x="date", y="price_diff")
        diff_fig = style_figure(diff_fig, "Recent Price Differences (Amazon - Flipkart)")
        st.plotly_chart(diff_fig, use_container_width=True)

    st.subheader("Recent Trend Records")
    with st.expander("📊 Dataset Options", expanded=False):
        filter_cols = st.columns(5)
        
        with filter_cols[0]:
            rows_to_show = st.slider("Rows to display", 10, 200, 50, 10, key="trend_rows")
        
        with filter_cols[1]:
            company = st.multiselect("Select Company", ["Amazon", "Flipkart"], default=["Amazon", "Flipkart"], key="trend_company")
        
        with filter_cols[2]:
            date_range = None
            if "date" in df.columns:
                df_sorted = df.dropna(subset=["date"]).sort_values("date")
                if not df_sorted.empty:
                    min_date = pd.to_datetime(df_sorted["date"].iloc[0]).date()
                    max_date = pd.to_datetime(df_sorted["date"].iloc[-1]).date()
                    date_range = st.date_input("Date range", value=(min_date, max_date), key="trend_date")
        
        with filter_cols[3]:
            all_prices = pd.concat([
                pd.to_numeric(df["amazon_price"], errors="coerce"),
                pd.to_numeric(df["flipkart_price"], errors="coerce")
            ]).dropna()
            if len(all_prices) > 0:
                min_price = float(all_prices.min())
                max_price = float(all_prices.max())
                price_range = st.slider("Price (INR)", min_price, max_price, (min_price, max_price), 100.0, key="trend_price")
        
        with filter_cols[4]:
            if st.button("🔄 Refresh Data", key="trend_refresh"):
                st.rerun()
    
    # Apply filters
    display_df = df.copy()
    
    # Apply date range filter
    if "date" in display_df.columns and len(date_range) == 2:
        display_df["date"] = pd.to_datetime(display_df["date"])
        display_df = display_df[(display_df["date"].dt.date >= date_range[0]) & (display_df["date"].dt.date <= date_range[1])]
    
    # Apply price range filter
    if len(price_range) == 2:
        if "amazon_price" in display_df.columns:
            display_df = display_df[(pd.to_numeric(display_df["amazon_price"], errors="coerce") >= price_range[0]) & (pd.to_numeric(display_df["amazon_price"], errors="coerce") <= price_range[1])]
        if "flipkart_price" in display_df.columns:
            display_df = display_df[(pd.to_numeric(display_df["flipkart_price"], errors="coerce") >= price_range[0]) & (pd.to_numeric(display_df["flipkart_price"], errors="coerce") <= price_range[1])]
    
    # Apply company filter
    if company and len(company) < 2:
        if len(company) == 1:
            if company[0] == "Amazon":
                display_df = display_df[["date", "amazon_price", "amazon_discount"]].dropna(subset=["amazon_price"])
            else:
                display_df = display_df[["date", "flipkart_price", "flipkart_discount"]].dropna(subset=["flipkart_price"])
    
    display_df = display_df.tail(rows_to_show)
    st.dataframe(display_df, use_container_width=True)


def render_reviews_page(df: pd.DataFrame) -> None:
    st.title("Review Output Insights")
    if df.empty:
        st.info("Review output file is empty or missing.")
        return

    df = df.copy()
    df = ensure_datetime(df, "Review_Date")
    sentiment_counts = (
        df.groupby("Sentiment_Label", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    col1, col2 = st.columns(2)
    col1.metric("Total Reviews", len(df))
    positive_share = (
        sentiment_counts.loc[sentiment_counts["Sentiment_Label"] == "Positive", "count"].sum()
        / max(len(df), 1)
        * 100
    )
    col2.metric("Positive Share", f"{positive_share:.1f}%")

    if not sentiment_counts.empty:
        fig = px.bar(sentiment_counts, x="Sentiment_Label", y="count", color="Sentiment_Label")
        fig = style_figure(fig, "Sentiment Distribution")
        st.plotly_chart(fig, use_container_width=True)

    if "Review_Stars" in df.columns:
        stars_fig = px.histogram(df, x="Review_Stars", nbins=10)
        stars_fig = style_figure(stars_fig, "Rating Spread")
        st.plotly_chart(stars_fig, use_container_width=True)

    if "Category" in df.columns:
        top_categories = (
            df.groupby("Category")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(10)
        )
        cat_fig = px.bar(top_categories, x="Category", y="count")
        cat_fig = style_figure(cat_fig, "Top Review Categories")
        st.plotly_chart(cat_fig, use_container_width=True)

    st.subheader("Latest Reviews")
    with st.expander("📊 Dataset Options", expanded=False):
        filter_cols = st.columns(4)
        
        with filter_cols[0]:
            rows_to_show = st.slider("Rows to display", 10, 200, 50, 10, key="reviews_rows")
        
        with filter_cols[1]:
            # Category filter
            selected_categories = None
            if "Category" in df.columns:
                available_categories = df["Category"].dropna().unique().tolist()
                if available_categories:
                    selected_categories = st.multiselect("Select Categories", available_categories, default=available_categories, key="reviews_category")
        
        with filter_cols[2]:
            date_range = None
            if "Review_Date" in df.columns:
                df_sorted = df.dropna(subset=["Review_Date"]).sort_values("Review_Date")
                if not df_sorted.empty:
                    min_date = pd.to_datetime(df_sorted["Review_Date"].iloc[0]).date()
                    max_date = pd.to_datetime(df_sorted["Review_Date"].iloc[-1]).date()
                    date_range = st.date_input("Date range", value=(min_date, max_date), key="reviews_date")
        
        with filter_cols[3]:
            if st.button("🔄 Refresh Data", key="reviews_refresh"):
                st.rerun()
    
    # Apply filters
    display_df = df.copy()
    
    # Apply category filter
    if selected_categories and "Category" in display_df.columns:
        display_df = display_df[display_df["Category"].isin(selected_categories)]
    
    # Apply date range filter
    if "Review_Date" in display_df.columns and date_range and len(date_range) == 2:
        display_df["Review_Date"] = pd.to_datetime(display_df["Review_Date"], errors="coerce")
        display_df = display_df[(display_df["Review_Date"].dt.date >= date_range[0]) & (display_df["Review_Date"].dt.date <= date_range[1])]
    
    display_df = display_df.sort_values("Review_Date", ascending=False, na_position="last").head(rows_to_show)
    st.dataframe(display_df, use_container_width=True)


def render_forecast_page(df: pd.DataFrame, label: str) -> None:
    df = df.copy()
    df = ensure_datetime(df, "date").sort_values("date")
    # ========================================
    # AUTO CALCULATE EM (Same for both models)
    # ========================================
    if {"actual", "predicted"}.issubset(df.columns):

        df_clean = df.dropna(subset=["actual", "predicted"])

        if not df_clean.empty:
            df_clean["error"] = df_clean["actual"] - df_clean["predicted"]
            df_clean["abs_error"] = df_clean["error"].abs()
            df_clean["sq_error"] = df_clean["error"] ** 2
            df_clean["ape"] = (df_clean["abs_error"] / df_clean["actual"]) * 100

            MAE = df_clean["abs_error"].mean()
            RMSE = (df_clean["sq_error"].mean()) ** 0.5
            MAPE = df_clean["ape"].mean()

            st.markdown(f"### 📊 {label} Model Evaluation Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("MAE", f"{MAE:,.2f}")
            col2.metric("RMSE", f"{RMSE:,.2f}")
            col3.metric("MAPE", f"{MAPE:.2f}%")
            st.markdown("---")

    # ----------------------------------------
    # FORECAST DASHBOARD
    # ----------------------------------------
    st.title(f"{label} Forecast Dashboard")
    
    if df.empty:
        st.info(f"{label} forecast data is not available.")
        return

    df = df.copy()
    df = ensure_datetime(df, "date").sort_values("date")

    col1, col2 = st.columns(2)
    latest = df.dropna(subset=["actual"]).tail(1)
    if not latest.empty:
        latest_row = latest.iloc[0]
        col1.metric("Latest Actual Price", f"INR {latest_row['actual']:,.0f}")
        col2.metric("Latest Predicted Price", f"INR {latest_row['predicted']:,.0f}")

    forecast_long = df.melt(
        "date",
        value_vars=["actual", "predicted"],
        var_name="Series",
        value_name="Price",
    )
    
    label_map = {"actual": "Actual Price", "predicted": "Predicted Price"}
    forecast_long["Series Label"] = forecast_long["Series"].map(label_map)

    fig = px.line(
        forecast_long,
        x="date",
        y="Price",
        color="Series Label",
        line_dash="Series Label",
        markers=True,
        color_discrete_map={
            "Actual Price": THEME["primary"],
            "Predicted Price": THEME["secondary"],
        },
    )
    fig = style_figure(fig, f"{label} Actual vs Predicted Prices")
    st.plotly_chart(fig, use_container_width=True)

    if {"actual", "predicted"}.issubset(df.columns):
        df["abs_error"] = (df["actual"] - df["predicted"]).abs()
        error_fig = px.area(
            df.tail(60),
            x="date",
            y="abs_error",
            color_discrete_sequence=[THEME["accent"]],
        )
        error_fig = style_figure(error_fig, f"{label} Absolute Forecast Error (latest 60 points)")
        st.plotly_chart(error_fig, use_container_width=True)

    # -------------------------------
    # TABLE + FILTERS
    # -------------------------------
    st.subheader("Forecast Table")
    with st.expander("📊 Dataset Options", expanded=False):
        filter_cols = st.columns(4)
        
        with filter_cols[0]:
            rows_to_show = st.slider("Rows to display", 10, 200, 80, 10, key=f"forecast_{label.lower()}_rows")
        
        with filter_cols[1]:
            date_range = None
            if "date" in df.columns:
                df_sorted = df.dropna(subset=["date"]).sort_values("date")
                if not df_sorted.empty:
                    min_date = pd.to_datetime(df_sorted["date"].iloc[0]).date()
                    max_date = pd.to_datetime(df_sorted["date"].iloc[-1]).date()
                    date_range = st.date_input("Date range", value=(min_date, max_date), key=f"forecast_{label.lower()}_date")
        
        with filter_cols[2]:
            price_range = None
            if "actual" in df.columns and "predicted" in df.columns:
                all_prices = pd.concat([df["actual"], df["predicted"]]).dropna()
                if len(all_prices) > 0:
                    min_price = float(all_prices.min())
                    max_price = float(all_prices.max())
                    price_range = st.slider("Price range (INR)", min_price, max_price, (min_price, max_price), 100.0, key=f"forecast_{label.lower()}_price")
        
        with filter_cols[3]:
            if st.button("🔄 Refresh Data", key=f"forecast_{label.lower()}_refresh"):
                st.rerun()
    
    # Apply filters
    display_df = df.copy()
    
    if date_range and len(date_range) == 2:
        display_df["date"] = pd.to_datetime(display_df["date"], errors="coerce")
        display_df = display_df[(display_df["date"].dt.date >= date_range[0]) & (display_df["date"].dt.date <= date_range[1])]
    
    if price_range and len(price_range) == 2:
        display_df = display_df[(display_df["actual"] >= price_range[0]) & (display_df["actual"] <= price_range[1])]
    
    display_df = display_df.tail(rows_to_show)
    st.dataframe(display_df, use_container_width=True)



def render_daily_page(df: pd.DataFrame) -> None:
    st.title("Daily Dataset Overview")
    if df.empty:
        st.info("Daily dataset is not available.")
        return

    df = df.copy()
    df = ensure_datetime(df, "date").sort_values("date")
    history_window = st.slider("History window (days)", 30, 180, 90, 15)
    recent = df.tail(history_window)

    price_long = recent[["date", "amazon_price", "flipkart_price"]].melt("date", var_name="Platform", value_name="Price")
    fig = px.line(price_long, x="date", y="Price", color="Platform", markers=True)
    fig = style_figure(fig, "Daily Price Book")
    st.plotly_chart(fig, use_container_width=True)

    # Parse discount percentages from daily dataset
    recent_copy = recent.copy()
    recent_copy["amazon_discount_pct"] = parse_percentage(recent_copy["amazon_discount"])
    recent_copy["flipkart_discount_pct"] = parse_percentage(recent_copy["flipkart_discount"])
    discount_data = recent_copy[["date", "amazon_discount_pct", "flipkart_discount_pct"]].dropna()
    if not discount_data.empty:
        discount_long = discount_data.melt("date", var_name="Platform", value_name="Discount %")
        disc_fig = px.line(discount_long, x="date", y="Discount %", color="Platform")
        disc_fig = style_figure(disc_fig, "Discount Trend")
        st.plotly_chart(disc_fig, use_container_width=True)

    st.subheader("Daily Dataset")
    with st.expander("📊 Dataset Options", expanded=False):
        filter_cols = st.columns(5)
        
        with filter_cols[0]:
            rows_to_show = st.slider("Rows to display", 10, 300, 100, 10, key="daily_rows")
        
        with filter_cols[1]:
            company = st.multiselect("Select Company", ["Amazon", "Flipkart"], default=["Amazon", "Flipkart"], key="daily_company")
        
        with filter_cols[2]:
            date_range = None
            if "date" in df.columns:
                df_sorted = df.dropna(subset=["date"]).sort_values("date")
                if not df_sorted.empty:
                    min_date = pd.to_datetime(df_sorted["date"].iloc[0]).date()
                    max_date = pd.to_datetime(df_sorted["date"].iloc[-1]).date()
                    date_range = st.date_input("Date range", value=(min_date, max_date), key="daily_date")
        
        with filter_cols[3]:
            all_prices = pd.concat([
                pd.to_numeric(df["amazon_price"], errors="coerce"),
                pd.to_numeric(df["flipkart_price"], errors="coerce")
            ]).dropna()
            if len(all_prices) > 0:
                min_price = float(all_prices.min())
                max_price = float(all_prices.max())
                price_range = st.slider("Price (INR)", min_price, max_price, (min_price, max_price), 100.0, key="daily_price")
        
        with filter_cols[4]:
            if st.button("🔄 Refresh Data", key="daily_refresh"):
                st.rerun()
    
    # Apply filters
    display_df = df.copy()
    
    # Apply date range filter
    if "date" in display_df.columns and len(date_range) == 2:
        display_df["date"] = pd.to_datetime(display_df["date"])
        display_df = display_df[(display_df["date"].dt.date >= date_range[0]) & (display_df["date"].dt.date <= date_range[1])]
    
    # Apply price range filter
    if len(price_range) == 2:
        if "amazon_price" in display_df.columns:
            display_df = display_df[(pd.to_numeric(display_df["amazon_price"], errors="coerce") >= price_range[0]) & (pd.to_numeric(display_df["amazon_price"], errors="coerce") <= price_range[1])]
        if "flipkart_price" in display_df.columns:
            display_df = display_df[(pd.to_numeric(display_df["flipkart_price"], errors="coerce") >= price_range[0]) & (pd.to_numeric(display_df["flipkart_price"], errors="coerce") <= price_range[1])]
    
    # Apply company filter
    if company and len(company) < 2:
        if len(company) == 1:
            if company[0] == "Amazon":
                display_df = display_df[["date", "amazon_price", "amazon_discount"]].dropna(subset=["amazon_price"])
            else:
                display_df = display_df[["date", "flipkart_price", "flipkart_discount"]].dropna(subset=["flipkart_price"])
    
    display_df = display_df.tail(rows_to_show)
    st.dataframe(display_df, use_container_width=True)


def render_comparison_page(trend_df: pd.DataFrame,
                           daily_df: pd.DataFrame,
                           amazon_df: pd.DataFrame,
                           flipkart_df: pd.DataFrame) -> None:
    st.title("Cross-Web Comparison")

    if daily_df.empty and trend_df.empty:
        st.info("Comparison needs at least one dataset (trend or daily).")
        return

    # Add graph selection filters
    st.subheader("📊 Graph Selection & Filters")
    with st.expander("Configure Graphs to Display", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Select Graphs to Display:**")
            show_daily_prices = st.checkbox("✅ Daily Price Comparison (Amazon vs Flipkart)", value=True, key="show_daily_prices")
            show_amazon_trend = st.checkbox("✅ Amazon Price Trend", value=True, key="show_amazon_trend")
            show_flipkart_trend = st.checkbox("✅ Flipkart Price Trend", value=True, key="show_flipkart_trend")
        
        with col2:
            st.markdown("**Forecast Graphs:**")
            show_amazon_forecast = st.checkbox("✅ Amazon Forecast (Actual vs Predicted)", value=True, key="show_amazon_forecast")
            show_flipkart_forecast = st.checkbox("✅ Flipkart Forecast (Actual vs Predicted)", value=True, key="show_flipkart_forecast")
            show_price_spread = st.checkbox("✅ Price Spread Comparison", value=True, key="show_price_spread")
        
        # Common filters
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            if not daily_df.empty:
                comparison_window = st.slider("Daily Comparison Window (days)", 30, 240, 120, 30, key="comparison_window")
        
        with col_filter2:
            selected_companies = st.multiselect(
                "Companies to Compare",
                ["Amazon", "Flipkart"],
                default=["Amazon", "Flipkart"],
                key="comparison_companies"
            )
        
        with col_filter3:
            if st.button("🔄 Refresh All Graphs", key="comparison_refresh"):
                st.rerun()

    # Display metrics
    col1, col2, col3 = st.columns(3)
    if not daily_df.empty:
        daily_sorted = ensure_datetime(daily_df.copy(), "date").sort_values("date")
        if not daily_sorted.empty:
            latest_daily = daily_sorted.iloc[-1]
            col1.metric("Amazon Latest", f"INR {latest_daily['amazon_price']:,.0f}")
            col2.metric("Flipkart Latest", f"INR {latest_daily['flipkart_price']:,.0f}")
            diff = latest_daily["amazon_price"] - latest_daily["flipkart_price"]
            col3.metric("Price Difference", f"INR {diff:,.0f}")

    st.markdown("---")

    # Daily Price Comparison
    if show_daily_prices and not daily_df.empty:
        st.subheader("💰 Daily Price Comparison (Amazon vs Flipkart)")
        recent = ensure_datetime(daily_df.copy(), "date").sort_values("date").tail(comparison_window)
        long_df = recent[["date", "amazon_price", "flipkart_price"]].melt(
            "date", var_name="Platform", value_name="Price"
        )
        
        # Filter by selected companies
        if len(selected_companies) < 2:
            company_map = {"Amazon": "amazon_price", "Flipkart": "flipkart_price"}
            for company in selected_companies:
                long_df = long_df[long_df["Platform"] == company]
        
        fig = px.line(long_df, x="date", y="Price", color="Platform", markers=True)
        fig = style_figure(fig, "Daily Price Comparison")
        st.plotly_chart(fig, use_container_width=True)

    # Amazon Trend
    if show_amazon_trend and not daily_df.empty:
        st.subheader("📈 Amazon Price Trend")
        recent = ensure_datetime(daily_df.copy(), "date").sort_values("date").tail(comparison_window)
        amazon_trend = recent[["date", "amazon_price"]].dropna()
        
        if not amazon_trend.empty:
            fig = px.line(amazon_trend, x="date", y="amazon_price", markers=True)
            fig = style_figure(fig, "Amazon Price Trend")
            st.plotly_chart(fig, use_container_width=True)

    # Flipkart Trend
    if show_flipkart_trend and not daily_df.empty:
        st.subheader("📈 Flipkart Price Trend")
        recent = ensure_datetime(daily_df.copy(), "date").sort_values("date").tail(comparison_window)
        flipkart_trend = recent[["date", "flipkart_price"]].dropna()
        
        if not flipkart_trend.empty:
            fig = px.line(flipkart_trend, x="date", y="flipkart_price", markers=True, line_shape="spline")
            fig.update_traces(line_color=THEME["secondary"])
            fig = style_figure(fig, "Flipkart Price Trend")
            st.plotly_chart(fig, use_container_width=True)

    # Amazon Forecast
    if show_amazon_forecast and not amazon_df.empty:
        st.subheader("🔮 Amazon Forecast (Actual vs Predicted)")
        amazon_copy = ensure_datetime(amazon_df.copy(), "date").sort_values("date")
        
        forecast_long = amazon_copy.melt(
            "date",
            value_vars=["actual", "predicted"],
            var_name="Series",
            value_name="Price",
        )
        label_map = {"actual": "Actual Price", "predicted": "Predicted Price"}
        forecast_long["Series Label"] = forecast_long["Series"].map(label_map)
        
        fig = px.line(
            forecast_long,
            x="date",
            y="Price",
            color="Series Label",
            line_dash="Series Label",
            markers=True,
            color_discrete_map={
                "Actual Price": THEME["primary"],
                "Predicted Price": THEME["secondary"],
            },
        )
        fig = style_figure(fig, "Amazon Actual vs Predicted Prices")
        st.plotly_chart(fig, use_container_width=True)

    # Flipkart Forecast
    if show_flipkart_forecast and not flipkart_df.empty:
        st.subheader("🔮 Flipkart Forecast (Actual vs Predicted)")
        flipkart_copy = ensure_datetime(flipkart_df.copy(), "date").sort_values("date")
        
        forecast_long = flipkart_copy.melt(
            "date",
            value_vars=["actual", "predicted"],
            var_name="Series",
            value_name="Price",
        )
        label_map = {"actual": "Actual Price", "predicted": "Predicted Price"}
        forecast_long["Series Label"] = forecast_long["Series"].map(label_map)
        
        fig = px.line(
            forecast_long,
            x="date",
            y="Price",
            color="Series Label",
            line_dash="Series Label",
            markers=True,
            color_discrete_map={
                "Actual Price": THEME["primary"],
                "Predicted Price": THEME["accent"],
            },
        )
        fig = style_figure(fig, "Flipkart Actual vs Predicted Prices")
        st.plotly_chart(fig, use_container_width=True)

    # Price Spread Comparison
    if show_price_spread and not trend_df.empty:
        st.subheader("📊 Price Spread Comparison (Amazon - Flipkart)")
        trend_subset = trend_df.copy()
        trend_subset = ensure_datetime(trend_subset, "date").sort_values("date")
        
        if "price_diff" in trend_subset.columns:
            diff_fig = px.line(trend_subset.tail(180), x="date", y="price_diff", markers=True)
            diff_fig = style_figure(diff_fig, "Price Spread Over Time")
            st.plotly_chart(diff_fig, use_container_width=True)

    # Combined Forecast Comparison
    if not (amazon_df.empty or flipkart_df.empty):
        st.markdown("---")
        st.subheader("🎯 Combined Forecast Comparison Across Platforms")
        amazon = ensure_datetime(amazon_df.copy(), "date").assign(Platform="Amazon")
        flipkart = ensure_datetime(flipkart_df.copy(), "date").assign(Platform="Flipkart")
        combined = pd.concat([amazon, flipkart], ignore_index=True)
        combined_long = combined.melt(
            id_vars=["date", "Platform"],
            value_vars=["actual", "predicted"],
            var_name="Series",
            value_name="Price",
        )
        combined_long["Curve"] = combined_long["Platform"] + " - " + combined_long["Series"].str.replace(
            "_price", "", regex=False
        ).str.title()
        
        # Filter by selected companies
        if len(selected_companies) < 2:
            combined_long = combined_long[combined_long["Platform"].isin(selected_companies)]
        
        forecast_fig = px.line(combined_long, x="date", y="Price", color="Curve", markers=True)
        forecast_fig = style_figure(forecast_fig, "All Forecasts Comparison")
        st.plotly_chart(forecast_fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Source Data Snapshots")
    tabs = st.tabs(["Trend", "Daily", "Amazon Forecast", "Flipkart Forecast"])
    with tabs[0]:
        st.dataframe(trend_df.tail(40), use_container_width=True)
    with tabs[1]:
        st.dataframe(daily_df.tail(40), use_container_width=True)
    with tabs[2]:
        st.dataframe(amazon_df.tail(40), use_container_width=True)
    with tabs[3]:
        st.dataframe(flipkart_df.tail(40), use_container_width=True)


def render_notifications_page(trend_df: pd.DataFrame):

    st.title("📧 Price Spike Alerts")

    # Session state initialization
    if "sent_spike_alerts" not in st.session_state:
        st.session_state.sent_spike_alerts = set()

    if "sent_alerts_log" not in st.session_state:
        st.session_state.sent_alerts_log = []

    # This controls auto-run email
    if "auto_sent_once" not in st.session_state:
        st.session_state.auto_sent_once = False

    st.markdown("---")

    # UI
    col1, col2 = st.columns([3, 1])

    with col1:
        receiver = st.text_input("📧 Email Address",
                                 EMAIL_RECEIVER,
                                 key="alert_email",
                                 placeholder="your-email@gmail.com")

    with col2:
        st.write("")
        manual_click = st.button("🚀 Send Latest Spike", width="stretch")   # New Streamlit style

    # Function to check last row and send email if spike
    def check_and_send_latest_spike():
        if trend_df.empty or "price_diff" not in trend_df.columns:
            st.info("No data available.")
            return

        # Get last row
        last_row = ensure_datetime(trend_df.copy(), "date").sort_values("date").iloc[-1]

        date = pd.to_datetime(last_row["date"], errors="coerce")
        price_diff = float(last_row["price_diff"])
        threshold = 3000

        # Check spike
        if abs(price_diff) < threshold:
            st.info("No spike detected in the latest row.")
            return

        # Identify higher/lower
        higher = "Amazon" if price_diff > 0 else "Flipkart"
        lower  = "Flipkart" if price_diff > 0 else "Amazon"

        diff_amount = abs(price_diff)

        # Unique alert ID
        alert_id = f"{receiver}_spike_{date.strftime('%Y%m%d')}_{higher}_{int(diff_amount)}"

        # Prevent duplicate sending
        if alert_id in st.session_state.sent_spike_alerts:
            st.info("Spike alert already sent for the latest row.")
            return

        # Email content
        subject = f"⚠️ PRICE SPIKE: {higher} ₹{diff_amount:,.2f} > {lower}"
        body = (
            f"🚨 ALERT\n\n"
            f"{higher} is ₹{diff_amount:,.2f} higher than {lower}\n"
            f"Date: {date.strftime('%Y-%m-%d')}\n"
            f"Time: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Send email
        success = send_alert_email(subject, body, receiver)

        if success:
            st.session_state.sent_spike_alerts.add(alert_id)
            st.success(f"✅ Email sent: {higher} ₹{diff_amount:,.0f} > {lower}")

    # ---------------------------------------------
    # 1️⃣ AUTO SEND ON FIRST RUN (only once)
    # ---------------------------------------------
    if st.session_state.auto_sent_once is False:
        check_and_send_latest_spike()
        st.session_state.auto_sent_once = True   # Prevent auto-run again

    # ---------------------------------------------
    # 2️⃣ MANUAL SEND WHEN BUTTON CLICKED
    # ---------------------------------------------
    if manual_click:
        check_and_send_latest_spike()

    st.markdown("---")
    st.subheader("📋 Sent Alerts")

    if st.session_state.sent_alerts_log:
        for entry in st.session_state.sent_alerts_log[-5:]:
            st.write(entry)
    else:
        st.write("No emails sent yet.")




trend_df = load_table(DATA_SOURCES["trend"])
daily_df = load_table(DATA_SOURCES["daily"])
amazon_forecast_df = load_table(DATA_SOURCES["amazon_forecast"])
flipkart_forecast_df = load_table(DATA_SOURCES["flipkart_forecast"])
reviews_df = load_table(DATA_SOURCES["reviews"], kind="excel")

PAGES = {
    "Trend Analysis": lambda: render_trend_page(trend_df, daily_df),
    "Review Output": lambda: render_reviews_page(reviews_df),
    "Amazon Forecast": lambda: render_forecast_page(amazon_forecast_df, "Amazon"),
    "Flipkart Forecast": lambda: render_forecast_page(flipkart_forecast_df, "Flipkart"),
    "Daily Dataset": lambda: render_daily_page(daily_df),
    "Cross-Web Comparison": lambda: render_comparison_page(
        trend_df, daily_df, amazon_forecast_df, flipkart_forecast_df
    ),
    "Notifications": lambda: render_notifications_page(trend_df),

    
}

if "page" not in st.session_state:
    st.session_state.page = "Trend Analysis"

st.markdown(
    """
    <style>
        .nav-container {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-bottom: 1.5rem;
        }
        .nav-button button {
            width: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

nav_cols = st.columns(len(PAGES))
for col, name in zip(nav_cols, PAGES.keys()):
    with col:
        if st.button(name, key=f"nav-{name}", use_container_width=True):
            st.session_state.page = name

PAGES[st.session_state.page]()

st.caption("© 2025 Marketplace Intelligence Hub")
