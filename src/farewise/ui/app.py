from __future__ import annotations

import base64
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from farewise.service.advise_service import advise_route
from farewise.service.data_service import fare_curves, get_data, route_summary
from farewise.service.deal_service import check_quote
from farewise.service.predict_service import FareQuery, predict_fare

st.set_page_config(
    page_title="FareWise | Flight fare intelligence",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)


PAGES = {
    "Overview": ("Your next trip,\nwith more clarity.", "Understand fare patterns before you book."),
    "Fare estimate": ("A clearer view of\nyour fare range.", "Compare an itinerary with observed fares for similar trips."),
    "Book or wait": ("Make the timing\nfeel less uncertain.", "Review historical signals for booking now or waiting."),
    "Quote check": ("Know where your\nquote stands.", "See how a quoted fare compares with the available history."),
    "Route explorer": ("Explore the route\nbefore you go.", "Compare route coverage and fare movement across booking horizons."),
    "Model & evidence": ("See the evidence\nbehind the estimate.", "Validation results, limits, and model notes."),
    "About": ("Built for thoughtful\ntravel decisions.", "An educational fare analysis tool, not a live price feed."),
}
PAGE_NAMES = list(PAGES)


@st.cache_data(show_spinner=False)
def _hero_image_data() -> str:
    path = Path(__file__).parent / "assets" / "airport-hero.png"
    return base64.b64encode(path.read_bytes()).decode("ascii")


def _inject_styles() -> None:
    image_data = _hero_image_data()
    st.markdown(
        f"""
        <style>
        :root {{ --ink:#172b46; --muted:#6e7c91; --blue:#2158a5; --blue-dark:#14396c; --gold:#e9b766; --line:#e5ebf2; }}
        html, body, [class*="css"] {{ font-family:'Segoe UI',Arial,sans-serif; }}
        .stApp {{ background:#f3f6fa; color:var(--ink); }}
        [data-testid="stHeader"] {{ background:transparent; }}
        [data-testid="stSidebar"] {{ background:linear-gradient(180deg,#12233b 0%,#182e4b 100%); border-right:1px solid rgba(255,255,255,.08); }}
        [data-testid="stSidebar"] * {{ color:#eaf1fb; }}
        [data-testid="stSidebar"] [data-testid="stRadio"] label {{ border-radius:9px; padding:8px 10px; }}
        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{ background:rgba(255,255,255,.08); }}
        [data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] + div {{ color:#fff; }}
        [data-testid="stSidebar"] hr {{ border-color:rgba(255,255,255,.14); }}
        .block-container {{ max-width:1380px; padding-top:1.5rem; padding-bottom:3rem; }}
        h1,h2,h3 {{ color:var(--ink); font-family:'Segoe UI',Arial,sans-serif; letter-spacing:-.035em; }}
        h2 {{ font-size:1.42rem !important; }}
        p,li {{ color:#52637a; }}
        .brand-lockup {{ display:flex; align-items:center; gap:11px; padding:8px 2px 22px; }}
        .brand-mark {{ width:40px; height:40px; border-radius:13px; display:grid; place-items:center; background:linear-gradient(135deg,#eabb71,#f5d8a0); color:#152a45; font-size:20px; box-shadow:0 8px 18px rgba(0,0,0,.18); }}
        .brand-name {{ font-family:'Segoe UI',Arial,sans-serif; font-size:20px; font-weight:800; letter-spacing:-.7px; color:#fff; }}
        .brand-sub {{ font-size:10px; letter-spacing:1.6px; text-transform:uppercase; color:#9fb1c9; }}
        .sidebar-label {{ color:#91a6c2; font-size:10px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; padding:0 0 7px 10px; }}
        .source-pill {{ margin-top:16px; display:inline-flex; align-items:center; gap:8px; padding:7px 11px; border-radius:999px; background:rgba(255,255,255,.09); color:#eaf1fb; font-size:11px; }}
        .source-dot {{ width:7px; height:7px; border-radius:50%; background:#eabb71; display:inline-block; }}
        .hero {{ min-height:268px; padding:35px 42px; display:flex; flex-direction:column; justify-content:center; border-radius:22px; overflow:hidden; background-image:linear-gradient(90deg,rgba(11,29,51,.94) 0%,rgba(14,36,61,.82) 42%,rgba(14,36,61,.16) 100%),url('data:image/png;base64,{image_data}'); background-position:center 48%; background-size:cover; box-shadow:0 18px 42px rgba(18,42,72,.14); margin:0 0 26px; }}
        .hero-kicker {{ color:#f2c982; text-transform:uppercase; letter-spacing:2px; font-size:10px; font-weight:700; margin-bottom:10px; }}
        .hero-title {{ font-family:'Segoe UI',Arial,sans-serif; color:#fff; white-space:pre-line; font-size:clamp(31px,4vw,49px); line-height:1.08; font-weight:800; letter-spacing:-1.7px; max-width:590px; }}
        .hero-copy {{ margin-top:12px; color:rgba(239,245,252,.86); font-size:14px; max-width:480px; }}
        .section-eyebrow {{ color:#8b99ac; font-size:10px; text-transform:uppercase; letter-spacing:1.6px; font-weight:700; margin-bottom:5px; }}
        .surface {{ background:#fff; border:1px solid var(--line); border-radius:16px; padding:19px 21px; box-shadow:0 5px 18px rgba(24,48,78,.045); }}
        .metric-card {{ background:#fff; border:1px solid var(--line); border-radius:15px; padding:17px 19px; min-height:105px; box-shadow:0 5px 18px rgba(24,48,78,.04); }}
        .metric-label {{ color:#7b899c; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.2px; }}
        .metric-value {{ font-family:'Segoe UI',Arial,sans-serif; color:#172b46; font-size:25px; font-weight:800; margin-top:6px; letter-spacing:-.7px; }}
        .metric-note {{ color:#8995a6; font-size:11px; margin-top:2px; }}
        .soft-note {{ color:#728198; font-size:12px; }}
        .result-banner {{ border-radius:14px; padding:17px 19px; margin:6px 0 16px; background:#eaf2fb; border:1px solid #d9e6f6; }}
        .result-banner.success {{ background:#eaf5ef; border-color:#d4eadc; }}
        .result-banner.warn {{ background:#fff5e7; border-color:#f3dfbc; }}
        .result-title {{ font-family:'Segoe UI',Arial,sans-serif; font-size:20px; font-weight:800; color:#183657; }}
        .result-copy {{ font-size:12px; color:#62738a; margin-top:4px; }}
        div.stButton > button {{ border-radius:10px; min-height:43px; font-weight:700; border:1px solid #d7e1ed; }}
        div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {{ background:linear-gradient(135deg,#245da9,#17457f); border:0; color:#fff; box-shadow:0 7px 17px rgba(33,88,165,.18); }}
        div.stButton > button:hover {{ border-color:#8ba9cf; color:#17457f; }}
        div.stFormSubmitButton > button {{ border-radius:10px; min-height:46px; font-weight:700; }}
        [data-testid="stMetric"] {{ background:#fff; border:1px solid var(--line); border-radius:14px; padding:14px 17px; box-shadow:0 5px 18px rgba(24,48,78,.04); }}
        [data-testid="stMetricLabel"] p {{ color:#718097; font-size:11px; text-transform:uppercase; letter-spacing:1px; }}
        [data-testid="stMetricValue"] {{ color:#17365a; font-family:'Segoe UI',Arial,sans-serif; }}
        [data-testid="stDataFrame"] {{ border:1px solid var(--line); border-radius:12px; overflow:hidden; }}
        [data-testid="stPlotlyChart"] {{ background:#fff; border:1px solid var(--line); border-radius:15px; padding:8px; }}
        div[data-testid="stSelectbox"] label, div[data-testid="stSlider"] label, div[data-testid="stNumberInput"] label {{ color:#52637a; font-weight:600; }}
        [data-testid="stForm"] {{ border:0; padding:0; }}
        .footer {{ color:#94a0af; font-size:11px; border-top:1px solid #e2e8f0; padding-top:16px; margin-top:36px; }}
        @media(max-width:800px) {{ .hero {{ min-height:230px; padding:26px 23px; background-position:62% center; }} .block-container {{ padding-top:1rem; }} }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _hero(page: str) -> None:
    title, copy = PAGES[page]
    st.markdown(
        f"""<section class="hero"><div class="hero-kicker">FareWise &nbsp;·&nbsp; Flight fare intelligence</div>
        <div class="hero-title">{title}</div><div class="hero-copy">{copy}</div></section>""",
        unsafe_allow_html=True,
    )


def _metric_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def _show_drivers(drivers: list[dict[str, object]] | None) -> None:
    if not drivers:
        return
    st.markdown("#### What shaped this result")
    st.caption("Observed historical patterns only; these are not causal effects or live market signals.")
    st.dataframe(pd.DataFrame(drivers), hide_index=True, use_container_width=True)


def _query_form(page: str) -> tuple[FareQuery | None, float | None, bool]:
    cities = sorted(data.source_city.unique())
    classes = sorted(data["class"].unique())
    with st.container(border=True):
        st.markdown('<div class="section-eyebrow">Trip details</div>', unsafe_allow_html=True)
        st.subheader("Set up your search")
        with st.form(f"farewise-{page}"):
            first, second = st.columns(2)
            source = first.selectbox("From", cities, key=f"{page}-source")
            destinations = [city for city in cities if city != source]
            destination = second.selectbox("To", destinations, key=f"{page}-destination")
            third, fourth = st.columns(2)
            fare_class = third.selectbox("Cabin class", classes, key=f"{page}-class")
            max_days = max(1, min(365, int(data.days_left.max())))
            days_left = fourth.slider(
                "Days until departure",
                min_value=1,
                max_value=max_days,
                value=min(14, max_days),
                key=f"{page}-days",
            )
            quote = None
            if page in {"Book or wait", "Quote check"}:
                quote = st.number_input(
                    "Your quoted fare (₹)",
                    min_value=1.0,
                    value=6000.0,
                    step=250.0,
                    key=f"{page}-quote",
                )
            submitted = st.form_submit_button("Analyze itinerary  →", type="primary", use_container_width=True)
    query = FareQuery(source=source, destination=destination, days_left=days_left, fare_class=fare_class)
    return query, quote, submitted


def _show_fare_estimate(query: FareQuery, page: str) -> None:
    result_key = "result-Fare estimate"
    query_key = "query-Fare estimate"
    if st.session_state.get("submit-Fare estimate"):
        st.session_state[result_key] = predict_fare(data, query)
        st.session_state[query_key] = query
        st.session_state["submit-Fare estimate"] = False
    result = st.session_state.get(result_key)
    if not result:
        st.info("Choose a route and submit to see a historically informed fare estimate.")
        return
    if not result.get("available"):
        st.warning(result.get("message", "There is not enough data for this estimate."))
        return
    st.markdown("### Estimated fare range")
    low, typical, high = st.columns(3)
    low.metric("Lower range · P10", f"₹{result['p10']:,.0f}")
    typical.metric("Typical fare · P50", f"₹{result['p50']:,.0f}")
    high.metric("Upper range · P90", f"₹{result['p90']:,.0f}")
    st.markdown(
        f'<div class="result-banner"><div class="result-title">{result.get("method", "Historical fare estimate")}</div>'
        f'<div class="result-copy">Based on {result["rows"]:,} nearby observations from {source_label}. This is historical analysis, not a live quote.</div></div>',
        unsafe_allow_html=True,
    )
    _show_drivers(result.get("drivers"))


def _show_advice(query: FareQuery, quote: float) -> None:
    key = "result-Book or wait"
    if st.session_state.get("submit-Book or wait"):
        st.session_state[key] = advise_route(data, query, quote)
        st.session_state["submit-Book or wait"] = False
    result = st.session_state.get(key)
    if not result:
        st.info("Enter a current quote to compare it with historical booking patterns.")
        return
    if result.get("limitation"):
        st.warning(result["limitation"])
        return
    action = str(result.get("action", "REVIEW"))
    style = "success" if action.startswith("WAIT") else "warn" if action == "BOOK NOW" else ""
    st.markdown(
        f'<div class="result-banner {style}"><div class="section-eyebrow">Historical decision signal</div>'
        f'<div class="result-title">{action.title()}</div>'
        '<div class="result-copy">A descriptive signal from observed fares. It cannot predict live price changes.</div></div>',
        unsafe_allow_html=True,
    )
    a, b, c = st.columns(3)
    a.metric("Expected saving", f"₹{result.get('expected_saving_inr', 0):,.0f}", f"{result.get('expected_saving_percent', 0):.1f}%")
    b.metric("Historical rise chance", f"{result.get('rise_probability', 0):.0%}")
    c.metric("Comparable observations", f"{result.get('data_rows', 0):,}")
    st.caption(f"Historical range: ₹{result.get('p10', 0):,.0f}–₹{result.get('p90', 0):,.0f}. Source: {source_label}.")
    _show_drivers(result.get("drivers"))


def _show_quote(query: FareQuery, quote: float) -> None:
    key = "result-Quote check"
    if st.session_state.get("submit-Quote check"):
        st.session_state[key] = check_quote(data, query, quote)
        st.session_state["submit-Quote check"] = False
    result = st.session_state.get(key)
    if not result:
        st.info("Enter a quote to see how it compares with fares for this route and class.")
        return
    if not result.get("available"):
        st.warning(result.get("message", "There is not enough route history."))
        return
    label = str(result.get("label", "Historical comparison"))
    style = "success" if label == "Great deal" else "warn" if label in {"Above expected", "Overpriced"} else ""
    st.markdown(
        f'<div class="result-banner {style}"><div class="section-eyebrow">Your quote</div>'
        f'<div class="result-title">{label}</div><div class="result-copy">Your quote is at the {result["percentile"]:.0f}th percentile of available route history.</div></div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Historical P10", f"₹{result['p10']:,.0f}")
    c2.metric("Historical median", f"₹{result['p50']:,.0f}")
    c3.metric("Historical P90", f"₹{result['p90']:,.0f}")
    _show_drivers(result.get("drivers"))


def _render_overview() -> None:
    st.markdown('<div class="section-eyebrow">Your travel snapshot</div>', unsafe_allow_html=True)
    st.subheader("A thoughtful starting point for your next booking")
    cols = st.columns(4)
    metrics = [
        ("Fare observations", f"{len(data):,}", "Records in the current dataset"),
        ("Flight groups", f"{data.flight.nunique():,}", "Distinct flight identifiers"),
        ("Cities covered", f"{data.source_city.nunique()}", "Origins represented"),
        ("Booking window", f"{int(data.days_left.min())}–{int(data.days_left.max())} days", "Before departure"),
    ]
    for col, (label, value, note) in zip(cols, metrics):
        with col:
            _metric_card(label, value, note)
    st.write("")
    st.markdown('<div class="section-eyebrow">Choose a tool</div>', unsafe_allow_html=True)
    st.subheader("What would you like to explore?")
    tool_cols = st.columns(3)
    tools = [
        ("Fare estimate", "View a typical fare and historical range for a route.", "Explore fare ranges"),
        ("Book or wait", "Compare a quote with observed booking patterns.", "Review booking timing"),
        ("Quote check", "See where your quote sits in route history.", "Check a quote"),
    ]
    for col, (page, description, label) in zip(tool_cols, tools):
        with col, st.container(border=True):
            st.markdown(f"#### {page}")
            st.caption(description)
            if st.button(label, key=f"go-{page}", use_container_width=True):
                st.session_state["farewise-next-page"] = page
                st.rerun()


def _render_route_explorer() -> None:
    st.markdown('<div class="section-eyebrow">Network overview</div>', unsafe_allow_html=True)
    st.subheader("Routes in the dataset")
    summary = route_summary(data)
    st.dataframe(
        summary,
        hide_index=True,
        use_container_width=True,
        column_config={
            "source_city": st.column_config.TextColumn("Origin"),
            "destination_city": st.column_config.TextColumn("Destination"),
            "class": st.column_config.TextColumn("Cabin"),
            "observations": st.column_config.NumberColumn("Observations", format="%d"),
            "median_fare": st.column_config.NumberColumn("Median fare", format="₹%.0f"),
        },
    )
    st.write("")
    st.markdown('<div class="section-eyebrow">Booking horizon</div>', unsafe_allow_html=True)
    st.subheader("How fares vary with days left")
    a, b, c = st.columns(3)
    source = a.selectbox("Origin", sorted(data.source_city.unique()), key="curve-source")
    destination = b.selectbox("Destination", [city for city in sorted(data.destination_city.unique()) if city != source], key="curve-destination")
    fare_class = c.selectbox("Cabin", sorted(data["class"].unique()), key="curve-class")
    curve = fare_curves(data, source, destination, fare_class)
    if curve.empty:
        st.info("No observations are available for this combination.")
        return
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=curve.days_left, y=curve.p90, line={"width": 0}, showlegend=False, hoverinfo="skip"))
    figure.add_trace(go.Scatter(x=curve.days_left, y=curve.p10, line={"width": 0}, fill="tonexty", fillcolor="rgba(45,103,173,.12)", name="Historical P10–P90"))
    figure.add_trace(go.Scatter(x=curve.days_left, y=curve["median"], mode="lines+markers", line={"color": "#245da9", "width": 3}, marker={"size": 6}, name="Median fare"))
    figure.update_layout(
        height=370,
        margin={"l": 10, "r": 10, "t": 15, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial", "color": "#52637a"},
        legend={"orientation": "h", "y": 1.08, "x": 0},
        xaxis={"title": "Days until departure", "gridcolor": "#edf1f5", "zeroline": False},
        yaxis={"title": "Fare (₹)", "gridcolor": "#edf1f5", "zeroline": False, "tickprefix": "₹"},
    )
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
    st.download_button("Download this fare curve", curve.to_csv(index=False), "fare_curve.csv", "text/csv")
    st.caption("Historical distribution only. It does not imply a future price movement.")


def _render_evidence() -> None:
    st.markdown('<div class="section-eyebrow">Measured results</div>', unsafe_allow_html=True)
    st.subheader("Model performance and evaluation")
    st.info(f"This evidence uses {source_label.lower()}. Synthetic metrics describe a simulation and are not real-market accuracy.")
    summary_path = Path("models/evaluation_summary.csv")
    if summary_path.exists():
        frame = pd.read_csv(summary_path)
        st.dataframe(frame, hide_index=True, use_container_width=True)
    else:
        st.warning("Evaluation summary is not available yet. Run the evaluate task to create it.")
    with st.expander("Read the full evaluation notes"):
        report_path = Path("docs/EVALUATION.md")
        if report_path.exists():
            st.markdown(report_path.read_text(encoding="utf-8"))
        else:
            st.caption("No evaluation report is available.")
    st.caption("Model validation groups flights to prevent flight-level leakage. Reported results are historical and not live fare guidance.")


def _render_about() -> None:
    with st.container(border=True):
        st.subheader("A decision-support prototype")
        st.write("FareWise compares a selected itinerary with fares in the dataset and summarizes historical patterns. It does not connect to airline systems or retrieve live prices.")
        st.markdown(f"**Current data source:** {source_label} ({len(data):,} observations).")
    st.write("")
    a, b = st.columns(2)
    with a, st.container(border=True):
        st.markdown("#### How to interpret results")
        st.write("Fare ranges and route curves describe the observations available in this dataset. Booking signals are heuristic summaries, not guarantees.")
    with b, st.container(border=True):
        st.markdown("#### Important limitations")
        st.write("Synthetic findings are not real-market performance. Historical data can be incomplete or stale. Fares can rise or fall after any estimate.")
    st.caption("FareWise is educational decision support, not travel or financial advice.")


data = get_data()
has_csv = any(Path("data/raw").glob("*.csv"))
source_label = "manually supplied CSV" if has_csv else "synthetic demo data"
next_page = st.session_state.pop("farewise-next-page", None)
if next_page in PAGE_NAMES:
    st.session_state["farewise-page"] = next_page

_inject_styles()
with st.sidebar:
    st.markdown(
        '<div class="brand-lockup"><div class="brand-mark">✈</div><div><div class="brand-name">FareWise</div>'
        '<div class="brand-sub">Travel with clarity</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-label">Workspace</div>', unsafe_allow_html=True)
    page = st.radio("Navigate", PAGE_NAMES, label_visibility="collapsed", key="farewise-page")
    st.divider()
    st.markdown('<div class="sidebar-label">Data status</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="source-pill"><span class="source-dot"></span>{source_label.title()}</div>', unsafe_allow_html=True)
    st.caption("No live fares are queried.")

_hero(page)

if page == "Overview":
    _render_overview()
elif page in {"Fare estimate", "Book or wait", "Quote check"}:
    query, quote, submitted = _query_form(page)
    st.session_state[f"submit-{page}"] = submitted
    if page == "Fare estimate":
        _show_fare_estimate(query, page)
    elif page == "Book or wait":
        _show_advice(query, float(quote or 1))
    else:
        _show_quote(query, float(quote or 1))
elif page == "Route explorer":
    _render_route_explorer()
elif page == "Model & evidence":
    _render_evidence()
else:
    _render_about()

st.markdown(
    f'<div class="footer">FareWise · {len(data):,} observations · {source_label.title()} · No live fare access</div>',
    unsafe_allow_html=True,
)
