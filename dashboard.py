import streamlit as st
import requests
import requests as req_lib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math

SPRING_URL  = "http://localhost:8080/api"
FASTAPI_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SENTINEL — Fraud Ops",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

:root {
    --bg:        #0a0a0f;
    --panel:     #0f0f1a;
    --panel2:    #13131f;
    --border:    #1e1e35;
    --violet:    #7c3aff;
    --violet-lo: #3d1a80;
    --cyan:      #00e5ff;
    --cyan-lo:   #00566b;
    --coral:     #ff4d6d;
    --coral-lo:  #7a1a2e;
    --lime:      #b6f000;
    --lime-lo:   #3d5000;
    --amber:     #ffb703;
    --amber-lo:  #664800;
    --pink:      #f72585;
    --teal:      #43dfb0;
    --text:      #e2e2f0;
    --text-dim:  #6b6b8a;
    --text-mid:  #a0a0c0;
}

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text);
}
.stApp { background-color: var(--bg) !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--violet-lo); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--violet); }

/* ══ SIDEBAR ══ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,
        #0d0818 0%, #0f0a1e 30%, #0a0f1e 60%, #0d1018 100%) !important;
    border-right: 1px solid #1e1e35 !important;
    position: relative;
}
[data-testid="stSidebar"]::before {
    content: "";
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg,
        var(--violet) 0%, var(--cyan) 20%,
        var(--coral) 40%, var(--lime) 60%,
        var(--amber) 80%, var(--pink) 100%);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stRadio > div { gap: 4px !important; }
[data-testid="stSidebar"] .stRadio label {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    padding: 11px 16px 11px 20px !important;
    border-radius: 6px !important;
    border: 1px solid transparent !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(124, 58, 255, 0.12) !important;
    border-color: var(--violet-lo) !important;
    color: #fff !important;
}

/* ══ METRICS ══ */
[data-testid="stMetric"] {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 18px 20px !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::after {
    content: "";
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--violet), var(--cyan));
    border-radius: 0 0 10px 10px;
}
[data-testid="stMetric"]:nth-child(2)::after { background: linear-gradient(90deg, var(--coral), var(--pink)); }
[data-testid="stMetric"]:nth-child(3)::after { background: linear-gradient(90deg, var(--teal), var(--lime)); }
[data-testid="stMetric"]:nth-child(4)::after { background: linear-gradient(90deg, var(--amber), var(--coral)); }
[data-testid="stMetric"]:nth-child(5)::after { background: linear-gradient(90deg, var(--pink), var(--violet)); }
[data-testid="stMetricLabel"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.1em !important;
    color: var(--text-dim) !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.9rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    line-height: 1.2 !important;
}

/* ══ HEADERS ══ */
h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2rem !important;
    color: #ffffff !important;
    margin-bottom: 4px !important;
}
h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    color: var(--text) !important;
}

/* ══ TABS ══ */
.stTabs [data-baseweb="tab-list"] {
    background: var(--panel);
    border-radius: 8px;
    padding: 4px;
    border: 1px solid var(--border);
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    color: var(--text-dim);
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 9px 20px;
    text-transform: uppercase;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    color: #fff !important;
    background: linear-gradient(135deg, var(--violet), #5b21ff) !important;
    box-shadow: 0 2px 12px rgba(124,58,255,0.35);
}

/* ══ BUTTONS ══ */
.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    background: linear-gradient(135deg, var(--violet) 0%, #5b21ff 100%) !important;
    border: none !important;
    color: #fff !important;
    border-radius: 8px !important;
    padding: 10px 22px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    box-shadow: 0 4px 20px rgba(124,58,255,0.5) !important;
    transform: translateY(-2px) !important;
}

/* ══ INPUTS ══ */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: #fff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--violet) !important;
    box-shadow: 0 0 0 2px rgba(124,58,255,0.2) !important;
}

/* ══ ALERT CARDS ══ */
.fraud-alert {
    background: linear-gradient(135deg, #180010 0%, #200015 100%);
    border: 1px solid #5a0025;
    border-top: 3px solid var(--coral);
    border-radius: 12px;
    padding: 32px;
    text-align: center;
    box-shadow: 0 8px 40px rgba(255,77,109,0.12);
}
.legit-alert {
    background: linear-gradient(135deg, #001418 0%, #001c1e 100%);
    border: 1px solid #004455;
    border-top: 3px solid var(--cyan);
    border-radius: 12px;
    padding: 32px;
    text-align: center;
    box-shadow: 0 8px 40px rgba(0,229,255,0.08);
}
.ring-alert {
    background: linear-gradient(135deg, #120d00 0%, #1a1200 100%);
    border: 1px solid #3d2d00;
    border-left: 4px solid var(--amber);
    border-radius: 8px;
    padding: 18px 22px;
    margin: 14px 0;
}
.info-box {
    background: var(--panel);
    border: 1px solid var(--border);
    border-left: 4px solid var(--violet);
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 28px;
}
.detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 14px;
    margin: 3px 0;
    background: var(--panel2);
    border-radius: 6px;
    border: 1px solid var(--border);
}
.stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #16162a;
}
[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── CHART THEME & COLOR SCALES ────────────────────────────────
PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,15,26,0.6)",
    font=dict(family="JetBrains Mono, monospace", color="#6b6b8a", size=11),
    xaxis=dict(gridcolor="#1a1a2e", linecolor="#1e1e35",
               tickfont=dict(family="JetBrains Mono", size=9, color="#6b6b8a")),
    yaxis=dict(gridcolor="#1a1a2e", linecolor="#1e1e35",
               tickfont=dict(family="JetBrains Mono", size=9, color="#6b6b8a")),
    margin=dict(t=32, b=32, l=40, r=20)
)

CHROMA_HEAT   = ["#0d0d1f","#3d1a80","#7c3aff","#00e5ff","#b6f000","#ffb703"]
CHROMA_THREAT = ["#1a0010","#6b0030","#cc0055","#ff4d6d","#ff9eb5","#ffd6e0"]
CHROMA_OCEAN  = ["#001428","#003d6b","#0077cc","#00bfff","#43dfb0","#b6f000"]
CHROMA_FIRE   = ["#1a0500","#6b1500","#cc3300","#ff6b35","#ffb703","#fff59d"]
CAT_COLORS    = ["#7c3aff","#00e5ff","#ff4d6d","#b6f000","#ffb703","#f72585","#43dfb0","#ff6b35"]

AMOUNT_MAX = 50000.0  # must match graph_loader.py training normalization

# ── DATA HELPERS ──────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_stats():
    try:
        r = requests.get(f"{FASTAPI_URL}/stats", timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

@st.cache_data(ttl=60)
def get_device_rings(min_users=10, limit=20):
    try:
        r = requests.get(f"{FASTAPI_URL}/rings/devices?min_users={min_users}&limit={limit}", timeout=10)
        return r.json().get("device_rings", []) if r.status_code == 200 else []
    except: return []

@st.cache_data(ttl=60)
def get_ip_rings(min_users=10, limit=20):
    try:
        r = requests.get(f"{FASTAPI_URL}/rings/ips?min_users={min_users}&limit={limit}", timeout=10)
        return r.json().get("ip_rings", []) if r.status_code == 200 else []
    except: return []

@st.cache_data(ttl=60)
def get_ring_transactions(identifier):
    try:
        r = requests.get(f"{FASTAPI_URL}/rings/transactions/{identifier}", timeout=10)
        return r.json() if r.status_code == 200 else {}
    except: return {}

@st.cache_data(ttl=30)
def get_all_transactions():
    try:
        r = requests.get(f"{SPRING_URL}/transactions", timeout=5)
        return r.json() if r.status_code == 200 else []
    except: return []

def check_fraud(tx_id):
    try:
        r = requests.post(f"{SPRING_URL}/transactions/{tx_id}/fraud-check", timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None

def get_transaction(tx_id):
    try:
        r = requests.get(f"{SPRING_URL}/transactions/{tx_id}", timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

def service_status(url):
    try: requests.get(url, timeout=2); return True
    except: return False

def scale_amount(amount: float) -> float:
    return math.log1p(amount) / math.log1p(AMOUNT_MAX)

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 28px 20px 20px 20px;">
        <div style="font-family: Syne, sans-serif; font-size: 1.6rem; font-weight: 800;
                    color: #fff; letter-spacing: 0.06em; line-height: 1;">
            SEN<span style="color: #7c3aff;">TI</span>NEL
        </div>
        <div style="font-family: JetBrains Mono, monospace; font-size: 0.6rem;
                    color: #6b6b8a; letter-spacing: 0.2em; margin-top: 5px;">
            FRAUD INTELLIGENCE · GNN
        </div>
        <div style="margin-top: 14px; height: 2px;
                    background: linear-gradient(90deg, #7c3aff, #00e5ff, #ff4d6d, #b6f000);
                    border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "📊   Overview",
        "🔍   Fraud Check",
        "🧪   Predict New TX",
        "🕸   Ring Detector",
        "📋   Transactions",
        "📈   Analytics",
    ], label_visibility="collapsed")

    st.markdown("""
    <div style="height:1px; background: linear-gradient(90deg,transparent,#1e1e35,transparent);
                margin: 8px 16px 20px 16px;"></div>
    """, unsafe_allow_html=True)

    stats = get_stats()
    if stats:
        st.markdown("""
        <div style="font-family: JetBrains Mono; font-size: 0.58rem; font-weight: 600;
                    letter-spacing: 0.18em; color: #6b6b8a; text-transform: uppercase;
                    padding: 0 16px; margin-bottom: 10px;">◈ Live Metrics</div>
        """, unsafe_allow_html=True)
        items = [
            ("Total TXs",    f"{stats.get('total_transactions',0):,}",  "#7c3aff"),
            ("Fraud Rate",   f"{stats.get('fraud_rate',0):.2f}%",       "#ff4d6d"),
            ("Model AUC",    f"{stats.get('model_auc',0):.4f}",         "#00e5ff"),
            ("Risk Devices", f"{stats.get('high_risk_devices',0):,}",   "#ffb703"),
            ("Risk IPs",     f"{stats.get('high_risk_ips',0):,}",       "#f72585"),
        ]
        for label, val, color in items:
            st.markdown(f"""
            <div class="stat-item" style="padding: 8px 16px;">
                <span style="font-family: JetBrains Mono; font-size: 0.72rem; color: #a0a0c0;">{label}</span>
                <span style="font-family: Syne, sans-serif; font-size: 0.82rem;
                             font-weight: 700; color: {color};">{val}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="height:1px; background: linear-gradient(90deg,transparent,#1e1e35,transparent);
                margin: 16px;"></div>
    <div style="font-family: JetBrains Mono; font-size: 0.58rem; font-weight: 600;
                letter-spacing: 0.18em; color: #6b6b8a; text-transform: uppercase;
                padding: 0 16px; margin-bottom: 10px;">◈ Services</div>
    """, unsafe_allow_html=True)

    for name, url in [("FastAPI  :8000", f"{FASTAPI_URL}/health"),
                       ("Spring  :8080",  f"{SPRING_URL}/transactions/TXN0000001")]:
        ok    = service_status(url)
        color = "#43dfb0" if ok else "#ff4d6d"
        bg    = "rgba(67,223,176,0.07)"  if ok else "rgba(255,77,109,0.07)"
        bd    = "rgba(67,223,176,0.2)"   if ok else "rgba(255,77,109,0.2)"
        label = "Online" if ok else "Offline"
        dot   = "●" if ok else "○"
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center;
                    padding: 8px 14px; margin: 4px 16px;
                    background: {bg}; border: 1px solid {bd}; border-radius: 7px;">
            <span style="font-family: JetBrains Mono; font-size: 0.67rem; color: #a0a0c0;">{name}</span>
            <span style="font-family: JetBrains Mono; font-size: 0.67rem; font-weight: 600; color: {color};">
                {dot} {label}
            </span>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="padding: 20px 16px 8px;">
        <div style="font-family: JetBrains Mono; font-size: 0.55rem;
                    color: #3a3a55; letter-spacing: 0.08em; line-height: 2;">
            GraphSAGE GNN · Neo4j AuraDB<br>MySQL RDS · Spring Boot · FastAPI
        </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
if "Overview" in page:
    st.markdown("""
    <h1>◈ Sentinel Overview</h1>
    <p style="font-family: JetBrains Mono; font-size: 0.72rem; color: #6b6b8a;
              letter-spacing: 0.08em; margin-bottom: 32px;">
        Real-time fraud intelligence · GraphSAGE GNN · Ring detection
    </p>""", unsafe_allow_html=True)

    if stats:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Transactions", f"{stats.get('total_transactions',0):,}")
        c2.metric("Fraud Cases",  f"{stats.get('fraud_count',0):,}",
                  delta=f"{stats.get('fraud_rate',0):.1f}%", delta_color="inverse")
        c3.metric("Avg Amount",   f"${stats.get('avg_amount',0):,.0f}")
        c4.metric("Risk Devices", f"{stats.get('high_risk_devices',0):,}")
        c5.metric("Risk IPs",     f"{stats.get('high_risk_ips',0):,}")

    st.markdown("<br>", unsafe_allow_html=True)
    all_txns = get_all_transactions()
    if all_txns:
        df = pd.DataFrame(all_txns)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Transaction Split")
            fraud_c = stats.get("fraud_count", 0)
            total_c = stats.get("total_transactions", 1)
            fig = go.Figure(go.Pie(
                values=[total_c - fraud_c, fraud_c],
                labels=["Legitimate", "Fraud"],
                hole=0.68,
                marker=dict(colors=["#7c3aff", "#ff4d6d"],
                            line=dict(color="#0a0a0f", width=4)),
                textfont=dict(family="JetBrains Mono", size=11),
                hovertemplate="<b>%{label}</b><br>%{value:,} · %{percent}<extra></extra>"
            ))
            fig.add_annotation(
                text=f"<b>{stats.get('fraud_rate',0):.1f}%</b><br>fraud",
                x=0.5, y=0.5,
                font=dict(family="Syne", size=20, color="#ff4d6d"),
                showarrow=False
            )
            fig.update_layout(**PLOT, height=330, showlegend=True,
                legend=dict(font=dict(family="JetBrains Mono", size=11), bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Amount Distribution")
            if "amount" in df.columns and "isFraud" in df.columns:
                sample = df.sample(min(3000, len(df)))
                sample["type"] = sample["isFraud"].map(
                    {True: "Fraud", False: "Legitimate", None: "Unknown"})
                fig2 = px.histogram(sample, x="amount", color="type",
                    color_discrete_map={"Fraud": "#ff4d6d", "Legitimate": "#7c3aff"},
                    nbins=50, barmode="overlay", opacity=0.78)
                fig2.update_layout(**PLOT, height=330,
                    legend=dict(font=dict(family="JetBrains Mono", size=11), bgcolor="rgba(0,0,0,0)"))
                st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Top Fraud Ring Threats")
    col1, col2 = st.columns(2)
    device_rings = get_device_rings(min_users=20, limit=10)
    ip_rings     = get_ip_rings(min_users=20, limit=10)

    with col1:
        st.markdown("""<div style="font-family:JetBrains Mono;font-size:0.62rem;letter-spacing:0.14em;
            color:#6b6b8a;text-transform:uppercase;margin-bottom:8px;">Suspicious Devices</div>""",
            unsafe_allow_html=True)
        if device_rings:
            dr_df = pd.DataFrame(device_rings)
            fig = go.Figure(go.Bar(
                x=dr_df["fraud_rate"], y=dr_df["device_id"], orientation="h",
                marker=dict(color=dr_df["fraud_rate"], colorscale=CHROMA_THREAT,
                            line=dict(color="rgba(0,0,0,0)", width=0)),
                text=dr_df["fraud_rate"].apply(lambda x: f"{x:.0f}%"),
                textfont=dict(family="JetBrains Mono", size=10, color="#fff"),
                hovertemplate="<b>%{y}</b><br>Fraud Rate: %{x:.1f}%<extra></extra>"
            ))
            fig.update_layout(**PLOT, height=300, xaxis_title="Fraud Rate %")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("""<div style="font-family:JetBrains Mono;font-size:0.62rem;letter-spacing:0.14em;
            color:#6b6b8a;text-transform:uppercase;margin-bottom:8px;">Suspicious IPs</div>""",
            unsafe_allow_html=True)
        if ip_rings:
            ip_df = pd.DataFrame(ip_rings)
            fig = go.Figure(go.Bar(
                x=ip_df["fraud_rate"], y=ip_df["ip_address"], orientation="h",
                marker=dict(color=ip_df["fraud_rate"], colorscale=CHROMA_FIRE,
                            line=dict(color="rgba(0,0,0,0)", width=0)),
                text=ip_df["fraud_rate"].apply(lambda x: f"{x:.0f}%"),
                textfont=dict(family="JetBrains Mono", size=10, color="#fff"),
                hovertemplate="<b>%{y}</b><br>Fraud Rate: %{x:.1f}%<extra></extra>"
            ))
            fig.update_layout(**PLOT, height=300, xaxis_title="Fraud Rate %")
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# PAGE 2 — FRAUD CHECK (existing TX from DB)
# ══════════════════════════════════════════════════════════════
elif "Fraud Check" in page:
    st.markdown("""
    <h1>🔍 Fraud Check</h1>
    <p style="font-family: JetBrains Mono; font-size: 0.72rem; color: #6b6b8a;
              letter-spacing: 0.08em; margin-bottom: 32px;">
        Look up any existing transaction ID and run it through the GNN · Requires DB record
    </p>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        tx_id = st.text_input("", placeholder="Transaction ID  —  e.g. TXN0000001",
                              label_visibility="collapsed")
    with col2:
        check_btn = st.button("Analyze →", use_container_width=True)

    st.markdown("""<div style="font-family:JetBrains Mono;font-size:0.6rem;letter-spacing:0.14em;
        color:#6b6b8a;text-transform:uppercase;margin:18px 0 8px;">Quick load</div>""",
        unsafe_allow_html=True)
    ex_cols = st.columns(6)
    examples = ["TXN0000001","TXN0000010","TXN0000050",
                "TXN0000100","TXN0001000","TXN0005000"]
    for i, ex in enumerate(examples):
        if ex_cols[i].button(ex, key=f"btn_{i}", use_container_width=True):
            tx_id     = ex
            check_btn = True

    if check_btn and tx_id:
        with st.spinner("Analyzing graph topology..."):
            result    = check_fraud(tx_id)
            tx_detail = get_transaction(tx_id)

        if result is None:
            st.error(f"Transaction **{tx_id}** not found in the database. "
                     f"To predict on arbitrary inputs use **🧪 Predict New TX** in the sidebar.")
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            is_fraud = result["prediction"] == 1
            prob     = result["fraud_probability"]

            if is_fraud:
                st.markdown(f"""
                <div class='fraud-alert'>
                    <div style="font-family:JetBrains Mono;font-size:0.65rem;
                                letter-spacing:0.2em;color:#ff4d6d;margin-bottom:10px;">
                        ⚠ THREAT DETECTED
                    </div>
                    <div style="font-family:Syne,sans-serif;font-size:2.6rem;font-weight:800;
                                color:#ff4d6d;letter-spacing:0.04em;line-height:1;">
                        FRAUD CONFIRMED
                    </div>
                    <div style="font-family:JetBrains Mono;font-size:0.88rem;
                                color:#ff9eb5;margin-top:12px;letter-spacing:0.05em;">
                        {tx_id}  ·  Risk Score: {prob:.1%}
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='legit-alert'>
                    <div style="font-family:JetBrains Mono;font-size:0.65rem;
                                letter-spacing:0.2em;color:#00e5ff;margin-bottom:10px;">
                        ✓ CLEARANCE GRANTED
                    </div>
                    <div style="font-family:Syne,sans-serif;font-size:2.6rem;font-weight:800;
                                color:#00e5ff;letter-spacing:0.04em;line-height:1;">
                        AUTHORIZED
                    </div>
                    <div style="font-family:JetBrains Mono;font-size:0.88rem;
                                color:#80f3ff;margin-top:12px;letter-spacing:0.05em;">
                        {tx_id}  ·  Risk Score: {prob:.1%}
                    </div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Risk Gauge")
                bar_color = "#ff4d6d" if is_fraud else "#00e5ff"
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=prob * 100,
                    number=dict(suffix="%", font=dict(family="Syne", size=34, color=bar_color)),
                    gauge=dict(
                        axis=dict(range=[0, 100],
                                  tickfont=dict(family="JetBrains Mono", size=10, color="#6b6b8a")),
                        bar=dict(color=bar_color, thickness=0.38),
                        bgcolor="#0f0f1a", bordercolor="#1e1e35",
                        steps=[
                            {"range": [0,  30],  "color": "#0a1a0f"},
                            {"range": [30, 60],  "color": "#1a1000"},
                            {"range": [60, 100], "color": "#1a0008"},
                        ],
                        threshold=dict(
                            line=dict(color="#ffb703", width=2),
                            thickness=0.75,
                            value=result.get("threshold_used", 0.38) * 100
                        )
                    )
                ))
                fig.update_layout(**PLOT, height=280)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("### Transaction Details")
                if tx_detail:
                    fields = [
                        ("TX ID",       tx_detail.get("transactionId", "—")),
                        ("Amount",      f"${tx_detail.get('amount', 0):,.2f}"),
                        ("User",        tx_detail.get("userId", "—")),
                        ("Merchant",    tx_detail.get("merchantId", "—")),
                        ("Device",      tx_detail.get("deviceId", "—")),
                        ("IP Address",  tx_detail.get("ipAddress", "—")),
                        ("Foreign Txn", "Yes" if tx_detail.get("isForeignTxn") else "No"),
                        ("New Device",  "Yes" if tx_detail.get("isNewDevice")  else "No"),
                        ("High Risk",   "Yes" if tx_detail.get("isHighRiskCountry") else "No"),
                        ("True Label",  "Fraud" if tx_detail.get("isFraud") else "Legit"),
                        ("GNN Verdict", "Fraud" if is_fraud else "Legit"),
                    ]
                    for k, v in fields:
                        vc = "#ff4d6d" if v in {"Yes", "Fraud"} else \
                             "#43dfb0" if v in {"No",  "Legit"} else "#e2e2f0"
                        st.markdown(f"""
                        <div class="detail-row">
                            <span style="font-family:JetBrains Mono;font-size:0.67rem;
                                         color:#6b6b8a;letter-spacing:0.06em;">{k}</span>
                            <span style="font-family:JetBrains Mono;font-size:0.75rem;
                                         font-weight:600;color:{vc};">{v}</span>
                        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 3 — PREDICT NEW TX (direct FastAPI, no DB needed)
# ══════════════════════════════════════════════════════════════
elif "Predict New" in page:
    st.markdown("""
    <h1>🧪 Predict New Transaction</h1>
    <p style="font-family: JetBrains Mono; font-size: 0.72rem; color: #6b6b8a;
              letter-spacing: 0.08em; margin-bottom: 24px;">
        Predict fraud on any transaction — no DB record needed · Posts directly to FastAPI /predict
    </p>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <div style="font-family:Syne,sans-serif;font-size:0.85rem;font-weight:700;
                    color:#7c3aff;margin-bottom:6px;">How this works</div>
        <div style="font-family:JetBrains Mono;font-size:0.7rem;color:#a0a0c0;line-height:1.9;">
            Bypasses Spring Boot + MySQL entirely and calls
            <span style="color:#00e5ff;">FastAPI /predict</span> with raw feature values.
            The GNN model runs on whatever inputs you provide — fully generalized to unseen transactions.<br>
            Ring scores: set higher if the device/IP is shared by many users. Leave at 0 for unknown.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── PRESETS ───────────────────────────────────────────────
    st.markdown("""<div style="font-family:JetBrains Mono;font-size:0.62rem;letter-spacing:0.14em;
        color:#6b6b8a;text-transform:uppercase;margin-bottom:10px;">Quick Presets</div>""",
        unsafe_allow_html=True)

    PRESETS = {
        "🟢  Low Risk":    dict(amount=45.0,   device_ring_score=0.0,  ip_ring_score=0.0,
                                combined_ring_score=0.0,  is_new_device=False,
                                is_high_risk=False, is_foreign=False,
                                user_tx_count=50,  user_avg_amount=80.0,
                                merch_tx_count=500, merch_fraud_rate=0.02),
        "🟡  Medium Risk": dict(amount=850.0,  device_ring_score=0.3,  ip_ring_score=0.25,
                                combined_ring_score=0.3,  is_new_device=True,
                                is_high_risk=False, is_foreign=True,
                                user_tx_count=3,   user_avg_amount=200.0,
                                merch_tx_count=100, merch_fraud_rate=0.15),
        "🔴  High Risk":   dict(amount=4200.0, device_ring_score=0.75, ip_ring_score=0.68,
                                combined_ring_score=0.75, is_new_device=True,
                                is_high_risk=True,  is_foreign=True,
                                user_tx_count=1,   user_avg_amount=500.0,
                                merch_tx_count=50,  merch_fraud_rate=0.45),
        "💀  Ring Attack": dict(amount=9999.0, device_ring_score=0.95, ip_ring_score=0.92,
                                combined_ring_score=0.95, is_new_device=True,
                                is_high_risk=True,  is_foreign=True,
                                user_tx_count=1,   user_avg_amount=9000.0,
                                merch_tx_count=20,  merch_fraud_rate=0.80),
    }

    # Store preset selection in session state
    if "preset_vals" not in st.session_state:
        st.session_state.preset_vals = PRESETS["🟢  Low Risk"].copy()

    pcols = st.columns(4)
    for i, (label, vals) in enumerate(PRESETS.items()):
        if pcols[i].button(label, key=f"preset_{i}", use_container_width=True):
            st.session_state.preset_vals = vals.copy()
            st.rerun()

    p = st.session_state.preset_vals

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""<div style="font-family:JetBrains Mono;font-size:0.62rem;letter-spacing:0.14em;
            color:#6b6b8a;text-transform:uppercase;margin-bottom:12px;">◈ Transaction Basics</div>""",
            unsafe_allow_html=True)

        tx_id_new    = st.text_input("Transaction ID",
                                      value="NEW_TX_001",
                                      help="Any identifier — doesn't need to exist in DB")
        amount       = st.number_input("Amount ($)",
                                        min_value=0.0, max_value=100000.0,
                                        value=float(p["amount"]), step=10.0)
        user_enc     = st.number_input("User ID (encoded int)",
                                        min_value=0, max_value=100000,
                                        value=0, step=1,
                                        help="Encoded user integer — 0 = unknown user")
        merchant_enc = st.number_input("Merchant ID (encoded int)",
                                        min_value=0, max_value=10000,
                                        value=0, step=1)
        device_enc   = st.number_input("Device ID (encoded int)",
                                        min_value=0, max_value=50000,
                                        value=0, step=1)

        st.markdown("""<div style="font-family:JetBrains Mono;font-size:0.62rem;letter-spacing:0.14em;
            color:#6b6b8a;text-transform:uppercase;margin:20px 0 12px;">◈ Boolean Flags</div>""",
            unsafe_allow_html=True)

        is_new_device = st.toggle("New Device",           value=bool(p["is_new_device"]))
        is_high_risk  = st.toggle("High Risk Country",    value=bool(p["is_high_risk"]))
        is_foreign    = st.toggle("Foreign Transaction",  value=bool(p["is_foreign"]))

    with col_b:
        st.markdown("""<div style="font-family:JetBrains Mono;font-size:0.62rem;letter-spacing:0.14em;
            color:#6b6b8a;text-transform:uppercase;margin-bottom:12px;">◈ Ring Scores (0.0 – 1.0)</div>""",
            unsafe_allow_html=True)

        st.markdown("""<div style="font-family:JetBrains Mono;font-size:0.65rem;color:#6b6b8a;
            margin-bottom:14px;line-height:1.8;padding:10px 14px;background:#0f0f1a;
            border-radius:6px;border:1px solid #1e1e35;">
            These are the <span style="color:#ffb703;">most impactful features</span> for the GNN.<br>
            High score = device/IP shared by many users = <span style="color:#ff4d6d;">ring signal.</span>
        </div>""", unsafe_allow_html=True)

        device_ring_score   = st.slider("Device Ring Score",   0.0, 1.0,
                                         float(p["device_ring_score"]),   0.01)
        ip_ring_score       = st.slider("IP Ring Score",       0.0, 1.0,
                                         float(p["ip_ring_score"]),       0.01)
        combined_ring_score = st.slider("Combined Ring Score", 0.0, 1.0,
                                         float(p["combined_ring_score"]), 0.01,
                                         help="Typically max(device_ring, ip_ring)")

        st.markdown("""<div style="font-family:JetBrains Mono;font-size:0.62rem;letter-spacing:0.14em;
            color:#6b6b8a;text-transform:uppercase;margin:20px 0 12px;">
            ◈ User & Merchant History</div>""", unsafe_allow_html=True)

        user_tx_count    = st.number_input("User TX Count",        min_value=1,   max_value=10000,
                                            value=int(p["user_tx_count"]),  step=1)
        user_avg_amount  = st.number_input("User Avg Amount ($)",  min_value=0.0, max_value=50000.0,
                                            value=float(p["user_avg_amount"]), step=10.0)
        merch_tx_count   = st.number_input("Merchant TX Count",    min_value=1,   max_value=100000,
                                            value=int(p["merch_tx_count"]),  step=10)
        merch_fraud_rate = st.slider("Merchant Fraud Rate",        0.0, 1.0,
                                      float(p["merch_fraud_rate"]), 0.01)

    # ── RUN BUTTON ────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    run_col, _ = st.columns([1, 3])
    run_btn = run_col.button("▶  Run Prediction", use_container_width=True)

    if run_btn:
        amount_scaled = scale_amount(amount)

        payload = {
            "transaction_id":      tx_id_new,
            "amount":              amount,
            "user_enc":            int(user_enc),
            "merchant_enc":        int(merchant_enc),
            "device_enc":          int(device_enc),
            "device_ring_score":   device_ring_score,
            "ip_ring_score":       ip_ring_score,
            "combined_ring_score": combined_ring_score,
            "user_tx_count":       float(user_tx_count),
            "user_avg_amount":     user_avg_amount,
            "merch_tx_count":      float(merch_tx_count),
            "merch_fraud_rate":    merch_fraud_rate,
            "is_new_device":       1.0 if is_new_device else 0.0,
            "is_high_risk":        1.0 if is_high_risk  else 0.0,
            "is_foreign":          1.0 if is_foreign    else 0.0,
        }

        with st.spinner("Running GNN inference..."):
            try:
                r      = req_lib.post(f"{FASTAPI_URL}/predict", json=payload, timeout=10)
                result = r.json() if r.status_code == 200 else None
                if r.status_code != 200:
                    st.error(f"FastAPI error {r.status_code}: {r.text}")
            except Exception as e:
                result = None
                st.error(f"FastAPI unreachable: {e}")

        if result:
            is_fraud  = result["prediction"] == 1
            prob      = result["fraud_probability"]
            ring_risk = result.get("ring_risk", "LOW")

            st.markdown("<br>", unsafe_allow_html=True)

            if is_fraud:
                st.markdown(f"""
                <div class='fraud-alert'>
                    <div style="font-family:JetBrains Mono;font-size:0.65rem;
                                letter-spacing:0.2em;color:#ff4d6d;margin-bottom:10px;">
                        ⚠ MODEL VERDICT
                    </div>
                    <div style="font-family:Syne,sans-serif;font-size:2.6rem;font-weight:800;
                                color:#ff4d6d;letter-spacing:0.04em;line-height:1;">
                        FRAUD DETECTED
                    </div>
                    <div style="font-family:JetBrains Mono;font-size:0.88rem;
                                color:#ff9eb5;margin-top:12px;letter-spacing:0.05em;">
                        {tx_id_new}  ·  Risk: {prob:.1%}  ·  Ring Risk: {ring_risk}
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='legit-alert'>
                    <div style="font-family:JetBrains Mono;font-size:0.65rem;
                                letter-spacing:0.2em;color:#00e5ff;margin-bottom:10px;">
                        ✓ MODEL VERDICT
                    </div>
                    <div style="font-family:Syne,sans-serif;font-size:2.6rem;font-weight:800;
                                color:#00e5ff;letter-spacing:0.04em;line-height:1;">
                        LEGITIMATE
                    </div>
                    <div style="font-family:JetBrains Mono;font-size:0.88rem;
                                color:#80f3ff;margin-top:12px;letter-spacing:0.05em;">
                        {tx_id_new}  ·  Risk: {prob:.1%}  ·  Ring Risk: {ring_risk}
                    </div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown("### Risk Score")
                bar_color = "#ff4d6d" if is_fraud else "#00e5ff"
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=prob * 100,
                    number=dict(suffix="%", font=dict(family="Syne", size=30, color=bar_color)),
                    gauge=dict(
                        axis=dict(range=[0, 100],
                                  tickfont=dict(family="JetBrains Mono", size=10, color="#6b6b8a")),
                        bar=dict(color=bar_color, thickness=0.38),
                        bgcolor="#0f0f1a", bordercolor="#1e1e35",
                        steps=[
                            {"range": [0,  30],  "color": "#0a1a0f"},
                            {"range": [30, 60],  "color": "#1a1000"},
                            {"range": [60, 100], "color": "#1a0008"},
                        ],
                        threshold=dict(
                            line=dict(color="#ffb703", width=2),
                            thickness=0.75,
                            value=result.get("threshold_used", 0.38) * 100
                        )
                    )
                ))
                fig.update_layout(**PLOT, height=260)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.markdown("### Feature Profile")
                categories = ["Amount", "Dev Ring", "IP Ring",
                              "New Dev", "High Risk", "Foreign", "Merch Fraud"]
                values = [
                    min(amount / AMOUNT_MAX, 1.0),
                    device_ring_score,
                    ip_ring_score,
                    1.0 if is_new_device else 0.0,
                    1.0 if is_high_risk  else 0.0,
                    1.0 if is_foreign    else 0.0,
                    merch_fraud_rate,
                ]
                radar_color = "#ff4d6d" if is_fraud else "#00e5ff"
                fig2 = go.Figure(go.Scatterpolar(
                    r=values + [values[0]],
                    theta=categories + [categories[0]],
                    fill="toself",
                    fillcolor=f"rgba(255,77,109,0.15)" if is_fraud else "rgba(0,229,255,0.15)",
                    line=dict(color=radar_color, width=2),
                    marker=dict(color=radar_color, size=6)
                ))
                fig2.update_layout(
                    **PLOT, height=260,
                    polar=dict(
                        bgcolor="rgba(15,15,26,0.8)",
                        radialaxis=dict(visible=True, range=[0, 1],
                                        tickfont=dict(family="JetBrains Mono", size=8, color="#6b6b8a"),
                                        gridcolor="#1e1e35"),
                        angularaxis=dict(
                            tickfont=dict(family="JetBrains Mono", size=9, color="#a0a0c0"),
                            gridcolor="#1e1e35")
                    )
                )
                st.plotly_chart(fig2, use_container_width=True)

            with c3:
                st.markdown("### Inputs Summary")
                ring_colors = {"HIGH": "#ff4d6d", "MEDIUM": "#ffb703", "LOW": "#43dfb0"}
                summary = [
                    ("Amount",           f"${amount:,.2f}"),
                    ("Amount (scaled)",  f"{scale_amount(amount):.4f}"),
                    ("Device Ring",      f"{device_ring_score:.2f}"),
                    ("IP Ring",          f"{ip_ring_score:.2f}"),
                    ("Combined Ring",    f"{combined_ring_score:.2f}"),
                    ("Ring Risk",        ring_risk),
                    ("New Device",       "Yes" if is_new_device else "No"),
                    ("High Risk Cntry",  "Yes" if is_high_risk  else "No"),
                    ("Foreign TX",       "Yes" if is_foreign    else "No"),
                    ("User TX Count",    str(user_tx_count)),
                    ("Merch Fraud Rate", f"{merch_fraud_rate:.2f}"),
                    ("Threshold",        f"{result.get('threshold_used', 0.38):.4f}"),
                ]
                for k, v in summary:
                    vc = "#ff4d6d" if v == "Yes"  else \
                         "#43dfb0" if v == "No"   else \
                         ring_colors.get(v, "#e2e2f0")
                    st.markdown(f"""
                    <div class="detail-row">
                        <span style="font-family:JetBrains Mono;font-size:0.67rem;
                                     color:#6b6b8a;letter-spacing:0.06em;">{k}</span>
                        <span style="font-family:JetBrains Mono;font-size:0.75rem;
                                     font-weight:600;color:{vc};">{v}</span>
                    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 4 — RING DETECTOR
# ══════════════════════════════════════════════════════════════
elif "Ring" in page:
    st.markdown("""
    <h1>🕸 Ring Detector</h1>
    <p style="font-family: JetBrains Mono; font-size: 0.72rem; color: #6b6b8a;
              letter-spacing: 0.08em; margin-bottom: 32px;">
        Graph-based detection of coordinated fraud networks
    </p>""", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📱  Device Rings", "🌐  IP Rings"])

    for tab, ring_type in zip([tab1, tab2], ["device", "ip"]):
        with tab:
            st.markdown("<br>", unsafe_allow_html=True)
            ctrl, main = st.columns([1, 4])
            with ctrl:
                st.markdown("""<div style="font-family:JetBrains Mono;font-size:0.6rem;
                    letter-spacing:0.14em;color:#6b6b8a;text-transform:uppercase;
                    margin-bottom:10px;">Filters</div>""", unsafe_allow_html=True)
                min_u = st.slider("Min users", 5, 50, 10, key=f"{ring_type}_min")
                lim   = st.slider("Top N",     5, 50, 20, key=f"{ring_type}_lim")

            rings = get_device_rings(min_u, lim) if ring_type == "device" else get_ip_rings(min_u, lim)
            if not rings:
                st.info("No rings found with current filters.")
                continue

            rdf       = pd.DataFrame(rings)
            id_col    = "device_id" if ring_type == "device" else "ip_address"
            label     = "Device"   if ring_type == "device" else "IP Address"
            high_risk = rdf[rdf["fraud_rate"] >= 50]

            with main:
                c1, c2, c3 = st.columns(3)
                c1.metric(f"Suspicious {label}s", len(rdf))
                c2.metric("High Risk (>50%)",      len(high_risk))
                c3.metric("Max Fraud Rate",         f"{rdf['fraud_rate'].max():.1f}%")

            st.markdown(f"<br>### {label} Risk Map", unsafe_allow_html=True)
            fig  = go.Figure()
            low  = rdf[rdf["fraud_rate"] <  50]
            high = rdf[rdf["fraud_rate"] >= 50]

            if not low.empty:
                fig.add_trace(go.Scatter(
                    x=low["user_count"], y=low["fraud_rate"], mode="markers",
                    name="Moderate Risk",
                    marker=dict(size=low["tx_count"] / low["tx_count"].max() * 40 + 10,
                                color="#ffb703", opacity=0.8,
                                line=dict(color="#0a0a0f", width=1)),
                    text=low[id_col],
                    hovertemplate="<b>%{text}</b><br>Users: %{x}<br>Fraud: %{y:.1f}%<extra></extra>"
                ))
            if not high.empty:
                fig.add_trace(go.Scatter(
                    x=high["user_count"], y=high["fraud_rate"], mode="markers",
                    name="High Risk",
                    marker=dict(size=high["tx_count"] / rdf["tx_count"].max() * 40 + 12,
                                color="#ff4d6d", opacity=0.9,
                                line=dict(color="#ff9eb5", width=1.5)),
                    text=high[id_col],
                    hovertemplate="<b>%{text}</b><br>Users: %{x}<br>Fraud: %{y:.1f}%<extra></extra>"
                ))
            fig.add_hline(y=50, line_dash="dash", line_color="#6b6b8a",
                annotation_text="50% threshold",
                annotation_font=dict(family="JetBrains Mono", size=10, color="#a0a0c0"))
            fig.update_layout(**PLOT, height=430,
                xaxis_title=f"Users Sharing {label}", yaxis_title="Fraud Rate %",
                legend=dict(font=dict(family="JetBrains Mono", size=11), bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig, use_container_width=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Top Threats — Fraud Rate")
                t15 = rdf.nlargest(15, "fraud_rate")
                fig2 = go.Figure(go.Bar(
                    x=t15["fraud_rate"], y=t15[id_col], orientation="h",
                    marker=dict(color=t15["fraud_rate"], colorscale=CHROMA_THREAT),
                    text=t15["fraud_rate"].apply(lambda x: f"{x:.0f}%"),
                    textfont=dict(family="JetBrains Mono", size=10, color="#fff"),
                    hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>"
                ))
                fig2.update_layout(**PLOT, height=380, xaxis_title="Fraud Rate %")
                st.plotly_chart(fig2, use_container_width=True)

            with c2:
                st.markdown("### Top Threats — Volume")
                t15v = rdf.nlargest(15, "tx_count")
                fig3 = go.Figure(go.Bar(
                    x=t15v["tx_count"], y=t15v[id_col], orientation="h",
                    marker=dict(color=t15v["user_count"], colorscale=CHROMA_OCEAN),
                    text=t15v["tx_count"],
                    textfont=dict(family="JetBrains Mono", size=10, color="#fff"),
                    hovertemplate="<b>%{y}</b><br>%{x} txs<extra></extra>"
                ))
                fig3.update_layout(**PLOT, height=380, xaxis_title="Transaction Count")
                st.plotly_chart(fig3, use_container_width=True)

            st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#1e1e35,transparent);margin:24px 0;'></div>",
                unsafe_allow_html=True)
            st.markdown("### Investigate Ring")
            sel = st.selectbox(f"Select {label}", rdf[id_col].tolist(), key=f"{ring_type}_sel")
            if st.button(f"Investigate {sel}", key=f"{ring_type}_btn"):
                with st.spinner("Querying graph database..."):
                    data = get_ring_transactions(sel)
                if data and data.get("transactions"):
                    txns    = data["transactions"]
                    fraud_n = data.get("fraud_count", 0)
                    total_n = data.get("total", 0)
                    rate    = fraud_n / total_n * 100 if total_n > 0 else 0
                    st.markdown(f"""
                    <div class='ring-alert'>
                        <div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;
                                    color:#ffb703;margin-bottom:8px;">Ring: {sel}</div>
                        <div style="font-family:JetBrains Mono;font-size:0.75rem;color:#e2e2f0;
                                    letter-spacing:0.04em;line-height:1.8;">
                            {total_n} transactions  ·
                            {len(set(t['user_id'] for t in txns))} unique users  ·
                            {fraud_n} fraud cases  ·
                            <span style="color:#ff4d6d;font-weight:600;">{rate:.1f}% fraud rate</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    st.dataframe(pd.DataFrame(txns), use_container_width=True)


# ══════════════════════════════════════════════════════════════
# PAGE 5 — TRANSACTIONS
# ══════════════════════════════════════════════════════════════
elif "Transactions" in page:
    st.markdown("""
    <h1>📋 Transaction Ledger</h1>
    <p style="font-family: JetBrains Mono; font-size: 0.72rem; color: #6b6b8a;
              letter-spacing: 0.08em; margin-bottom: 32px;">
        Full transaction database · 50,000 records
    </p>""", unsafe_allow_html=True)

    all_txns = get_all_transactions()
    if all_txns:
        df = pd.DataFrame(all_txns)
        c1, c2, c3 = st.columns(3)
        with c1:
            fraud_filter = st.selectbox("Filter", ["All", "Fraud Only", "Legitimate Only"])
        with c2:
            search = st.text_input("Search User ID")
        with c3:
            limit = st.slider("Show Rows", 10, 500, 100)

        if fraud_filter == "Fraud Only":
            df = df[df["isFraud"] == True]
        elif fraud_filter == "Legitimate Only":
            df = df[df["isFraud"] == False]
        if search:
            df = df[df["userId"].str.contains(search, na=False)]

        st.markdown(f"""
        <div style="font-family:JetBrains Mono;font-size:0.68rem;color:#6b6b8a;
                    letter-spacing:0.1em;margin:12px 0;padding:10px 14px;
                    background:#0f0f1a;border-radius:6px;border:1px solid #1e1e35;">
            Showing <span style="color:#7c3aff;">{min(limit, len(df)):,}</span>
            of <span style="color:#a0a0c0;">{len(df):,}</span> records
        </div>""", unsafe_allow_html=True)
        st.dataframe(df.head(limit), use_container_width=True)
    else:
        st.error("Spring Boot unreachable on port 8080")


# ══════════════════════════════════════════════════════════════
# PAGE 6 — ANALYTICS
# ══════════════════════════════════════════════════════════════
elif "Analytics" in page:
    st.markdown("""
    <h1>📈 Analytics</h1>
    <p style="font-family: JetBrains Mono; font-size: 0.72rem; color: #6b6b8a;
              letter-spacing: 0.08em; margin-bottom: 32px;">
        Statistical analysis of fraud patterns
    </p>""", unsafe_allow_html=True)

    all_txns = get_all_transactions()
    if all_txns:
        df = pd.DataFrame(all_txns)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Fraud by Day of Week")
            if "dayOfWeek" in df.columns:
                days = {0:"Mon",1:"Tue",2:"Wed",3:"Thu",4:"Fri",5:"Sat",6:"Sun"}
                fdf  = df[df["isFraud"] == True].copy()
                fdf["day"] = fdf["dayOfWeek"].map(days)
                dc = fdf["day"].value_counts().reindex(
                    ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]).fillna(0).reset_index()
                dc.columns = ["day", "count"]
                fig = go.Figure(go.Bar(
                    x=dc["day"], y=dc["count"],
                    marker=dict(color=CAT_COLORS[:7],
                                line=dict(color="rgba(0,0,0,0)", width=0)),
                    hovertemplate="<b>%{x}</b><br>%{y} fraud cases<extra></extra>"
                ))
                fig.update_layout(**PLOT, height=320)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Top Fraud Merchants")
            if "merchantId" in df.columns:
                top_m = (df[df["isFraud"] == True]["merchantId"]
                         .value_counts().head(10).reset_index())
                top_m.columns = ["merchant", "count"]
                fig2 = go.Figure(go.Bar(
                    x=top_m["count"], y=top_m["merchant"], orientation="h",
                    marker=dict(color=CAT_COLORS[:len(top_m)],
                                line=dict(color="rgba(0,0,0,0)", width=0)),
                    hovertemplate="<b>%{y}</b><br>%{x} cases<extra></extra>"
                ))
                fig2.update_layout(**PLOT, height=320)
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### Amount Range vs Fraud Rate")
        if "amount" in df.columns:
            df["amount_bin"] = pd.cut(df["amount"], bins=10)
            bs = df.groupby("amount_bin", observed=True).agg(
                total=("transactionId", "count"),
                fraud=("isFraud", "sum")
            ).reset_index()
            bs["fraud_rate"] = bs["fraud"] / bs["total"] * 100
            bs["range"]      = bs["amount_bin"].astype(str)
            fig3 = go.Figure(go.Bar(
                x=bs["range"], y=bs["fraud_rate"],
                marker=dict(color=bs["fraud_rate"], colorscale=CHROMA_HEAT,
                            line=dict(color="rgba(0,0,0,0)", width=0)),
                hovertemplate="<b>%{x}</b><br>Fraud Rate: %{y:.1f}%<extra></extra>"
            ))
            fig3.update_layout(**PLOT, height=350,
                xaxis_tickangle=40, yaxis_title="Fraud Rate %")
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("### Ring Score Correlation")
        device_rings = get_device_rings(min_users=5, limit=100)
        if device_rings:
            dr_df = pd.DataFrame(device_rings)
            fig4  = go.Figure(go.Scatter(
                x=dr_df["user_count"], y=dr_df["fraud_rate"],
                mode="markers",
                marker=dict(
                    size=dr_df["tx_count"] / dr_df["tx_count"].max() * 35 + 10,
                    color=dr_df["fraud_rate"],
                    colorscale=CHROMA_HEAT,
                    showscale=True,
                    line=dict(color="#1e1e35", width=0.5),
                    colorbar=dict(
                        title=dict(text="Fraud %",
                                   font=dict(family="JetBrains Mono", size=10, color="#6b6b8a")),
                        tickfont=dict(family="JetBrains Mono", size=10, color="#6b6b8a")
                    )
                ),
                text=dr_df["device_id"],
                hovertemplate="<b>%{text}</b><br>Users: %{x}<br>Fraud: %{y:.1f}%<extra></extra>"
            ))
            fig4.add_hline(y=50, line_dash="dash", line_color="#6b6b8a",
                annotation_text="50% threshold",
                annotation_font=dict(family="JetBrains Mono", size=10, color="#a0a0c0"))
            fig4.update_layout(**PLOT, height=440,
                xaxis_title="Users Sharing Device", yaxis_title="Fraud Rate %",
                title=dict(text="More shared users → higher fraud rate",
                           font=dict(family="JetBrains Mono", size=11, color="#6b6b8a")))
            st.plotly_chart(fig4, use_container_width=True)
    else:
        st.error("Spring Boot unreachable on port 8080")