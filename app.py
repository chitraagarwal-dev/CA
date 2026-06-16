import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

# Anthropic SDK is optional: only required if the user runs the Company Analysis section.
try:
    from anthropic import Anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False

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

# ── S&P 500 (top ~120 by market cap, mapped to GICS sectors) ───────────────────
# Third tuple field is approximate index-weight rank, not Fortune 500 rank.
SP500_LARGE_CAPS = {
    # Technology — Software & Services
    "MSFT":  ("Microsoft",                   "Software",                  1),
    "GOOGL": ("Alphabet (Class A)",          "Internet / Advertising",    4),
    "GOOG":  ("Alphabet (Class C)",          "Internet / Advertising",    5),
    "META":  ("Meta Platforms",              "Internet / Advertising",    7),
    "ORCL":  ("Oracle",                      "Software",                 18),
    "CRM":   ("Salesforce",                  "Software",                 32),
    "ADBE":  ("Adobe",                       "Software",                 36),
    "NOW":   ("ServiceNow",                  "Software",                 41),
    "INTU":  ("Intuit",                      "Software",                 47),
    "IBM":   ("IBM",                         "IT Services",              52),
    "PANW":  ("Palo Alto Networks",          "Cybersecurity",            58),
    "FTNT":  ("Fortinet",                    "Cybersecurity",            93),
    "SNPS":  ("Synopsys",                    "EDA Software",             82),
    "CDNS":  ("Cadence Design Systems",      "EDA Software",             80),
    "ADSK":  ("Autodesk",                    "Design Software",          95),
    "WDAY":  ("Workday",                     "Software",                 91),
    "ACN":   ("Accenture",                   "IT Services",              35),

    # Technology — Hardware & Semiconductors
    "AAPL":  ("Apple",                       "Hardware",                  2),
    "NVDA":  ("NVIDIA",                      "Semiconductors",            3),
    "AVGO":  ("Broadcom",                    "Semiconductors",            8),
    "AMD":   ("Advanced Micro Devices",      "Semiconductors",           22),
    "QCOM":  ("Qualcomm",                    "Semiconductors",           38),
    "TXN":   ("Texas Instruments",           "Semiconductors",           48),
    "AMAT":  ("Applied Materials",           "Semi Equipment",           42),
    "LRCX":  ("Lam Research",                "Semi Equipment",           65),
    "KLAC":  ("KLA Corporation",             "Semi Equipment",           67),
    "MU":    ("Micron Technology",           "Memory Chips",             55),
    "INTC":  ("Intel",                       "Semiconductors",           54),
    "CSCO":  ("Cisco Systems",               "Networking",               43),
    "DELL":  ("Dell Technologies",           "Hardware",                 96),
    "HPQ":   ("HP Inc",                      "Hardware",                108),
    "HPE":   ("Hewlett Packard Enterprise",  "Hardware",                115),

    # Communication Services
    "NFLX":  ("Netflix",                     "Streaming Media",          25),
    "DIS":   ("Walt Disney",                 "Media / Entertainment",    53),
    "CMCSA": ("Comcast",                     "Media / Telecom",          50),
    "T":     ("AT&T",                        "Telecom",                  60),
    "VZ":    ("Verizon",                     "Telecom",                  56),
    "TMUS":  ("T-Mobile US",                 "Telecom",                  31),
    "CHTR":  ("Charter Communications",      "Telecom",                 110),

    # Consumer Discretionary
    "AMZN":  ("Amazon",                      "E-Commerce / Cloud",        6),
    "TSLA":  ("Tesla",                       "EV / Automotive",          12),
    "HD":    ("Home Depot",                  "Home Improvement",         26),
    "MCD":   ("McDonald's",                  "Restaurants",              45),
    "NKE":   ("Nike",                        "Apparel",                  77),
    "SBUX":  ("Starbucks",                   "Restaurants",              71),
    "LOW":   ("Lowe's",                      "Home Improvement",         57),
    "BKNG":  ("Booking Holdings",            "Travel",                   46),
    "TJX":   ("TJX Companies",               "Off-Price Retail",         59),
    "ABNB":  ("Airbnb",                      "Travel",                  100),

    # Consumer Staples
    "WMT":   ("Walmart",                     "Retail",                   13),
    "PG":    ("Procter & Gamble",            "Consumer Staples",         15),
    "COST":  ("Costco",                      "Retail",                   17),
    "KO":    ("Coca-Cola",                   "Beverages",                21),
    "PEP":   ("PepsiCo",                     "Beverages",                28),
    "PM":    ("Philip Morris",               "Tobacco",                  39),
    "MO":    ("Altria Group",                "Tobacco",                  78),
    "MDLZ":  ("Mondelez",                    "Packaged Foods",           69),
    "CL":    ("Colgate-Palmolive",           "Consumer Staples",         85),

    # Financials
    "BRK-B": ("Berkshire Hathaway (B)",      "Conglomerate",              9),
    "JPM":   ("JPMorgan Chase",              "Banks",                    11),
    "V":     ("Visa",                        "Payments",                 14),
    "MA":    ("Mastercard",                  "Payments",                 19),
    "BAC":   ("Bank of America",             "Banks",                    27),
    "WFC":   ("Wells Fargo",                 "Banks",                    33),
    "GS":    ("Goldman Sachs",               "Investment Banking",       40),
    "MS":    ("Morgan Stanley",              "Investment Banking",       49),
    "AXP":   ("American Express",            "Payments",                 51),
    "BLK":   ("BlackRock",                   "Asset Management",         44),
    "SCHW":  ("Charles Schwab",              "Brokerage",                68),
    "C":     ("Citigroup",                   "Banks",                    63),
    "PYPL":  ("PayPal",                      "Payments",                113),

    # Healthcare
    "LLY":   ("Eli Lilly",                   "Pharmaceuticals",          10),
    "UNH":   ("UnitedHealth",                "Health Insurance",         16),
    "JNJ":   ("Johnson & Johnson",           "Pharmaceuticals",          20),
    "ABBV":  ("AbbVie",                      "Pharmaceuticals",          23),
    "MRK":   ("Merck",                       "Pharmaceuticals",          29),
    "TMO":   ("Thermo Fisher Scientific",    "Life Sciences Tools",      30),
    "ABT":   ("Abbott Laboratories",         "Medical Devices",          34),
    "PFE":   ("Pfizer",                      "Pharmaceuticals",          61),
    "DHR":   ("Danaher",                     "Life Sciences Tools",      37),
    "AMGN":  ("Amgen",                       "Biotech",                  64),
    "GILD":  ("Gilead Sciences",             "Biotech",                  86),
    "BMY":   ("Bristol-Myers Squibb",        "Pharmaceuticals",          88),
    "ISRG":  ("Intuitive Surgical",          "Medical Devices",          62),
    "ELV":   ("Elevance Health",             "Health Insurance",         70),
    "CVS":   ("CVS Health",                  "Pharmacy / Insurance",     79),

    # Industrials
    "GE":    ("GE Aerospace",                "Aerospace",                72),
    "CAT":   ("Caterpillar",                 "Machinery",                66),
    "BA":    ("Boeing",                      "Aerospace",                98),
    "HON":   ("Honeywell",                   "Industrial Conglomerate",  73),
    "UNP":   ("Union Pacific",               "Railroads",                75),
    "RTX":   ("RTX Corporation",             "Aerospace & Defense",      74),
    "LMT":   ("Lockheed Martin",             "Defense",                  84),
    "DE":    ("Deere & Company",             "Machinery",                81),
    "UPS":   ("United Parcel Service",       "Logistics",                89),

    # Energy
    "XOM":   ("ExxonMobil",                  "Integrated Oil",           24),
    "CVX":   ("Chevron",                     "Integrated Oil",           37),
    "COP":   ("ConocoPhillips",              "Oil & Gas E&P",            76),
    "SLB":   ("Schlumberger",                "Oilfield Services",       105),

    # Utilities
    "NEE":   ("NextEra Energy",              "Electric Utilities",       83),
    "DUK":   ("Duke Energy",                 "Electric Utilities",       99),
    "SO":    ("Southern Company",            "Electric Utilities",      102),

    # Materials
    "LIN":   ("Linde",                       "Industrial Gases",         60),
    "SHW":   ("Sherwin-Williams",            "Paints / Coatings",        92),

    # Real Estate
    "PLD":   ("Prologis",                    "Industrial REIT",          87),
    "AMT":   ("American Tower",              "Cell Tower REIT",          90),
    "EQIX":  ("Equinix",                     "Data Center REIT",         94),
}

UNIVERSES = {
    "Fortune 500 Tech Companies": FORTUNE500_TECH,
    "Top Fortune 500 Companies": TOP_FORTUNE500,
    "S&P 500 (Top ~120 by Mkt Cap)": SP500_LARGE_CAPS,
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
        "Value Score", "DCF Value", "DCF Premium (%)", "P/E", "Subsector Avg P/E", "P/B", "Subsector Avg P/B",
        "ROE (%)", "P/B ÷ ROE", "PEG",
        "EV/EBITDA", "Subsector Avg EV/EBITDA", "FCF Yield (%)", "Rev Growth (%)", "EPS Growth (%)", "Market Cap ($B)",
        "Analyst Score"
    ]
    sort_by = st.selectbox("Order companies by", sort_by_options, index=0)

    refresh = st.button("🔄 Refresh data", use_container_width=True)

# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=3600)
def load_financials(tickers: list[str], universe_name: str = "Fortune 500 Tech Companies") -> pd.DataFrame:
    """Pulls live yfinance data for each ticker and shapes it for the dashboard.

    `universe_name` selects which metadata dictionary to look up subsector / rank from;
    it's included in the cache key so switching universes invalidates correctly.
    """
    meta_dict = UNIVERSES.get(universe_name, FORTUNE500_TECH)
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

            meta = meta_dict.get(ticker, (ticker, "Other", None))

            shares = info.get("sharesOutstanding")

            # ROE comes as a decimal (e.g. 0.27 → 27.0%)
            roe_raw = info.get("returnOnEquity")
            roe_pct = round(roe_raw * 100, 1) if roe_raw is not None else None

            # P/B ÷ ROE: "price paid per $1 of annual return on equity" (lower = better).
            # Uses ROE in decimal form so the ratio is in the same units as P/B itself.
            pb_val = info.get("priceToBook")
            pb_over_roe = round(pb_val / roe_raw, 2) if pb_val and roe_raw and roe_raw > 0 else None

            # Analyst recommendations (yfinance fields)
            rec_key  = info.get("recommendationKey")        # "strong_buy" | "buy" | "hold" | "sell" | "strong_sell" | "none"
            rec_mean = info.get("recommendationMean")       # 1.0 (strong buy) → 5.0 (strong sell)
            rec_n    = info.get("numberOfAnalystOpinions")
            rec_label = (
                rec_key.replace("_", " ").title()
                if isinstance(rec_key, str) and rec_key not in (None, "", "none")
                else None
            )

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
                "ROE (%)":         roe_pct,
                "P/B ÷ ROE":       pb_over_roe,
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
                "Analyst Rating":  rec_label,
                "Analyst Score":   round(rec_mean, 2) if rec_mean is not None else None,
                "Analyst Count":   rec_n,
            })
        except Exception as exc:
            rows.append({
                "Ticker": ticker,
                "Company": meta_dict.get(ticker, (ticker, "Other", None))[0],
                "Subsector": meta_dict.get(ticker, ("", "Other", None))[1],
                "F500 Rank": meta_dict.get(ticker, ("", "", None))[2],
            })
    progress.empty()
    out = pd.DataFrame(rows)

    # Guarantee the full schema even if every yfinance call failed (rate limit, network, etc.).
    expected_cols = [
        "Ticker", "Company", "Subsector", "F500 Rank", "Price", "Market Cap ($B)",
        "P/E", "Fwd P/E", "P/B", "ROE (%)", "P/B ÷ ROE", "PEG", "EV/EBITDA",
        "FCF Yield (%)", "Free Cash Flow ($B)", "Shares Outstanding",
        "Rev Growth (%)", "EPS Growth (%)", "Gross Margin (%)",
        "Div Yield (%)", "Beta", "52W High", "52W Low", "Revenue ($B)",
        "Analyst Rating", "Analyst Score", "Analyst Count",
    ]
    for col in expected_cols:
        if col not in out.columns:
            out[col] = np.nan
    return out


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

    def _has(col):
        return col in df.columns and df[col].notna().any()

    components = {}
    if weights["pe"] and _has("P/E"):
        components["pe"] = norm_rank(df["P/E"], ascending=True) * weights["pe"]
    if weights["pb"] and _has("P/B"):
        components["pb"] = norm_rank(df["P/B"], ascending=True) * weights["pb"]
    if weights["peg"] and _has("PEG"):
        components["peg"] = norm_rank(df["PEG"], ascending=True) * weights["peg"]
    if weights["ev"] and _has("EV/EBITDA"):
        components["ev"] = norm_rank(df["EV/EBITDA"], ascending=True) * weights["ev"]
    if weights["fcf"] and _has("FCF Yield (%)"):
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
st.title(f"{universe_name}: Undervalued Company Dashboard")
st.caption(
    "Scores each company using a weighted composite of P/E, P/B, PEG, EV/EBITDA, and FCF Yield. "
    "Lower score = relatively more undervalued vs. peers. Data via Yahoo Finance · refreshes hourly."
)

if not selected_tickers:
    st.error("No tickers selected.")
    st.stop()

with st.spinner(f"Loading financial data for {universe_name}…"):
    df_raw = load_financials(tuple(selected_tickers), universe_name=universe_name)

# If Yahoo Finance returned nothing usable for any ticker (rate-limited, network failure, etc.),
# warn loudly but still let the page render the structural columns so the app doesn't crash.
if "P/E" in df_raw.columns and df_raw["P/E"].notna().sum() == 0 and df_raw["Price"].notna().sum() == 0:
    st.error(
        "Yahoo Finance returned no usable data for any selected ticker. "
        "This is almost always a Yahoo rate-limit or network failure on the Streamlit Cloud IP. "
        "Try clicking '🔄 Refresh data' in the sidebar in a minute, or reboot the app. "
        "The Company Analysis / Company Background sections below will still work because they call yfinance per-ticker on demand."
    )

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

# Calculate subsector averages
df["Subsector Avg P/E"] = df.groupby("Subsector")["P/E"].transform("mean").round(1)
df["Subsector Avg P/B"] = df.groupby("Subsector")["P/B"].transform("mean").round(2)
df["Subsector Avg EV/EBITDA"] = df.groupby("Subsector")["EV/EBITDA"].transform("mean").round(1)

sort_ascending = {
    "Value Score": True,
    "P/E": True,
    "Subsector Avg P/E": True,
    "P/B": True,
    "Subsector Avg P/B": True,
    "ROE (%)": False,         # higher ROE = better, so descending
    "P/B ÷ ROE": True,        # lower = cheaper per unit of return
    "PEG": True,
    "EV/EBITDA": True,
    "Subsector Avg EV/EBITDA": True,
    "FCF Yield (%)": False,
    "Rev Growth (%)": False,
    "EPS Growth (%)": False,
    "Market Cap ($B)": False,
    "Analyst Score": True,    # 1 = strong buy → ascending puts strongest buys first
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
    "P/E", "Subsector Avg P/E", "Fwd P/E", "P/B", "Subsector Avg P/B",
    "ROE (%)", "P/B ÷ ROE",
    "PEG", "EV/EBITDA", "Subsector Avg EV/EBITDA", "FCF Yield (%)",
    "DCF Value", "DCF Premium (%)",
    "Rev Growth (%)", "EPS Growth (%)", "Gross Margin (%)", "% from 52W High",
    "Div Yield (%)", "Beta",
    "Analyst Rating", "Analyst Score", "Analyst Count",
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

def highlight_below_subsector_avg(row, col, avg_col):
    """Return a CSS style if `col` is below the subsector average in `avg_col`."""
    if pd.notna(row.get(col)) and pd.notna(row.get(avg_col)) and row[col] < row[avg_col]:
        return "background-color: #d1ecf1; color: #0c5460"   # light blue
    return ""

def color_analyst_rating(val):
    """Color analyst rating string: greens for buy, red for sell."""
    if not isinstance(val, str):
        return ""
    v = val.lower()
    if "strong buy" in v:
        return "background-color: #c3e6cb; color: #155724; font-weight: 600"  # darker green
    if v == "buy":
        return "background-color: #d4edda; color: #155724"                    # green
    if v == "hold":
        return "background-color: #fff3cd; color: #856404"                    # yellow
    if v == "sell":
        return "background-color: #f8d7da; color: #721c24"                    # red
    if "strong sell" in v:
        return "background-color: #f5c6cb; color: #721c24; font-weight: 600"  # darker red
    return ""


def highlight_row_vs_subsector(row):
    """Build a per-column style list highlighting valuation cells when they look favorable."""
    out = []
    for col in display_cols:
        if col == "P/E":
            out.append(highlight_below_subsector_avg(row, "P/E", "Subsector Avg P/E"))
        elif col == "P/B":
            out.append(highlight_below_subsector_avg(row, "P/B", "Subsector Avg P/B"))
        elif col == "EV/EBITDA":
            out.append(highlight_below_subsector_avg(row, "EV/EBITDA", "Subsector Avg EV/EBITDA"))
        elif col == "ROE (%)":
            # Highlight ROE > 20% as a strength signal
            val = row.get("ROE (%)")
            out.append("background-color: #d4edda; color: #155724" if pd.notna(val) and val >= 20 else "")
        elif col == "P/B ÷ ROE":
            # Lower P/B÷ROE = better "price per unit of return on equity"
            val = row.get("P/B ÷ ROE")
            out.append("background-color: #d4edda; color: #155724" if pd.notna(val) and 0 < val < 15 else "")
        else:
            out.append("")
    return out

styled = (
    df[display_cols]
    .style
    .map(color_score, subset=["Value Score"])
    .map(color_analyst_rating, subset=[c for c in ["Analyst Rating"] if c in display_cols])
    .apply(highlight_row_vs_subsector, axis=1)
    .format(
        {
            "Price": "${:.2f}",
            "Market Cap ($B)": "${:.1f}B",
            "Value Score": "{:.3f}",
            "P/E": "{:.1f}",
            "Subsector Avg P/E": "{:.1f}",
            "Fwd P/E": "{:.1f}",
            "P/B": "{:.2f}",
            "Subsector Avg P/B": "{:.2f}",
            "ROE (%)": "{:.1f}%",
            "P/B ÷ ROE": "{:.1f}",
            "Analyst Score": "{:.2f}",
            "Analyst Count": "{:.0f}",
            "PEG": "{:.2f}",
            "EV/EBITDA": "{:.1f}",
            "Subsector Avg EV/EBITDA": "{:.1f}",
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

# ── Company Analysis (LLM-driven equity research) ──────────────────────────────
st.markdown("---")
st.subheader("Company Analysis")
st.caption(
    "Enter a ticker to generate an independent buy-side DCF analysis using Claude. "
    "Live price is passed to the model for the upside/downside comparison only — "
    "the valuation itself is intended to be derived from cash-flow assumptions, not anchored to price."
)

COMPANY_ANALYSIS_PROMPT_TEMPLATE = """Assume you are a buy-side equity research analyst (but do not use insider shorthand). Create a detailed DCF model for {company_name} ({ticker}) that is critical and rational. Do not go by company speak or what other analysts are doing. Do not look at other people's estimates to inform your valuation. Watch out for the tendency to generate DCF estimates that drift toward the current stock price. I want an independent DCF estimate solely derived from a realistic assessment of cash flows. Keep the depth and precision of the analysis intact, but write it in straightforward, professional English rather than insider shorthand or compressed jargon. Think "smart memo to an investment committee" instead of "analyst desk notes." Be aware that most sell-side analysts develop aggressive estimates and then put forward convenient narratives that are actually false — analyze every claim rigorously, but be a truth seeker. Do not dial down the valuation to match the stock price; sometimes stocks really are discounted. You can run scenarios and give me ranges. Your basic objective is valuation and to justify the assumptions. Do not give verbose company background unless it is tied to a valuation assumption.

REFERENCE DATA (provided by the dashboard, use only where useful):
- Ticker: {ticker}
- Company name (as reported): {company_name}
- Current market price (USD): {price}
- Market cap ($B): {market_cap_b}
- Trailing P/E: {pe}
- Forward P/E: {fwd_pe}
- Revenue TTM ($B): {revenue_b}
- Free cash flow TTM ($B): {fcf_b}
- Revenue growth (yoy %): {rev_growth}
- EPS growth (yoy %): {eps_growth}
- Gross margin: {gross_margin}
- ROE: {roe}
- Beta: {beta}
- Sell-side analyst consensus: {analyst_rating} (mean score {analyst_score}, n={analyst_n}) — note this is provided only for context; do not anchor to it.

Carry out the following work:

(1) Comprehensive business and market analysis: examine the company's annual reports and investor presentations to understand business segments, product lines, pricing power, and market positioning. Research main competitors to analyze market share, competitive strategies, and industry trends.

(2) Analyze the customer base, operational assets, and strategic initiatives. Investigate the track record for innovation, acquisition history, and capital allocation (buybacks, dividends, debt management), critically assessing the timing and effectiveness of each action.

(3) Gather and structure the last five years of financial statements (Income Statement, Balance Sheet, Cash Flow Statement). Identify any critical accounting rules or assumptions that materially affect the reported financials.

(4) Calculate and analyze key financial ratios and performance indicators over a five-year historical period: ROIC, ROE, leverage ratios, profitability margins, and operational KPIs such as volume/pricing growth, recurring revenue metrics, and customer churn.

(5) Risk assessment: review the 'Risk Factors' section of regulatory filings and address any significant regulatory, legal, product liability, or environmental issues.

(6) Develop detailed financial projections for the next 5–10 years. Build segment-specific revenue forecasts with explicit assumptions for volume and pricing. Project operating expenses, capex, and changes in net working capital based on historical trends and strategic plans.

(7) Calculate WACC by determining an appropriate risk-free rate, equity risk premium, company beta, and cost of debt. Estimate a justifiable terminal growth rate based on long-term industry and economic outlooks.

(8) Synthesize the projections and discount rate to calculate intrinsic value per share. Then — and only then — compare this value to the current market price (shown above) to determine potential upside or downside. Conclude with a sensitivity analysis showing how the valuation changes with variations in WACC, terminal growth, and revenue forecasts.

(9) Provide a Worst Case / Base Case / Upside Case intrinsic value per share, and compare each against the current price shown above. Be explicit: "Base case = $X, current price = ${price}, implied upside/downside = ±Y%."

Formatting: use Markdown headings (##) for each numbered section. Use tables for the historical financial summary, projections, WACC build, sensitivity grid, and scenario summary. Keep prose tight; cut anything not tied to a valuation assumption."""


def _fmt(val, suffix="", fmt="{:.2f}"):
    """Format a number for the prompt, or 'N/A' if missing."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    try:
        return fmt.format(val) + suffix
    except (ValueError, TypeError):
        return str(val)


def build_analysis_prompt(ticker: str, financials: dict) -> str:
    """Fill the template with whatever financial context we have for this ticker."""
    return COMPANY_ANALYSIS_PROMPT_TEMPLATE.format(
        ticker=ticker,
        company_name=financials.get("company_name") or ticker,
        price=_fmt(financials.get("price"), fmt="${:.2f}"),
        market_cap_b=_fmt(financials.get("market_cap_b"), suffix="B", fmt="${:.1f}"),
        pe=_fmt(financials.get("pe"), fmt="{:.1f}"),
        fwd_pe=_fmt(financials.get("fwd_pe"), fmt="{:.1f}"),
        revenue_b=_fmt(financials.get("revenue_b"), suffix="B", fmt="${:.1f}"),
        fcf_b=_fmt(financials.get("fcf_b"), suffix="B", fmt="${:.1f}"),
        rev_growth=_fmt(financials.get("rev_growth"), suffix="%", fmt="{:.1f}"),
        eps_growth=_fmt(financials.get("eps_growth"), suffix="%", fmt="{:.1f}"),
        gross_margin=_fmt(financials.get("gross_margin"), suffix="%", fmt="{:.1f}"),
        roe=_fmt(financials.get("roe"), suffix="%", fmt="{:.1f}"),
        beta=_fmt(financials.get("beta"), fmt="{:.2f}"),
        analyst_rating=financials.get("analyst_rating") or "N/A",
        analyst_score=_fmt(financials.get("analyst_score"), fmt="{:.2f}"),
        analyst_n=_fmt(financials.get("analyst_n"), fmt="{:.0f}"),
    )


def extract_financials_for_prompt(ticker: str, df_universe: pd.DataFrame) -> dict:
    """Pull what we already have from the dashboard's df; fall back to a fresh yfinance call if not in universe."""
    row = df_universe[df_universe["Ticker"] == ticker]
    if not row.empty:
        r = row.iloc[0]
        return {
            "company_name":   r.get("Company"),
            "price":          r.get("Price"),
            "market_cap_b":   r.get("Market Cap ($B)"),
            "pe":             r.get("P/E"),
            "fwd_pe":         r.get("Fwd P/E"),
            "revenue_b":      r.get("Revenue ($B)"),
            "fcf_b":          r.get("Free Cash Flow ($B)"),
            "rev_growth":     r.get("Rev Growth (%)"),
            "eps_growth":     r.get("EPS Growth (%)"),
            "gross_margin":   r.get("Gross Margin (%)"),
            "roe":            r.get("ROE (%)"),
            "beta":           r.get("Beta"),
            "analyst_rating": r.get("Analyst Rating"),
            "analyst_score":  r.get("Analyst Score"),
            "analyst_n":      r.get("Analyst Count"),
        }
    # Not in the loaded universe — do a one-off yfinance fetch.
    try:
        info = yf.Ticker(ticker).info
        return {
            "company_name":   info.get("shortName") or info.get("longName") or ticker,
            "price":          info.get("regularMarketPrice") or info.get("previousClose"),
            "market_cap_b":   (info.get("marketCap") or 0) / 1e9 if info.get("marketCap") else None,
            "pe":             info.get("trailingPE"),
            "fwd_pe":         info.get("forwardPE"),
            "revenue_b":      (info.get("totalRevenue") or 0) / 1e9 if info.get("totalRevenue") else None,
            "fcf_b":          (info.get("freeCashflow") or 0) / 1e9 if info.get("freeCashflow") else None,
            "rev_growth":     (info.get("revenueGrowth") or 0) * 100 if info.get("revenueGrowth") is not None else None,
            "eps_growth":     (info.get("earningsGrowth") or 0) * 100 if info.get("earningsGrowth") is not None else None,
            "gross_margin":   (info.get("grossMargins") or 0) * 100 if info.get("grossMargins") is not None else None,
            "roe":            (info.get("returnOnEquity") or 0) * 100 if info.get("returnOnEquity") is not None else None,
            "beta":           info.get("beta"),
            "analyst_rating": (info.get("recommendationKey") or "").replace("_", " ").title() or None,
            "analyst_score":  info.get("recommendationMean"),
            "analyst_n":      info.get("numberOfAnalystOpinions"),
        }
    except Exception as exc:
        return {"company_name": ticker}


@st.cache_data(show_spinner=False, ttl=3600)
def run_company_analysis(ticker: str, prompt: str, model: str = "claude-sonnet-4-6", max_tokens: int = 8192) -> str:
    """Cached so the same (ticker, prompt) doesn't re-bill within an hour."""
    api_key = st.secrets.get("ANTHROPIC_API_KEY") if hasattr(st, "secrets") else None
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not configured. In Streamlit Cloud, open Manage app → Settings → Secrets "
            "and add a line: ANTHROPIC_API_KEY = \"sk-ant-...\""
        )
    client = Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    # Concatenate all text blocks from the response.
    return "".join(
        block.text for block in msg.content if getattr(block, "type", None) == "text"
    )


with st.form("company_analysis_form"):
    col_a, col_b = st.columns([3, 1])
    with col_a:
        analysis_ticker = st.text_input(
            "Ticker",
            placeholder="e.g. HPE, AAPL, MSFT",
            help="Type a ticker to run an independent buy-side DCF analysis.",
        )
    with col_b:
        analysis_model = st.selectbox(
            "Model",
            ["claude-sonnet-4-6", "claude-opus-4-6"],
            index=0,
            help="Sonnet is faster and cheaper; Opus is higher quality for deep reasoning.",
        )
    run_analysis = st.form_submit_button("Run analysis", use_container_width=True)

if run_analysis and analysis_ticker:
    ticker_clean = analysis_ticker.strip().upper()
    if not _ANTHROPIC_AVAILABLE:
        st.error(
            "The `anthropic` package isn't installed. Add `anthropic>=0.40.0` to "
            "your `requirements.txt` and redeploy."
        )
    else:
        financials = extract_financials_for_prompt(ticker_clean, df)
        prompt = build_analysis_prompt(ticker_clean, financials)
        with st.expander("Prompt sent to Claude", expanded=False):
            st.code(prompt, language="markdown")
        try:
            with st.spinner(f"Generating buy-side analysis for {ticker_clean} ({analysis_model})…"):
                analysis_text = run_company_analysis(ticker_clean, prompt, model=analysis_model)
            st.markdown(analysis_text)

            # Live upside/downside vs current price, computed by the app (not the LLM).
            price_now = financials.get("price")
            if price_now is not None:
                st.info(
                    f"Live reference price for **{ticker_clean}** at run time: **${price_now:.2f}**. "
                    "The intrinsic values above were produced independently — compare them yourself."
                )
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")


# ── Company Background (LLM-driven 25-page memo) ───────────────────────────────
st.markdown("---")
st.subheader("Company Background")
st.caption(
    "Enter a ticker to generate a detailed buy-side information memorandum (~25 pages) using Claude. "
    "Covers business overview, segments, competitors, customers, financials, hidden liabilities, and a basic DCF. "
    "Generation takes 1–3 minutes due to the length of the output."
)

COMPANY_BACKGROUND_PROMPT_TEMPLATE = """Assume you are a buy-side equity research analyst. Create a detailed 25-page information memorandum on {company_name} ({ticker}) that includes substantial factual data while maintaining concise language. Present findings in separate categories with bullet-point format where appropriate. Use neutral language based on facts only. Present financial ratios and operational metrics in properly formatted Markdown tables. Use the latest data available and cite sources where you can (e.g. "Source: FY24 10-K, p.32" or "Source: Q2-25 earnings release").

REFERENCE DATA (provided by the dashboard, use only where useful):
- Ticker: {ticker}
- Company name (as reported): {company_name}
- Current market price (USD): {price}
- Market cap ($B): {market_cap_b}
- Trailing P/E: {pe}
- Forward P/E: {fwd_pe}
- Revenue TTM ($B): {revenue_b}
- Free cash flow TTM ($B): {fcf_b}
- Revenue growth (yoy %): {rev_growth}
- EPS growth (yoy %): {eps_growth}
- Gross margin: {gross_margin}
- ROE: {roe}
- Beta: {beta}
- Sell-side analyst consensus: {analyst_rating} (mean score {analyst_score}, n={analyst_n}) — for context only.

REQUIRED CONTENT SECTIONS (use ## Markdown headings, numbered exactly as below):

## 1. Business Overview
Provide a concise summary of the company's core business.

## 2. Business History
Include key milestones and significant events in the company's development.

## 3. Business Segments
Detail all major business divisions and their contributions to overall operations. Use a table for segment revenue and operating margins where data is available.

## 4. Key Products
- Catalog major products and their pricing structure.
- Analyze pricing power and trends.
- Include detailed pricing data across various products and services.
- Customer churn rate where disclosed.

## 5. End Markets and Industry Trends
- Evaluate growth or decline rates across different end markets.
- Identify geographical and segment-specific performance variations.
- Provide quantitative data on market trajectories.

## 6. Supply-Demand Dynamics
- Analyze supply-demand balance and impacts on pricing.
- Identify potential product substitutes.
- Document current and projected pricing trends.

## 7. Competitive Landscape
- List main competitors with 4–5 line descriptions of each.
- Document key competitor strategies, initiatives, and market share.
- Analyze industry consolidation activities.
- Track market share changes over recent years.
- Identify any bankruptcies within the industry.
- Document new market entrants.
- Compare products against industry alternatives.

## 8. Product Benchmarking
Compare products against competitors' offerings using a table. Include cost, performance, features, and other relevant metrics.

## 9. Business Model
Explain the company's revenue generation and operational structure.

## 10. Customer Analysis
- Identify main customers and their size.
- Detail key customer value propositions.
- Include customer feedback (both favorable and unfavorable).
- Analyze customer perception regarding brand appeal, trust, cost, performance, reliability, usability, and service.
- Document customer economics, usage frequency, contract terms, and churn rates.

## 11. Geographic and Segment Revenue Distribution
Present revenue breakdown by geography and business segment in a table.

## 12. Organizational Capabilities
- Assess employee talent, technology assets, manufacturing facilities.
- Track record of introducing new products.
- Document patents, R&D activities, and intellectual capital.
- Evaluate marketing effectiveness and service infrastructure.
- Detail recruitment sources (colleges, universities, regions).
- Analyze employee educational backgrounds.
- Report on employee satisfaction and retention rates.
- Document any union-related issues.

## 13. Acquisition History
Present a table showing acquired companies, acquisition prices, and years of completion. Do a deep dive into the success and failure of these acquisitions — did they create value?

## 14. Future Initiatives
Document planned strategic moves and growth initiatives.

## 15. Regulatory Environment
Identify specific regulations with potential favorable or unfavorable impacts.

## 16. Capital Allocation
- Analyze stock buyback policy, dividend strategy, leverage approach, and debt structure.
- Did the buybacks come at the right time? Was debt raised at a good time?

## 17. Key Investors and Founders
- Identify major shareholders.
- Provide background information on company founders.

## 18. Management Assessment
- Detail compensation packages for top executives.
- Document any known corporate governance issues or fraud concerns.

## 19. Financial Performance
Present 5-year historical data in tabular format covering:
- Income statement
- Cash flow statement
- Balance sheet
- Debt profile
- Stock options
Highlight any specific accounting rules/assumptions critical to understanding the business.

## 20. Hidden Liabilities
- Identify off-balance-sheet items.
- Document pension liabilities.
- Detail lease commitments.
- List corporate guarantees.

## 21. Financial Ratios
Present 5-year historical data in tabular format for:
- Return on Capital (ROIC)
- Return on Equity (ROE)
- Leverage ratios
- Gross Margin
- Net Margin
- Revenue Turnover

## 22. Operational Metrics
Document key performance indicators such as:
- Volume
- Average Revenue Per User (ARPU)
- Gross margin
- Capacity utilization
- Pricing growth
- Volume growth
- Employee turnover
- Same-store sales growth
- Percentage of revenue from services/consumables
- Recurring revenue metrics
- Net revenue retention

## 23. Risk Factors
Identify specific weaknesses or risks related to:
- Regulatory concerns
- Legal issues
- Product liability
- Health hazards
- Environmental hazards

## 24. Basic DCF Valuation
- Develop estimates of WACC, ROIC, growth, etc.
- Calculate Enterprise Value, Market Value of Debt, Equity Value.
- Provide detailed justifications of the assumptions.
- Compare to current share price ({price}) for upside/downside. Use the price provided here — do not generate a random price target based on other analysts' thinking. We want a DCF-driven price target.
- Show key sensitivities (WACC, terminal growth, revenue growth) in a sensitivity table.

Output the entire memorandum in Markdown. Use tables liberally where data is structured. Keep prose tight and factual. If data for a particular sub-bullet is not publicly available or you are uncertain, say so explicitly rather than fabricating numbers."""


def build_background_prompt(ticker: str, financials: dict) -> str:
    """Fill the background template with whatever financial context we have."""
    return COMPANY_BACKGROUND_PROMPT_TEMPLATE.format(
        ticker=ticker,
        company_name=financials.get("company_name") or ticker,
        price=_fmt(financials.get("price"), fmt="${:.2f}"),
        market_cap_b=_fmt(financials.get("market_cap_b"), suffix="B", fmt="${:.1f}"),
        pe=_fmt(financials.get("pe"), fmt="{:.1f}"),
        fwd_pe=_fmt(financials.get("fwd_pe"), fmt="{:.1f}"),
        revenue_b=_fmt(financials.get("revenue_b"), suffix="B", fmt="${:.1f}"),
        fcf_b=_fmt(financials.get("fcf_b"), suffix="B", fmt="${:.1f}"),
        rev_growth=_fmt(financials.get("rev_growth"), suffix="%", fmt="{:.1f}"),
        eps_growth=_fmt(financials.get("eps_growth"), suffix="%", fmt="{:.1f}"),
        gross_margin=_fmt(financials.get("gross_margin"), suffix="%", fmt="{:.1f}"),
        roe=_fmt(financials.get("roe"), suffix="%", fmt="{:.1f}"),
        beta=_fmt(financials.get("beta"), fmt="{:.2f}"),
        analyst_rating=financials.get("analyst_rating") or "N/A",
        analyst_score=_fmt(financials.get("analyst_score"), fmt="{:.2f}"),
        analyst_n=_fmt(financials.get("analyst_n"), fmt="{:.0f}"),
    )


with st.form("company_background_form"):
    col_a, col_b = st.columns([3, 1])
    with col_a:
        background_ticker = st.text_input(
            "Ticker",
            placeholder="e.g. WTC.AX, HPE, AAPL",
            help="Type a ticker to generate a 25-page information memorandum.",
            key="background_ticker_input",
        )
    with col_b:
        background_model = st.selectbox(
            "Model",
            ["claude-sonnet-4-6", "claude-opus-4-6"],
            index=0,
            help="Opus produces deeper analysis but takes longer and costs more.",
            key="background_model_select",
        )
    run_background = st.form_submit_button("Generate memorandum", use_container_width=True)

if run_background and background_ticker:
    bticker_clean = background_ticker.strip().upper()
    if not _ANTHROPIC_AVAILABLE:
        st.error(
            "The `anthropic` package isn't installed. Add `anthropic>=0.40.0` to "
            "your `requirements.txt` and redeploy."
        )
    else:
        b_financials = extract_financials_for_prompt(bticker_clean, df)
        b_prompt = build_background_prompt(bticker_clean, b_financials)
        with st.expander("Prompt sent to Claude", expanded=False):
            st.code(b_prompt, language="markdown")
        try:
            with st.spinner(
                f"Generating 25-page memorandum for {bticker_clean} ({background_model}) — this can take 1–3 minutes…"
            ):
                # Much higher max_tokens for the long memo.
                background_text = run_company_analysis(
                    bticker_clean, b_prompt, model=background_model, max_tokens=16000
                )
            st.markdown(background_text)

            # Download button so the user can save the full memo.
            st.download_button(
                "Download memorandum (.md)",
                data=background_text,
                file_name=f"{bticker_clean}_background_memo.md",
                mime="text/markdown",
            )

            b_price_now = b_financials.get("price")
            if b_price_now is not None:
                st.info(
                    f"Live reference price for **{bticker_clean}** at run time: **${b_price_now:.2f}** "
                    "(this is what the model was given for the Section 24 DCF comparison)."
                )
        except Exception as exc:
            st.error(f"Memorandum generation failed: {exc}")


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Data sourced from Yahoo Finance via yfinance. Not investment advice. "
    f"Universe: {len(df)} companies · Last loaded: refreshes hourly."
)
