from __future__ import annotations

import pandas as pd


def top_drivers(data:pd.DataFrame,query:dict[str,object],limit:int=5)->list[dict[str,object]]:
    drivers=[]
    for key,value in query.items():
        if key not in data.columns:continue
        matching=data.loc[data[key].astype(str)==str(value),"price"]
        if matching.empty:continue
        difference=float(matching.median()-data.price.median())
        drivers.append({"feature":key,"value":str(value),"median_shift_inr":difference})
    return sorted(drivers,key=lambda row:abs(row["median_shift_inr"]),reverse=True)[:limit]


def shap_explanation(model,features:pd.DataFrame,limit:int=5)->list[dict[str,object]]:
    """Return per-row TreeSHAP impacts when SHAP is installed."""
    try:
        import shap
    except ImportError as exc:
        raise RuntimeError("SHAP is not installed; use cohort-shift explanations instead") from exc
    transformed=model.named_steps["prep"].transform(features)
    if hasattr(transformed,"toarray"): transformed=transformed.toarray()
    estimator=model.named_steps["model"]
    values=shap.TreeExplainer(estimator)(transformed).values
    names=model.named_steps["prep"].get_feature_names_out()
    impacts=values[0] if getattr(values,"ndim",1)>1 else values
    rows=[{"feature":str(name),"log_price_impact":float(value)} for name,value in zip(names,impacts)]
    return sorted(rows,key=lambda row:abs(row["log_price_impact"]),reverse=True)[:limit]
