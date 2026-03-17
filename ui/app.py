import streamlit as st
import sys, os, re

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from tools.llm import call_llm

st.set_page_config(
    page_title="Hedge Fund Intern · AI Due Diligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
# DESIGN SYSTEM & CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Playfair+Display:ital,wght@0,700;1,400&display=swap');

:root {
    --bg:        #07070E;
    --s1:        #0C0C18;
    --s2:        #111122;
    --s3:        #17172A;
    --border:    #1E1E32;
    --border-hi: #2A2A44;

    --gold:      #D4A843;
    --gold-2:    #ECC55A;
    --gold-3:    #F7DE8A;
    --gold-glow: rgba(212,168,67,0.18);

    --bull:      #00C67A;
    --bull-bg:   rgba(0,198,122,0.10);
    --bull-b:    rgba(0,198,122,0.30);

    --bear:      #FF3D5A;
    --bear-bg:   rgba(255,61,90,0.10);
    --bear-b:    rgba(255,61,90,0.30);

    --amber:     #F59E0B;
    --purple:    #7C6FF7;
    --blue:      #4F7EF7;

    --t1: #EEEEF6;
    --t2: #7878A0;
    --t3: #3E3E5E;

    --mono: 'JetBrains Mono', monospace;
    --sans: 'Inter', sans-serif;
    --serif: 'Playfair Display', serif;
    --r: 14px;
    --r-sm: 8px;
}

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--t1) !important;
    font-family: var(--sans) !important;
}

.stApp { background: radial-gradient(ellipse 120% 60% at 50% -10%, #0F0F28 0%, var(--bg) 60%) !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--s1) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div { padding: 1.5rem 1rem !important; }
[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: var(--s3) !important;
    border: 1px solid var(--border) !important;
    color: var(--t1) !important;
    border-radius: var(--r-sm) !important;
    font-family: var(--mono) !important;
    font-size: 0.8rem !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    padding: 0.5rem 0.75rem !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px var(--gold-glow) !important;
}
[data-testid="stSidebar"] label { color: var(--t2) !important; font-size: 0.75rem !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 !important;
    margin-bottom: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--t2) !important;
    font-family: var(--mono) !important;
    font-size: 0.68rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    padding: 0.9rem 1.4rem !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    transition: color 0.2s, border-color 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--t1) !important; }
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding: 1.5rem 0 !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ── Buttons ── */
.stButton > button {
    background: var(--gold) !important;
    color: #08080F !important;
    border: none !important;
    border-radius: var(--r-sm) !important;
    font-family: var(--sans) !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.3px !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 0 24px rgba(212,168,67,0.25) !important;
}
.stButton > button:hover {
    background: var(--gold-2) !important;
    box-shadow: 0 0 36px rgba(212,168,67,0.4) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Text Input (main area) ── */
.stTextInput > div > div > input {
    background: var(--s2) !important;
    border: 1px solid var(--border-hi) !important;
    color: var(--t1) !important;
    border-radius: var(--r) !important;
    font-family: var(--mono) !important;
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    letter-spacing: 6px !important;
    text-transform: uppercase !important;
    text-align: center !important;
    padding: 1rem !important;
    transition: all 0.2s !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--t3) !important;
    letter-spacing: 4px !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px var(--gold-glow), 0 0 40px rgba(212,168,67,0.08) !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: var(--gold) !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: var(--s2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    color: var(--t1) !important;
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    letter-spacing: 1px !important;
}
.streamlit-expanderContent {
    background: var(--s1) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--r-sm) var(--r-sm) !important;
}

/* ── Misc overrides ── */
div[data-testid="stMarkdownContainer"] p { color: var(--t1) !important; line-height: 1.75 !important; }
.stAlert { background: var(--s2) !important; border-color: var(--border) !important; color: var(--t1) !important; border-radius: var(--r-sm) !important; }
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 2rem 0 !important; }
.stDownloadButton > button { background: var(--s3) !important; color: var(--gold) !important; border: 1px solid var(--gold) !important; box-shadow: none !important; }
.stDownloadButton > button:hover { background: var(--gold-glow) !important; box-shadow: 0 0 20px var(--gold-glow) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius: 3px; }

/* ── Custom Components ── */

/* Agent cards */
.agent-card {
    background: var(--s1);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 1.75rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    line-height: 1.75;
}
.agent-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.agent-card.bull   { border-color: var(--bull-b); }
.agent-card.bull::before { background: var(--bull); box-shadow: 0 0 16px rgba(0,198,122,0.5); }
.agent-card.bear   { border-color: var(--bear-b); }
.agent-card.bear::before { background: var(--bear); box-shadow: 0 0 16px rgba(255,61,90,0.5); }
.agent-card.debate::before { background: linear-gradient(90deg, var(--bull) 0%, var(--amber) 50%, var(--bear) 100%); }
.agent-card.risk::before { background: var(--amber); }
.agent-card.planner::before { background: var(--purple); }

.agent-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: var(--mono);
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 4px;
    margin-bottom: 1rem;
}
.agent-badge.bull   { background: var(--bull-bg);  color: var(--bull);  border: 1px solid var(--bull-b); }
.agent-badge.bear   { background: var(--bear-bg);  color: var(--bear);  border: 1px solid var(--bear-b); }
.agent-badge.debate { background: rgba(245,158,11,0.1); color: var(--amber); border: 1px solid rgba(245,158,11,0.3); }
.agent-badge.risk   { background: rgba(245,158,11,0.1); color: var(--amber); border: 1px solid rgba(245,158,11,0.3); }
.agent-badge.planner{ background: rgba(124,111,247,0.1); color: var(--purple); border: 1px solid rgba(124,111,247,0.3); }
.agent-badge.cio    { background: var(--gold-glow); color: var(--gold); border: 1px solid rgba(212,168,67,0.35); }

.agent-body {
    font-size: 0.9rem;
    color: var(--t1);
    white-space: pre-wrap;
    font-family: var(--sans);
    line-height: 1.8;
}

/* Metrics strip */
.metrics-strip {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 1.25rem 0;
}
.mc {
    background: var(--s2);
    border: 1px solid var(--border);
    border-radius: var(--r-sm);
    padding: 0.65rem 1rem;
    min-width: 90px;
    flex: 1;
}
.mc-label { font-family: var(--mono); font-size: 0.58rem; letter-spacing: 1.5px; text-transform: uppercase; color: var(--t3); display: block; margin-bottom: 4px; }
.mc-value { font-family: var(--mono); font-size: 0.95rem; font-weight: 600; color: var(--t1); }
.mc-value.green  { color: var(--bull); }
.mc-value.red    { color: var(--bear); }
.mc-value.gold   { color: var(--gold); }
.mc-value.purple { color: var(--purple); }

/* Pipeline stepper */
.stepper {
    display: flex;
    align-items: center;
    gap: 0;
    background: var(--s1);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 1.25rem 1.5rem;
    margin: 1.5rem 0;
    overflow-x: auto;
}
.step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    flex: 1;
    min-width: 70px;
    position: relative;
}
.step-item:not(:last-child)::after {
    content: '';
    position: absolute;
    top: 14px;
    left: 50%;
    width: 100%;
    height: 1px;
    background: var(--border-hi);
    z-index: 0;
}
.step-item.done:not(:last-child)::after { background: var(--bull); opacity: 0.5; }
.step-item.active:not(:last-child)::after { background: var(--gold); opacity: 0.4; }

.step-dot {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    border: 2px solid var(--border-hi);
    background: var(--s2);
    color: var(--t3);
    position: relative;
    z-index: 1;
    transition: all 0.3s;
}
.step-dot.done   { background: var(--bull-bg); border-color: var(--bull); color: var(--bull); }
.step-dot.active {
    background: var(--gold-glow);
    border-color: var(--gold);
    color: var(--gold);
    box-shadow: 0 0 16px var(--gold-glow);
    animation: pulse-gold 1.8s ease-in-out infinite;
}
@keyframes pulse-gold {
    0%, 100% { box-shadow: 0 0 12px var(--gold-glow); }
    50%       { box-shadow: 0 0 28px rgba(212,168,67,0.4); }
}

.step-label {
    font-family: var(--mono);
    font-size: 0.58rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--t3);
    text-align: center;
}
.step-label.done   { color: var(--bull); }
.step-label.active { color: var(--gold); }

/* Data source pills */
.ds-row { display: flex; gap: 10px; margin: 1rem 0; flex-wrap: wrap; }
.ds-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 6px 14px;
    border-radius: 100px;
    font-family: var(--mono);
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.ds-pill.live  { background: rgba(0,198,122,0.1); color: var(--bull); border: 1px solid var(--bull-b); }
.ds-pill.warn  { background: rgba(245,158,11,0.1); color: var(--amber); border: 1px solid rgba(245,158,11,0.3); }
.ds-pill.off   { background: rgba(78,78,110,0.15); color: var(--t2); border: 1px solid var(--border-hi); }
.ds-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; display: inline-block; }

/* Verdict hero */
.verdict-hero {
    background: linear-gradient(135deg, var(--s2) 0%, #0D0D20 100%);
    border: 1px solid rgba(212,168,67,0.35);
    border-radius: var(--r);
    padding: 2.5rem;
    margin: 1.5rem 0;
    position: relative;
    overflow: hidden;
}
.verdict-hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.verdict-hero::after {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 260px; height: 260px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(212,168,67,0.06) 0%, transparent 70%);
    pointer-events: none;
}

.verdict-kpis { display: flex; gap: 1rem; margin-bottom: 1.75rem; flex-wrap: wrap; }
.verdict-kpi {
    background: var(--s1);
    border: 1px solid var(--border-hi);
    border-radius: var(--r-sm);
    padding: 1rem 1.5rem;
    min-width: 140px;
}
.verdict-kpi-label { font-family: var(--mono); font-size: 0.6rem; letter-spacing: 2px; text-transform: uppercase; color: var(--t2); margin-bottom: 6px; }
.verdict-kpi-value { font-family: var(--mono); font-size: 1.3rem; font-weight: 700; }
.verdict-kpi-value.strong-buy { color: var(--bull); text-shadow: 0 0 20px rgba(0,198,122,0.4); }
.verdict-kpi-value.buy        { color: #4ADE80; }
.verdict-kpi-value.hold       { color: var(--amber); }
.verdict-kpi-value.avoid      { color: #FB923C; }
.verdict-kpi-value.short      { color: var(--bear); text-shadow: 0 0 20px rgba(255,61,90,0.4); }
.verdict-kpi-value.gold       { color: var(--gold); }

/* HITL */
.hitl-section {
    background: var(--s2);
    border: 1px solid rgba(212,168,67,0.25);
    border-radius: var(--r);
    padding: 2rem;
    text-align: center;
    margin: 1.5rem 0;
}
.hitl-title {
    font-family: var(--serif);
    font-size: 1.35rem;
    color: var(--gold);
    margin-bottom: 0.5rem;
}
.hitl-sub { color: var(--t2); font-size: 0.875rem; margin-bottom: 1.5rem; line-height: 1.6; }

/* Hero input area */
.hero-container {
    text-align: center;
    padding: 2.5rem 0 2rem;
}
.hero-title {
    font-family: var(--serif);
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--gold-3) 0%, var(--gold) 50%, #B8892A 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.35rem;
    line-height: 1.1;
}
.hero-sub {
    font-family: var(--mono);
    font-size: 0.68rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: var(--t2);
}

/* Sidebar logo */
.sb-logo {
    font-family: var(--mono);
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--gold);
    letter-spacing: 2px;
    margin-bottom: 1.5rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid var(--border);
}
.sb-section { font-family: var(--mono); font-size: 0.6rem; letter-spacing: 2.5px; text-transform: uppercase; color: var(--t3); margin: 1.5rem 0 0.75rem; }

/* Data table in expander */
.data-table { font-family: var(--mono); font-size: 0.8rem; color: var(--t1); line-height: 1.9; white-space: pre-wrap; }

/* Landing page */
.landing-card {
    background: var(--s1);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 1.5rem;
}
.landing-feature { display: flex; align-items: flex-start; gap: 12px; padding: 0.6rem 0; border-bottom: 1px solid var(--border); }
.landing-feature:last-child { border-bottom: none; }
.landing-feature-icon { font-size: 1.1rem; margin-top: 1px; flex-shrink: 0; }
.landing-feature-text { font-size: 0.875rem; color: var(--t2); line-height: 1.5; }
.landing-feature-text strong { color: var(--t1); }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def parse_verdict(text: str) -> dict:
    """Extract FINAL VERDICT, confidence %, and position size from judge text."""
    verdict, css_cls, confidence, position = "HOLD", "hold", "N/A", "N/A"
    for v, cls in [("STRONG BUY","strong-buy"),("BUY","buy"),("SHORT","short"),("AVOID","avoid"),("HOLD","hold")]:
        if v in text.upper():
            verdict, css_cls = v, cls
            break
    m = re.search(r'CONFIDENCE[^:]*:\s*(\d+)\s*%', text, re.IGNORECASE)
    if m:
        confidence = f"{m.group(1)}%"
    m2 = re.search(r'POSITION SIZE[^:]*:\s*([^\n\.]+)', text, re.IGNORECASE)
    if m2:
        position = m2.group(1).strip()[:30]
    return {"verdict": verdict, "cls": css_cls, "confidence": confidence, "position": position}


def mc(label, value, cls=""):
    return f'<div class="mc"><span class="mc-label">{label}</span><span class="mc-value {cls}">{value}</span></div>'


def agent_card(cls, badge_icon, badge_label, body):
    return f"""<div class="agent-card {cls}">
  <div class="agent-badge {cls}">{badge_icon} {badge_label}</div>
  <div class="agent-body">{body}</div>
</div>"""


def stepper_html(steps, step_statuses, current_status):
    n_done = sum(1 for _, _, k in steps if step_statuses.get(k))
    html = '<div class="stepper">'
    for i, (icon, name, key) in enumerate(steps):
        done = step_statuses.get(key, False)
        is_active = (not done) and (i == n_done)
        if done:
            cls = "done"; dot_content = "✓"
        elif is_active:
            cls = "active"; dot_content = icon
        else:
            cls = ""; dot_content = str(i + 1)
        html += f'''<div class="step-item {cls}">
  <div class="step-dot {cls}">{dot_content}</div>
  <div class="step-label {cls}">{name}</div>
</div>'''
    html += '</div>'
    return html


def ds_pills(tavily_on: bool, edgar_ok: bool):
    pills = [
        ('live', '◉', 'yfinance'),
        ('live' if edgar_ok else 'warn', '◉', 'SEC EDGAR'),
        ('live' if tavily_on else 'off', '◉', 'Tavily' + ('' if tavily_on else ' (no key)')),
    ]
    html = '<div class="ds-row">'
    for cls, dot, label in pills:
        html += f'<span class="ds-pill {cls}"><span class="ds-dot"></span>{label}</span>'
    html += '</div>'
    return html


# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
defaults = {
    "analysis_state": None,
    "running": False,
    "human_reviewed": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

STEPS = [
    ("◈", "Data Fetch",  "data_done"),
    ("◎", "Planner",     "planner_done"),
    ("▲", "Bull",        "bull_done"),
    ("▽", "Bear",        "bear_done"),
    ("⚔", "Debate",      "debate_done"),
    ("◉", "Risk Audit",  "risk_done"),
    ("⊕", "CIO Verdict", "judge_done"),
    ("✓", "Human Review","approved"),
]


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sb-logo">◈ HEDGE FUND INTERN</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-section">API Configuration</div>', unsafe_allow_html=True)
    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...", key="groq_key")
    oai_key  = st.text_input("OpenAI Key (fallback)", type="password", placeholder="sk-...", key="oai_key")
    tav_key  = st.text_input("Tavily API Key", type="password", placeholder="tvly-...", key="tav_key")

    st.markdown('<div class="sb-section">Data Sources</div>', unsafe_allow_html=True)
    tavily_active = bool(tav_key or os.environ.get("TAVILY_API_KEY"))
    st.markdown(ds_pills(tavily_active, True), unsafe_allow_html=True)

    if st.session_state.running and st.session_state.analysis_state:
        s = st.session_state.analysis_state
        st.markdown('<div class="sb-section">Live Analysis</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:var(--mono);font-size:0.78rem;color:var(--t2);line-height:2;">
        <span style="color:var(--t3);">TICKER</span><br>
        <span style="color:var(--gold);font-size:1.1rem;font-weight:600;">{s['ticker']}</span><br><br>
        <span style="color:var(--t3);">STATUS</span><br>
        <span style="color:var(--t1);">{s.get('status','starting').replace('_',' ').upper()}</span>
        </div>
        """, unsafe_allow_html=True)

        if s.get("financial_data") and not s["financial_data"].get("error"):
            fd = s["financial_data"]
            chg = fd.get("price_change_30d", 0)
            chg_color = "#00C67A" if chg >= 0 else "#FF3D5A"
            st.markdown(f"""
            <div style="margin-top:1rem;font-family:var(--mono);font-size:0.8rem;">
            <div style="color:var(--t3);font-size:0.6rem;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;">Current Price</div>
            <div style="color:var(--t1);font-size:1.4rem;font-weight:700;">${fd.get('current_price','—')}</div>
            <div style="color:{chg_color};font-size:0.8rem;">{'▲' if chg >= 0 else '▼'} {abs(chg)}% 30d</div>
            <div style="margin-top:0.75rem;color:var(--t3);font-size:0.6rem;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;">Market Cap</div>
            <div style="color:var(--t1);font-size:0.95rem;">{fd.get('market_cap_fmt','—')}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        '<span style="font-family:var(--mono);font-size:0.62rem;color:var(--t3);letter-spacing:1px;">'
        'GROQ PRIMARY · OPENAI FALLBACK<br>SEC EDGAR · YFINANCE · TAVILY</span>',
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════

# ── Hero Header ──
st.markdown("""
<div class="hero-container">
  <div class="hero-title">AI Hedge Fund Intern</div>
  <div class="hero-sub">Multi-Agent · Real Data · Human-in-the-Loop Due Diligence</div>
</div>
""", unsafe_allow_html=True)

# ── Ticker Input ──
_, col_ticker, _ = st.columns([1, 2, 1])
with col_ticker:
    ticker = st.text_input("ticker", placeholder="NVDA", label_visibility="collapsed", key="ticker_input")
    run_btn = st.button("Run Due Diligence →", use_container_width=True)

# ── Validation & Trigger ──
if run_btn:
    if not ticker:
        st.warning("Enter a stock ticker to begin.")
    elif not groq_key and not oai_key:
        st.warning("Add at least a Groq or OpenAI API key in the sidebar.")
    else:
        if groq_key: os.environ["GROQ_API_KEY"] = groq_key
        if oai_key:  os.environ["OPENAI_API_KEY"] = oai_key
        if tav_key:  os.environ["TAVILY_API_KEY"] = tav_key
        st.session_state.running = True
        st.session_state.human_reviewed = False
        st.session_state.analysis_state = {
            "ticker": ticker.upper(), "company_name": ticker.upper(),
            "financial_data": {}, "financial_summary": "",
            "edgar_summary": "", "web_summary": "",
            "planner_output": "", "bull_analysis": "",
            "bear_analysis": "", "debate_round": "",
            "risk_audit": "", "judge_verdict": "", "report": "",
            "human_approved": False, "iteration": 0,
            "status": "starting", "error": None,
        }


# ═══════════════════════════════════════════════════════════════
# ANALYSIS PIPELINE
# ═══════════════════════════════════════════════════════════════
if st.session_state.running and st.session_state.analysis_state:
    state = st.session_state.analysis_state
    sym   = state["ticker"]

    step_statuses = {
        "data_done":    bool(state["financial_summary"]),
        "planner_done": bool(state["planner_output"]),
        "bull_done":    bool(state["bull_analysis"]),
        "bear_done":    bool(state["bear_analysis"]),
        "debate_done":  bool(state["debate_round"]),
        "risk_done":    bool(state["risk_audit"]),
        "judge_done":   bool(state["judge_verdict"]),
        "approved":     st.session_state.human_reviewed,
    }

    # Progress stepper
    st.markdown(stepper_html(STEPS, step_statuses, state["status"]), unsafe_allow_html=True)

    # ── STEP 1: Data Fetch ──────────────────────────────────────
    if not state["financial_summary"]:
        from tools.yfinance_tool import get_stock_financials, format_financials_for_agent
        from tools.sec_edgar_tool import format_edgar_for_agent
        from tools.tavily_tool import format_tavily_for_agent

        with st.spinner(f"yfinance — fetching price, fundamentals & options for {sym}..."):
            fd = get_stock_financials(sym)
            state["financial_data"] = fd
            state["financial_summary"] = format_financials_for_agent(fd)
            state["company_name"] = fd.get("company_name", sym)

        with st.spinner("SEC EDGAR — pulling verified 10-K / 8-K filing history..."):
            state["edgar_summary"] = format_edgar_for_agent(sym)

        with st.spinner("Tavily — scanning analyst upgrades, earnings news, insider activity..."):
            state["web_summary"] = format_tavily_for_agent(sym, state["company_name"])

        state["status"] = "data_done"
        st.rerun()

    # ── Metrics strip ───────────────────────────────────────────
    fd = state["financial_data"]
    if fd and not fd.get("error"):
        p   = fd.get("current_price", "—")
        c30 = fd.get("price_change_30d", 0)
        c3m = fd.get("price_change_3m", 0)
        sign30 = ("+" if c30 >= 0 else "") + str(c30) + "%"
        sign3m = ("+" if c3m >= 0 else "") + str(c3m) + "%"
        rec = (fd.get("analyst_recommendation") or "N/A").upper()
        pcr = fd.get("put_call_ratio")
        pcr_str = str(pcr) if pcr else "N/A"
        pcr_cls = "red" if (pcr and pcr > 1) else "green"

        st.markdown(f"""<div class="metrics-strip">
  {mc("Ticker",    sym,                              "gold")}
  {mc("Price",     f"${p}",                          "")}
  {mc("30D",       sign30,                           "green" if c30 >= 0 else "red")}
  {mc("3M",        sign3m,                           "green" if c3m >= 0 else "red")}
  {mc("Mkt Cap",   fd.get("market_cap_fmt","N/A"),   "")}
  {mc("P/E",       fd.get("pe_ratio","N/A"),         "")}
  {mc("Analyst",   fd.get("analyst_target","N/A"),   "gold")}
  {mc("Consensus", rec,                              "green" if "buy" in rec.lower() else ("red" if "sell" in rec.lower() else ""))}
  {mc("Put/Call",  pcr_str,                          pcr_cls)}
  {mc("Beta",      fd.get("beta","N/A"),             "")}
  {mc("Short %",   str(round(float(fd.get("short_percent_float",0) or 0)*100,1))+"%", "")}
  {mc("Sector",    fd.get("sector","N/A"),           "purple")}
</div>""", unsafe_allow_html=True)

    # ── STEP 2: Planner ─────────────────────────────────────────
    if state["financial_summary"] and not state["planner_output"]:
        from prompts.agent_prompts import PLANNER_PROMPT
        with st.spinner("Planner Agent — structuring research focus areas..."):
            ctx = f"{state['financial_summary']}\n{state['edgar_summary']}\n{state['web_summary']}"
            state["planner_output"] = call_llm(
                messages=[
                    {"role": "system", "content": PLANNER_PROMPT},
                    {"role": "user", "content": f"Research plan for {sym}\n\n{ctx}"},
                ],
                temperature=0.3,
            )
            state["status"] = "planner_done"
        st.rerun()

    # ── STEP 3: Bull ─────────────────────────────────────────────
    if state["planner_output"] and not state["bull_analysis"]:
        from prompts.agent_prompts import BULL_PROMPT
        with st.spinner("Bull Agent — building the buy case..."):
            ctx = "\n".join(filter(None, [state["financial_summary"], state["edgar_summary"], state["web_summary"], f"Research focus:\n{state['planner_output']}"] ))
            state["bull_analysis"] = call_llm(
                messages=[
                    {"role": "system", "content": BULL_PROMPT},
                    {"role": "user", "content": f"Bull case for {sym}\n\n{ctx}"},
                ],
                temperature=0.7,
            )
            state["status"] = "bull_done"
        st.rerun()

    # ── STEP 4: Bear ─────────────────────────────────────────────
    if state["bull_analysis"] and not state["bear_analysis"]:
        from prompts.agent_prompts import BEAR_PROMPT
        with st.spinner("Bear Agent — building the short case..."):
            ctx = "\n".join(filter(None, [state["financial_summary"], state["edgar_summary"], state["web_summary"], f"Research focus:\n{state['planner_output']}"] ))
            state["bear_analysis"] = call_llm(
                messages=[
                    {"role": "system", "content": BEAR_PROMPT},
                    {"role": "user", "content": f"Bear case for {sym}\n\n{ctx}"},
                ],
                temperature=0.7,
            )
            state["status"] = "bear_done"
        st.rerun()

    # ── STEP 5: Debate ───────────────────────────────────────────
    if state["bear_analysis"] and not state["debate_round"]:
        from prompts.agent_prompts import DEBATE_PROMPT
        with st.spinner("Debate — analysts rebutting each other's strongest points..."):
            state["debate_round"] = call_llm(
                messages=[
                    {"role": "system", "content": DEBATE_PROMPT},
                    {"role": "user", "content": f"BULL:\n{state['bull_analysis']}\n\nBEAR:\n{state['bear_analysis']}"},
                ],
                temperature=0.8,
            )
            state["status"] = "debate_done"
        st.rerun()

    # ── STEP 6: Risk Audit ───────────────────────────────────────
    if state["debate_round"] and not state["risk_audit"]:
        from prompts.agent_prompts import RISK_AUDITOR_PROMPT
        with st.spinner("Risk Auditor — scoring 5 risk dimensions objectively..."):
            ctx = "\n".join(filter(None, [state["financial_summary"], state["edgar_summary"], state["web_summary"]]))
            state["risk_audit"] = call_llm(
                messages=[
                    {"role": "system", "content": RISK_AUDITOR_PROMPT},
                    {"role": "user", "content": f"Audit {sym}\n\n{ctx}"},
                ],
                temperature=0.2,
            )
            state["status"] = "risk_done"
        st.rerun()

    # ── STEP 7: CIO Judge ────────────────────────────────────────
    if state["risk_audit"] and not state["judge_verdict"]:
        from prompts.agent_prompts import JUDGE_PROMPT
        with st.spinner("CIO — reviewing all evidence and making final call..."):
            full_ctx = (
                f"STOCK: {sym} — {state['company_name']}\n\n"
                f"FINANCIALS:\n{state['financial_summary']}\n\n"
                f"SEC EDGAR:\n{state['edgar_summary']}\n\n"
                f"WEB INTEL:\n{state['web_summary']}\n\n"
                f"BULL:\n{state['bull_analysis']}\n\n"
                f"BEAR:\n{state['bear_analysis']}\n\n"
                f"DEBATE:\n{state['debate_round']}\n\n"
                f"RISK:\n{state['risk_audit']}"
            )
            state["judge_verdict"] = call_llm(
                messages=[
                    {"role": "system", "content": JUDGE_PROMPT},
                    {"role": "user", "content": full_ctx},
                ],
                temperature=0.4,
            )
            state["status"] = "judge_done"
        st.rerun()

    # ══════════════════════════════════════════════════════════
    # TABBED OUTPUT — shown as soon as we have any agent output
    # ══════════════════════════════════════════════════════════
    if any([state["planner_output"], state["bull_analysis"], state["bear_analysis"],
            state["debate_round"], state["risk_audit"], state["judge_verdict"]]):

        tab_labels = ["◎ Research Plan", "▲ Bull Case", "▽ Bear Case", "⚔ Debate", "◉ Risk Audit", "⊕ CIO Verdict"]
        tabs = st.tabs(tab_labels)

        # Tab 0 — Research Plan
        with tabs[0]:
            if state["planner_output"]:
                st.markdown(agent_card("planner","◎","Planner Agent — Research Strategy", state["planner_output"]), unsafe_allow_html=True)
                with st.expander("Raw Data Sources", expanded=False):
                    sub1, sub2, sub3 = st.tabs(["yfinance", "SEC EDGAR", "Tavily"])
                    with sub1:
                        st.markdown(f'<div class="data-table">{state["financial_summary"]}</div>', unsafe_allow_html=True)
                    with sub2:
                        st.markdown(f'<div class="data-table">{state["edgar_summary"] or "_SEC EDGAR data not loaded_"}</div>', unsafe_allow_html=True)
                    with sub3:
                        st.markdown(f'<div class="data-table">{state["web_summary"] or "_Tavily not configured — add TAVILY_API_KEY_"}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:var(--t3);font-family:var(--mono);font-size:0.8rem;padding:2rem 0;">Generating research plan...</div>', unsafe_allow_html=True)

        # Tab 1 — Bull
        with tabs[1]:
            if state["bull_analysis"]:
                st.markdown(agent_card("bull","▲","Bull Analyst — Buy Case", state["bull_analysis"]), unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:var(--t3);font-family:var(--mono);font-size:0.8rem;padding:2rem 0;">Bull Agent not yet run...</div>', unsafe_allow_html=True)

        # Tab 2 — Bear
        with tabs[2]:
            if state["bear_analysis"]:
                st.markdown(agent_card("bear","▽","Bear Analyst — Short Case", state["bear_analysis"]), unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:var(--t3);font-family:var(--mono);font-size:0.8rem;padding:2rem 0;">Bear Agent not yet run...</div>', unsafe_allow_html=True)

        # Tab 3 — Debate
        with tabs[3]:
            if state["debate_round"]:
                st.markdown(agent_card("debate","⚔","Debate — Cross-Examination & Rebuttals", state["debate_round"]), unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:var(--t3);font-family:var(--mono);font-size:0.8rem;padding:2rem 0;">Debate not yet run...</div>', unsafe_allow_html=True)

        # Tab 4 — Risk
        with tabs[4]:
            if state["risk_audit"]:
                st.markdown(agent_card("risk","◉","Risk Auditor — Objective Risk Scoring", state["risk_audit"]), unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:var(--t3);font-family:var(--mono);font-size:0.8rem;padding:2rem 0;">Risk audit not yet run...</div>', unsafe_allow_html=True)

        # Tab 5 — Verdict
        with tabs[5]:
            if state["judge_verdict"]:
                v = parse_verdict(state["judge_verdict"])
                st.markdown(f"""
<div class="verdict-hero">
  <div class="verdict-kpis">
    <div class="verdict-kpi">
      <div class="verdict-kpi-label">Final Verdict</div>
      <div class="verdict-kpi-value {v['cls']}">{v['verdict']}</div>
    </div>
    <div class="verdict-kpi">
      <div class="verdict-kpi-label">CIO Confidence</div>
      <div class="verdict-kpi-value gold">{v['confidence']}</div>
    </div>
    <div class="verdict-kpi">
      <div class="verdict-kpi-label">Position Size</div>
      <div class="verdict-kpi-value gold">{v['position']}</div>
    </div>
    <div class="verdict-kpi">
      <div class="verdict-kpi-label">Stock</div>
      <div class="verdict-kpi-value gold">{sym}</div>
    </div>
  </div>
  <div class="agent-badge cio">⊕ Chief Investment Officer — Final Decision</div>
  <div class="agent-body" style="margin-top:1.25rem;">{state['judge_verdict']}</div>
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:var(--t3);font-family:var(--mono);font-size:0.8rem;padding:2rem 0;">CIO verdict pending...</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # HUMAN-IN-THE-LOOP APPROVAL
    # ══════════════════════════════════════════════════════════
    if state["judge_verdict"] and not st.session_state.human_reviewed:
        st.markdown("""
<div class="hitl-section">
  <div class="hitl-title">Human Review Required</div>
  <div class="hitl-sub">The AI investment committee has reached a verdict.<br>
  Review the full analysis in the tabs above, then approve or reject below.</div>
</div>
""", unsafe_allow_html=True)

        ca, cb, cc = st.columns(3)
        with ca:
            if st.button("✓  Approve & Generate Report", use_container_width=True):
                st.session_state.human_reviewed = True
                state["human_approved"] = True
                st.rerun()
        with cb:
            if st.button("↺  Re-run Analysis", use_container_width=True):
                st.session_state.analysis_state = None
                st.session_state.running = False
                st.rerun()
        with cc:
            if st.button("✕  Reject & Dismiss", use_container_width=True):
                st.session_state.running = False
                st.rerun()

    # ══════════════════════════════════════════════════════════
    # APPROVED STATE — Download Report
    # ══════════════════════════════════════════════════════════
    if st.session_state.human_reviewed:
        v = parse_verdict(state["judge_verdict"])
        st.markdown(f"""
<div style="background:var(--bull-bg);border:1px solid var(--bull-b);border-radius:var(--r);
padding:1.25rem 1.75rem;display:flex;align-items:center;gap:14px;margin-top:1.5rem;">
  <span style="font-size:1.4rem;">✓</span>
  <div>
    <div style="font-weight:600;color:var(--bull);font-size:0.95rem;">Report Approved</div>
    <div style="color:var(--t2);font-size:0.82rem;margin-top:2px;">
      {sym} · Verdict: <strong style="color:var(--t1);">{v['verdict']}</strong> ·
      Confidence: <strong style="color:var(--t1);">{v['confidence']}</strong>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        from agents.report_agent import run as build_report
        from tools.pdf_report import generate_pdf
        state["human_approved"] = True
        report = build_report(state)["report"]

        # Generate PDF (cached in session state so it's not rebuilt on every rerun)
        if "pdf_bytes" not in st.session_state or st.session_state.get("pdf_ticker") != sym:
            with st.spinner("Rendering PDF report..."):
                st.session_state.pdf_bytes = generate_pdf(state)
                st.session_state.pdf_ticker = sym

        safe_name = state["company_name"].replace(" ", "_").replace("/", "-")
        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button(
                "↓  Download PDF Report",
                data=st.session_state.pdf_bytes,
                file_name=f"{sym}_due_diligence_{safe_name}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with d2:
            st.download_button(
                "↓  Download Markdown",
                data=report,
                file_name=f"{sym}_due_diligence_{safe_name}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with d3:
            if st.button("◈  Analyze Another Stock", use_container_width=True):
                st.session_state.analysis_state = None
                st.session_state.running = False
                st.session_state.human_reviewed = False
                st.session_state.pop("pdf_bytes", None)
                st.session_state.pop("pdf_ticker", None)
                st.rerun()


# ═══════════════════════════════════════════════════════════════
# LANDING PAGE (empty state)
# ═══════════════════════════════════════════════════════════════
if not st.session_state.running:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.4, 1])

    with c1:
        st.markdown("""
<div class="landing-card">
  <div style="font-family:var(--mono);font-size:0.62rem;letter-spacing:2.5px;text-transform:uppercase;color:var(--t3);margin-bottom:1rem;">Pipeline Overview</div>

  <div class="landing-feature">
    <div class="landing-feature-icon">◈</div>
    <div class="landing-feature-text">
      <strong>Real Data Pull</strong> — yfinance (price, fundamentals, options), SEC EDGAR (10-K XBRL verified history), Tavily (live news & analyst activity)
    </div>
  </div>
  <div class="landing-feature">
    <div class="landing-feature-icon">◎</div>
    <div class="landing-feature-text">
      <strong>Planner Agent</strong> — Decomposes the research question into bull focus, bear focus, and risk dimensions
    </div>
  </div>
  <div class="landing-feature">
    <div class="landing-feature-icon">▲</div>
    <div class="landing-feature-text">
      <strong>Bull Analyst</strong> — Builds the strongest possible BUY case with cited data points and price target
    </div>
  </div>
  <div class="landing-feature">
    <div class="landing-feature-icon">▽</div>
    <div class="landing-feature-text">
      <strong>Bear Analyst</strong> — Constructs the SHORT/AVOID thesis, challenges bull assumptions with hard numbers
    </div>
  </div>
  <div class="landing-feature">
    <div class="landing-feature-icon">⚔</div>
    <div class="landing-feature-text">
      <strong>Debate Round</strong> — Each analyst rebuts the other's strongest argument in a structured cross-examination
    </div>
  </div>
  <div class="landing-feature">
    <div class="landing-feature-icon">◉</div>
    <div class="landing-feature-text">
      <strong>Risk Auditor</strong> — Scores 5 risk dimensions (valuation, liquidity, regulatory, insider, macro) 1–10
    </div>
  </div>
  <div class="landing-feature">
    <div class="landing-feature-icon">⊕</div>
    <div class="landing-feature-text">
      <strong>CIO Judge</strong> — Synthesizes all evidence into a FINAL VERDICT with confidence % and position size
    </div>
  </div>
  <div class="landing-feature">
    <div class="landing-feature-icon">✓</div>
    <div class="landing-feature-text">
      <strong>Human Review</strong> — You approve or reject the committee's decision before a report is generated
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    with c2:
        st.markdown("""
<div class="landing-card" style="margin-bottom:1rem;">
  <div style="font-family:var(--mono);font-size:0.62rem;letter-spacing:2.5px;text-transform:uppercase;color:var(--t3);margin-bottom:1rem;">Try These Tickers</div>
  <div style="display:flex;flex-wrap:wrap;gap:8px;">
""" + "".join([
    f'<span style="background:var(--s3);border:1px solid var(--border-hi);border-radius:6px;padding:6px 14px;font-family:var(--mono);font-size:0.85rem;font-weight:600;color:var(--gold);">{t}</span>'
    for t in ["NVDA","AAPL","TSLA","MSFT","META","AMZN","GOOGL","JPM","PLTR","COIN"]
]) + """
  </div>
</div>

<div class="landing-card">
  <div style="font-family:var(--mono);font-size:0.62rem;letter-spacing:2.5px;text-transform:uppercase;color:var(--t3);margin-bottom:1rem;">Setup</div>
  <div style="font-size:0.82rem;color:var(--t2);line-height:2;">
    <span style="color:var(--bull);">●</span> Groq API key — <strong style="color:var(--t1);">Required</strong> (free tier available)<br>
    <span style="color:var(--t2);">●</span> OpenAI API key — Optional fallback<br>
    <span style="color:var(--amber);">●</span> Tavily API key — Optional, enables live news<br>
    <span style="color:var(--purple);">●</span> SEC EDGAR — No key needed, always live<br>
    <span style="color:var(--bull);">●</span> yfinance — No key needed, always live
  </div>
</div>
""", unsafe_allow_html=True)
