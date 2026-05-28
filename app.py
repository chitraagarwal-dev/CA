import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

st.set_page_config(
    page_title="Fortune 500 Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Fortune 500 tech companies (2024 list, ranked by revenue) ──────────────────
FORTUNE500_TECH = {
    # Ticker: (Company Name, Subsector, Fortune500 Rank)
    "AMZN":  ("Amazon",                     "E-Commerce / Cloud",         2),
    "AAPL":  ("Apple",                       "Hardware / Consumer",        3),
    "GOOGL": ("Alphabet",                    "Internet / Advertising",     8),
    "MSFT":  ("Microsoft",                   "Software / Cloud",          13),
    "AT&T":  ("AT&T",                        "Telecom",                   11),
    "T":     ("AT&T",                        "Telecom",                   11),
    "VZ":    ("Verizon",                     "Telecom",                   16),
    "CMCSA": ("Comcast",                     "Media / Telecom",           20),
    "META":  ("Meta Platforms",              "Internet / Advertising",    27),
    "DELL":  ("Dell Technologies",           "Hardware / IT Services",    28),
    "HPQ":   ("HP Inc",                      "Hardware / Printing",       35),
    "IBM":   ("IBM",                         "IT Services / Cloud",       60),
    "ACN":   ("Accenture",                   "IT Services / Consulting",  61),
    "INTC":  ("Intel",                       "Semiconductors",            64),
    "CSCO":  ("Cisco Systems",              "Networking",                 74),
    "HPE":   ("Hewlett Packard Enterprise",  "Hardware / IT Services",    76),
    "ORCL":  ("Oracle",                      "Software / Cloud",          86),
    "ADP":   ("Automatic Data Processing",   "HR / Payroll Software",    235),
    "AVGO":  ("Broadcom",                    "Semiconductors",            99),
    "NVDA":  ("NVIDIA",                      "Semiconductors / AI",      173),
    "QCOM":  ("Qualcomm",                    "Semiconductors",           154),
    "TXN":   ("Texas Instruments",           "Semiconductors",           187),
    "MU":    ("Micron Technology",           "Memory Chips",             146),
    "AMD":   ("Advanced Micro Devices",      "Semiconductors",           161),
    "AMAT":  ("Applied Materials",           "Semiconductor Equipment",  183),
    "LRCX":  ("Lam Research",               "Semiconductor Equipment",  274),
    "KLAC":  ("KLA Corporation",             "Semiconductor Equipment",  395),
    "WDC":   ("Western Digital",             "Storage Hardware",         202),
    "STX":   ("Seagate Technology",          "Storage Hardware",         278),
    "NTAP":  ("NetApp",                      "Storage / Cloud",          370),
    "CRM":   ("Salesforce",                  "CRM / Cloud Software",     154),
    "ADBE":  ("Adobe",                       "Creative / Cloud Software", 301),
    "NOW":   ("ServiceNow",                  "Enterprise Software",      436),
    "INTU":  ("Intuit",                      "Financial Software",       240),
    "SNPS":  ("Synopsys",                    "EDA Software",             468),
    "CDNS":  ("Cadence Design Systems",      "EDA Software",             469),
    "ADSK":  ("Autodesk",                    "Design Software",          478),
    "PANW":  ("Palo Alto Networks",          "Cybersecurity",            381),
    "FTNT":  ("Fortinet",                    "Cybersecurity",            426),
    "CTSH":  ("Cognizant Technology",        "IT Services / Consulting",  195),
    "DXC":   ("DXC Technology",              "IT Services",              186),
    "FISV":  ("Fiserv",                      "Fintech / Payments",       198),
    "FIS":   ("FIS",                         "Fintech / Payments",       203),
    "GPN":   ("Global Payments",             "Fintech / Payments",       392),
    "PYPL":  ("PayPal",                      "Fintech / Payments",       215),
    "MSI":   ("Motorola Solutions",          "Communications Hardware",   449),
    "JNPR":  ("Juniper Networks",            "Networking",               479),
    "AKAM":  ("Akamai Technologies",         "CDN / Cloud Security",     457),
    "KEYS":  ("Keysight Technologies",       "Test & Measurement",       448),
    "LDOS":  ("Leidos Holdings",             "Defense / IT Services",    224),
    "BAH":   ("Booz Allen Hamilton",         "Defense / IT Consulting",  362),
    "SAIC":  ("Science Applications Intl",   "Defense / IT Services",    270),
    "JBL":   ("Jabil",                       "Electronics Manufacturing", 118),
    "FLEX":  ("Flex",                        "Electronics Manufacturing", 138),
    "SNX":   ("TD Synnex",                   "IT Distribution",           93),
    "ARW":   ("Arrow Electronics",           "Electronics Distribution",  136),
    "AVT":   ("Avnet",                       "Electronics Distribution",  165),
    "ROP":   ("Roper Technologies",          "Diversified Tech",          484),
    "IT":    ("Gartner",                     "IT Research / Advisory",   497),
    "TRMB":  ("Trimble",                     "GPS / Survey Tech",        476),
}

TOP_FORTUNE500 = {
    "WMT":   ("Walmart",                     "Retail",                    1),
    "AMZN":  ("Amazon",                      "E-Commerce",                2),
    "AAPL":  ("Apple",                       "Consumer Electronics",      3),
    "CVS":   ("CVS Health",                  "Healthcare",                4),
    "UNH":   ("UnitedHealth Group",         "Healthcare",                5),
    "BRK-B": ("Berkshire Hathaway",         "Conglomerate",              6),
    "MCK":   ("McKesson",                   "Healthcare",                7),
    "CI":    ("Cigna",                      "Healthcare",                8),
    "PEP":   ("PepsiCo",                    "Consumer Staples",          9),
    "JNJ":   ("Johnson & Johnson",          "Healthcare",               10),
    "WBA":   ("Walgreens Boots Alliance",   "Retail Pharmacy",          11),
    "XOM":   ("Exxon Mobil",                "Energy",                   12),
    "CVX":   ("Chevron",                    "Energy",                   13),
    "KR":    ("Kroger",                     "Retail",                   14),
    "MA":    ("Mastercard",                 "Payments",                 15),
    "V":     ("Visa",                       "Payments",                 16),
    "HD":    ("Home Depot",                 "Retail",                   17),
    "LOW":   ("Lowe's",                     "Retail",                   18),
    "PG":    ("Procter & Gamble",           "Consumer Staples",         19),
    "TSLA":  ("Tesla",                      "Automotive / Energy",      20),
    "DIS":   ("Disney",                     "Entertainment",            21),
    "BMY":   ("Bristol Myers Squibb",       "Pharmaceuticals",          22),
    "KO":    ("Coca-Cola",                  "Beverages",                23),
    "META":  ("Meta Platforms",             "Technology",               24),
    "MSFT":  ("Microsoft",                  "Technology",               25),
    "NVDA":  ("NVIDIA",                     "Semiconductors",           26),
    "ORCL":  ("Oracle",                     "Technology",               27),
    "INTC":  ("Intel",                      "Semiconductors",           28),
    "IBM":   ("IBM",                        "Technology",               29),
    "HPE":   ("Hewlett Packard Enterprise", "Technology",               76),
    "GE":    ("General Electric",           "Industrial",               30),
    "BA":    ("Boeing",                     "Aerospace",                31),
    "UPS":   ("United Parcel Service",      "Logistics",                32),
    "CAT":   ("Caterpillar",                "Industrial",               33),
    "GM":    ("General Motors",             "Automotive",               34),
    "F":     ("Ford",                       "Automotive",               35),
    "NKE":   ("Nike",                       "Apparel",                  36),
    "ADP":   ("Automatic Data Processing",  "Business Services",        37),
    "AXP":   ("American Express",           "Financial Services",       38),
    "TMUS":  ("T-Mobile US",                "Telecom",                  39),
    "CRM":   ("Salesforce",                 "Software",                 40),
    "MMM":   ("3M",                         "Industrial",               41),
    "RTX":   ("Raytheon Technologies",      "Aerospace",                42),
    "CSCO":  ("Cisco Systems",              "Technology",               43),
    "TXN":   ("Texas Instruments",          "Semiconductors",           44),
    "SPG":   ("Simon Property Group",       "Real Estate",              45),
}

UNIVERSES = {
    "Fortune 500 Tech Companies": FORTUNE500_TECH,
    "Top Fortune 500 Companies": TOP_FORTUNE500,
}

DEFAULT_TICKERS = list(FORTUNE500_TECH.keys())

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 Fortune 500 Dashboard")
    st.markdown("Rank and compare top Fortune 500 companies using valuation and growth metrics.")

    st.markdown("---")
    st.subheader("Universe")
    universe_name = st.selectbox("Select universe", list(UNIVERSES.keys()), index=0)
    universe = UNIVERSES[universe_name]
    use_all = st.checkbox("Use full universe list", value=True)

    if "HPE" in universe:
        st.markdown("✅ `HPE` is included in this universe.")

    if use_all:
        selected_tickers = list(universe.keys())
    else:
        default_example = ", ".join(list(universe.keys())[:8])
        custom = st.text_area(
            "Custom tickers (comma-separated)",
            value=default_example,
        )
        selected_tickers = [t.strip().upper() for t in custom.split(",") if t.strip()]

    st.markdown("---")
    st.subheader("Filters")
    subsectors = ["All"] + sorted({v[1] for v in universe.values()})
    sector_filter = st.selectbox("Subsector", subsectors)

    min_mktcap_b = st.slider("Min Market Cap ($B)", 0, 500, 0)

    st.markdown("---")
    st.subheader("Scoring weights")
    w_pe  = st.slider("P/E weight",         0, 10, 3)
    w_pb  = st.slider("P/B weight",         0, 10, 2)
    w_peg = st.slider("PEG weight",         0, 10, 3)
    w_ev  = st.slider("EV/EBITDA weight",   0, 10, 2)
    w_fcf = st.slider("FCF Yield weight",   0, 10, 2)

    st.markdown("---")
    st.subheader("DCF assumptions")
    dcf_discount_rate = st.slider("Discount rate (%)", 5.0, 20.0, 10.0, 0.1)
    dcf_terminal_growth = st.slider("Terminal growth rate (%)", 0.0, 6.0, 2.0, 0.1)
    st.markdown("---")
    st.subheader("Sort order")
    sort_by_options = [
        "Value Score", "DCF Value", "DCF Premium (%)", "P/E", "Subsector Avg P/E", "P/B", "PEG",
        "EV/EBITDA", "FCF Yield (%)", "Rev Growth (%)", "EPS Growth (%)", "Market Cap ($B)"
    ]
    sort_by = st.selectbox("Order companies by", sort_by_options, index=0)

    refresh = st.button("🔄 Refresh data", use_container_width=True)

# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=3600)
def load_financials(tickers: list[str]) -> pd.DataFrame:
    rows = []
    progress = st.progress(0, text="Fetching financial data…")
    for i, ticker in enumerate(tickers):
        progress.progress((i + 1) / len(tickers), text=f"Fetching {ticker}…")
        try:
            info = yf.Ticker(ticker).info
            price = info.get("regularMarketPrice") or info.get("previousClose")
            fcf   = info.get("freeCashflow")
            mktcap = info.get("marketCap")
            ebitda = info.get("ebitda")
            ev     = info.get("enterpriseValue")

            meta = FORTUNE500_TECH.get(ticker, (ticker, "Other", None))

            shares = info.get("sharesOutstanding")
            rows.append({
                "Ticker":          ticker,
                "Company":         info.get("shortName") or meta[0],
                "Subsector":       meta[1],
                "F500 Rank":       meta[2],
                "Price":           price,
                "Market Cap ($B)": round(mktcap / 1e9, 2) if mktcap else None,
                "P/E":             info.get("trailingPE"),
                "Fwd P/E":         info.get("forwardPE"),
                "P/B":             info.get("priceToBook"),
                "PEG":             info.get("pegRatio"),
                "EV/EBITDA":       round(ev / ebitda, 2) if ev and ebitda and ebitda > 0 else None,
                "FCF Yield (%)":   round(fcf / mktcap * 100, 2) if fcf and mktcap else None,
                "Free Cash Flow ($B)": round(fcf / 1e9, 2) if fcf else None,
                "Shares Outstanding": shares,
                "Rev Growth (%)":  round((info.get("revenueGrowth") or 0) * 100, 1),
                "EPS Growth (%)":  round((info.get("earningsGrowth") or 0) * 100, 1),
                "Gross Margin (%)":round((info.get("grossMargins") or 0) * 100, 1),
                "Div Yield (%)":   round((info.get("dividendYield") or 0) * 100, 2),
                "Beta":            info.get("beta"),
                "52W High":        info.get("fiftyTwoWeekHigh"),
                "52W Low":         info.get("fiftyTwoWeekLow"),
                "Revenue ($B)":    round(info.get("totalRevenue", 0) / 1e9, 2) if info.get("totalRevenue") else None,
            })
        except Exception as exc:
            rows.append({
                "Ticker": ticker,
                "Company": FORTUNE500_TECH.get(ticker, (ticker,))[0],
                "Subsector": FORTUNE500_TECH.get(ticker, ("", "Other"))[1],
                "F500 Rank": FORTUNE500_TECH.get(ticker, ("", "", None))[2],
            })
    progress.empty()
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False, ttl=3600)
def load_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    return yf.Ticker(ticker).history(period=period, interval="1d")


def pct_from_high(row) -> Optional[float]:
    if pd.notna(row.get("Price")) and pd.notna(row.get("52W High")) and row["52W High"] > 0:
        return round((row["Price"] - row["52W High"]) / row["52W High"] * 100, 1)
    return None


def compute_score(df: pd.DataFrame, weights: dict) -> pd.DataFrame:
    df = df.copy()

    def norm_rank(series, ascending=True):
        s = pd.to_numeric(series, errors="coerce")
        s = s.replace([np.inf, -np.inf], np.nan)
        valid = s.dropna()
        if valid.empty:
            return pd.Series(np.nan, index=s.index)
        # Rank percentile within each subsector — lower value is better for most metrics (ascending=True → low is undervalued)
        return s.groupby(df['Subsector']).rank(ascending=ascending, pct=True)

    components = {}
    if weights["pe"] and df["P/E"].notna().any():
        components["pe"] = norm_rank(df["P/E"], ascending=True) * weights["pe"]
    if weights["pb"] and df["P/B"].notna().any():
        components["pb"] = norm_rank(df["P/B"], ascending=True) * weights["pb"]
    if weights["peg"] and df["PEG"].notna().any():
        components["peg"] = norm_rank(df["PEG"], ascending=True) * weights["peg"]
    if weights["ev"] and df["EV/EBITDA"].notna().any():
        components["ev"] = norm_rank(df["EV/EBITDA"], ascending=True) * weights["ev"]
    if weights["fcf"] and df["FCF Yield (%)"].notna().any():
        components["fcf"] = norm_rank(df["FCF Yield (%)"], ascending=False) * weights["fcf"]  # higher FCF yield = better

    total_w = sum(v for k, v in weights.items() if k in components)
    if components and total_w > 0:
        score = pd.concat(components.values(), axis=1).sum(axis=1, min_count=1) / total_w
        df["Value Score"] = score.round(3)
    else:
        df["Value Score"] = np.nan

    df["% from 52W High"] = df.apply(pct_from_high, axis=1)
    return df


def calculate_dcf(fcf: Optional[float], shares: Optional[float], growth_rate_pct: Optional[float], discount_rate: float, terminal_growth_pct: float, years: int = 5) -> Optional[float]:
    if fcf is None or shares is None or fcf <= 0 or shares <= 0:
        return None
    growth = (growth_rate_pct or 0.0) / 100.0
    growth = max(min(growth, 0.30), -0.20)
    discount = discount_rate / 100.0
    terminal_growth = terminal_growth_pct / 100.0
    if discount <= terminal_growth:
        return None

    cash = fcf
    pv = 0.0
    for year in range(1, years + 1):
        cash *= (1 + growth)
        pv += cash / ((1 + discount) ** year)

    terminal = cash * (1 + terminal_growth) / (discount - terminal_growth)
    pv_total = pv + terminal / ((1 + discount) ** years)
    return pv_total / shares


# ── Main ───────────────────────────────────────────────────────────────────────
st.title("Fortune 500: Undervalued Company Dashboard")
st.caption(
    "Scores each company using a weighted composite of P/E, P/B, PEG, EV/EBITDA, and FCF Yield. "
    "Lower score = relatively more undervalued vs. peers. Data via Yahoo Finance · refreshes hourly."
)

if not selected_tickers:
    st.error("No tickers selected.")
    st.stop()

with st.spinner("Loading financial data for Fortune 500 tech companies…"):
    df_raw = load_financials(tuple(selected_tickers))

weights = {"pe": w_pe, "pb": w_pb, "peg": w_peg, "ev": w_ev, "fcf": w_fcf}
df = compute_score(df_raw, weights)

# DCF calculations
df["DCF Value"] = df.apply(
    lambda row: calculate_dcf(
        fcf=row.get("Free Cash Flow ($B)") * 1e9 if pd.notna(row.get("Free Cash Flow ($B)")) else None,
        shares=row.get("Shares Outstanding"),
        growth_rate_pct=row.get("EPS Growth (%)"),
        discount_rate=dcf_discount_rate,
        terminal_growth_pct=dcf_terminal_growth,
    ),
    axis=1,
)

df["DCF Premium (%)"] = df.apply(
    lambda row: round((row["Price"] - row["DCF Value"]) / row["DCF Value"] * 100, 1)
    if pd.notna(row.get("DCF Value")) and pd.notna(row.get("Price")) and row["DCF Value"] != 0
    else None,
    axis=1,
)

# Apply filters
if sector_filter != "All":
    df = df[df["Subsector"] == sector_filter]

df = df[df["Market Cap ($B)"].fillna(0) >= min_mktcap_b]

# Calculate subsector average P/E
df["Subsector Avg P/E"] = df.groupby("Subsector")["P/E"].transform("mean").round(1)

sort_ascending = {
    "Value Score": True,
    "P/E": True,
    "Subsector Avg P/E": True,
    "P/B": True,
    "PEG": True,
    "EV/EBITDA": True,
    "FCF Yield (%)": False,
    "Rev Growth (%)": False,
    "EPS Growth (%)": False,
    "Market Cap ($B)": False,
}

if sort_by in df.columns:
    df = df.sort_values(sort_by, ascending=sort_ascending.get(sort_by, True))
else:
    df = df.sort_values("Value Score", ascending=True)   # fallback sorting

if df.empty:
    st.warning("No companies match the current filters.")
    st.stop()

# ── KPI row ────────────────────────────────────────────────────────────────────
st.markdown("---")
top5 = df.dropna(subset=[sort_by]).head(5)

st.subheader(f"Top 5 by {sort_by}")
cols = st.columns(5)
for col, (_, row) in zip(cols, top5.iterrows()):
    metric_value = "N/A"
    if pd.notna(row.get(sort_by)):
        if sort_by.endswith("%"):
            metric_value = f"{row[sort_by]:.1f}%"
        elif sort_by == "Market Cap ($B)":
            metric_value = f"${row[sort_by]:.1f}B"
        else:
            metric_value = f"{row[sort_by]:.1f}"

    col.metric(
        label=f"{row['Ticker']} — {row['Company']}",
        value=metric_value,
        delta=f"P/E {row['P/E']:.1f}" if pd.notna(row.get("P/E")) else "P/E N/A",
        delta_color="off",
    )

# ── Scatter: Value Score vs Revenue Growth ────────────────────────────────────
st.markdown("---")
st.subheader("Value Score vs. Revenue Growth")

scatter_df = df.dropna(subset=["Value Score", "Rev Growth (%)"])
if not scatter_df.empty:
    fig_scatter = px.scatter(
        scatter_df,
        x="Rev Growth (%)",
        y="Value Score",
        size="Market Cap ($B)",
        color="Subsector",
        hover_name="Company",
        hover_data={"Ticker": True, "P/E": True, "P/B": True, "EV/EBITDA": True, "FCF Yield (%)": True, "EPS Growth (%)": True},
        labels={"Value Score": "Value Score (lower = more undervalued)"},
        height=480,
    )
    fig_scatter.update_layout(legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_scatter, use_container_width=True)

# ── Rankings table ─────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Full Valuation Rankings")

display_cols = [
    "F500 Rank", "Ticker", "Company", "Subsector",
    "Price", "Market Cap ($B)", "Value Score",
    "P/E", "Subsector Avg P/E", "Fwd P/E", "P/B", "PEG", "EV/EBITDA", "FCF Yield (%)",
    "DCF Value", "DCF Premium (%)",
    "Rev Growth (%)", "EPS Growth (%)", "Gross Margin (%)", "% from 52W High",
    "Div Yield (%)", "Beta",
]
display_cols = [c for c in display_cols if c in df.columns]

def color_score(val):
    if pd.isna(val):
        return ""
    if val < 0.3:
        return "background-color: #d4edda; color: #155724"   # green
    if val < 0.5:
        return "background-color: #fff3cd; color: #856404"   # yellow
    return "background-color: #f8d7da; color: #721c24"       # red

def highlight_pe_below_subsector(row):
    """Highlight P/E if it's below subsector average."""
    if pd.notna(row.get("P/E")) and pd.notna(row.get("Subsector Avg P/E")) and row["P/E"] < row["Subsector Avg P/E"]:
        return "background-color: #d1ecf1; color: #0c5460"   # light blue
    return ""

styled = (
    df[display_cols]
    .style
    .map(color_score, subset=["Value Score"])
    .apply(lambda row: [highlight_pe_below_subsector(row) if col == "P/E" else "" for col in display_cols], axis=1)
    .format(
        {
            "Price": "${:.2f}",
            "Market Cap ($B)": "${:.1f}B",
            "Value Score": "{:.3f}",
            "P/E": "{:.1f}",
            "Subsector Avg P/E": "{:.1f}",
            "Fwd P/E": "{:.1f}",
            "P/B": "{:.2f}",
            "PEG": "{:.2f}",
            "EV/EBITDA": "{:.1f}",
            "FCF Yield (%)": "{:.1f}%",
            "DCF Value": "${:.2f}",
            "DCF Premium (%)": "{:.1f}%",
            "Rev Growth (%)": "{:.1f}%",
            "EPS Growth (%)": "{:.1f}%",
            "Gross Margin (%)": "{:.1f}%",
            "% from 52W High": "{:.1f}%",
            "Div Yield (%)": "{:.2f}%",
            "Beta": "{:.2f}",
        },
        na_rep="—",
    )
)
st.dataframe(styled, use_container_width=True, height=500)

# ── Metric bar charts ──────────────────────────────────────────────────────────
st.markdown("---")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("P/E Ratio by Company")
    pe_df = df[df["P/E"].notna()].sort_values("P/E").head(20)
    fig_pe = px.bar(pe_df, x="Ticker", y="P/E", color="Subsector", height=350,
                    labels={"P/E": "Trailing P/E"})
    fig_pe.add_hline(y=pe_df["P/E"].median(), line_dash="dash",
                     annotation_text=f"Median {pe_df['P/E'].median():.1f}")
    st.plotly_chart(fig_pe, use_container_width=True)

with col_b:
    st.subheader("EV/EBITDA by Company")
    ev_df = df[df["EV/EBITDA"].notna()].sort_values("EV/EBITDA").head(20)
    fig_ev = px.bar(ev_df, x="Ticker", y="EV/EBITDA", color="Subsector", height=350)
    fig_ev.add_hline(y=ev_df["EV/EBITDA"].median(), line_dash="dash",
                     annotation_text=f"Median {ev_df['EV/EBITDA'].median():.1f}")
    st.plotly_chart(fig_ev, use_container_width=True)

# ── FCF Yield chart ────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("FCF Yield — Top Companies")
fcf_df = df[df["FCF Yield (%)"].notna()].sort_values("FCF Yield (%)", ascending=False).head(20)
fig_fcf = px.bar(fcf_df, x="Ticker", y="FCF Yield (%)", color="Subsector", height=350,
                 text_auto=".1f")
st.plotly_chart(fig_fcf, use_container_width=True)

# ── Deep-dive: single company ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("Company Deep-Dive")

all_tickers_sorted = df.sort_values("Value Score")["Ticker"].tolist()
selected = st.selectbox("Select a company", all_tickers_sorted)

if selected:
    row = df[df["Ticker"] == selected].iloc[0]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Price",       f"${row['Price']:.2f}"       if pd.notna(row.get("Price")) else "N/A")
    c2.metric("Value Score", f"{row['Value Score']:.3f}"  if pd.notna(row.get("Value Score")) else "N/A")
    c3.metric("P/E",         f"{row['P/E']:.1f}"          if pd.notna(row.get("P/E")) else "N/A")
    c4.metric("Rev Growth",  f"{row['Rev Growth (%)']:.1f}%" if pd.notna(row.get("Rev Growth (%)")) else "N/A")
    c5.metric("EPS Growth",  f"{row['EPS Growth (%)']:.1f}%" if pd.notna(row.get("EPS Growth (%)")) else "N/A")

    hist = load_history(selected)
    if not hist.empty:
        left, right = st.columns(2)
        with left:
            fig_price = go.Figure()
            fig_price.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Close",
                                           line=dict(color="#0066cc")))
            fig_price.update_layout(title=f"{selected} — 1-Year Price", height=300,
                                    margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig_price, use_container_width=True)
        with right:
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Bar(x=hist.index, y=hist["Volume"], name="Volume",
                                     marker_color="#6c757d"))
            fig_vol.update_layout(title=f"{selected} — Volume", height=300,
                                  margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig_vol, use_container_width=True)
    else:
        st.warning("No historical price data available.")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Data sourced from Yahoo Finance via yfinance. Not investment advice. "
    f"Universe: {len(df)} companies · Last loaded: refreshes hourly."
)
