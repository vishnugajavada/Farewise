from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from pydantic import BaseModel, Field, model_validator

from farewise.explain.explain import shap_explanation, top_drivers
from farewise.features.build import build_features


class FareQuery(BaseModel):
    source:str
    destination:str
    days_left:int=Field(gt=0,le=365)
    fare_class:str="Economy"
    @model_validator(mode="after")
    def different_cities(self):
        if self.source.casefold()==self.destination.casefold():raise ValueError("source and destination must differ")
        return self

def route_history(data:pd.DataFrame,query:FareQuery)->pd.DataFrame:
    return data[(data.source_city.str.casefold()==query.source.casefold())&(data.destination_city.str.casefold()==query.destination.casefold())&(data["class"].str.casefold()==query.fare_class.casefold())]

def predict_fare(data:pd.DataFrame,query:FareQuery)->dict[str,object]:
    cohort=route_history(data,query)
    if cohort.empty:cohort=data[data["class"].str.casefold()==query.fare_class.casefold()]
    if cohort.empty:return {"available":False,"message":"Not enough fare observations for this class."}
    nearest=cohort[cohort.days_left.sub(query.days_left).abs()<=7]
    if nearest.empty:nearest=cohort
    fallback=route_history(data,query).empty
    model_path=Path("models/fare_model.joblib"); metadata_path=Path("models/metadata.json")
    metadata=json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    compatible=metadata.get("sklearn_version")==sklearn.__version__
    if model_path.exists() and metadata_path.exists() and compatible:
        example=nearest.iloc[[int(np.argmin(np.abs(nearest.days_left.to_numpy()-query.days_left)))]].copy();example.loc[:,"days_left"]=query.days_left
        model=joblib.load(model_path);features=build_features(example);prediction=float(np.exp(model.predict(features)[0]))
        radius=float(metadata.get("conformal_radius_inr",0))
        try:drivers=shap_explanation(model,features)
        except Exception:drivers=top_drivers(nearest,{"source_city":query.source,"destination_city":query.destination,"class":query.fare_class,"days_left":query.days_left})  # noqa: BLE001
        return {"available":True,"p10":max(0,prediction-radius),"p50":prediction,"p90":prediction+radius,"rows":len(nearest),"fallback":fallback,"method":f"trained {metadata.get('champion','model')} with group-calibrated conformal interval","drivers":drivers}
    return {"available":True,"p10":float(nearest.price.quantile(.1)),"p50":float(nearest.price.median()),"p90":float(nearest.price.quantile(.9)),"rows":len(nearest),"fallback":fallback,"method":"empirical route and class quantiles; model artifact unavailable","drivers":top_drivers(nearest,{"source_city":query.source,"destination_city":query.destination,"class":query.fare_class,"days_left":query.days_left})}
