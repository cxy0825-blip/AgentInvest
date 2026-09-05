import os
import json
import re

from dotenv import load_dotenv
from openai import OpenAI

from market_data import get_stock_data


# ============================================================
# 1. 加载 OpenAI API Key
# ============================================================

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")


def get_api_key():
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        return api_key

    try:
        import streamlit as st

        return st.secrets.get("OPENAI_API_KEY")
    except Exception:
        return None


def get_client():
    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not configured. Add it to your local .env file "
            "or to Streamlit Cloud Secrets before running a new analysis."
        )

    return OpenAI(api_key=api_key)


def run_llm(prompt):
    response = get_client().responses.create(
        model=MODEL,
        input=prompt
    )

    return response.output_text


# ============================================================
# 2. Fundamental Agent
# ============================================================

def fundamental_agent(stock_data):

    fundamental_data = {
        "ticker": stock_data["ticker"],
        "company": stock_data["company"],
        "price": stock_data["price"],
        "market_cap": stock_data["market_cap"],
        "pe_ratio": stock_data["pe_ratio"],
        "revenue_growth": stock_data["revenue_growth"],
        "profit_margin": stock_data["profit_margin"],
        "52_week_high": stock_data["52_week_high"],
        "52_week_low": stock_data["52_week_low"]
    }

    prompt = f"""
You are a professional equity research fundamental analyst.

Analyze the following company data:

{json.dumps(fundamental_data, indent=2)}

Evaluate:

1. Valuation
2. Revenue growth
3. Profitability
4. Company strengths
5. Fundamental risks

Important:
Only use the supplied data.
Do not invent financial information.

Keep the report concise.

At the end provide exactly:

Fundamental Score: XX/100
Fundamental View: Bullish, Neutral, or Bearish
"""

    return run_llm(prompt)


# ============================================================
# 3. Technical Agent
# ============================================================

def technical_agent(stock_data):

    technical_data = {
        "ticker": stock_data["ticker"],
        "price": stock_data["price"],
        "ma20": stock_data["ma20"],
        "ma50": stock_data["ma50"],
        "rsi": stock_data["rsi"],
        "macd": stock_data["macd"],
        "macd_signal": stock_data["macd_signal"],
        "volume": stock_data["volume"],
        "52_week_high": stock_data["52_week_high"],
        "52_week_low": stock_data["52_week_low"]
    }

    prompt = f"""
You are a professional technical analyst.

Analyze the following stock data:

{json.dumps(technical_data, indent=2)}

Evaluate:

1. Short-term price trend
2. MA20 and MA50
3. RSI
4. MACD
5. Momentum
6. Technical risks

Important:
Only use the supplied data.
Do not invent chart patterns or historical prices.

Keep the report concise.

At the end provide exactly:

Technical Score: XX/100
Technical View: Bullish, Neutral, or Bearish
"""

    return run_llm(prompt)


# ============================================================
# 4. News Agent
# ============================================================

def news_agent(stock_data):

    news_data = {
        "ticker": stock_data["ticker"],
        "company": stock_data["company"],
        "news": stock_data["news"]
    }

    prompt = f"""
You are a financial news and market sentiment analyst.

Analyze the following recent news headlines:

{json.dumps(news_data, indent=2)}

Evaluate:

1. Overall news sentiment
2. Positive catalysts
3. Negative catalysts
4. Important company developments
5. Short-term investor implications
6. News-related risks

Important rules:

- Only use the headlines and information supplied.
- Do not claim to have read the full article.
- Do not invent facts that are not present in the supplied data.
- If the available headlines are insufficient, clearly say so.
- Distinguish between company-specific news and unrelated market news.

Keep the report concise.

At the end provide exactly:

News Score: XX/100
News Sentiment: Positive, Neutral, or Negative
"""

    return run_llm(prompt)


# ============================================================
# 5. 从 Agent 报告中提取分数
# ============================================================

def extract_score(report, score_name):

    pattern = rf"{score_name}\s*Score:\s*(\d+)"
    match = re.search(pattern, report, re.IGNORECASE)

    if match:
        return int(match.group(1))

    return None


# ============================================================
# 6. Decision Agent
# ============================================================

def decision_agent(
    stock_data,
    fundamental_report,
    technical_report,
    news_report
):

    fundamental_score = extract_score(
        fundamental_report,
        "Fundamental"
    )

    technical_score = extract_score(
        technical_report,
        "Technical"
    )

    news_score = extract_score(
        news_report,
        "News"
    )

    decision_input = {
        "ticker": stock_data["ticker"],
        "company": stock_data["company"],
        "price": stock_data["price"],
        "fundamental_score": fundamental_score,
        "technical_score": technical_score,
        "news_score": news_score,
        "fundamental_report": fundamental_report,
        "technical_report": technical_report,
        "news_report": news_report
    }

    prompt = f"""
You are the lead decision agent of a multi-agent equity research team.

Three specialist analysts have completed their work.

Review all of their reports and make a final research decision.

INPUT:

{json.dumps(decision_input, indent=2)}

Your task:

1. Compare the fundamental, technical, and news evidence.
2. Identify where the analysts agree.
3. Identify where they disagree.
4. Produce a Bull Case.
5. Produce a Bear Case.
6. Identify the most important risks.
7. Assign an overall confidence score from 0 to 100.
8. Assign a risk level: Low, Medium, or High.
9. Produce a final research rating:
   BUY, HOLD, or SELL.
10. Write a short final investment thesis.

Important:

- This is a research simulation, not personalized financial advice.
- Do not invent additional financial data.
- Base the decision only on the supplied analyst reports.
- A BUY rating should require meaningful positive evidence.
- High valuation, overbought conditions, uncertainty, or conflicting
  evidence should reduce confidence.

Use this exact ending format:

Final Rating: BUY / HOLD / SELL
Confidence: XX/100
Risk Level: Low / Medium / High
"""

    return run_llm(prompt)


# ============================================================
# 7. 提取最终 Rating
# ============================================================

def extract_rating(decision_report):

    match = re.search(
        r"Final Rating:\s*(BUY|HOLD|SELL)",
        decision_report,
        re.IGNORECASE
    )

    if match:
        return match.group(1).upper()

    return "UNKNOWN"


# ============================================================
# 8. 提取 Confidence
# ============================================================

def extract_confidence(decision_report):

    match = re.search(
        r"Confidence:\s*(\d+)",
        decision_report,
        re.IGNORECASE
    )

    if match:
        return int(match.group(1))

    return None


# ============================================================
# 9. 提取 Risk Level
# ============================================================

def extract_risk(decision_report):

    match = re.search(
        r"Risk Level:\s*(Low|Medium|High)",
        decision_report,
        re.IGNORECASE
    )

    if match:
        return match.group(1).title()

    return "Unknown"


# ============================================================
# 10. 保存 Day 3 完整报告
# ============================================================

def save_day3_report(
    ticker,
    stock_data,
    fundamental_report,
    technical_report,
    news_report,
    decision_report
):

    os.makedirs(
        "reports",
        exist_ok=True
    )

    fundamental_score = extract_score(
        fundamental_report,
        "Fundamental"
    )

    technical_score = extract_score(
        technical_report,
        "Technical"
    )

    news_score = extract_score(
        news_report,
        "News"
    )

    final_rating = extract_rating(
        decision_report
    )

    confidence = extract_confidence(
        decision_report
    )

    risk_level = extract_risk(
        decision_report
    )

    final_data = {
        "ticker": ticker,

        "company": stock_data["company"],

        "analysis_date": stock_data["analysis_date"],

        "summary": {
            "fundamental_score": fundamental_score,
            "technical_score": technical_score,
            "news_score": news_score,
            "final_rating": final_rating,
            "confidence": confidence,
            "risk_level": risk_level
        },

        "market_data": stock_data,

        "agents": {
            "fundamental_agent": fundamental_report,
            "technical_agent": technical_report,
            "news_agent": news_report
        },

        "decision_agent": decision_report,

        "disclaimer": (
            "This report is generated for educational and "
            "research purposes only and is not financial advice."
        )
    }

    file_path = f"reports/{ticker}_day3.json"

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            final_data,
            f,
            indent=4,
            ensure_ascii=False
        )

    return file_path


# ============================================================
# 11. 主程序
# ============================================================

if __name__ == "__main__":

    try:

        print("\n======================================")
        print("   MULTI-AGENT EQUITY RESEARCH")
        print("======================================")

        ticker = input(
            "\nEnter stock ticker: "
        ).strip().upper()


        # ----------------------------------------------------
        # STEP 1 — Market Data
        # ----------------------------------------------------

        print(
            "\n[1/5] Collecting market data..."
        )

        stock_data = get_stock_data(
            ticker
        )

        print(
            "✓ Market data collected"
        )


        # ----------------------------------------------------
        # STEP 2 — Fundamental Agent
        # ----------------------------------------------------

        print(
            "\n[2/5] Fundamental Agent is analyzing..."
        )

        fundamental_report = fundamental_agent(
            stock_data
        )

        print(
            "✓ Fundamental Agent completed"
        )


        # ----------------------------------------------------
        # STEP 3 — Technical Agent
        # ----------------------------------------------------

        print(
            "\n[3/5] Technical Agent is analyzing..."
        )

        technical_report = technical_agent(
            stock_data
        )

        print(
            "✓ Technical Agent completed"
        )


        # ----------------------------------------------------
        # STEP 4 — News Agent
        # ----------------------------------------------------

        print(
            "\n[4/5] News Agent is analyzing..."
        )

        news_report = news_agent(
            stock_data
        )

        print(
            "✓ News Agent completed"
        )


        # ----------------------------------------------------
        # STEP 5 — Decision Agent
        # ----------------------------------------------------

        print(
            "\n[5/5] Decision Agent is reviewing "
            "all analyst reports..."
        )

        decision_report = decision_agent(
            stock_data,
            fundamental_report,
            technical_report,
            news_report
        )

        print(
            "✓ Decision Agent completed"
        )


        # ----------------------------------------------------
        # 提取 Summary
        # ----------------------------------------------------

        fundamental_score = extract_score(
            fundamental_report,
            "Fundamental"
        )

        technical_score = extract_score(
            technical_report,
            "Technical"
        )

        news_score = extract_score(
            news_report,
            "News"
        )

        final_rating = extract_rating(
            decision_report
        )

        confidence = extract_confidence(
            decision_report
        )

        risk_level = extract_risk(
            decision_report
        )


        # ----------------------------------------------------
        # 打印 Summary
        # ----------------------------------------------------

        print(
            "\n\n======================================"
        )

        print(
            "            FINAL SUMMARY"
        )

        print(
            "======================================"
        )

        print(
            f"\nCompany: {stock_data['company']}"
        )

        print(
            f"Ticker: {ticker}"
        )

        print(
            f"Current Price: {stock_data['price']}"
        )

        print(
            "\n--------------------------------------"
        )

        print(
            f"Fundamental Score: {fundamental_score}/100"
        )

        print(
            f"Technical Score: {technical_score}/100"
        )

        print(
            f"News Score: {news_score}/100"
        )

        print(
            "--------------------------------------"
        )

        print(
            f"\nFINAL RATING: {final_rating}"
        )

        print(
            f"CONFIDENCE: {confidence}/100"
        )

        print(
            f"RISK LEVEL: {risk_level}"
        )


        # ----------------------------------------------------
        # 打印三个 Analyst
        # ----------------------------------------------------

        print(
            "\n\n======================================"
        )

        print(
            " FUNDAMENTAL AGENT"
        )

        print(
            "======================================\n"
        )

        print(
            fundamental_report
        )


        print(
            "\n\n======================================"
        )

        print(
            " TECHNICAL AGENT"
        )

        print(
            "======================================\n"
        )

        print(
            technical_report
        )


        print(
            "\n\n======================================"
        )

        print(
            " NEWS AGENT"
        )

        print(
            "======================================\n"
        )

        print(
            news_report
        )


        # ----------------------------------------------------
        # Decision Report
        # ----------------------------------------------------

        print(
            "\n\n======================================"
        )

        print(
            " DECISION AGENT"
        )

        print(
            "======================================\n"
        )

        print(
            decision_report
        )


        # ----------------------------------------------------
        # 保存
        # ----------------------------------------------------

        file_path = save_day3_report(
            ticker,
            stock_data,
            fundamental_report,
            technical_report,
            news_report,
            decision_report
        )


        print(
            "\n\n======================================"
        )

        print(
            " ANALYSIS COMPLETED"
        )

        print(
            "======================================"
        )

        print(
            f"\nSaved to: {file_path}"
        )

        print(
            "\nEducational research only — "
            "not financial advice."
        )


    except Exception as e:

        print(
            "\nError:",
            e
        )
