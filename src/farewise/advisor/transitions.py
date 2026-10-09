from __future__ import annotations

import pandas as pd

COHORTS=("route_group","class","airline_tier","days_bucket")

def build_transitions(data: pd.DataFrame, min_samples: int=5) -> pd.DataFrame:
    """Build observed log price ratios from earlier to later quote horizons."""
    required={"flight","source_city","destination_city","class","airline","days_left","price"}
    if missing:=required-set(data.columns): raise ValueError(f"Missing columns: {sorted(missing)}")
    rows=[]
    work=data.copy(); work["route_group"]=work.source_city.astype(str)+"->"+work.destination_city.astype(str)
    tiers={"IndiGo":"low_cost","AirAsia":"low_cost","SpiceJet":"low_cost","GO_FIRST":"low_cost"}
    work["airline_tier"]=work.airline.map(tiers).fillna("full_service")
    work["days_bucket"]=pd.cut(work.days_left,[0,2,7,14,21,30,float("inf")],labels=["0-2","3-7","8-14","15-21","22-30","31+"])
    for _, group in work.groupby(["flight","route_group","class"],observed=True):
        group=group.sort_values("days_left")
        records=list(group.to_dict("records"))
        for earlier in records:
            for later in records:
                if earlier["days_left"] < later["days_left"]:
                    rows.append({"route_group":earlier["route_group"],"class":earlier["class"],"airline_tier":earlier["airline_tier"],"days_bucket":str(later["days_bucket"]),"d0":int(later["days_left"]),"d1":int(earlier["days_left"]),"ratio":float(earlier["price"]/later["price"]),"log_ratio":float(__import__("math").log(earlier["price"]/later["price"]))})
    result=pd.DataFrame(rows)
    if result.empty: return pd.DataFrame(columns=[*COHORTS,"d0","d1","ratio","log_ratio"])
    counts=result.groupby(list(COHORTS),observed=True).ratio.transform("size")
    result["cohort_fallback"]=counts < min_samples
    return result

def ratio_samples(transitions: pd.DataFrame, route_group: str, fare_class: str, tier: str, bucket: str) -> pd.Series:
    if transitions.empty: return pd.Series([1.0])
    mask=(transitions.route_group==route_group)&(transitions["class"]==fare_class)&(transitions.airline_tier==tier)&(transitions.days_bucket==bucket)
    exact=transitions.loc[mask,"ratio"]
    if len(exact)>=5: return exact
    for cols in [("route_group","class"),("route_group",),("class","airline_tier"),("class",)]:
        m=pd.Series(True,index=transitions.index)
        values_by_column={"route_group":route_group,"class":fare_class,"airline_tier":tier}
        for col in cols: m &= transitions[col] == values_by_column[col]
        values=transitions.loc[m,"ratio"]
        if len(values)>=5: return values
    return transitions.ratio
