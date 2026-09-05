import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime


# ============================================================
# 工具函数：把 numpy / NaN 转成普通 Python 数据
# ============================================================

def clean_number(value):

    if pd.isna(value):
        return None

    return float(value)


# ============================================================
# 获取股票数据
# ============================================================

def get_stock_data(ticker_symbol):

    ticker_symbol = ticker_symbol.strip().upper()

    if not ticker_symbol:
        raise ValueError("Ticker cannot be empty.")

    # --------------------------------------------------------
    # 1. 获取股票对象
    # --------------------------------------------------------

    stock = yf.Ticker(ticker_symbol)

    # 一次抓 6 个月历史数据
    history = stock.history(
        period="6mo"
    )

    if history.empty:
        raise ValueError(
            f"No market data found for {ticker_symbol}. "
            "Please check the ticker symbol."
        )

    info = stock.info


    # --------------------------------------------------------
    # 2. Moving Average
    # --------------------------------------------------------

    history["MA20"] = (
        history["Close"]
        .rolling(window=20)
        .mean()
    )

    history["MA50"] = (
        history["Close"]
        .rolling(window=50)
        .mean()
    )


    # --------------------------------------------------------
    # 3. RSI
    # --------------------------------------------------------

    delta = history["Close"].diff()

    gain = delta.where(
        delta > 0,
        0
    )

    loss = -delta.where(
        delta < 0,
        0
    )

    avg_gain = gain.rolling(
        window=14
    ).mean()

    avg_loss = loss.rolling(
        window=14
    ).mean()

    rs = avg_gain / avg_loss

    history["RSI"] = (
        100 - (100 / (1 + rs))
    )


    # --------------------------------------------------------
    # 4. MACD
    # --------------------------------------------------------

    ema12 = history["Close"].ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = history["Close"].ewm(
        span=26,
        adjust=False
    ).mean()

    history["MACD"] = (
        ema12 - ema26
    )

    history["MACD_Signal"] = (
        history["MACD"]
        .ewm(
            span=9,
            adjust=False
        )
        .mean()
    )


    # --------------------------------------------------------
    # 5. 最新交易日
    # --------------------------------------------------------

    latest = history.iloc[-1]


    # --------------------------------------------------------
    # 6. 新闻
    # --------------------------------------------------------

    news_list = []

    try:

        news = stock.news

        for item in news[:5]:

            if "content" in item:

                content = item.get(
                    "content",
                    {}
                )

                title = content.get(
                    "title"
                )

                publisher = (
                    content
                    .get("provider", {})
                    .get("displayName")
                )

                link = (
                    content
                    .get("canonicalUrl", {})
                    .get("url")
                )

            else:

                title = item.get(
                    "title"
                )

                publisher = item.get(
                    "publisher"
                )

                link = item.get(
                    "link"
                )

            news_list.append(
                {
                    "title": title,
                    "publisher": publisher,
                    "link": link
                }
            )

    except Exception as e:

        print(
            "News could not be loaded:",
            e
        )


    # --------------------------------------------------------
    # 7. 保存走势图历史数据
    # --------------------------------------------------------

    price_history = []

    for date, row in history.iterrows():

        price_history.append(
            {
                "date": date.strftime(
                    "%Y-%m-%d"
                ),

                "close": clean_number(
                    row["Close"]
                ),

                "ma20": clean_number(
                    row["MA20"]
                ),

                "ma50": clean_number(
                    row["MA50"]
                )
            }
        )


    # --------------------------------------------------------
    # 8. 当前价格
    # --------------------------------------------------------

    current_price = info.get(
        "currentPrice"
    )

    if current_price is None:

        current_price = latest[
            "Close"
        ]


    # --------------------------------------------------------
    # 9. 最终结构
    # --------------------------------------------------------

    stock_data = {

        "ticker": ticker_symbol,

        "company": info.get(
            "longName"
        ),

        "analysis_date": (
            datetime.now()
            .strftime("%Y-%m-%d")
        ),

        "price": clean_number(
            current_price
        ),

        "market_cap": (
            info.get("marketCap")
        ),

        "pe_ratio": (
            clean_number(
                info.get("trailingPE")
            )
            if info.get("trailingPE")
            is not None
            else None
        ),

        "revenue_growth": (
            clean_number(
                info.get("revenueGrowth")
            )
            if info.get("revenueGrowth")
            is not None
            else None
        ),

        "profit_margin": (
            clean_number(
                info.get("profitMargins")
            )
            if info.get("profitMargins")
            is not None
            else None
        ),

        "52_week_high": (
            clean_number(
                info.get("fiftyTwoWeekHigh")
            )
            if info.get("fiftyTwoWeekHigh")
            is not None
            else None
        ),

        "52_week_low": (
            clean_number(
                info.get("fiftyTwoWeekLow")
            )
            if info.get("fiftyTwoWeekLow")
            is not None
            else None
        ),

        "ma20": clean_number(
            round(
                latest["MA20"],
                2
            )
        ),

        "ma50": clean_number(
            round(
                latest["MA50"],
                2
            )
        ),

        "rsi": clean_number(
            round(
                latest["RSI"],
                2
            )
        ),

        "macd": clean_number(
            round(
                latest["MACD"],
                2
            )
        ),

        "macd_signal": clean_number(
            round(
                latest["MACD_Signal"],
                2
            )
        ),

        "volume": int(
            latest["Volume"]
        ),

        "news": news_list,

        # 关键新增
        "price_history": price_history
    }

    return stock_data


# ============================================================
# 保存 Market Data
# ============================================================

def save_stock_data(data):

    os.makedirs(
        "reports",
        exist_ok=True
    )

    ticker = data["ticker"]

    file_path = (
        f"reports/{ticker}.json"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

    return file_path


# ============================================================
# 单独运行测试
# ============================================================

if __name__ == "__main__":

    try:

        ticker = input(
            "Enter stock ticker: "
        ).strip().upper()

        data = get_stock_data(
            ticker
        )

        print(
            "\n=== STOCK DATA ==="
        )

        print(
            data
        )

        file_path = save_stock_data(
            data
        )

        print(
            f"\nSaved to: {file_path}"
        )

    except Exception as e:

        print(
            "\nError:",
            e
        )