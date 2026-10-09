from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

BUCKETS=[0,2,7,14,21,30,float("inf")]
LABELS=["0-2","3-7","8-14","15-21","22-30","31+"]
TIME_ORDER=["Early_Morning","Morning","Afternoon","Evening","Night","Late_Night"]

def build_features(frame:pd.DataFrame)->pd.DataFrame:
    x=frame.copy();x["route"]=x.source_city.astype(str)+" → "+x.destination_city.astype(str)
    x["days_bucket"]=pd.cut(x.days_left,bins=BUCKETS,labels=LABELS,include_lowest=True)
    x["duration_bin"]=pd.cut(x.duration,bins=[0,2,4,7,float("inf")],labels=["short","medium","long","very_long"])
    x["departure_bucket"]=pd.Categorical(x.departure_time,categories=TIME_ORDER,ordered=True)
    x["red_eye"]=x.departure_time.isin(["Late_Night","Early_Morning"]).astype(int)
    config_path=Path("configs/airlines.yaml")
    tiers=yaml.safe_load(config_path.read_text(encoding="utf-8"))["tiers"] if config_path.exists() else {}
    x["airline_tier"]=x.airline.map(tiers).fillna("unknown")
    return x.drop(columns=["flight","price","outlier_flag"],errors="ignore")
