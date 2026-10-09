from __future__ import annotations

from pathlib import Path

import plotly.express as px
import streamlit as st

from farewise.service.advise_service import advise_route
from farewise.service.data_service import fare_curves, get_data, route_summary
from farewise.service.deal_service import check_quote
from farewise.service.predict_service import FareQuery, predict_fare

st.set_page_config(page_title="FareWise",page_icon="✈️",layout="wide")
data=get_data()
has_csv=any(Path("data/raw").glob("*.csv"));source_label="Manually supplied CSV" if has_csv else "SYNTHETIC demo data"
st.title("FareWise ✈️")
page=st.sidebar.radio("Page",["Home","Fare Predictor","Book Now or Wait","Deal Checker","Route Explorer","Model & Evidence","About & Limitations"])
if page=="Home":
 st.write("Estimate a fare range, assess a quote, and explore booking horizons from observed fares.")
 st.info(f"Loaded {len(data):,} rows from {source_label}. No live prices are queried.")
elif page in {"Fare Predictor","Book Now or Wait","Deal Checker"}:
 a,b=st.columns(2);source=a.selectbox("From",sorted(data.source_city.unique()));destinations=sorted(c for c in data.destination_city.unique() if c!=source);destination=b.selectbox("To",destinations)
 cls=st.selectbox("Class",sorted(data["class"].unique()));days=st.slider("Days left",1,int(max(1,data.days_left.max())),min(14,int(max(1,data.days_left.max()))));quote=st.number_input("Quoted fare (INR)",min_value=1.0,value=6000.0,step=250.0)
 query=FareQuery(source=source,destination=destination,days_left=days,fare_class=cls)
 if page=="Fare Predictor":
  if st.button("Estimate fare"):
   result=predict_fare(data,query)
   if result["available"]:st.metric("Typical fare",f"₹{result['p50']:,.0f}");st.write(f"Historical 10th–90th percentile: ₹{result['p10']:,.0f}–₹{result['p90']:,.0f}; observations: {result['rows']}. Data window/source: {source_label}. Method: {result.get('method','historical cohort')}.")
   if result.get("drivers"):st.dataframe(result["drivers"],use_container_width=True)
   else:st.info(result["message"])
   if result.get("available") and result.get("drivers"):st.write("Observed fare drivers (cohort median shifts, not causal effects):");st.dataframe(result["drivers"],use_container_width=True)
 elif page=="Book Now or Wait":
  result=advise_route(data,query,quote);st.subheader(str(result["action"]));st.write(f"Expected saving: ₹{result.get('expected_saving_inr',0):,.0f} ({result.get('expected_saving_percent',0):.1f}%); chance of fare rising: {result.get('rise_probability',0):.0%}.")
  st.write(f"Fare range: ₹{result.get('p10',0):,.0f}–₹{result.get('p90',0):,.0f}. Data window: {source_label}; {result.get('data_rows',0)} matching observations.")
  if result.get("drivers"):st.write("Observed fare drivers (cohort median shifts, not causal effects):");st.dataframe(result["drivers"],use_container_width=True)
  st.caption(f"FareWise historically tends to describe patterns in the available data. Data window/source: {source_label}; not live. It cannot predict live changes; fares may rise or fall.")
 else:
  result=check_quote(data,query,quote);st.subheader(str(result.get("label",result.get("message"))));st.write(f"Quote percentile: {result.get('percentile',0):.0f}; historical P10/P50/P90: ₹{result.get('p10',0):,.0f} / ₹{result.get('p50',0):,.0f} / ₹{result.get('p90',0):,.0f}. Data window/source: {source_label}.")
elif page=="Route Explorer":
 st.dataframe(route_summary(data),use_container_width=True);source=st.selectbox("Curve origin",sorted(data.source_city.unique()),key="curve_source");dest=st.selectbox("Curve destination",sorted(x for x in data.destination_city.unique() if x!=source),key="curve_dest");cls=st.selectbox("Curve class",sorted(data["class"].unique()),key="curve_class");curve=fare_curves(data,source,dest,cls)
 if not curve.empty:st.plotly_chart(px.line(curve,x="days_left",y="median",title="Observed median fare by days left"),use_container_width=True);st.download_button("Download fare curve CSV",curve.to_csv(index=False),"fare_curve.csv","text/csv")
elif page=="Model & Evidence":
 from pathlib import Path
 for file in ["docs/EVALUATION.md"]:
  if Path(file).exists():st.markdown(Path(file).read_text(encoding="utf-8"))
 st.caption("Run scripts/tasks.py evaluate and simulate to refresh results from current data.")
elif page=="About & Limitations":
 st.markdown("""FareWise is an educational decision-support prototype. The optional Kaggle Flight Price Prediction (EaseMyTrip) CSV is a historical snapshot; verify the source dataset's licence before redistribution. The commonly distributed dataset describes Feb–Mar 2022 fares and contains no journey dates, so separate days-left rows may represent different physical departures. Synthetic data results do not establish real fare performance. This is not travel advice.""")
