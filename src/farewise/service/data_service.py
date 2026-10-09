from __future__ import annotations

import pandas as pd

from farewise.data.loader import load_data


def get_data()->pd.DataFrame:return load_data()
def route_summary(data:pd.DataFrame)->pd.DataFrame:return data.groupby(["source_city","destination_city","class"],as_index=False).agg(observations=("price","size"),median_fare=("price","median"))
def fare_curves(data:pd.DataFrame,source:str,destination:str,fare_class:str)->pd.DataFrame:
    subset=data[(data.source_city==source)&(data.destination_city==destination)&(data["class"]==fare_class)]
    return subset.groupby("days_left",as_index=False).agg(median=("price","median"),p10=("price",lambda x:x.quantile(.1)),p90=("price",lambda x:x.quantile(.9)))
