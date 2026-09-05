import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from market_data import (
    get_stock_data,
    save_stock_data
)


# ==========================================
# 1. 加载 API Key
# ==========================================

load_dotenv()

api_key = os.getenv(
    "OPENAI_API_KEY"
)

if not api_key:

    raise ValueError(
        "OPENAI_API_KEY not found. "
        "Please check your .env file."
    )


client = OpenAI(
    api_key=api_key
)


# ==========================================
# 2. Fundamental Agent
# ==========================================

def fundamental_agent(stock_data):

    fundamental_data = {

        "ticker":
            stock_data["ticker"],

        "company":
            stock_data["company"],

        "price":
            stock_data["price"],

        "market_cap":
            stock_data["market_cap"],

        "pe_ratio":
            stock_data["pe_ratio"],

        "revenue_growth":
            stock_data["revenue_growth"],

        "profit_margin":
            stock_data["profit_margin"],

        "52_week_high":
            stock_data["52_week_high"],

        "52_week_low":
            stock_data["52_week_low"]
    }


    prompt = f"""
You are a professional equity research
fundamental analyst.

Analyze the following company data:

{json.dumps(
    fundamental_data,
    indent=2
)}

Evaluate:

1. Valuation
2. Revenue growth
3. Profitability
4. Company strengths
5. Fundamental risks

Important:
Only use the data provided.
Do not invent financial information.

Return a concise equity research report.

At the end, provide exactly:

Fundamental Score: XX/100

Fundamental View:
Bullish, Neutral, or Bearish
"""


    response = client.responses.create(

        model="gpt-5.6-luna",

        input=prompt
    )


    return response.output_text


# ==========================================
# 3. Technical Agent
# ==========================================

def technical_agent(stock_data):

    technical_data = {

        "ticker":
            stock_data["ticker"],

        "price":
            stock_data["price"],

        "ma20":
            stock_data["ma20"],

        "ma50":
            stock_data["ma50"],

        "rsi":
            stock_data["rsi"],

        "macd":
            stock_data["macd"],

        "macd_signal":
            stock_data["macd_signal"],

        "volume":
            stock_data["volume"],

        "52_week_high":
            stock_data["52_week_high"],

        "52_week_low":
            stock_data["52_week_low"]
    }


    prompt = f"""
You are a professional technical analyst.

Analyze the following stock data:

{json.dumps(
    technical_data,
    indent=2
)}

Evaluate:

1. Short-term price trend
2. MA20 and MA50 relationship
3. RSI
4. MACD and MACD signal
5. Momentum
6. Technical risks

Important:
Only use the supplied data.
Do not invent chart patterns or price data.

Return a concise technical research report.

At the end, provide exactly:

Technical Score: XX/100

Technical View:
Bullish, Neutral, or Bearish
"""


    response = client.responses.create(

        model="gpt-5.6-luna",

        input=prompt
    )


    return response.output_text


# ==========================================
# 4. 保存 Day 2 Agent 报告
# ==========================================

def save_agent_report(

    ticker,
    stock_data,
    fundamental_report,
    technical_report

):

    os.makedirs(
        "reports",
        exist_ok=True
    )


    final_data = {

        "ticker":
            ticker,

        "market_data":
            stock_data,

        "fundamental_agent":
            fundamental_report,

        "technical_agent":
            technical_report
    }


    file_path = (
        f"reports/"
        f"{ticker}_day2.json"
    )


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


# ==========================================
# 5. 主程序
# ==========================================

if __name__ == "__main__":

    try:

        print(
            "\n"
            "=============================="
        )

        print(
            " AI Equity Research System"
        )

        print(
            "=============================="
        )


        ticker = input(
            "\nEnter stock ticker: "
        ).strip().upper()


        # ----------------------------------
        # Step 1 Market Data
        # ----------------------------------

        print(
            "\n[1/3] Collecting market data..."
        )

        stock_data = get_stock_data(
            ticker
        )

        print(
            "✓ Market data collected"
        )


        # ----------------------------------
        # Step 2 Fundamental Agent
        # ----------------------------------

        print(
            "\n[2/3] Fundamental Agent "
            "is analyzing..."
        )

        fundamental_report = (
            fundamental_agent(
                stock_data
            )
        )

        print(
            "✓ Fundamental Agent completed"
        )


        # ----------------------------------
        # Step 3 Technical Agent
        # ----------------------------------

        print(
            "\n[3/3] Technical Agent "
            "is analyzing..."
        )

        technical_report = (
            technical_agent(
                stock_data
            )
        )

        print(
            "✓ Technical Agent completed"
        )


        # ----------------------------------
        # 展示报告
        # ----------------------------------

        print(
            "\n"
            "=============================="
        )

        print(
            " FUNDAMENTAL ANALYST"
        )

        print(
            "==============================\n"
        )

        print(
            fundamental_report
        )


        print(
            "\n"
            "=============================="
        )

        print(
            " TECHNICAL ANALYST"
        )

        print(
            "==============================\n"
        )

        print(
            technical_report
        )


        # ----------------------------------
        # 保存报告
        # ----------------------------------

        file_path = save_agent_report(

            ticker,

            stock_data,

            fundamental_report,

            technical_report
        )


        print(
            "\n"
            "=============================="
        )

        print(
            " ANALYSIS COMPLETED"
        )

        print(
            "=============================="
        )

        print(
            f"\nSaved to: {file_path}"
        )


    except Exception as e:

        print(
            "\nError:",
            e
        )