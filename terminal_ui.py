"""
terminal_ui.py 鈥?renders the AgentInvest terminal UI as a single HTML string.

Usage from Streamlit:

    import streamlit.components.v1 as components
    from terminal_ui import build_terminal_html

    components.html(build_terminal_html(data), height=2400, scrolling=True)

`data` is one of your reports/<TICKER>_day3.json dicts.
All navigation happens inside the component (no Streamlit reruns).
"""

import html as _html
import re

# ------------------------------------------------------------------
# palette
# ------------------------------------------------------------------

BG      = "#08090b"
PANEL   = "#0b0e13"
PANEL2  = "#0d1116"
LINE    = "#1c2230"
LINE2   = "#161c26"
TEXT    = "#e8ecf2"
TEXT2   = "#c3cbd8"
DIM     = "#8b95a5"
FAINT   = "#5b6572"
AMBER   = "#d8a341"
UP      = "#34c98a"
DOWN    = "#f2585b"
BLUE    = "#5b8def"

MONO = "'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
SANS = "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"


# ------------------------------------------------------------------
# formatting helpers
# ------------------------------------------------------------------

def _num(v, fmt="{:,.2f}", fallback="N/A"):
    try:
        return fmt.format(float(v))
    except (TypeError, ValueError):
        return fallback


def _pct(v, digits=1, fallback="N/A"):
    """0.096 -> +9.6%"""
    try:
        return "{:+.{d}f}%".format(float(v) * 100, d=digits)
    except (TypeError, ValueError):
        return fallback


def _cap(v, fallback="N/A"):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return fallback
    if v >= 1e12:
        return "${:.2f}T".format(v / 1e12)
    if v >= 1e9:
        return "${:.2f}B".format(v / 1e9)
    if v >= 1e6:
        return "${:.1f}M".format(v / 1e6)
    return "${:,.0f}".format(v)


def _score_color(score):
    try:
        score = float(score)
    except (TypeError, ValueError):
        return DIM
    if score >= 67:
        return UP
    if score >= 45:
        return AMBER
    return DOWN


def _rating_color(rating):
    r = (rating or "").upper()
    if r == "BUY":
        return UP
    if r == "SELL":
        return DOWN
    return AMBER


def _stance(score):
    try:
        score = float(score)
    except (TypeError, ValueError):
        return "N/A"
    if score >= 67:
        return "BUY"
    if score >= 45:
        return "HOLD"
    return "SELL"


# ------------------------------------------------------------------
# minimal markdown -> html (agent reports are LLM markdown)
# ------------------------------------------------------------------

def md_to_html(text):
    if not text:
        return '<div class="p" style="color:%s">No report available.</div>' % FAINT

    def inline(s):
        s = _html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r'<strong style="color:%s;font-weight:600">\1</strong>' % TEXT, s)
        s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", s)
        s = re.sub(r"`(.+?)`", r'<code style="font-family:%s;font-size:12px;color:%s">\1</code>' % (MONO, AMBER), s)
        return s

    out, bullets = [], []

    def flush():
        if bullets:
            out.append('<div class="bullets">' + "".join(bullets) + "</div>")
            bullets.clear()

    for raw in text.split("\n"):
        line = raw.rstrip()
        s = line.strip()
        if not s:
            flush()
            continue
        if s.startswith("####"):
            flush()
            out.append('<div class="h3">%s</div>' % inline(s.lstrip("#").strip()))
        elif s.startswith("###") or s.startswith("##") or s.startswith("#"):
            flush()
            out.append('<div class="h2"><span class="tick"></span>%s</div>'
                       % inline(s.lstrip("#").strip()))
        elif s.startswith(("- ", "* ")):
            bullets.append('<div class="li"><span class="dot"></span><span>%s</span></div>'
                           % inline(s[2:].strip()))
        elif re.match(r"^\d+[.)]\s", s):
            n, rest = re.split(r"[.)]\s", s, 1)
            bullets.append('<div class="li"><span class="num">%s</span><span>%s</span></div>'
                           % (_html.escape(n), inline(rest)))
        elif set(s) <= set("-=_") and len(s) >= 3:
            flush()
            out.append('<div class="rule"></div>')
        else:
            flush()
            out.append('<div class="p">%s</div>' % inline(s))
    flush()
    return "".join(out)


# ------------------------------------------------------------------
# svg price chart from price_history
# ------------------------------------------------------------------

def _chart(price_history):
    rows = [r for r in (price_history or []) if r.get("close") is not None]
    if len(rows) < 2:
        return None

    closes = [float(r["close"]) for r in rows]
    ma20 = [(float(r["ma20"]) if r.get("ma20") is not None else None) for r in rows]
    ma50 = [(float(r["ma50"]) if r.get("ma50") is not None else None) for r in rows]
    dates = [str(r.get("date", ""))[:10] for r in rows]

    vals = closes + [v for v in ma20 if v] + [v for v in ma50 if v]
    lo, hi = min(vals), max(vals)
    if hi == lo:
        hi = lo + 1.0
    n = len(rows)

    def X(i):
        return (i / (n - 1)) * 1000.0

    def Y(v):
        return 290.0 - ((v - lo) / (hi - lo)) * 280.0

    def path(series):
        d, open_ = [], False
        for i, v in enumerate(series):
            if v is None:
                open_ = False
                continue
            d.append(("L" if open_ else "M") + " %.2f %.2f" % (X(i), Y(v)))
            open_ = True
        return " ".join(d)

    close_p = path(closes)
    area_p = close_p + " L 1000 300 L 0 300 Z" if close_p else ""

    y_ticks = []
    for i in range(5):
        v = lo + (hi - lo) * i / 4.0
        y = Y(v)
        y_ticks.append((y, y / 300.0 * 100.0, "%.0f" % v))

    x_ticks = []
    for i in range(6):
        idx = round((n - 1) * i / 5.0)
        x = X(idx)
        x_ticks.append((x, x / 1000.0 * 100.0, dates[idx][5:] or dates[idx]))

    return {
        "close": close_p,
        "ma20": path(ma20),
        "ma50": path(ma50),
        "area": area_p,
        "y": y_ticks,
        "x": x_ticks,
    }


# ------------------------------------------------------------------
# small markup helpers
# ------------------------------------------------------------------

def _cell(label, value, note="", note_color=DIM):
    return (
        '<div class="cell">'
        '<div class="cell-l">%s</div>'
        '<div class="cell-v"><span>%s</span><span class="cell-n" style="color:%s">%s</span></div>'
        "</div>" % (_html.escape(label), _html.escape(str(value)), note_color, _html.escape(note))
    )


def _kv(label, value, color=TEXT):
    return (
        '<div class="kv"><span>%s</span><span style="color:%s">%s</span></div>'
        % (_html.escape(label), color, _html.escape(str(value)))
    )


CSS = """
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:__BG__;color:__TEXT__;font-family:__SANS__;
  -webkit-font-smoothing:antialiased;font-size:13px}
a{color:__AMBER__;text-decoration:none}
a:hover{color:#f0c273;text-decoration:underline}
.mono{font-family:__MONO__}
.wrap{display:flex;min-height:100vh}
.main{flex:1 1 auto;min-width:0}
.top{display:flex;align-items:center;gap:18px;height:46px;padding:0 18px;
  border-bottom:1px solid __LINE__;background:__PANEL__}
.brand{display:flex;align-items:center;gap:9px;font-size:14px;font-weight:700;letter-spacing:2.4px}
.sq{width:11px;height:11px;background:__AMBER__}
.vr{width:1px;height:18px;background:__LINE__}
.top-sub{font-size:10.5px;letter-spacing:1.6px;color:__DIM__;font-weight:600}
.spacer{flex:1 1 auto}
.head{display:flex;border-bottom:1px solid __LINE__;background:__PANEL2__}
.head-l{flex:1 1 auto;padding:20px 24px}
.tk{font-family:__MONO__;font-size:26px;font-weight:600;letter-spacing:1px}
.co{font-size:17px;font-weight:600;color:__TEXT2__}
.meta{font-family:__MONO__;font-size:10.5px;color:__FAINT__;letter-spacing:1px}
.px{font-family:__MONO__;font-size:42px;font-weight:500;line-height:1}
.quote{display:flex;gap:26px;margin-top:18px;padding-top:14px;border-top:1px solid __LINE2__;flex-wrap:wrap}
.quote>div{display:flex;flex-direction:column;gap:4px}
.quote .ql{font-size:9.5px;letter-spacing:1.2px;color:__FAINT__;font-weight:600}
.quote .qv{font-family:__MONO__;font-size:12.5px;color:#d3dae4}
.side{width:268px;flex:0 0 268px;border-left:1px solid __LINE__;padding:20px 22px;background:__PANEL__}
.side-h{font-size:9.5px;letter-spacing:1.6px;color:__DIM__;font-weight:700}
.kv{display:flex;justify-content:space-between;gap:10px;padding:8px 0;
  border-bottom:1px solid #151b25;font-family:__MONO__;font-size:11px;color:__DIM__}
.bar{height:3px;background:#171d27;margin-top:10px}
.bar>i{display:block;height:3px}
.scores{display:grid;grid-template-columns:repeat(3,1fr);border-bottom:1px solid __LINE__}
.score{padding:16px 22px;border-right:1px solid __LINE__;cursor:pointer;background:#0a0d12}
.score:hover{background:#0f141c}
.score-l{font-size:9.5px;letter-spacing:1.6px;color:__DIM__;font-weight:700}
.score-v{font-family:__MONO__;font-size:30px;font-weight:500;margin-top:8px}
.sec-h{font-size:10px;letter-spacing:1.6px;color:__DIM__;font-weight:700}
.grid{display:grid;gap:1px;background:__LINE2__;border:1px solid __LINE2__;margin-top:12px}
.g5{grid-template-columns:repeat(5,1fr)}
.g4{grid-template-columns:repeat(4,1fr)}
.g2{grid-template-columns:repeat(2,1fr)}
.cell{background:__PANEL__;padding:12px 14px}
.cell-l{font-size:9.5px;letter-spacing:1.1px;color:__FAINT__;font-weight:600}
.cell-v{display:flex;align-items:baseline;gap:7px;margin-top:6px;font-family:__MONO__;font-size:15px;color:__TEXT__}
.cell-n{font-size:10px}
.dossier{background:__PANEL__;padding:15px 18px;cursor:pointer;display:flex;flex-direction:column;gap:8px}
.dossier:hover{background:#101620}
.dossier .code{font-family:__MONO__;font-size:10px;color:__AMBER__;letter-spacing:1px}
.dossier .t{font-size:14px;font-weight:600;letter-spacing:.4px}
.dossier .sum{font-size:11.5px;color:__DIM__;line-height:1.6;text-wrap:pretty}
.crumb{display:flex;align-items:center;gap:12px;padding:10px 22px;
  border-bottom:1px solid __LINE__;background:__PANEL__}
.crumb .b{font-family:__MONO__;font-size:10.5px;color:__AMBER__;letter-spacing:1px;cursor:pointer}
.crumb .b:hover{color:#f0c273}
.kicker{font-family:__MONO__;font-size:10px;letter-spacing:1.8px;color:__AMBER__;font-weight:600}
.title{font-size:30px;font-weight:700;margin-top:8px}
.desc{font-size:13px;color:__DIM__;line-height:1.65;margin-top:8px;max-width:720px;text-wrap:pretty}
.body{padding:22px 24px 34px;max-width:880px}
.body .h2{display:flex;align-items:center;gap:10px;font-size:13px;font-weight:700;
  letter-spacing:1.2px;margin:26px 0 4px}
.body .tick{width:4px;height:13px;background:__AMBER__;display:inline-block}
.body .h3{font-size:12px;font-weight:700;letter-spacing:1px;color:__TEXT2__;margin:18px 0 2px}
.body .p{font-size:13.5px;line-height:1.8;color:__TEXT2__;margin-top:12px;text-wrap:pretty}
.body .bullets{display:flex;flex-direction:column;gap:8px;margin-top:14px;
  border-left:1px solid __LINE__;padding-left:16px}
.body .li{display:flex;gap:10px;font-size:12.5px;line-height:1.7;color:#a7b1bf}
.body .dot{width:4px;height:4px;background:__AMBER__;margin-top:8px;flex:0 0 4px}
.body .num{font-family:__MONO__;font-size:10.5px;color:__AMBER__;flex:0 0 18px}
.body .rule{height:1px;background:__LINE__;margin:20px 0}
.news{border-top:1px solid __LINE2__;padding:14px 0}
.news .h{font-size:14px;font-weight:600;color:__TEXT__}
.news .p{font-family:__MONO__;font-size:10.5px;color:__FAINT__;letter-spacing:.8px;margin-top:5px}
.foot{display:flex;gap:16px;padding:10px 22px;border-top:1px solid __LINE__;background:__PANEL__;
  font-family:__MONO__;font-size:10px;color:#4e5764;letter-spacing:.8px}
.view{display:none}
.view.on{display:block}
@media(max-width:900px){.wrap{flex-direction:column}
  .scores,.g5,.g4,.g2{grid-template-columns:1fr}.head{flex-direction:column}
  .side{width:100%;flex:0 0 auto;border-left:0;border-top:1px solid __LINE__}}
"""


def _css():
    out = CSS
    for k, v in [("__BG__", BG), ("__PANEL2__", PANEL2), ("__PANEL__", PANEL),
                 ("__LINE2__", LINE2), ("__LINE__", LINE), ("__TEXT2__", TEXT2),
                 ("__TEXT__", TEXT), ("__DIM__", DIM), ("__FAINT__", FAINT),
                 ("__AMBER__", AMBER), ("__MONO__", MONO), ("__SANS__", SANS)]:
        out = out.replace(k, v)
    return out


# ------------------------------------------------------------------
# main entry point
# ------------------------------------------------------------------

def build_terminal_html(data):
    d = data or {}
    m = d.get("market_data", {}) or {}
    s = d.get("summary", {}) or {}
    agents = d.get("agents", {}) or {}

    ticker = d.get("ticker", "-")
    company = d.get("company", "Unknown Company")
    date = d.get("analysis_date", "-")

    f_score = s.get("fundamental_score", 0)
    t_score = s.get("technical_score", 0)
    n_score = s.get("news_score", 0)
    rating = s.get("final_rating", "N/A")
    conf = s.get("confidence", 0)
    risk = s.get("risk_level", "N/A")
    rc = _rating_color(rating)

    price = m.get("price")
    price_txt = _num(price, "{:,.2f}")

    # ---------- overview: quote bar ----------
    quote_items = [
        ("MARKET CAP", _cap(m.get("market_cap"))),
        ("P/E (TTM)", _num(m.get("pe_ratio"), "{:.2f}x")),
        ("REVENUE GROWTH", _pct(m.get("revenue_growth"))),
        ("PROFIT MARGIN", _pct(m.get("profit_margin"))),
        ("MA20 / MA50", "%s / %s" % (_num(m.get("ma20")), _num(m.get("ma50")))),
        ("RSI (14)", _num(m.get("rsi"), "{:.1f}")),
    ]
    quote_html = "".join(
        '<div><span class="ql">%s</span><span class="qv">%s</span></div>'
        % (_html.escape(k), _html.escape(v)) for k, v in quote_items
    )

    # ---------- overview: score cards ----------
    def score_card(label, score, view):
        c = _score_color(score)
        try:
            pct = max(0.0, min(100.0, float(score)))
        except (TypeError, ValueError):
            pct = 0.0
        return (
            '<div class="score" onclick="show(\'%s\')">'
            '<div style="display:flex;justify-content:space-between;align-items:center">'
            '<span class="score-l">%s</span>'
            '<span class="mono" style="font-size:10px;letter-spacing:.8px;color:%s">%s</span></div>'
            '<div class="score-v">%s<span class="mono" style="font-size:12px;color:%s">/100</span></div>'
            '<div class="bar"><i style="width:%.0f%%;background:%s"></i></div>'
            '<div style="margin-top:10px;font-size:11px;color:%s">Open the %s dossier -&gt;</div>'
            "</div>"
            % (view, _html.escape(label), c, _stance(score), _html.escape(str(score)),
               FAINT, pct, c, DIM, view)
        )

    scores_html = (
        score_card("FUNDAMENTAL ANALYST", f_score, "fundamental")
        + score_card("TECHNICAL ANALYST", t_score, "technical")
        + score_card("NEWS ANALYST", n_score, "news")
    )

    # ---------- overview: chart ----------
    ch = _chart(m.get("price_history"))
    if ch:
        grid = "".join(
            '<line x1="0" y1="%.1f" x2="1000" y2="%.1f" stroke="%s" stroke-width="1" '
            'vector-effect="non-scaling-stroke"></line>' % (y, y, LINE2) for y, _, _ in ch["y"]
        ) + "".join(
            '<line x1="%.1f" y1="0" x2="%.1f" y2="300" stroke="#12171f" stroke-width="1" '
            'vector-effect="non-scaling-stroke"></line>' % (x, x) for x, _, _ in ch["x"]
        )
        y_labels = "".join(
            '<div style="position:absolute;right:6px;top:%.2f%%;transform:translateY(-50%%);'
            'font-family:%s;font-size:10px;color:#6b7686">%s</div>' % (top, MONO, lbl)
            for _, top, lbl in ch["y"]
        )
        x_labels = "".join(
            '<div style="position:absolute;left:%.2f%%;transform:translateX(-50%%);'
            'font-family:%s;font-size:10px;color:%s;letter-spacing:.6px">%s</div>'
            % (left, MONO, FAINT, _html.escape(lbl)) for _, left, lbl in ch["x"]
        )
        chart_html = (
            '<div style="display:flex;margin-top:14px">'
            '<div style="flex:1 1 auto;min-width:0;height:268px;border:1px solid %s;border-right:0;background:#0a0d12">'
            '<svg viewBox="0 0 1000 300" preserveAspectRatio="none" style="width:100%%;height:100%%;display:block">'
            '%s<path d="%s" fill="#111820"></path>'
            '<path d="%s" fill="none" stroke="%s" stroke-width="1.4" vector-effect="non-scaling-stroke"></path>'
            '<path d="%s" fill="none" stroke="%s" stroke-width="1.4" vector-effect="non-scaling-stroke"></path>'
            '<path d="%s" fill="none" stroke="%s" stroke-width="1.6" vector-effect="non-scaling-stroke"></path>'
            "</svg></div>"
            '<div style="width:58px;flex:0 0 58px;height:268px;border:1px solid %s;position:relative;background:#0a0d12">%s</div>'
            "</div>"
            '<div style="position:relative;height:16px;margin:4px 58px 0 0">%s</div>'
            % (LINE2, grid, ch["area"], ch["ma50"], BLUE, ch["ma20"], AMBER,
               ch["close"], TEXT, LINE2, y_labels, x_labels)
        )
    else:
        chart_html = (
            '<div style="margin-top:12px;border:1px solid %s;background:#0a0d12;padding:26px;'
            'font-family:%s;font-size:11px;color:%s;letter-spacing:.8px">'
            "NO SYNCHRONISED PRICE HISTORY IN THIS SAVED REPORT 鈥?RUN A NEW ANALYSIS TO GENERATE IT."
            "</div>" % (LINE2, MONO, FAINT)
        )

    legend = (
        '<div style="display:flex;gap:16px">'
        + "".join(
            '<div style="display:flex;align-items:center;gap:6px">'
            '<div style="width:14px;height:2px;background:%s"></div>'
            '<span class="mono" style="font-size:10px;color:%s">%s</span></div>' % (c, DIM, l)
            for c, l in [(TEXT, "CLOSE"),
                         (AMBER, "MA20 " + _num(m.get("ma20"))),
                         (BLUE, "MA50 " + _num(m.get("ma50")))]
        )
        + "</div>"
    )

    # ---------- overview: data grids ----------
    fund_cells = "".join([
        _cell("P/E (TTM)", _num(m.get("pe_ratio"), "{:.2f}x")),
        _cell("REVENUE GROWTH", _pct(m.get("revenue_growth")), "", UP),
        _cell("PROFIT MARGIN", _pct(m.get("profit_margin")), "", UP),
        _cell("MARKET CAP", _cap(m.get("market_cap"))),
        _cell("FUNDAMENTAL", "%s/100" % f_score, _stance(f_score), _score_color(f_score)),
    ])
    tech_cells = "".join([
        _cell("MA20", _num(m.get("ma20"))),
        _cell("MA50", _num(m.get("ma50"))),
        _cell("RSI (14)", _num(m.get("rsi"), "{:.1f}")),
        _cell("MACD", _num(m.get("macd"), "{:.2f}")),
        _cell("MACD SIGNAL", _num(m.get("macd_signal"), "{:.2f}")),
    ])

    # ---------- overview: dossier tiles ----------
    def tile(code, title, verdict, vc, summary, meta, view):
        return (
            '<div class="dossier" onclick="show(\'%s\')">'
            '<div style="display:flex;align-items:center;gap:10px">'
            '<span class="code">%s</span><span class="t">%s</span>'
            '<span class="spacer"></span>'
            '<span class="mono" style="font-size:11px;color:%s">%s</span></div>'
            '<div class="sum">%s</div>'
            '<div style="display:flex;align-items:center;gap:10px">'
            '<span class="mono" style="font-size:10px;color:%s;letter-spacing:.8px">%s</span>'
            '<span class="spacer"></span>'
            '<span class="mono" style="font-size:10px;color:%s;letter-spacing:.8px">OPEN -&gt;</span></div>'
            "</div>"
            % (view, code, _html.escape(title), vc, _html.escape(verdict),
               _html.escape(summary), FAINT, meta, AMBER)
        )

    tiles = (
        tile("F-01", "Fundamental Analyst", "%s 路 %s" % (_stance(f_score), f_score),
             _score_color(f_score), "Valuation, growth durability, profitability and balance-sheet risk.",
             "VALUATION 路 GROWTH 路 PROFITABILITY", "fundamental")
        + tile("T-02", "Technical Analyst", "%s 路 %s" % (_stance(t_score), t_score),
               _score_color(t_score), "Trend structure, momentum and actionable levels on the daily series.",
               "TREND 路 MOMENTUM 路 LEVELS", "technical")
        + tile("N-03", "News & Sentiment Analyst", "%s 路 %s" % (_stance(n_score), n_score),
               _score_color(n_score), "Catalysts, headline risk and tone of coverage across the source set.",
               "CATALYSTS 路 RISKS 路 SENTIMENT", "news")
        + tile("C-04", "Investment Committee", "%s 路 %s%% CONF" % (rating, conf), rc,
               "Synthesis of all specialist evidence into the final recommendation.",
               "BULL CASE 路 BEAR CASE 路 RISK", "decision")
    )

    # ---------- report views ----------
    def report_view(view, kicker, title, desc, score_label, score_value, score_suffix,
                    pct, metrics, body_html, side_title, side_rows, extra=""):
        met = "".join(_cell(l, v, n, c) for l, v, n, c in metrics)
        rows = "".join(_kv(l, v, c) for l, v, c in side_rows)
        try:
            width = max(0.0, min(100.0, float(pct)))
        except (TypeError, ValueError):
            width = 0.0
        return (
            '<div class="view" id="v-%s">'
            '<div class="crumb"><span class="b" onclick="show(\'overview\')">&lt;- OVERVIEW</span>'
            '<span class="vr"></span>'
            '<span class="meta">%s 路 %s 路 %s</span></div>'
            '<div class="head"><div class="head-l">'
            '<div class="kicker">%s</div><div class="title">%s</div><div class="desc">%s</div></div>'
            '<div class="side"><div class="side-h">%s</div>'
            '<div style="display:flex;align-items:baseline;gap:6px;margin-top:8px">'
            '<span class="mono" style="font-size:36px;font-weight:500">%s</span>'
            '<span class="mono" style="font-size:13px;color:%s">%s</span></div>'
            '<div class="bar"><i style="width:%.0f%%;background:%s"></i></div></div></div>'
            '<div class="grid g4" style="margin:0;border:0;border-bottom:1px solid %s">%s</div>'
            '<div style="display:flex;align-items:flex-start">'
            '<div class="body">%s%s</div>'
            '<div class="side" style="align-self:stretch"><div class="side-h">%s</div>'
            '<div style="margin-top:12px">%s</div></div></div>'
            "</div>"
            % (view, _html.escape(ticker), _html.escape(company), _html.escape(str(date)),
               kicker, _html.escape(title), _html.escape(desc), score_label,
               _html.escape(str(score_value)), FAINT, score_suffix, width, AMBER,
               LINE2, met, body_html, extra, side_title, rows)
        )

    fundamental_view = report_view(
        "fundamental", "SPECIALIST DOSSIER 路 01", "Fundamental Analyst",
        "%s (%s) 路 valuation, growth, profitability and fundamental risk." % (company, ticker),
        "FUNDAMENTAL SCORE", f_score, "/100", f_score,
        [("P/E (TTM)", _num(m.get("pe_ratio"), "{:.2f}x"), "", DIM),
         ("REVENUE GROWTH", _pct(m.get("revenue_growth")), "", UP),
         ("PROFIT MARGIN", _pct(m.get("profit_margin")), "", UP),
         ("MARKET CAP", _cap(m.get("market_cap")), "", DIM)],
        md_to_html(agents.get("fundamental_agent")),
        "FUNDAMENTAL DATA",
        [("SCORE", "%s / 100" % f_score, _score_color(f_score)),
         ("STANCE", _stance(f_score), _score_color(f_score)),
         ("P/E (TTM)", _num(m.get("pe_ratio"), "{:.2f}x"), TEXT),
         ("REVENUE GROWTH", _pct(m.get("revenue_growth")), UP),
         ("PROFIT MARGIN", _pct(m.get("profit_margin")), UP),
         ("MARKET CAP", _cap(m.get("market_cap")), TEXT),
         ("LAST PRICE", price_txt, TEXT)],
    )

    technical_view = report_view(
        "technical", "SPECIALIST DOSSIER 路 02", "Technical Analyst",
        "%s (%s) 路 price trend, momentum and technical indicators." % (company, ticker),
        "TECHNICAL SCORE", t_score, "/100", t_score,
        [("MA20", _num(m.get("ma20")), "", DIM),
         ("MA50", _num(m.get("ma50")), "", DIM),
         ("RSI (14)", _num(m.get("rsi"), "{:.1f}"), "", AMBER),
         ("MACD", _num(m.get("macd"), "{:.2f}"), "SIG " + _num(m.get("macd_signal"), "{:.2f}"), DIM)],
        md_to_html(agents.get("technical_agent")),
        "LEVELS & SIGNALS",
        [("SCORE", "%s / 100" % t_score, _score_color(t_score)),
         ("LAST", price_txt, TEXT),
         ("MA20", _num(m.get("ma20")), DIM),
         ("MA50", _num(m.get("ma50")), DIM),
         ("RSI (14)", _num(m.get("rsi"), "{:.1f}"), AMBER),
         ("MACD", _num(m.get("macd"), "{:.2f}"), DIM),
         ("MACD SIGNAL", _num(m.get("macd_signal"), "{:.2f}"), DIM)],
    )

    # news headlines
    items = m.get("news", []) or []
    if items:
        heads = ['<div class="h2"><span class="tick"></span>SOURCE HEADLINES</div>']
        for a in items:
            link = a.get("link")
            title_txt = _html.escape(a.get("title", "Untitled"))
            pub = _html.escape(a.get("publisher", "Unknown"))
            head = ('<a href="%s" target="_blank" rel="noopener">%s -&gt;</a>' % (_html.escape(link), title_txt)
                    if link else title_txt)
            heads.append('<div class="news"><div class="h">%s</div><div class="p">%s</div></div>'
                         % (head, pub))
        news_extra = "".join(heads)
    else:
        news_extra = ""

    news_view = report_view(
        "news", "SPECIALIST DOSSIER 路 03", "News & Sentiment Analyst",
        "%s (%s) 路 recent catalysts, risks and market sentiment." % (company, ticker),
        "SENTIMENT SCORE", n_score, "/100", n_score,
        [("SENTIMENT", "%s/100" % n_score, _stance(n_score), _score_color(n_score)),
         ("ARTICLES SCORED", str(len(items)), "", DIM),
         ("FINAL RATING", rating, "", rc),
         ("RISK LEVEL", risk, "", AMBER)],
        md_to_html(agents.get("news_agent")),
        "SENTIMENT CONTEXT",
        [("SCORE", "%s / 100" % n_score, _score_color(n_score)),
         ("STANCE", _stance(n_score), _score_color(n_score)),
         ("ARTICLES", str(len(items)), TEXT),
         ("FUNDAMENTAL", str(f_score), DIM),
         ("TECHNICAL", str(t_score), DIM),
         ("COMMITTEE", rating, rc)],
        extra=news_extra,
    )

    decision_view = report_view(
        "decision", "FINAL RESEARCH DECISION", "AI Investment Committee",
        "%s (%s) 路 final synthesis of fundamental, technical and news evidence." % (company, ticker),
        "RATING 路 CONFIDENCE", rating, "%s/100" % conf, conf,
        [("FINAL RATING", rating, "", rc),
         ("CONFIDENCE", "%s%%" % conf, "", UP),
         ("RISK LEVEL", risk, "", AMBER),
         ("LAST PRICE", price_txt, "", TEXT)],
        md_to_html(d.get("decision_agent")),
        "AGENT VOTES",
        [("FUNDAMENTAL", "%s 路 %s" % (_stance(f_score), f_score), _score_color(f_score)),
         ("TECHNICAL", "%s 路 %s" % (_stance(t_score), t_score), _score_color(t_score)),
         ("NEWS", "%s 路 %s" % (_stance(n_score), n_score), _score_color(n_score)),
         ("FINAL RATING", rating, rc),
         ("CONFIDENCE", "%s%%" % conf, TEXT),
         ("RISK LEVEL", risk, AMBER),
         ("REPORT DATE", str(date), DIM)],
    )

    return """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>%(css)s</style></head>
<body><div class="wrap">
  <div class="main">
    <div class="top">
      <div class="brand"><div class="sq"></div>AGENTINVEST</div>
      <div class="vr"></div>
      <div class="top-sub">MULTI-AGENT EQUITY RESEARCH TERMINAL</div>
      <div class="spacer"></div>
      <div class="meta">%(ticker)s 路 REPORT %(date)s</div>
    </div>

    <div class="view on" id="v-overview">
      <div class="head">
        <div class="head-l">
          <div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap">
            <div class="tk">%(ticker)s</div><div class="co">%(company)s</div>
            <div class="meta">AI EQUITY RESEARCH 路 %(date)s</div>
          </div>
          <div style="display:flex;align-items:flex-end;gap:16px;margin-top:14px">
            <div class="px">%(price)s</div>
            <div class="meta" style="padding-bottom:4px">LAST CLOSE 路 USD</div>
          </div>
          <div class="quote">%(quote)s</div>
        </div>
        <div class="side" style="background:#0b0e13">
          <div class="side-h">AI COMMITTEE RATING</div>
          <div style="font-size:40px;font-weight:700;letter-spacing:1px;color:%(rc)s;line-height:1;margin-top:10px">%(rating)s</div>
          <div style="margin-top:16px">
            <div class="kv"><span>CONFIDENCE</span><span style="color:%(text)s">%(conf)s / 100</span></div>
            <div class="bar"><i style="width:%(confpct)s%%;background:%(rc)s"></i></div>
            <div class="kv" style="margin-top:9px"><span>RISK LEVEL</span><span style="color:%(amber)s">%(risk)s</span></div>
            <div class="kv"><span>REPORT DATE</span><span style="color:%(text)s">%(date)s</span></div>
          </div>
        </div>
      </div>

      <div class="scores">%(scores)s</div>

      <div style="padding:16px 22px 18px;border-bottom:1px solid %(line)s">
        <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap">
          <div class="sec-h">PRICE &amp; TREND 路 DAILY</div><div class="spacer"></div>%(legend)s
        </div>
        %(chart)s
      </div>

      <div style="padding:16px 22px;border-bottom:1px solid %(line)s">
        <div class="sec-h">FUNDAMENTAL SNAPSHOT</div>
        <div class="grid g5">%(fund)s</div>
      </div>

      <div style="padding:16px 22px;border-bottom:1px solid %(line)s">
        <div class="sec-h">TECHNICAL SNAPSHOT</div>
        <div class="grid g5">%(tech)s</div>
      </div>

      <div style="padding:16px 22px 22px">
        <div class="sec-h">SPECIALIST RESEARCH</div>
        <div class="grid g2">%(tiles)s</div>
      </div>
    </div>

    %(fundamental)s%(technical)s%(news)s%(decision)s

    <div class="foot"><span>AGENTINVEST 路 %(ticker)s 路 MODEL RUN %(date)s 路 4 AGENTS</span>
      <span class="spacer"></span><span>NOT INVESTMENT ADVICE</span></div>
  </div>
</div>
<script>
function show(v){
  document.querySelectorAll('.view').forEach(function(e){e.classList.toggle('on', e.id === 'v-' + v);});
  window.scrollTo(0, 0);
}
</script>
</body></html>""" % {
        "css": _css(),
        "line": LINE,
        "text": TEXT,
        "amber": AMBER,
        "ticker": _html.escape(str(ticker)),
        "company": _html.escape(str(company)),
        "date": _html.escape(str(date)),
        "price": _html.escape(price_txt),
        "quote": quote_html,
        "rating": _html.escape(str(rating)),
        "rc": rc,
        "conf": _html.escape(str(conf)),
        "confpct": _num(conf, "{:.0f}", "0"),
        "risk": _html.escape(str(risk)),
        "scores": scores_html,
        "legend": legend,
        "chart": chart_html,
        "fund": fund_cells,
        "tech": tech_cells,
        "tiles": tiles,
        "fundamental": fundamental_view,
        "technical": technical_view,
        "news": news_view,
        "decision": decision_view,
    }
