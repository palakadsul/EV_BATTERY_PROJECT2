import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

API = "http://localhost:5000/api"

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EV Battery Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global Theme ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0a0e1a; color: #e8eaf0; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1225 0%, #0a0e1a 100%);
    border-right: 1px solid #1e2640;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p { color: #a0aec0 !important; }

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #ffffff !important;
    letter-spacing: -0.02em;
}

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #111827 0%, #1a2035 100%);
    border: 1px solid #1e2a45;
    border-radius: 14px;
    padding: 20px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    transition: transform 0.2s, box-shadow 0.2s;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(99, 179, 237, 0.15);
    border-color: #2d4a7a;
}
[data-testid="metric-container"] label {
    color: #7c8db5 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e8eaf0 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
}

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #1e2640;
}

.stButton > button {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.02em;
    transition: all 0.2s;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.35);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #06d6a0 0%, #059669 100%) !important;
    box-shadow: 0 4px 15px rgba(6, 214, 160, 0.35) !important;
}

.stSelectbox > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #111827 !important;
    border: 1px solid #1e2a45 !important;
    border-radius: 10px !important;
    color: #e8eaf0 !important;
}
.stSelectbox label, .stTextInput label, .stNumberInput label,
.stSlider label, .stMultiSelect label {
    color: #7c8db5 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
}

.streamlit-expanderHeader {
    background: #111827 !important;
    border: 1px solid #1e2640 !important;
    border-radius: 10px !important;
    color: #a0aec0 !important;
}
.streamlit-expanderContent {
    background: #0d1225 !important;
    border: 1px solid #1e2640 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #111827;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #1e2640;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #7c8db5 !important;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: #2563eb !important;
    color: white !important;
}

hr { border-color: #1e2640 !important; margin: 1.5rem 0 !important; }

[data-testid="stSidebar"] .stRadio > div { gap: 4px; }
[data-testid="stSidebar"] .stRadio label {
    background: #111827;
    border: 1px solid #1e2640;
    border-radius: 8px;
    padding: 8px 12px !important;
    color: #a0aec0 !important;
    transition: all 0.15s;
    font-size: 0.88rem !important;
    cursor: pointer;
}
[data-testid="stSidebar"] .stRadio label:hover {
    border-color: #2563eb;
    color: #63b3ed !important;
}

.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.25rem;
}
.page-subtitle {
    font-size: 0.88rem;
    color: #5a6785;
    margin-bottom: 1.5rem;
    font-weight: 400;
}

.rec-card {
    background: linear-gradient(135deg, #111827 0%, #1a2035 100%);
    border: 1px solid #1e2a45;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 14px;
    transition: all 0.2s;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
.rec-brand { font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700; color:#fff; }
.rec-badge {
    background:rgba(37,99,235,0.2); color:#63b3ed;
    border:1px solid rgba(99,179,237,0.3); border-radius:20px;
    padding:2px 10px; font-size:0.75rem; font-weight:600;
}
.rec-stat { background:#0a0e1a; border-radius:8px; padding:8px 12px; text-align:center; }
.rec-stat-val { font-family:'Syne',sans-serif; font-size:1.05rem; font-weight:700; color:#06d6a0; }
.rec-stat-lbl { font-size:0.72rem; color:#5a6785; text-transform:uppercase; letter-spacing:0.08em; }
.match-badge { font-family:'Syne',sans-serif; font-size:0.78rem; font-weight:600; border-radius:20px; padding:3px 12px; }
.match-high { background:rgba(6,214,160,0.15); color:#06d6a0; border:1px solid rgba(6,214,160,0.3); }
.match-med  { background:rgba(251,191,36,0.15); color:#fbbf24; border:1px solid rgba(251,191,36,0.3); }
.match-low  { background:rgba(239,68,68,0.15);  color:#ef4444; border:1px solid rgba(239,68,68,0.3); }

.login-card {
    background:linear-gradient(135deg,#111827 0%,#1a2035 100%);
    border:1px solid #1e2a45; border-radius:20px;
    padding:40px; box-shadow:0 20px 60px rgba(0,0,0,0.5);
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #1e2a45; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Plotly base theme ────────────────────────────────────────────────────────
CHART_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#a0aec0"),
    title_font=dict(family="Syne", color="#ffffff", size=15),
    xaxis=dict(gridcolor="#1e2640", linecolor="#1e2640", tickfont=dict(color="#5a6785")),
    yaxis=dict(gridcolor="#1e2640", linecolor="#1e2640", tickfont=dict(color="#5a6785")),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#a0aec0")),
    margin=dict(t=50, b=40, l=40, r=20),
)

# CHART_THEME without yaxis — used when we need a custom yaxis / yaxis2
CHART_THEME_NO_YAXIS = {k: v for k, v in CHART_THEME.items() if k != "yaxis"}

# ── Session bootstrap ────────────────────────────────────────────────────────
if "http_session" not in st.session_state:
    st.session_state["http_session"] = requests.Session()

def get_http():
    return st.session_state["http_session"]

def api_get(endpoint):
    try:
        r = get_http().get(f"{API}/{endpoint}")
        if r.status_code == 200:
            return r.json()
        if r.status_code == 401:
            st.error("Session expired — please log in again")
            for k in ["user", "role", "owner_id"]:
                st.session_state.pop(k, None)
            st.rerun()
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None

def api_post(endpoint, data=None):
    try:
        r = get_http().post(f"{API}/{endpoint}", json=data)
        return r
    except Exception as e:
        st.error(f"API error: {e}")
        return None

# ── Auth ─────────────────────────────────────────────────────────────────────
def show_login():
    st.markdown("""
    <div style="text-align:center;padding:3rem 0 2rem 0;">
        <div style="font-family:'Syne',sans-serif;font-size:3rem;font-weight:800;
                    background:linear-gradient(135deg,#2563eb,#06d6a0);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.1;">
            ⚡ EV Battery<br>Intelligence
        </div>
        <p style="color:#5a6785;margin-top:0.75rem;font-size:0.95rem;">
            Fleet monitoring &amp; smart battery analytics
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("<p style='font-family:Syne;font-weight:700;font-size:1.2rem;color:#fff;margin-bottom:1.5rem;'>Sign In</p>", unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        if st.button("Login →", use_container_width=True):
            r = api_post("login", {"username": username, "password": password})
            if r and r.status_code == 200:
                data = r.json()
                st.session_state["user"]     = data["username"]
                st.session_state["role"]     = data["role"]
                st.session_state["owner_id"] = data.get("owner_id")
                st.rerun()
            else:
                msg = "Invalid credentials"
                if r:
                    try: msg = r.json().get("error", msg)
                    except: pass
                st.error(msg)
        with st.expander("Test credentials"):
            st.markdown("""
| Username | Password | Role |
|----------|----------|------|
| `admin`  | `admin123` | Admin |
| `tech1`  | `tech123`  | Technician |
| `amit`   | `test123`  | EV Owner |
| `riya`   | `test123`  | EV Owner |
            """)
        st.markdown('</div>', unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding:16px 8px 8px 8px;">
            <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;
                        background:linear-gradient(135deg,#2563eb,#06d6a0);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                ⚡ EV Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)

        role = st.session_state["role"]
        user = st.session_state["user"]
        role_color = {"admin": "#ef4444", "technician": "#fbbf24", "ev_owner": "#06d6a0"}.get(role, "#7c8db5")
        st.markdown(f"""
        <div style="background:#111827;border:1px solid #1e2640;border-radius:10px;
                    padding:12px 14px;margin:8px 0 16px 0;">
            <div style="font-size:0.78rem;color:#5a6785;text-transform:uppercase;letter-spacing:0.08em;">Logged in as</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;color:#fff;font-size:1rem;">{user}</div>
            <span style="background:rgba(0,0,0,0.3);border:1px solid {role_color}33;
                         color:{role_color};font-size:0.72rem;border-radius:20px;
                         padding:2px 10px;font-weight:600;">{role.upper().replace('_',' ')}</span>
        </div>
        """, unsafe_allow_html=True)

        pages = ["Fleet Overview", "Battery Analysis", "Alerts"]
        if role in ("admin", "technician"):
            pages += ["Owner Analysis", "Car Recommendation", "Maintenance"]
        if role == "admin":
            pages += ["Admin Panel", "ADBMS Features"]
        if role == "ev_owner":
            pages += ["My Vehicle", "Car Recommendation"]

        page = st.radio("Navigate", pages, label_visibility="collapsed")
        st.divider()
        if st.button("Logout", use_container_width=True):
            api_post("logout")
            st.session_state["http_session"] = requests.Session()
            for k in ["user", "role", "owner_id"]:
                st.session_state.pop(k, None)
            st.rerun()
    return page

# ── SOH Gauge ────────────────────────────────────────────────────────────────
def soh_gauge(soh, title="SOH"):
    if soh >= 90: bar_color = "#06d6a0"
    elif soh >= 80: bar_color = "#3b82f6"
    elif soh >= 70: bar_color = "#fbbf24"
    else: bar_color = "#ef4444"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=soh,
        number={"suffix": "%", "font": {"family": "Syne", "color": "#ffffff", "size": 26}},
        title={"text": title, "font": {"family": "Syne", "color": "#a0aec0", "size": 12}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": "#5a6785", "size": 9},
                     "tickcolor": "#1e2640"},
            "bar":  {"color": bar_color, "thickness": 0.7},
            "bgcolor": "#0a0e1a",
            "bordercolor": "#1e2640",
            "steps": [
                {"range": [0, 70],   "color": "rgba(239,68,68,0.08)"},
                {"range": [70, 80],  "color": "rgba(251,191,36,0.08)"},
                {"range": [80, 90],  "color": "rgba(59,130,246,0.08)"},
                {"range": [90, 100], "color": "rgba(6,214,160,0.08)"},
            ],
        }
    ))
    fig.update_layout(
        height=200, margin=dict(t=40, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

# ── Pages ─────────────────────────────────────────────────────────────────────

def page_fleet():
    st.markdown('<div class="page-title">Fleet Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Real-time battery health across your entire fleet</div>', unsafe_allow_html=True)

    data = api_get("fleet-summary")
    if not data:
        st.warning("No data available"); return
    df = pd.DataFrame(data)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Vehicles", len(df))
    c2.metric("Fleet Avg SOH", f"{df['soh'].mean():.1f}%")
    c3.metric("Excellent ≥90%", len(df[df["soh"] >= 90]))
    c4.metric("Warning 70-80%", len(df[(df["soh"] >= 70) & (df["soh"] < 80)]))
    c5.metric("Critical <70%", len(df[df["soh"] < 70]))

    st.divider()

    col_l, col_r = st.columns([1.4, 1])

    with col_l:
        st.markdown("#### Vehicle Health Gauges")
        n = min(len(df), 4)
        cols = st.columns(n)
        for i, row in df.iterrows():
            with cols[i % n]:
                st.plotly_chart(soh_gauge(float(row["soh"]), row["vehicle_number"]),
                                use_container_width=True)

    with col_r:
        st.markdown("#### SOH Distribution")
        labels = ["Excellent\n≥90%", "Good\n80-89%", "Fair\n70-79%", "Critical\n<70%"]
        values = [
            len(df[df["soh"] >= 90]),
            len(df[(df["soh"] >= 80) & (df["soh"] < 90)]),
            len(df[(df["soh"] >= 70) & (df["soh"] < 80)]),
            len(df[df["soh"] < 70]),
        ]
        colors = ["#06d6a0", "#3b82f6", "#fbbf24", "#ef4444"]
        fig_bar = go.Figure(go.Bar(
            x=labels, y=values,
            marker=dict(color=colors, opacity=0.85),
            text=values, textposition="outside",
            textfont=dict(family="Syne", color="#ffffff", size=14),
        ))
        fig_bar.update_layout(**CHART_THEME, height=230, showlegend=False)
        fig_bar.update_yaxes(showgrid=False, showticklabels=False, linecolor="#1e2640")
        fig_bar.update_xaxes(tickfont=dict(size=11, color="#a0aec0"), gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.markdown("#### Fleet Details")
    display_df = df.copy()
    if "soh" in display_df.columns:
        display_df["SOH %"] = display_df["soh"].apply(lambda x: f"{x:.1f}%")
    if "degradation" in display_df.columns:
        display_df["Degradation"] = display_df["degradation"].apply(lambda x: f"{x:.1f}%")
    cols_show = [c for c in ["vehicle_number","model","owner_name","SOH %","Degradation","health_status"] if c in display_df.columns]
    st.dataframe(display_df[cols_show], use_container_width=True, height=280)


def page_battery():
    st.markdown('<div class="page-title">Battery Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Battery health, voltage, temperature and charge levels</div>', unsafe_allow_html=True)

    vehicles = api_get("vehicles")
    if not vehicles:
        st.warning("No vehicles found"); return

    df_v = pd.DataFrame(vehicles)
    vehicle_options = {f"{r['vehicle_number']} — {r['model']}": r["vehicle_id"]
                       for _, r in df_v.iterrows()}
    selected = st.selectbox("Select Vehicle", list(vehicle_options.keys()))
    vid = vehicle_options[selected]

    health   = api_get(f"battery-health/{vid}")
    readings = api_get(f"battery-readings/{vid}")

    # ── Top KPI strip ──────────────────────────────────────────────────────
    if health:
        df_h = pd.DataFrame(health)
        df_h["record_date"] = pd.to_datetime(df_h["record_date"])
        df_h = df_h.sort_values("record_date").reset_index(drop=True)
        latest = df_h.iloc[-1]

        g1, g2, g3, g4, g5 = st.columns([1.2, 1, 1, 1, 1])
        with g1:
            st.plotly_chart(soh_gauge(float(latest["soh"]), "State of Health"),
                            use_container_width=True)
        with g2:
            st.metric("Current SOH", f"{float(latest['soh']):.1f}%")
            st.metric("Degradation", f"{float(latest['degradation']):.1f}%",
                      delta=f"−{float(latest['degradation']):.1f}%", delta_color="inverse")
        if readings:
            dr = pd.DataFrame(readings)
            with g3:
                st.metric("Avg Voltage", f"{dr['voltage'].mean():.2f} V")
                st.metric("Voltage Range", f"{dr['voltage'].min():.1f}–{dr['voltage'].max():.1f} V")
            with g4:
                st.metric("Avg Temperature", f"{dr['temperature'].mean():.1f} °C")
                peak = dr['temperature'].max()
                st.metric("Peak Temperature", f"{peak:.1f} °C",
                          delta="⚠️ High" if peak > 40 else "Normal",
                          delta_color="inverse" if peak > 40 else "normal")
            with g5:
                st.metric("Avg SOC", f"{dr['soc'].mean():.1f}%")
                st.metric("Min SOC Seen", f"{dr['soc'].min():.1f}%",
                          delta="⚠️ Low" if dr['soc'].min() < 20 else "OK",
                          delta_color="inverse" if dr['soc'].min() < 20 else "normal")

    st.divider()

    # ── Prepare readings with clean labels ────────────────────────────────
    df_r = None
    if readings:
        df_r = pd.DataFrame(readings).sort_values("reading_time").reset_index(drop=True)
        df_r["label"] = [f"R{i+1}" for i in range(len(df_r))]

    # ── Row 1: SOH Trend (full width) ─────────────────────────────────────
    if health and not df_h.empty:
        df_h["label"] = [f"Check {i+1}" for i in range(len(df_h))]
        df_h["month"] = df_h["record_date"].dt.strftime("%b %Y")

        fig_soh = go.Figure()
        fig_soh.add_trace(go.Scatter(
            x=df_h["month"], y=df_h["soh"],
            mode="lines+markers+text",
            name="SOH %",
            line=dict(color="#3b82f6", width=3),
            marker=dict(size=10, color="#3b82f6", line=dict(width=2, color="#0a0e1a")),
            text=[f"{v:.1f}%" for v in df_h["soh"]],
            textposition="top center",
            textfont=dict(color="#ffffff", size=11),
            hovertemplate="<b>%{x}</b><br>SOH: %{y:.1f}%<extra></extra>"
        ))
        fig_soh.add_hrect(y0=90, y1=105, fillcolor="rgba(6,214,160,0.06)", line_width=0,
                          annotation_text="Excellent", annotation_font_color="#06d6a0",
                          annotation_font_size=10)
        fig_soh.add_hrect(y0=80, y1=90, fillcolor="rgba(59,130,246,0.06)", line_width=0,
                          annotation_text="Good", annotation_font_color="#3b82f6",
                          annotation_font_size=10)
        fig_soh.add_hline(y=80, line_dash="dash", line_color="#fbbf24", line_width=1.5,
                          annotation_text="⚠ Warning 80%",
                          annotation_font_color="#fbbf24", annotation_font_size=10)
        fig_soh.add_hline(y=70, line_dash="dash", line_color="#ef4444", line_width=1.5,
                          annotation_text="🔴 Critical 70%",
                          annotation_font_color="#ef4444", annotation_font_size=10)
        fig_soh.update_layout(**CHART_THEME, height=300,
                              title="Battery Health (SOH) Over Time",
                              showlegend=False)
        fig_soh.update_yaxes(range=[50, 105], title="SOH (%)",
                             gridcolor="#1e2640", tickfont=dict(color="#5a6785"))
        fig_soh.update_xaxes(tickfont=dict(color="#a0aec0", size=12))
        st.plotly_chart(fig_soh, use_container_width=True)

    st.divider()

    # ── Row 2: Voltage | Temperature ──────────────────────────────────────
    if df_r is not None:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🔌 Voltage per Reading")
            fig_v = go.Figure()
            fig_v.add_trace(go.Bar(
                x=df_r["label"], y=df_r["voltage"],
                name="Voltage",
                marker=dict(color="#3b82f6", opacity=0.85),
                text=[f"{v:.1f}V" for v in df_r["voltage"]],
                textposition="outside",
                textfont=dict(color="#ffffff", size=10),
                hovertemplate="<b>%{x}</b><br>Voltage: %{y:.2f} V<extra></extra>"
            ))
            fig_v.update_layout(**CHART_THEME, height=280,
                                title="Voltage (V)", showlegend=False)
            fig_v.update_yaxes(title="Voltage (V)", gridcolor="#1e2640",
                               tickfont=dict(color="#5a6785"))
            fig_v.update_xaxes(tickfont=dict(color="#a0aec0"))
            st.plotly_chart(fig_v, use_container_width=True)

        with col2:
            st.markdown("#### 🌡️ Temperature per Reading")
            temp_colors = ["#ef4444" if t > 40 else "#f97316" if t > 35 else "#06d6a0"
                           for t in df_r["temperature"]]
            fig_t = go.Figure()
            fig_t.add_trace(go.Bar(
                x=df_r["label"], y=df_r["temperature"],
                name="Temperature",
                marker=dict(color=temp_colors, opacity=0.85),
                text=[f"{v:.1f}°C" for v in df_r["temperature"]],
                textposition="outside",
                textfont=dict(color="#ffffff", size=10),
                hovertemplate="<b>%{x}</b><br>Temp: %{y:.1f} °C<extra></extra>"
            ))
            fig_t.add_hline(y=40, line_dash="dot", line_color="#ef4444", line_width=1.5,
                            annotation_text="⚠ Danger 40°C",
                            annotation_font_color="#ef4444", annotation_font_size=10)
            fig_t.update_layout(**CHART_THEME, height=280,
                                title="Temperature (°C)", showlegend=False)
            fig_t.update_yaxes(title="Temp (°C)", gridcolor="#1e2640",
                               tickfont=dict(color="#5a6785"))
            fig_t.update_xaxes(tickfont=dict(color="#a0aec0"))
            st.plotly_chart(fig_t, use_container_width=True)

    st.divider()

    # ── Row 3: SOC | Current ──────────────────────────────────────────────
    if df_r is not None:
        colA, colB = st.columns(2)

        with colA:
            st.markdown("#### 🔋 State of Charge (SOC)")
            fig_soc = go.Figure()
            fig_soc.add_trace(go.Bar(
                x=df_r["label"], y=df_r["soc"],
                name="SOC %",
                marker=dict(
                    color=["#ef4444" if s < 20 else "#fbbf24" if s < 50 else "#06d6a0"
                           for s in df_r["soc"]],
                    opacity=0.85
                ),
                text=[f"{v:.0f}%" for v in df_r["soc"]],
                textposition="outside",
                textfont=dict(color="#ffffff", size=10),
                hovertemplate="<b>%{x}</b><br>SOC: %{y:.1f}%<extra></extra>"
            ))
            fig_soc.add_hline(y=20, line_dash="dot", line_color="#fbbf24", line_width=1.5,
                              annotation_text="⚠ Low 20%",
                              annotation_font_color="#fbbf24", annotation_font_size=10)
            fig_soc.add_hline(y=80, line_dash="dot", line_color="#3b82f6", line_width=1.5,
                              annotation_text="Optimal 80%",
                              annotation_font_color="#3b82f6", annotation_font_size=10)
            fig_soc.update_layout(**CHART_THEME, height=280,
                                  title="State of Charge (%)", showlegend=False)
            fig_soc.update_yaxes(range=[0, 115], title="SOC (%)",
                                 gridcolor="#1e2640", tickfont=dict(color="#5a6785"))
            fig_soc.update_xaxes(tickfont=dict(color="#a0aec0"))
            st.plotly_chart(fig_soc, use_container_width=True)

        with colB:
            st.markdown("#### ⚡ Current Draw (A)")
            col_name = "current_amp" if "current_amp" in df_r.columns else (
                "current" if "current" in df_r.columns else None)
            if col_name:
                fig_cur = go.Figure()
                fig_cur.add_trace(go.Bar(
                    x=df_r["label"], y=df_r[col_name],
                    name="Current",
                    marker=dict(color="#6366f1", opacity=0.85),
                    text=[f"{v:.1f}A" for v in df_r[col_name]],
                    textposition="outside",
                    textfont=dict(color="#ffffff", size=10),
                    hovertemplate="<b>%{x}</b><br>Current: %{y:.1f} A<extra></extra>"
                ))
                fig_cur.update_layout(**CHART_THEME, height=280,
                                      title="Current Draw (A)", showlegend=False)
                fig_cur.update_yaxes(title="Current (A)", gridcolor="#1e2640",
                                     tickfont=dict(color="#5a6785"))
                fig_cur.update_xaxes(tickfont=dict(color="#a0aec0"))
                st.plotly_chart(fig_cur, use_container_width=True)
            else:
                st.info("No current readings available")

    # ── Raw data table ────────────────────────────────────────────────────
    if readings:
        with st.expander("📋 Raw Sensor Readings"):
            df_show = pd.DataFrame(readings).sort_values("reading_time", ascending=False)
            df_show["reading_time"] = pd.to_datetime(df_show["reading_time"]).dt.strftime("%Y-%m-%d %H:%M:%S")
            cols_show = [c for c in ["reading_time", "voltage", "current_amp", "temperature", "soc"]
                         if c in df_show.columns]
            st.dataframe(df_show[cols_show], use_container_width=True, height=250)

    # ── Admin / Technician Edit Panel ─────────────────────────────────────
    if st.session_state.get("role") in ("admin", "technician"):
        st.divider()
        st.markdown("### ✏️ Update Battery Data")
        st.markdown(
            '<div style="background:#111827;border:1px solid #1e2640;border-radius:16px;padding:24px;">',
            unsafe_allow_html=True
        )

        edit_tab1, edit_tab2 = st.tabs(["Add Health Record", "Add Live Reading"])

        with edit_tab1:
            st.markdown(
                '<div style="color:#7c8db5;font-size:0.85rem;margin-bottom:16px;">'
                'Insert a new SOH / degradation checkpoint for this vehicle.</div>',
                unsafe_allow_html=True
            )
            h_col1, h_col2, h_col3 = st.columns(3)
            with h_col1:
                new_soh = st.number_input(
                    "State of Health (%)", min_value=0.0, max_value=100.0,
                    value=float(latest["soh"]) if health else 85.0,
                    step=0.1, format="%.1f", key="new_soh"
                )
            with h_col2:
                new_deg = st.number_input(
                    "Degradation (%)", min_value=0.0, max_value=100.0,
                    value=float(latest["degradation"]) if health else 5.0,
                    step=0.1, format="%.1f", key="new_deg"
                )
            with h_col3:
                new_date = st.date_input("Record Date", key="new_date")

            if st.button("💾 Save Health Record", type="primary", key="save_health"):
                payload = {
                    "soh":         new_soh,
                    "degradation": new_deg,
                    "record_date": str(new_date),
                }
                r = api_post(f"battery-health/{vid}", payload)
                if r and r.status_code == 201:
                    st.success(f"✅ Health record saved — SOH: {new_soh}%, Degradation: {new_deg}%")
                    st.rerun()
                else:
                    err = r.json().get("error", "Unknown error") if r else "No response"
                    st.error(f"❌ Failed: {err}")

        with edit_tab2:
            st.markdown(
                '<div style="color:#7c8db5;font-size:0.85rem;margin-bottom:16px;">'
                'Log a live sensor snapshot (timestamped to now).</div>',
                unsafe_allow_html=True
            )
            r_col1, r_col2, r_col3, r_col4 = st.columns(4)
            with r_col1:
                new_voltage = st.number_input(
                    "Voltage (V)", min_value=0.0, max_value=500.0,
                    value=float(readings[0]["voltage"]) if readings else 350.0,
                    step=0.1, format="%.1f", key="new_voltage"
                )
            with r_col2:
                new_current = st.number_input(
                    "Current (A)", min_value=-500.0, max_value=500.0,
                    value=float(readings[0].get("current_amp", readings[0].get("current", 0.0))) if readings else 20.0,
                    step=0.1, format="%.1f", key="new_current"
                )
            with r_col3:
                new_temp = st.number_input(
                    "Temperature (°C)", min_value=-20.0, max_value=100.0,
                    value=float(readings[0]["temperature"]) if readings else 28.0,
                    step=0.1, format="%.1f", key="new_temp"
                )
            with r_col4:
                new_soc = st.number_input(
                    "State of Charge (%)", min_value=0.0, max_value=100.0,
                    value=float(readings[0]["soc"]) if readings else 75.0,
                    step=0.1, format="%.1f", key="new_soc"
                )

            if new_temp > 45:
                st.warning(f"⚠️ Temperature {new_temp}°C is dangerously high!")
            if new_soc < 10:
                st.warning(f"⚠️ SOC {new_soc}% is critically low!")

            if st.button("💾 Save Live Reading", type="primary", key="save_reading"):
                payload = {
                    "voltage":     new_voltage,
                    "current":     new_current,
                    "temperature": new_temp,
                    "soc":         new_soc,
                }
                r = api_post(f"battery-readings/{vid}", payload)
                if r and r.status_code == 201:
                    st.success("✅ Live reading logged successfully!")
                    st.rerun()
                else:
                    err = r.json().get("error", "Unknown error") if r else "No response"
                    st.error(f"❌ Failed: {err}")

        st.markdown('</div>', unsafe_allow_html=True)


def page_alerts():
    st.markdown('<div class="page-title">Alerts</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Active warnings and resolved incidents</div>', unsafe_allow_html=True)

    data = api_get("alerts")
    if not data:
        st.info("No alerts"); return

    df = pd.DataFrame(data)
    unresolved = df[df["is_resolved"] == False]
    resolved   = df[df["is_resolved"] == True]

    c1, c2, c3 = st.columns(3)
    c1.metric("Unresolved", len(unresolved))
    c2.metric("Resolved",   len(resolved))
    c3.metric("Total",      len(df))

    tab1, tab2 = st.tabs(["Active Alerts", "Resolved"])

    with tab1:
        if unresolved.empty:
            st.success("No active alerts — fleet is healthy!")
        else:
            for _, row in unresolved.iterrows():
                sev   = str(row.get("severity", "GENERAL")).upper()
                is_crit = "CRITICAL" in sev or row.get("severity") in ("LOW_SOH","HIGH_TEMP")
                border  = "#ef4444" if is_crit else "#fbbf24"
                icon    = "🔴" if is_crit else "🟡"
                st.markdown(f"""
                <div style="background:#111827;border:1px solid {border}33;border-left:3px solid {border};
                            border-radius:10px;padding:14px 18px;margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <span style="font-family:Syne;font-weight:700;color:#fff;">{icon} {row['vehicle_number']}</span>
                            <span style="color:#7c8db5;font-size:0.85rem;margin-left:12px;">{row['alert_message']}</span>
                        </div>
                        <span style="color:#5a6785;font-size:0.78rem;">{row['created_at']}</span>
                    </div>
                    <div style="margin-top:6px;">
                        <span style="background:rgba(0,0,0,0.3);color:{border};font-size:0.72rem;
                                     border-radius:20px;padding:2px 10px;border:1px solid {border}44;">{sev}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.session_state["role"] in ("admin", "technician"):
                    if st.button("Mark Resolved", key=f"res_{row['alert_id']}"):
                        api_post(f"alerts/{row['alert_id']}/resolve")
                        st.rerun()

    with tab2:
        if resolved.empty:
            st.info("No resolved alerts yet")
        else:
            st.dataframe(resolved[["vehicle_number","alert_message","severity","created_at"]],
                         use_container_width=True, height=350)


def page_owner_analysis():
    st.markdown('<div class="page-title">Owner Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Per-owner battery trends and charging behaviour</div>', unsafe_allow_html=True)

    owners = api_get("owners")
    if not owners:
        st.warning("No owners found"); return

    df_o = pd.DataFrame(owners)
    owner_options = {r["owner_name"]: r["owner_id"] for _, r in df_o.iterrows()}
    selected = st.selectbox("Select Owner", list(owner_options.keys()))
    oid = owner_options[selected]

    data = api_get(f"owner-analysis/{oid}")
    if not data:
        st.warning("No analysis data available"); return

    col1, col2 = st.columns(2)

    with col1:
        if data.get("battery_trend"):
            df_bt = pd.DataFrame(data["battery_trend"])
            df_bt["record_date"] = pd.to_datetime(df_bt["record_date"])
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_bt["record_date"], y=df_bt["soh"],
                mode="lines", name="Actual SOH",
                line=dict(color="#3b82f6", width=2),
                fill="tozeroy", fillcolor="rgba(59,130,246,0.06)",
            ))
            fig.add_trace(go.Scatter(
                x=df_bt["record_date"], y=df_bt["soh_moving_avg"],
                mode="lines", name="3-pt Moving Avg",
                line=dict(color="#ef4444", width=2, dash="dot"),
            ))
            fig.add_hline(y=80, line_dash="dash", line_color="#fbbf24",
                          annotation_text="Warning 80%", annotation_font_color="#fbbf24", annotation_font_size=10)
            fig.update_layout(**CHART_THEME, height=320, title=f"Battery Health Trend — {selected}")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        dist = data.get("health_distribution", {})
        if dist:
            labels = ["Excellent (≥90)", "Good (80-89)", "Fair (70-79)", "Critical (<70)"]
            values = [dist.get("excellent",0), dist.get("good",0),
                      dist.get("fair",0), dist.get("critical",0)]
            fig3 = go.Figure(go.Pie(
                labels=labels, values=values,
                marker=dict(colors=["#06d6a0","#3b82f6","#fbbf24","#ef4444"],
                            line=dict(color="#0a0e1a", width=2)),
                hole=0.55,
                textinfo="label+percent",
                textfont=dict(family="DM Sans", size=12, color="#a0aec0"),
            ))
            fig3.update_layout(**CHART_THEME, height=320, title="Health Distribution", showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)

    if data.get("charging_stats"):
        df_cs = pd.DataFrame(data["charging_stats"])
        if not df_cs.empty:
            st.markdown("#### Charging Session Breakdown")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(name="Fast Charge", x=df_cs["vehicle_number"],
                                  y=df_cs["fast_charge_count"], marker_color="#3b82f6", marker_opacity=0.85))
            fig2.add_trace(go.Bar(name="Slow Charge", x=df_cs["vehicle_number"],
                                  y=df_cs["slow_charge_count"], marker_color="#06d6a0", marker_opacity=0.85))
            fig2.update_layout(**CHART_THEME, height=260, barmode="group", title="Charging Sessions by Type")
            st.plotly_chart(fig2, use_container_width=True)


def page_recommendation():
    st.markdown('<div class="page-title">Car Recommendation</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Personalised EV upgrade suggestions based on battery health &amp; your preferences</div>', unsafe_allow_html=True)

    vehicles = api_get("vehicles")
    if not vehicles:
        st.warning("No vehicles found"); return

    df_v = pd.DataFrame(vehicles)
    vehicle_options = {f"{r['vehicle_number']} — {r['model']}": r["vehicle_id"]
                       for _, r in df_v.iterrows()}

    # ── Input Panel ──────────────────────────────────────────────────────────
    st.markdown("### Your Preferences")
    st.markdown('<div style="background:#111827;border:1px solid #1e2640;border-radius:16px;padding:24px;">', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        selected_v = st.selectbox("Vehicle to Analyse", list(vehicle_options.keys()))
        vid = vehicle_options[selected_v]

        budget_lakh = st.slider(
            "Max Budget (₹ Lakhs)", min_value=5, max_value=100, value=40, step=5,
            help="Maximum price you're willing to pay for a new EV"
        )
        daily_km = st.slider(
            "Daily Drive (km)", min_value=10, max_value=300, value=60, step=10,
            help="How many kilometres you typically drive per day"
        )

    with col_b:
        use_case = st.selectbox(
            "Primary Use Case",
            ["City Commuting", "Highway / Long Distance", "Mixed Use", "Ride Sharing / Commercial"],
        )
        charging_pref = st.selectbox(
            "Preferred Charging",
            ["Fast Charge (DC)", "Slow / Home Charge (AC)", "No Preference"],
            index=2
        )
        priority = st.selectbox(
            "Top Priority",
            ["Max Range", "Low Price", "Large Battery Capacity", "Brand Reputation"],
        )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    if st.button("Get My Recommendation", type="primary", use_container_width=True):
        with st.spinner("Analysing battery health and matching cars..."):
            prefs_payload = {
                "budget_inr":    budget_lakh * 100_000,
                "daily_km":      daily_km,
                "use_case":      use_case,
                "charging_pref": charging_pref,
                "priority":      priority,
            }
            r = api_post(f"recommend/{vid}", prefs_payload)
            data = r.json() if r and r.status_code == 200 else None

        if not data:
            st.error("Could not fetch recommendation"); return

        soh         = data["current_soh"]
        degradation = data["degradation"]
        fast_pct    = data["fast_charge_pct"]
        urgency     = data["upgrade_urgency"]

        urgency_clr = {"Critical": "#ef4444", "High": "#fbbf24", "Low": "#06d6a0"}.get(urgency, "#06d6a0")
        urgency_ico = {"Critical": "🔴", "High": "🟡", "Low": "🟢"}.get(urgency, "🟢")

        st.divider()
        st.markdown("### Current Battery Status")

        m1, m2, m3, m4 = st.columns(4)
        m1.plotly_chart(soh_gauge(soh, "SOH"), use_container_width=True)
        m2.metric("State of Health", f"{soh:.1f}%",
                  delta=f"-{degradation:.1f}% degraded", delta_color="inverse")
        m3.metric("Fast Charge Usage", f"{fast_pct:.0f}%",
                  delta="Accelerates wear" if fast_pct > 60 else "Acceptable",
                  delta_color="inverse" if fast_pct > 60 else "normal")
        m4.markdown(f"""
        <div style="background:#111827;border:1px solid #1e2640;border-radius:12px;
                    padding:20px;text-align:center;min-height:150px;
                    display:flex;flex-direction:column;justify-content:center;align-items:center;">
            <div style="font-size:0.72rem;color:#5a6785;text-transform:uppercase;
                        letter-spacing:0.1em;margin-bottom:8px;">UPGRADE URGENCY</div>
            <div style="font-family:Syne;font-size:1.9rem;font-weight:800;color:{urgency_clr};">
                {urgency_ico} {urgency}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Why This Recommendation?")
        for reason in data["reasons"]:
            st.markdown(f"""
            <div style="background:#111827;border:1px solid #1e2640;border-left:3px solid #3b82f6;
                        border-radius:8px;padding:12px 16px;margin-bottom:8px;
                        color:#a0aec0;font-size:0.9rem;">
                ℹ️ {reason}
            </div>
            """, unsafe_allow_html=True)

        # ── Preference summary banner ──
        budget_inr      = budget_lakh * 100000
        min_range_needed = daily_km * 2

        st.markdown(f"""
        <div style="background:rgba(37,99,235,0.08);border:1px solid rgba(37,99,235,0.25);
                    border-radius:10px;padding:14px 18px;margin:16px 0;font-size:0.88rem;color:#a0aec0;">
            🎯 <b style="color:#fff;">Filters applied:</b>
            Budget ≤ ₹{budget_lakh}L &nbsp;·&nbsp;
            Daily {daily_km} km (need {min_range_needed} km range) &nbsp;·&nbsp;
            {use_case} &nbsp;·&nbsp;
            Priority: {priority}
        </div>
        """, unsafe_allow_html=True)

        if data.get("recommendations"):
            st.markdown("### Matched EVs For You")

            for car in data["recommendations"]:
                price    = float(car["price_inr"])
                range_km = float(car["range_km"])
                cap      = float(car["battery_capacity_kwh"])

                score = 0
                if price <= budget_inr: score += 1
                if range_km >= min_range_needed: score += 1
                if priority == "Max Range" and range_km >= min_range_needed * 1.5: score += 1
                if priority == "Low Price" and price <= budget_inr * 0.7: score += 1
                if priority == "Large Battery Capacity" and cap >= 60: score += 1

                if score >= 3:   match_cls, match_txt = "match-high", "Great Match"
                elif score >= 2: match_cls, match_txt = "match-med",  "Good Match"
                else:            match_cls, match_txt = "match-low",  "Partial Match"

                fits_budget = price <= budget_inr
                fits_range  = range_km >= min_range_needed

                st.markdown(f"""
                <div class="rec-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;flex-wrap:wrap;gap:8px;">
                        <div>
                            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                                <span class="rec-brand">{car['brand']} {car['car_name']}</span>
                                <span class="rec-badge">{car['category']}</span>
                                <span class="match-badge {match_cls}">{match_txt}</span>
                            </div>
                            <div style="color:#5a6785;font-size:0.83rem;margin-top:4px;">
                                {str(car.get('charge_type_supported','')).title()} Charging
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-family:Syne;font-size:1.3rem;font-weight:800;color:#fff;">
                                ₹{price/100000:.1f}L
                            </div>
                            <div style="font-size:0.75rem;color:{'#06d6a0' if fits_budget else '#ef4444'};">
                                {'✓ Within budget' if fits_budget else '✗ Over budget'}
                            </div>
                        </div>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
                        <div class="rec-stat">
                            <div class="rec-stat-val">{range_km:.0f} km</div>
                            <div class="rec-stat-lbl">Range</div>
                        </div>
                        <div class="rec-stat">
                            <div class="rec-stat-val">{cap:.0f} kWh</div>
                            <div class="rec-stat-lbl">Battery</div>
                        </div>
                        <div class="rec-stat">
                            <div class="rec-stat-val" style="color:{'#06d6a0' if fits_range else '#fbbf24'};">
                                {'✓' if fits_range else '~'} {min_range_needed} km
                            </div>
                            <div class="rec-stat-lbl">Range needed</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(6,214,160,0.1);border:1px solid rgba(6,214,160,0.3);
                        border-radius:12px;padding:20px 24px;text-align:center;">
                <div style="font-family:Syne;font-size:1.1rem;font-weight:700;color:#06d6a0;">
                    ✅ No Upgrade Needed
                </div>
                <div style="color:#7c8db5;margin-top:6px;">
                    Your current battery health is excellent. Keep monitoring regularly.
                </div>
            </div>
            """, unsafe_allow_html=True)


def page_my_vehicle():
    st.markdown('<div class="page-title">My Vehicle</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Your personal EV battery health dashboard</div>', unsafe_allow_html=True)

    vehicles = api_get("vehicles")
    if not vehicles:
        st.warning("No vehicle found"); return

    for v in vehicles:
        st.markdown(f"#### {v['vehicle_number']} — {v['model']}")
        health = api_get(f"battery-health/{v['vehicle_id']}")
        if health:
            df_h = pd.DataFrame(health)
            df_h["record_date"] = pd.to_datetime(df_h["record_date"])
            latest = df_h.iloc[-1]

            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(soh_gauge(float(latest["soh"]), "State of Health"), use_container_width=True)
                mx, my = st.columns(2)
                mx.metric("SOH", f"{float(latest['soh']):.1f}%")
                my.metric("Degradation", f"{float(latest['degradation']):.1f}%")
            with c2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_h["record_date"], y=df_h["soh"],
                    mode="lines+markers", name="SOH",
                    line=dict(color="#3b82f6", width=2.5),
                    fill="tozeroy", fillcolor="rgba(59,130,246,0.07)",
                    marker=dict(size=5)
                ))
                fig.add_hline(y=80, line_dash="dash", line_color="#fbbf24",
                              annotation_text="Warning", annotation_font_color="#fbbf24", annotation_font_size=10)
                fig.add_hline(y=70, line_dash="dash", line_color="#ef4444",
                              annotation_text="Critical", annotation_font_color="#ef4444", annotation_font_size=10)
                fig.update_layout(**CHART_THEME, height=280, title="SOH History")
                fig.update_yaxes(range=[50, 105])
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No health records for {v['vehicle_number']}")
        st.divider()


def page_maintenance():
    st.markdown('<div class="page-title">Maintenance Schedule</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Scheduled and completed service records</div>', unsafe_allow_html=True)

    data = api_get("maintenance")
    if not data:
        st.info("No maintenance records")
        return

    df = pd.DataFrame(data)
    if "is_completed" in df.columns:
        df["is_completed"] = df["is_completed"].astype(bool)
        pending   = df[~df["is_completed"]]
        completed = df[df["is_completed"]]
    else:
        pending, completed = df, pd.DataFrame()

    c1, c2 = st.columns(2)
    c1.metric("Pending Services", len(pending))
    c2.metric("Completed",        len(completed))

    tab1, tab2 = st.tabs(["Pending", "Completed"])

    def _render_card(row, show_action=False):
        mid          = row.get("maintenance_id", "")
        vehicle      = row.get("vehicle_number", "—")
        reason       = row.get("reason", "—")
        sched        = str(row.get("scheduled_date", "—"))[:10]
        created      = str(row.get("created_at", "—"))[:10]
        done         = bool(row.get("is_completed", False))
        status_color = "#06d6a0" if done else "#fbbf24"
        status_label = "Completed" if done else "Pending"

        st.markdown(f"""
        <div style="background:#111827;border:1px solid #1e2640;border-left:3px solid {status_color};
                    border-radius:12px;padding:16px 20px;margin-bottom:10px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                <div>
                    <span style="font-family:Syne;font-weight:700;color:#fff;font-size:1rem;">
                        Vehicle: {vehicle}
                    </span>
                    <span style="background:rgba(0,0,0,0.35);color:{status_color};font-size:0.72rem;
                                 border-radius:20px;padding:2px 10px;border:1px solid {status_color}44;
                                 margin-left:10px;font-weight:600;">{"✓ " if done else "⏳ "}{status_label}</span>
                </div>
                <span style="color:#5a6785;font-size:0.78rem;">ID #{mid}</span>
            </div>
            <div style="color:#a0aec0;font-size:0.88rem;margin-top:8px;">{reason}</div>
            <div style="display:flex;gap:24px;margin-top:10px;font-size:0.8rem;color:#5a6785;">
                <span>Scheduled: <b style="color:#7c8db5;">{sched}</b></span>
                <span>Created: <b style="color:#7c8db5;">{created}</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if show_action and st.session_state.get("role") in ("admin", "technician"):
            if st.button("Mark Complete", key=f"maint_{mid}", type="primary"):
                r = api_post(f"maintenance/{mid}/complete")
                if r and r.status_code == 200:
                    st.success("Marked as complete!")
                    st.rerun()
                else:
                    st.error("Could not update — check the backend route exists.")

    with tab1:
        if pending.empty:
            st.success("No pending maintenance — fleet is in great shape!")
        else:
            for _, row in pending.iterrows():
                _render_card(row, show_action=True)

    with tab2:
        if completed.empty:
            st.info("No completed records yet")
        else:
            for _, row in completed.iterrows():
                _render_card(row, show_action=False)


def page_admin():
    st.markdown('<div class="page-title">Admin Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">User management and system audit trail</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Users", "Audit Trail"])
    with tab1:
        users = api_get("admin/users")
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True)
    with tab2:
        audit = api_get("admin/audit-trail")
        if audit:
            st.dataframe(pd.DataFrame(audit), use_container_width=True)
        else:
            st.info("No audit records yet")


def page_adbms():
    st.markdown('<div class="page-title">ADBMS Features</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Advanced database concepts powering this project</div>', unsafe_allow_html=True)

    features = [
        ("Partitioning",       "battery_readings partitioned by reading_time (quarterly range)", "🗂️"),
        ("Triggers",           "fn_battery_health_alert() fires on INSERT/UPDATE — auto-generates alerts", "⚡"),
        ("Auto-Maintenance",   "fn_auto_maintenance() schedules service when SOH < 80%", "🔧"),
        ("Row-Level Security", "Owners see only their own vehicles via RLS policy", "🔒"),
        ("RBAC",               "3 roles: admin_role, technician_role, ev_owner_role with column-level grants", "👥"),
        ("Materialized View",  "mv_fleet_health_summary — pre-aggregated for fast fleet queries", "📊"),
        ("Window Functions",   "AVG(soh) OVER (PARTITION BY vehicle_id ... ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)", "📈"),
        ("Partial Indexes",    "Index on unresolved alerts + descending index on reading_time", "⚙️"),
        ("XML/XPath",          "battery_xml_reports table with XPath queries for structured reports", "📄"),
        ("Audit Trail",        "INSERT/UPDATE operations logged via trigger to audit_trail", "📝"),
        ("pgcrypto",           "Passwords hashed with crypt() + gen_salt('bf')", "🔐"),
    ]

    cols = st.columns(2)
    for i, (feat, desc, icon) in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:#111827;border:1px solid #1e2640;border-radius:12px;
                        padding:14px 18px;margin-bottom:10px;">
                <div style="font-family:Syne;font-weight:700;color:#fff;font-size:0.95rem;">{icon} {feat}</div>
                <div style="color:#7c8db5;font-size:0.83rem;margin-top:4px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("#### Window Function — SOH Moving Average")
    st.code("""
SELECT bh.record_date, bh.soh,
       AVG(bh.soh) OVER (
           PARTITION BY bh.vehicle_id
           ORDER BY bh.record_date
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       ) AS soh_moving_avg
FROM battery_health bh
JOIN vehicles v ON bh.vehicle_id = v.vehicle_id
WHERE v.owner_id = :owner_id;
    """, language="sql")

    st.markdown("#### Car Recommendation SQL Rule Engine")
    st.code("""
SELECT car_name, brand, range_km, battery_capacity_kwh
FROM car_catalog
WHERE battery_capacity_kwh >= :min_capacity
  AND (charge_type_supported = 'both' OR charge_type_supported = :preferred_charge)
ORDER BY
  CASE WHEN :soh < 70 THEN battery_capacity_kwh END DESC NULLS LAST,
  range_km DESC
LIMIT 3;
    """, language="sql")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if "user" not in st.session_state:
        show_login()
        return

    page = sidebar()

    dispatch = {
        "Fleet Overview":     page_fleet,
        "Battery Analysis":   page_battery,
        "Alerts":             page_alerts,
        "Owner Analysis":     page_owner_analysis,
        "Car Recommendation": page_recommendation,
        "My Vehicle":         page_my_vehicle,
        "Maintenance":        page_maintenance,
        "Admin Panel":        page_admin,
        "ADBMS Features":     page_adbms,
    }

    fn = dispatch.get(page)
    if fn:
        fn()

if __name__ == "__main__":
    main()