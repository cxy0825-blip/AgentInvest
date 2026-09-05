import os

from market_data import get_stock_data

from day3_agents import (
    fundamental_agent,
    technical_agent,
    news_agent,
    decision_agent,
    save_day3_report
)


# ============================================================
# 要分析的股票
# ============================================================

TICKERS = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "TSLA"
]


# ============================================================
# 单只股票分析
# ============================================================

def analyze_stock(ticker):

    print("\n")
    print("=" * 50)
    print(f" STARTING ANALYSIS: {ticker}")
    print("=" * 50)


    # --------------------------------------------------------
    # 1. Market Data
    # --------------------------------------------------------

    print(
        f"\n[{ticker}] 1/5 Collecting market data..."
    )

    stock_data = get_stock_data(
        ticker
    )

    print(
        f"✓ {ticker} market data collected"
    )


    # --------------------------------------------------------
    # 2. Fundamental Agent
    # --------------------------------------------------------

    print(
        f"\n[{ticker}] 2/5 Fundamental Agent..."
    )

    fundamental_report = fundamental_agent(
        stock_data
    )

    print(
        f"✓ {ticker} Fundamental Agent completed"
    )


    # --------------------------------------------------------
    # 3. Technical Agent
    # --------------------------------------------------------

    print(
        f"\n[{ticker}] 3/5 Technical Agent..."
    )

    technical_report = technical_agent(
        stock_data
    )

    print(
        f"✓ {ticker} Technical Agent completed"
    )


    # --------------------------------------------------------
    # 4. News Agent
    # --------------------------------------------------------

    print(
        f"\n[{ticker}] 4/5 News Agent..."
    )

    news_report = news_agent(
        stock_data
    )

    print(
        f"✓ {ticker} News Agent completed"
    )


    # --------------------------------------------------------
    # 5. Decision Agent
    # --------------------------------------------------------

    print(
        f"\n[{ticker}] 5/5 Decision Agent..."
    )

    decision_report = decision_agent(
        stock_data,
        fundamental_report,
        technical_report,
        news_report
    )

    print(
        f"✓ {ticker} Decision Agent completed"
    )


    # --------------------------------------------------------
    # 保存报告
    # --------------------------------------------------------

    file_path = save_day3_report(
        ticker,
        stock_data,
        fundamental_report,
        technical_report,
        news_report,
        decision_report
    )

    print(
        f"\n✓ Saved: {file_path}"
    )

    print(
        f"✓ {ticker} ANALYSIS COMPLETE"
    )


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 55)
    print("     MULTI-STOCK AI EQUITY RESEARCH")
    print("=" * 55)

    print(
        "\nTarget Stocks:"
    )

    for ticker in TICKERS:
        print(
            f"- {ticker}"
        )


    print(
        "\nExisting Day 3 reports will be skipped "
        "to avoid unnecessary API usage."
    )


    completed = []
    skipped = []
    failed = []


    for ticker in TICKERS:

        report_path = (
            f"reports/{ticker}_day3.json"
        )


        # ----------------------------------------------------
        # 已经跑过就跳过
        # ----------------------------------------------------

        if os.path.exists(
            report_path
        ):

            print("\n")
            print("-" * 50)

            print(
                f"SKIPPING {ticker}"
            )

            print(
                f"Report already exists: {report_path}"
            )

            skipped.append(
                ticker
            )

            continue


        # ----------------------------------------------------
        # 跑新的股票
        # ----------------------------------------------------

        try:

            analyze_stock(
                ticker
            )

            completed.append(
                ticker
            )

        except Exception as e:

            print("\n")
            print(
                f"ERROR analyzing {ticker}:"
            )

            print(
                e
            )

            failed.append(
                ticker
            )


    # ========================================================
    # 最终结果
    # ========================================================

    print("\n")
    print("=" * 55)
    print("             BATCH COMPLETE")
    print("=" * 55)


    print(
        "\nNew Reports:"
    )

    if completed:

        for ticker in completed:
            print(
                f"✓ {ticker}"
            )

    else:

        print(
            "None"
        )


    print(
        "\nSkipped Existing Reports:"
    )

    if skipped:

        for ticker in skipped:
            print(
                f"→ {ticker}"
            )

    else:

        print(
            "None"
        )


    print(
        "\nFailed:"
    )

    if failed:

        for ticker in failed:
            print(
                f"✗ {ticker}"
            )

    else:

        print(
            "None"
        )


    print("\n")
    print(
        "Open the Streamlit dashboard to view all reports."
    )