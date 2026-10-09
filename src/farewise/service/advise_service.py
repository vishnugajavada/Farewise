from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from farewise.advisor.heuristic import choose_wait
from farewise.explain.explain import top_drivers
from farewise.service.predict_service import FareQuery, route_history


def advise_route(data:pd.DataFrame,query:FareQuery,quoted_fare:float)->dict[str,object]:
    if quoted_fare<=0:raise ValueError("quoted fare must be positive")
    panel=route_history(data,query)
    if panel.empty:return {"action":"NOT ENOUGH DATA","limitation":"No matching route and class observations."}
    current=panel[panel.days_left.sub(query.days_left).abs()<=3]
    if current.empty:current=panel
    config=yaml.safe_load(Path("configs/advisor.yaml").read_text(encoding="utf-8"))
    common={"p10":float(current.price.quantile(.1)),"p50":float(current.price.median()),"p90":float(current.price.quantile(.9)),"data_rows":len(current),"data_window":"Historical snapshot or synthetic demo","drivers":top_drivers(panel,{"source_city":query.source,"destination_city":query.destination,"class":query.fare_class,"days_left":query.days_left})}
    if query.days_left<=int(config["danger_zone_days_left"]):
        return {"action":"BOOK NOW","expected_saving_inr":0.0,"expected_saving_percent":0.0,"rise_probability":0.0,**common}
    means={};risks={};window=min(int(config["flexibility_days"]),query.days_left-1)
    for wait in range(1,window+1):
        target_day=query.days_left-wait; candidates=panel[panel.days_left.sub(target_day).abs()<=max(1,wait//3)]
        if candidates.empty:candidates=panel[panel.days_left.lt(query.days_left)&panel.days_left.ge(target_day)]
        if candidates.empty:continue
        means[wait]=float(candidates.price.mean());risks[wait]=float((candidates.price>quoted_fare).mean())
    result=choose_wait(quoted_fare,means,risks,float(config["minimum_saving_inr"]),float(config["max_risk"]))
    result.update(common);return result
