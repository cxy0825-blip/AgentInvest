"""
app.py — AgentInvest, terminal edition.

Drop this next to your existing market_data.py / day3_agents.py and run:

    streamlit run app.py

Everything visual lives in terminal_ui.py; this file only handles data
(loading saved reports, running a new analysis) and mounts the UI.
"""

import glob
import json
import os

import streamlit as st
import streamlit.components.v1 as components

from terminal_ui import build_terminal_html

REPORTS_DIR = "reports"

st.set_page_config(
    page_title="AgentInvest Terminal",
    page_icon="▪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# strip Streamlit chrome so the component reads as a full-bleed terminal
st.markdown(
    """
    <style>
      #MainMenu, footer, header {visibility: hidden;}
      .block-container {padding: 0 !important; max-width: 100% !important;}
      [data-testid="stAppViewContainer"] {background: #08090b;}
      [data-testid="stSidebar"] {background: #0b0e13; border-right: 1px solid #1c2230;}
      [data-testid="stSidebar"] * {color: #c3cbd8;}
      [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
      [data-testid="stSidebar"] h3 {color: #e8ecf2; letter-spacing: 1.4px;}
      iframe {border: 0;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------
# data
# ------------------------------------------------------------------

def load_report(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def saved_reports():
    out = {}
    for path in glob.glob(os.path.join(REPORTS_DIR, "*_day3.json")):
        ticker = os.path.basename(path).replace("_day3.json", "")
        out[ticker] = path
    return out


def run_new_analysis(ticker):
    """Unchanged pipeline — only the status copy is terminal-styled."""
    from market_data import get_stock_data
    from day3_agents import (
        fundamental_agent,
        technical_agent,
        news_agent,
        decision_agent,
        save_day3_report,
    )

    ticker = (ticker or "").strip().upper()
    if not ticker:
        raise ValueError("Enter a valid ticker.")

    with st.status("BUILDING %s RESEARCH FILE" % ticker, expanded=True) as status:
        st.write("01 · INGEST — market and company data")
        stock_data = get_stock_data(ticker)

        st.write("02A · FUNDAMENTAL — valuation, growth, profitability")
        fundamental = fundamental_agent(stock_data)

        st.write("02B · TECHNICAL — trend and momentum")
        technical = technical_agent(stock_data)

        st.write("02C · NEWS — catalysts and sentiment")
        news = news_agent(stock_data)

        st.write("03 · COMMITTEE — synthesising analyst evidence")
        decision = decision_agent(stock_data, fundamental, technical, news)

        path = save_day3_report(ticker, stock_data, fundamental, technical, news, decision)
        status.update(label="%s RESEARCH COMPLETE" % ticker, state="complete", expanded=False)

    return load_report(path)


# ------------------------------------------------------------------
# sidebar controls
# ------------------------------------------------------------------

if "data" not in st.session_state:
    st.session_state.data = None

st.sidebar.markdown("### ▪ AGENTINVEST")
st.sidebar.caption("Multi-agent equity research terminal")
st.sidebar.divider()

st.sidebar.markdown("##### NEW ANALYSIS")
ticker_input = st.sidebar.text_input(
    "Ticker", placeholder="GOOGL, META, JPM…", label_visibility="collapsed"
)
if st.sidebar.button("RUN AGENTS", type="primary", use_container_width=True):
    try:
        st.session_state.data = run_new_analysis(ticker_input)
        st.rerun()
    except Exception as exc:  # noqa: BLE001
        st.sidebar.error("Analysis failed: %s" % exc)

st.sidebar.divider()
st.sidebar.markdown("##### SAVED COVERAGE")

reports = saved_reports()
tickers = sorted(reports)

if tickers:
    choice = st.sidebar.selectbox("Report", tickers, label_visibility="collapsed")
    if st.sidebar.button("OPEN REPORT", use_container_width=True):
        st.session_state.data = load_report(reports[choice])
        st.rerun()
    # auto-open the first report so the terminal is never empty
    if st.session_state.data is None:
        st.session_state.data = load_report(reports[tickers[0]])
else:
    st.sidebar.caption("No saved reports yet.")

st.sidebar.divider()
st.sidebar.caption("Educational research only. Not financial advice.")


# ------------------------------------------------------------------
# render
# ------------------------------------------------------------------

if st.session_state.data is None:
    st.markdown(
        """
        <div style="font-family:'IBM Plex Mono',monospace;color:#8b95a5;padding:60px 40px;
                    letter-spacing:1px;background:#08090b;min-height:70vh">
          <div style="color:#d8a341;font-size:11px;letter-spacing:2px">AGENTINVEST · IDLE</div>
          <div style="color:#e8ecf2;font-size:26px;margin-top:14px;font-family:'IBM Plex Sans',sans-serif">
            No research file loaded</div>
          <div style="margin-top:10px;font-size:12px">
            Enter a ticker and run the agents, or open a saved report.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    components.html(
        build_terminal_html(st.session_state.data),
        height=2600,
        scrolling=True,
    )
