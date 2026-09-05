import streamlit as st
import json
import os
import glob
import pandas as pd
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AgentInvest",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

html, body, [class*="css"] {
    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}


/* =========================================================
   HERO
   ========================================================= */

.hero-box {
    padding: 34px 38px;
    border: 1px solid #e4e4e4;
    border-radius: 22px;
    margin-bottom: 22px;
}

.hero-label {
    font-size: 12px;
    font-weight: 750;
    letter-spacing: 1.2px;
    color: #888888;
}

.hero-title {
    font-size: 48px;
    font-weight: 850;
    line-height: 1.05;
    margin-top: 7px;
}

.hero-subtitle {
    font-size: 17px;
    color: #747474;
    line-height: 1.6;
    margin-top: 10px;
    max-width: 800px;
}


/* =========================================================
   COMPANY HEADER
   ========================================================= */

.company-name {
    font-size: 34px;
    font-weight: 800;
}

.company-meta {
    color: #777777;
    font-size: 14px;
}


/* =========================================================
   RATING CARD
   ========================================================= */

.rating-card {
    padding: 28px;
    border-radius: 20px;
    text-align: center;
    min-height: 190px;
}

.rating-buy {
    border: 2px solid #35a853;
    background: rgba(53, 168, 83, 0.07);
}

.rating-hold {
    border: 2px solid #d9a404;
    background: rgba(217, 164, 4, 0.07);
}

.rating-sell {
    border: 2px solid #d94a4a;
    background: rgba(217, 74, 74, 0.07);
}

.rating-label {
    color: #777777;
    font-size: 12px;
    font-weight: 750;
    letter-spacing: 1px;
}

.rating-main {
    font-size: 48px;
    font-weight: 850;
    margin-top: 10px;
}

.rating-meta {
    font-size: 14px;
    color: #666666;
    margin-top: 5px;
}


/* =========================================================
   SCORE CARDS
   ========================================================= */

.score-card {
    border: 1px solid #e4e4e4;
    border-radius: 16px;
    padding: 19px;
}

.score-label {
    color: #777777;
    font-size: 13px;
    font-weight: 650;
}

.score-value {
    font-size: 32px;
    font-weight: 800;
    margin-top: 5px;
}


/* =========================================================
   HOME FLOWCHART
   ========================================================= */

.home-flow {
    margin-top: 30px;
    margin-bottom: 30px;
}

.flow-main-node {
    max-width: 430px;
    margin: 0 auto;
    padding: 22px 25px;
    border: 1px solid #dddddd;
    border-radius: 17px;
    text-align: center;
    background: #fafafa;
}

.flow-node-title {
    font-size: 17px;
    font-weight: 750;
}

.flow-node-desc {
    font-size: 13px;
    color: #888888;
    margin-top: 6px;
    line-height: 1.5;
}

.flow-down-arrow {
    text-align: center;
    font-size: 30px;
    color: #999999;
    margin: 10px 0;
}

.flow-agent-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin-top: 5px;
    margin-bottom: 5px;
}

.flow-agent-node {
    padding: 24px 15px;
    border: 1px solid #dddddd;
    border-radius: 17px;
    text-align: center;
    background: white;
}

.flow-agent-icon {
    font-size: 28px;
    margin-bottom: 7px;
}

.flow-agent-name {
    font-size: 16px;
    font-weight: 750;
}

.flow-agent-desc {
    font-size: 12px;
    color: #888888;
    margin-top: 6px;
}

.flow-output {
    max-width: 540px;
    margin: 0 auto;
    padding: 23px 25px;
    border: 1px solid #dddddd;
    border-radius: 17px;
    text-align: center;
    background: white;
}


/* =========================================================
   AGENT REPORT BUTTON CARDS
   ========================================================= */

.st-key-fundamental_card button,
.st-key-technical_card button,
.st-key-news_card button {

    min-height: 170px;
    border-radius: 18px;
    font-size: 16px;
    white-space: pre-line;
    line-height: 1.7;
    border: 1px solid #dedede;
}

.st-key-decision_card button {

    min-height: 145px;
    border-radius: 18px;
    font-size: 16px;
    white-space: pre-line;
    line-height: 1.7;
    border: 1px solid #dedede;
}


/* =========================================================
   REPORT PAGES
   ========================================================= */

.report-kicker {
    font-size: 13px;
    font-weight: 750;
    color: #888888;
    letter-spacing: 1px;
}

.report-title {
    font-size: 42px;
    font-weight: 850;
    margin-top: 6px;
}

.report-description {
    font-size: 16px;
    color: #777777;
    margin-top: 7px;
    margin-bottom: 20px;
    line-height: 1.6;
}

.report-score {
    padding: 25px;
    border-radius: 17px;
    border: 1px solid #e4e4e4;
}

.report-score-label {
    font-size: 13px;
    color: #777777;
}

.report-score-value {
    font-size: 40px;
    font-weight: 850;
}


/* make long AI reports easier to read */

div[data-testid="stMarkdownContainer"] p {
    line-height: 1.75;
}

div[data-testid="stMarkdownContainer"] li {
    line-height: 1.7;
}


/* =========================================================
   FOOTER
   ========================================================= */

.footer {
    text-align: center;
    font-size: 12px;
    color: #888888;
    padding-top: 30px;
}


/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 800px) {

    .flow-agent-grid {
        grid-template-columns: 1fr;
    }

    .hero-title {
        font-size: 38px;
    }

}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# FILE HELPERS
# ============================================================

def load_report(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def get_saved_reports():

    files = glob.glob(
        os.path.join(
            "reports",
            "*_day3.json"
        )
    )

    reports = {}

    for file_path in files:

        filename = os.path.basename(
            file_path
        )

        ticker = filename.replace(
            "_day3.json",
            ""
        )

        reports[ticker] = file_path

    return reports


# ============================================================
# RUN A NEW AI ANALYSIS
# ============================================================

def run_new_analysis(ticker):

    from market_data import get_stock_data

    from day3_agents import (
        fundamental_agent,
        technical_agent,
        news_agent,
        decision_agent,
        save_day3_report
    )


    ticker = (
        ticker
        .strip()
        .upper()
    )


    if not ticker:

        raise ValueError(
            "Please enter a valid ticker."
        )


    with st.status(
        f"Building {ticker} research report...",
        expanded=True
    ) as status:


        # ----------------------------------------------------
        # MARKET DATA
        # ----------------------------------------------------

        st.write(
            "📡 Step 1 · Collecting market and company data"
        )

        stock_data = get_stock_data(
            ticker
        )

        st.write(
            "✅ Market data collected"
        )


        # ----------------------------------------------------
        # FUNDAMENTAL
        # ----------------------------------------------------

        st.write(
            "📊 Step 2 · Fundamental Analyst reviewing "
            "valuation, growth and profitability"
        )

        fundamental_report = (
            fundamental_agent(
                stock_data
            )
        )

        st.write(
            "✅ Fundamental analysis completed"
        )


        # ----------------------------------------------------
        # TECHNICAL
        # ----------------------------------------------------

        st.write(
            "📈 Step 3 · Technical Analyst evaluating "
            "trend and momentum"
        )

        technical_report = (
            technical_agent(
                stock_data
            )
        )

        st.write(
            "✅ Technical analysis completed"
        )


        # ----------------------------------------------------
        # NEWS
        # ----------------------------------------------------

        st.write(
            "📰 Step 4 · News Analyst evaluating "
            "catalysts and sentiment"
        )

        news_report = (
            news_agent(
                stock_data
            )
        )

        st.write(
            "✅ News analysis completed"
        )


        # ----------------------------------------------------
        # DECISION
        # ----------------------------------------------------

        st.write(
            "🧠 Step 5 · Decision Agent synthesizing "
            "all analyst evidence"
        )

        decision_report = (
            decision_agent(
                stock_data,
                fundamental_report,
                technical_report,
                news_report
            )
        )

        st.write(
            "✅ Final decision completed"
        )


        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        file_path = save_day3_report(
            ticker,
            stock_data,
            fundamental_report,
            technical_report,
            news_report,
            decision_report
        )


        status.update(
            label=f"{ticker} research completed",
            state="complete",
            expanded=False
        )


    return load_report(
        file_path
    )


# ============================================================
# SESSION STATE
# ============================================================

if "current_data" not in st.session_state:

    st.session_state.current_data = None


if "view" not in st.session_state:

    st.session_state.view = "overview"


# ============================================================
# SAVED REPORTS
# ============================================================

saved_reports = get_saved_reports()

saved_tickers = sorted(
    saved_reports.keys()
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "## 📈 AgentInvest"
)

st.sidebar.caption(
    "Multi-Agent Equity Research"
)

st.sidebar.divider()


st.sidebar.markdown(
    "### Saved Research"
)


if saved_tickers:

    saved_choice = st.sidebar.selectbox(
        "Previous reports",
        saved_tickers
    )


    if st.sidebar.button(
        "Open Report",
        use_container_width=True
    ):

        st.session_state.current_data = (
            load_report(
                saved_reports[
                    saved_choice
                ]
            )
        )

        st.session_state.view = (
            "overview"
        )

        st.rerun()


else:

    st.sidebar.caption(
        "No saved reports yet."
    )


st.sidebar.divider()


if st.sidebar.button(
    "🏠 Home",
    use_container_width=True
):

    st.session_state.current_data = None

    st.session_state.view = "overview"

    st.rerun()


st.sidebar.divider()

st.sidebar.caption(
    "Educational research only."
)

st.sidebar.caption(
    "Not financial advice."
)


# ============================================================
# BACK BUTTON
# ============================================================

def report_back_button():

    if st.button(
        "← Back to Research Overview"
    ):

        st.session_state.view = (
            "overview"
        )

        st.rerun()


# ============================================================
# FUNDAMENTAL REPORT PAGE
# ============================================================

def show_fundamental_page(data):

    market = data.get(
        "market_data",
        {}
    )

    agents = data.get(
        "agents",
        {}
    )

    summary = data.get(
        "summary",
        {}
    )

    company = data.get(
        "company",
        ""
    )

    ticker = data.get(
        "ticker",
        ""
    )

    score = summary.get(
        "fundamental_score",
        0
    )


    report_back_button()


    st.markdown(
        """
<div class="report-kicker">
SPECIALIST RESEARCH REPORT
</div>
""",
        unsafe_allow_html=True
    )


    st.markdown(
        """
<div class="report-title">
📊 Fundamental Analyst
</div>
""",
        unsafe_allow_html=True
    )


    st.markdown(
        f"""
<div class="report-description">

{company} ({ticker}) · Valuation, growth,
profitability and fundamental risk

</div>
""",
        unsafe_allow_html=True
    )


    st.divider()


    score_col, metrics_col = st.columns(
        [1, 3]
    )


    with score_col:

        st.markdown(
            f"""
<div class="report-score">

<div class="report-score-label">
FUNDAMENTAL SCORE
</div>

<div class="report-score-value">
{score}/100
</div>

</div>
""",
            unsafe_allow_html=True
        )


    with metrics_col:

        c1, c2, c3 = st.columns(
            3
        )


        with c1:

            pe = market.get(
                "pe_ratio"
            )

            st.metric(
                "P/E Ratio",
                (
                    f"{pe:.2f}x"
                    if pe is not None
                    else "N/A"
                )
            )


        with c2:

            growth = market.get(
                "revenue_growth"
            )

            st.metric(
                "Revenue Growth",
                (
                    f"{growth * 100:.1f}%"
                    if growth is not None
                    else "N/A"
                )
            )


        with c3:

            margin = market.get(
                "profit_margin"
            )

            st.metric(
                "Profit Margin",
                (
                    f"{margin * 100:.1f}%"
                    if margin is not None
                    else "N/A"
                )
            )


    st.divider()


    st.markdown(
        "## Fundamental Research"
    )


    st.markdown(
        agents.get(
            "fundamental_agent",
            "No fundamental report available."
        )
    )


# ============================================================
# TECHNICAL REPORT PAGE
# ============================================================

def show_technical_page(data):

    market = data.get(
        "market_data",
        {}
    )

    agents = data.get(
        "agents",
        {}
    )

    summary = data.get(
        "summary",
        {}
    )

    company = data.get(
        "company",
        ""
    )

    ticker = data.get(
        "ticker",
        ""
    )

    score = summary.get(
        "technical_score",
        0
    )


    report_back_button()


    st.markdown(
        """
<div class="report-kicker">
SPECIALIST RESEARCH REPORT
</div>
""",
        unsafe_allow_html=True
    )


    st.markdown(
        """
<div class="report-title">
📈 Technical Analyst
</div>
""",
        unsafe_allow_html=True
    )


    st.markdown(
        f"""
<div class="report-description">

{company} ({ticker}) · Price trend, momentum
and technical indicators

</div>
""",
        unsafe_allow_html=True
    )


    st.divider()


    score_col, metrics_col = st.columns(
        [1, 3]
    )


    with score_col:

        st.markdown(
            f"""
<div class="report-score">

<div class="report-score-label">
TECHNICAL SCORE
</div>

<div class="report-score-value">
{score}/100
</div>

</div>
""",
            unsafe_allow_html=True
        )


    with metrics_col:

        t1, t2, t3, t4 = st.columns(
            4
        )


        with t1:

            st.metric(
                "MA20",
                market.get(
                    "ma20",
                    "N/A"
                )
            )


        with t2:

            st.metric(
                "MA50",
                market.get(
                    "ma50",
                    "N/A"
                )
            )


        with t3:

            st.metric(
                "RSI",
                market.get(
                    "rsi",
                    "N/A"
                )
            )


        with t4:

            st.metric(
                "MACD",
                market.get(
                    "macd",
                    "N/A"
                )
            )


    st.divider()


    st.markdown(
        "## Technical Research"
    )


    st.markdown(
        agents.get(
            "technical_agent",
            "No technical report available."
        )
    )


# ============================================================
# NEWS REPORT PAGE
# ============================================================

def show_news_page(data):

    agents = data.get(
        "agents",
        {}
    )

    market = data.get(
        "market_data",
        {}
    )

    summary = data.get(
        "summary",
        {}
    )

    company = data.get(
        "company",
        ""
    )

    ticker = data.get(
        "ticker",
        ""
    )

    score = summary.get(
        "news_score",
        0
    )


    report_back_button()


    st.markdown(
        """
<div class="report-kicker">
SPECIALIST RESEARCH REPORT
</div>
""",
        unsafe_allow_html=True
    )


    st.markdown(
        """
<div class="report-title">
📰 News Analyst
</div>
""",
        unsafe_allow_html=True
    )


    st.markdown(
        f"""
<div class="report-description">

{company} ({ticker}) · Recent catalysts,
risks and market sentiment

</div>
""",
        unsafe_allow_html=True
    )


    st.divider()


    st.markdown(
        f"""
<div class="report-score">

<div class="report-score-label">
NEWS SENTIMENT SCORE
</div>

<div class="report-score-value">
{score}/100
</div>

</div>
""",
        unsafe_allow_html=True
    )


    st.divider()


    st.markdown(
        "## News & Sentiment Research"
    )


    st.markdown(
        agents.get(
            "news_agent",
            "No news report available."
        )
    )


    news_items = market.get(
        "news",
        []
    )


    if news_items:

        st.divider()

        st.markdown(
            "## Source Headlines"
        )


        for article in news_items:

            title = article.get(
                "title",
                "Untitled"
            )

            publisher = article.get(
                "publisher",
                "Unknown"
            )

            link = article.get(
                "link"
            )


            st.markdown(
                f"### {title}"
            )

            st.caption(
                publisher
            )


            if link:

                st.link_button(
                    "Open Source ↗",
                    link
                )


            st.divider()


# ============================================================
# DECISION REPORT PAGE
# ============================================================

def show_decision_page(data):

    summary = data.get(
        "summary",
        {}
    )

    report = data.get(
        "decision_agent",
        ""
    )

    company = data.get(
        "company",
        ""
    )

    ticker = data.get(
        "ticker",
        ""
    )


    rating = summary.get(
        "final_rating",
        "N/A"
    )

    confidence = summary.get(
        "confidence",
        0
    )

    risk = summary.get(
        "risk_level",
        "N/A"
    )


    report_back_button()


    st.markdown(
        """
<div class="report-kicker">
FINAL RESEARCH DECISION
</div>
""",
        unsafe_allow_html=True
    )


    st.markdown(
        """
<div class="report-title">
🧠 AI Investment Committee
</div>
""",
        unsafe_allow_html=True
    )


    st.markdown(
        f"""
<div class="report-description">

{company} ({ticker}) · Final synthesis of
fundamental, technical and news evidence

</div>
""",
        unsafe_allow_html=True
    )


    st.divider()


    d1, d2, d3 = st.columns(
        3
    )


    with d1:

        st.metric(
            "Final Rating",
            rating
        )


    with d2:

        st.metric(
            "Confidence",
            f"{confidence}%"
        )


    with d3:

        st.metric(
            "Risk Level",
            risk
        )


    st.divider()


    st.markdown(
        "## Investment Committee Report"
    )


    st.markdown(
        report
    )


# ============================================================
# ROUTING TO REPORT PAGES
# ============================================================

if st.session_state.current_data is not None:

    if st.session_state.view == "fundamental":

        show_fundamental_page(
            st.session_state.current_data
        )

        st.stop()


    elif st.session_state.view == "technical":

        show_technical_page(
            st.session_state.current_data
        )

        st.stop()


    elif st.session_state.view == "news":

        show_news_page(
            st.session_state.current_data
        )

        st.stop()


    elif st.session_state.view == "decision":

        show_decision_page(
            st.session_state.current_data
        )

        st.stop()


# ============================================================
# MAIN HOME / OVERVIEW PAGE
# ============================================================

st.markdown(
    """
<div class="hero-box">

<div class="hero-label">
AI-POWERED EQUITY RESEARCH
</div>

<div class="hero-title">
AgentInvest
</div>

<div class="hero-subtitle">

Analyze any US-listed company with specialized AI agents
covering fundamentals, technical signals, recent news
and investment risk.

</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# SEARCH BAR
# ============================================================

search_col, button_col = st.columns(
    [5, 1.4],
    vertical_alignment="bottom"
)


with search_col:

    ticker_input = st.text_input(
        "Search a stock",
        placeholder=(
            "Enter ticker, e.g. GOOGL, META, JPM..."
        ),
        label_visibility="collapsed"
    )


with button_col:

    analyze_button = st.button(
        "Analyze Stock",
        type="primary",
        use_container_width=True
    )


st.caption(
    "New analyses use AI API credits. "
    "Saved research can be opened without "
    "additional AI usage."
)


# ============================================================
# RUN ANALYSIS
# ============================================================

if analyze_button:

    try:

        st.session_state.current_data = (
            run_new_analysis(
                ticker_input
            )
        )

        st.session_state.view = (
            "overview"
        )

        st.rerun()


    except Exception as e:

        st.error(
            f"Analysis failed: {e}"
        )


# ============================================================
# HOME PAGE — FLOWCHART
# ============================================================

if st.session_state.current_data is None:

    st.divider()


    st.markdown(
        "## How AgentInvest Works"
    )


    st.caption(
        "One market data pipeline. "
        "Three independent analysts. "
        "One final investment committee."
    )


    st.markdown(
        """
<div class="home-flow">


<div class="flow-main-node">

<div class="flow-node-title">
📡 Market & Company Data
</div>

<div class="flow-node-desc">
Price · Valuation · Growth · Profitability ·
Historical Prices · Recent News
</div>

</div>


<div class="flow-down-arrow">
↓
</div>


<div class="flow-agent-grid">


<div class="flow-agent-node">

<div class="flow-agent-icon">
📊
</div>

<div class="flow-agent-name">
Fundamental Analyst
</div>

<div class="flow-agent-desc">
Valuation · Growth · Profitability
</div>

</div>


<div class="flow-agent-node">

<div class="flow-agent-icon">
📈
</div>

<div class="flow-agent-name">
Technical Analyst
</div>

<div class="flow-agent-desc">
Trend · Momentum · RSI · MACD
</div>

</div>


<div class="flow-agent-node">

<div class="flow-agent-icon">
📰
</div>

<div class="flow-agent-name">
News Analyst
</div>

<div class="flow-agent-desc">
Catalysts · Risks · Sentiment
</div>

</div>


</div>


<div class="flow-down-arrow">
↓
</div>


<div class="flow-main-node">

<div class="flow-node-title">
🧠 Decision Agent
</div>

<div class="flow-node-desc">
Compares analyst evidence · Identifies agreement
and disagreement · Evaluates downside risk
</div>

</div>


<div class="flow-down-arrow">
↓
</div>


<div class="flow-output">

<div class="flow-node-title">
📄 AI Equity Research Report
</div>

<div class="flow-node-desc">
BUY / HOLD / SELL · Confidence Score ·
Risk Level · Bull Case · Bear Case ·
Investment Thesis
</div>

</div>


</div>
""",
        unsafe_allow_html=True
    )


    st.markdown(
        """
<div class="footer">

AgentInvest · Educational and demonstration
purposes only.

<br>

Not financial advice.

</div>
""",
        unsafe_allow_html=True
    )


    st.stop()


# ============================================================
# CURRENT REPORT DATA
# ============================================================

data = st.session_state.current_data


ticker = data.get(
    "ticker",
    "N/A"
)

company = data.get(
    "company",
    "Unknown Company"
)

analysis_date = data.get(
    "analysis_date",
    "N/A"
)

summary = data.get(
    "summary",
    {}
)

market = data.get(
    "market_data",
    {}
)


fundamental_score = summary.get(
    "fundamental_score",
    0
)

technical_score = summary.get(
    "technical_score",
    0
)

news_score = summary.get(
    "news_score",
    0
)

final_rating = summary.get(
    "final_rating",
    "N/A"
)

confidence = summary.get(
    "confidence",
    0
)

risk_level = summary.get(
    "risk_level",
    "N/A"
)


# ============================================================
# RATING COLOR
# ============================================================

if final_rating == "BUY":

    rating_class = (
        "rating-buy"
    )

elif final_rating == "SELL":

    rating_class = (
        "rating-sell"
    )

else:

    rating_class = (
        "rating-hold"
    )


# ============================================================
# COMPANY HEADER
# ============================================================

st.divider()


company_col, rating_col = st.columns(
    [2.3, 1]
)


with company_col:

    st.markdown(
        f"""
<div class="company-name">
{company}
</div>

<div class="company-meta">
{ticker} · Report generated {analysis_date}
</div>
""",
        unsafe_allow_html=True
    )


    price = market.get(
        "price"
    )


    if price is not None:

        st.markdown(
            f"## ${price:,.2f}"
        )


with rating_col:

    st.markdown(
        f"""
<div class="rating-card {rating_class}">

<div class="rating-label">
AI RESEARCH RATING
</div>

<div class="rating-main">
{final_rating}
</div>

<div class="rating-meta">
Confidence · {confidence}/100
</div>

<div class="rating-meta">
Risk · {risk_level}
</div>

</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# RESEARCH TEAM SCORES
# ============================================================

st.markdown(
    "## Research Team Scores"
)


a1, a2, a3 = st.columns(
    3
)


with a1:

    st.markdown(
        f"""
<div class="score-card">

<div class="score-label">
📊 FUNDAMENTAL
</div>

<div class="score-value">
{fundamental_score}/100
</div>

</div>
""",
        unsafe_allow_html=True
    )

    st.progress(
        fundamental_score / 100
    )


with a2:

    st.markdown(
        f"""
<div class="score-card">

<div class="score-label">
📈 TECHNICAL
</div>

<div class="score-value">
{technical_score}/100
</div>

</div>
""",
        unsafe_allow_html=True
    )

    st.progress(
        technical_score / 100
    )


with a3:

    st.markdown(
        f"""
<div class="score-card">

<div class="score-label">
📰 NEWS
</div>

<div class="score-value">
{news_score}/100
</div>

</div>
""",
        unsafe_allow_html=True
    )

    st.progress(
        news_score / 100
    )


# ============================================================
# MARKET SNAPSHOT
# ============================================================

st.markdown(
    "## Market Snapshot"
)


m1, m2, m3, m4 = st.columns(
    4
)


pe = market.get(
    "pe_ratio"
)

growth = market.get(
    "revenue_growth"
)

margin = market.get(
    "profit_margin"
)

market_cap = market.get(
    "market_cap"
)


with m1:

    st.metric(
        "P/E Ratio",
        (
            f"{pe:.2f}x"
            if pe is not None
            else "N/A"
        )
    )


with m2:

    st.metric(
        "Revenue Growth",
        (
            f"{growth * 100:.1f}%"
            if growth is not None
            else "N/A"
        )
    )


with m3:

    st.metric(
        "Profit Margin",
        (
            f"{margin * 100:.1f}%"
            if margin is not None
            else "N/A"
        )
    )


with m4:

    if market_cap is None:

        cap_display = "N/A"

    elif market_cap >= 1e12:

        cap_display = (
            f"${market_cap / 1e12:.2f}T"
        )

    elif market_cap >= 1e9:

        cap_display = (
            f"${market_cap / 1e9:.2f}B"
        )

    else:

        cap_display = (
            f"${market_cap:,.0f}"
        )


    st.metric(
        "Market Cap",
        cap_display
    )


# ============================================================
# TECHNICAL SNAPSHOT
# ============================================================

st.markdown(
    "## Technical Snapshot"
)


t1, t2, t3, t4, t5 = st.columns(
    5
)


with t1:

    st.metric(
        "MA20",
        market.get(
            "ma20",
            "N/A"
        )
    )


with t2:

    st.metric(
        "MA50",
        market.get(
            "ma50",
            "N/A"
        )
    )


with t3:

    st.metric(
        "RSI",
        market.get(
            "rsi",
            "N/A"
        )
    )


with t4:

    st.metric(
        "MACD",
        market.get(
            "macd",
            "N/A"
        )
    )


with t5:

    st.metric(
        "MACD Signal",
        market.get(
            "macd_signal",
            "N/A"
        )
    )


# ============================================================
# PRICE CHART
# ============================================================

st.markdown(
    "## Price & Trend"
)


price_history = market.get(
    "price_history",
    []
)


if price_history:

    chart_df = pd.DataFrame(
        price_history
    )


    chart_df["date"] = (
        pd.to_datetime(
            chart_df["date"]
        )
    )


    fig = go.Figure()


    fig.add_trace(
        go.Scatter(
            x=chart_df["date"],
            y=chart_df["close"],
            mode="lines",
            name="Close",
            line=dict(
                width=3
            )
        )
    )


    fig.add_trace(
        go.Scatter(
            x=chart_df["date"],
            y=chart_df["ma20"],
            mode="lines",
            name="MA20",
            line=dict(
                width=1.8
            )
        )
    )


    fig.add_trace(
        go.Scatter(
            x=chart_df["date"],
            y=chart_df["ma50"],
            mode="lines",
            name="MA50",
            line=dict(
                width=1.8
            )
        )
    )


    fig.update_layout(
        height=460,
        margin=dict(
            l=10,
            r=10,
            t=30,
            b=10
        ),
        hovermode="x unified",
        yaxis_title="Price ($)",
        xaxis_title=None,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


else:

    st.info(
        "This saved report does not contain "
        "synchronized price history. "
        "Run a new analysis to generate it."
    )


# ============================================================
# EXPLORE REPORTS
# ============================================================

st.divider()


st.markdown(
    "## Explore Agent Reports"
)


st.caption(
    "Select an analyst to view the full research "
    "behind the final recommendation."
)


# ============================================================
# CLICKABLE SPECIALIST CARDS
# ============================================================

c1, c2, c3 = st.columns(
    3
)


with c1:

    if st.button(
        (
            "📊  Fundamental Analyst\n\n"
            "Valuation · Growth · Profitability\n\n"
            f"Score · {fundamental_score}/100\n\n"
            "View Full Report →"
        ),
        key="fundamental_card",
        use_container_width=True
    ):

        st.session_state.view = (
            "fundamental"
        )

        st.rerun()


with c2:

    if st.button(
        (
            "📈  Technical Analyst\n\n"
            "Trend · Momentum · Indicators\n\n"
            f"Score · {technical_score}/100\n\n"
            "View Full Report →"
        ),
        key="technical_card",
        use_container_width=True
    ):

        st.session_state.view = (
            "technical"
        )

        st.rerun()


with c3:

    if st.button(
        (
            "📰  News Analyst\n\n"
            "Catalysts · Risks · Sentiment\n\n"
            f"Score · {news_score}/100\n\n"
            "View Full Report →"
        ),
        key="news_card",
        use_container_width=True
    ):

        st.session_state.view = (
            "news"
        )

        st.rerun()


# ============================================================
# DECISION CARD
# ============================================================

if st.button(
    (
        "🧠  Decision Agent\n\n"
        "Synthesizes all specialist evidence into "
        "the final research recommendation\n\n"
        f"Final Rating · {final_rating}   |   "
        f"Confidence · {confidence}%   |   "
        f"Risk · {risk_level}\n\n"
        "View Investment Committee Report →"
    ),
    key="decision_card",
    use_container_width=True
):

    st.session_state.view = (
        "decision"
    )

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">

AgentInvest · AI-generated equity research
for educational and demonstration purposes only.

<br>

Not financial advice.

</div>
""",
    unsafe_allow_html=True
)