from __future__ import annotations

import numpy as np
import pandas as pd

CITIES=["Delhi","Mumbai","Bangalore","Kolkata","Hyderabad","Chennai"]
AIRLINES=["IndiGo","AirAsia","SpiceJet","Vistara","Air_India","GO_FIRST"]
TIMES=["Early_Morning","Morning","Afternoon","Evening","Night","Late_Night"]

def generate_fares(n_flights:int=500,seed:int=42)->pd.DataFrame:
    """Create reproducible synthetic route and flight quote panels."""
    if n_flights<1:raise ValueError("n_flights must be positive")
    rng=np.random.default_rng(seed);rows=[]
    for idx in range(n_flights):
        source,destination=rng.choice(CITIES,size=2,replace=False);airline=str(rng.choice(AIRLINES));flight=f"{airline[:2].upper()}{idx:04d}"
        fare_class=str(rng.choice(["Economy","Business"],p=[.82,.18]));base=float(rng.uniform(2200,7500))*(3.2 if fare_class=="Business" else 1.0)
        dep=str(rng.choice(TIMES));arr=str(rng.choice(TIMES));stops=str(rng.choice(["zero","one","two_or_more"],p=[.55,.4,.05]));duration=round(float(rng.uniform(1,8)),2)
        days=sorted(set([int(v) for v in rng.integers(1,61,size=7)]+[1,7,14,21,30,45,60]))
        for day in days:
            urgency=max(0,21-day)/21;price=base*(1+.60*urgency+.65*urgency**3)
            if airline in {"Vistara","Air_India"}:price*=1.15
            price*=float(np.exp(rng.normal(0,.11)))
            if rng.random()<.003:price*=float(rng.uniform(2.5,4.0))
            rows.append({"airline":airline,"flight":flight,"source_city":source,"departure_time":dep,"stops":stops,"arrival_time":arr,"destination_city":destination,"class":fare_class,"duration":duration,"days_left":day,"price":round(price,2)})
    return pd.DataFrame(rows)
