from __future__ import annotations

import pandas as pd

from farewise.advisor.deal import check_deal
from farewise.explain.explain import top_drivers
from farewise.service.predict_service import FareQuery, route_history


def check_quote(data:pd.DataFrame,query:FareQuery,quote:float)->dict[str,object]:
    history=route_history(data,query).price
    if history.empty:return {"available":False,"message":"Not enough matching route data."}
    result=check_deal(history,quote);result["available"]=True;result["drivers"]=top_drivers(data,{"source_city":query.source,"destination_city":query.destination,"class":query.fare_class,"days_left":query.days_left});return result
