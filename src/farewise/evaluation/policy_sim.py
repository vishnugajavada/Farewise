from __future__ import annotations

import numpy as np
import pandas as pd

from farewise.advisor.optimal_stopping import solve
from farewise.advisor.transitions import build_transitions, ratio_samples


def simulate(train:pd.DataFrame,heldout:pd.DataFrame,seed:int=42,max_wait:int=7,min_saving:float=250,max_risk:float=.4)->pd.DataFrame:
    """Run sequential policies. At each decision only the current observed quote and training-only ratios are used."""
    transitions=build_transitions(train); rng=np.random.default_rng(seed); rows=[]
    for flight,group in heldout.groupby("flight",sort=False):
        panel=group.sort_values("days_left",ascending=False).reset_index(drop=True)
        if len(panel)<2:continue
        start=panel.iloc[0]; route=f"{start['source_city']}->{start['destination_city']}"; cls=str(start["class"]); tier="low_cost" if start.airline in {"IndiGo","AirAsia","SpiceJet","GO_FIRST"} else "full_service"
        quotes={int(row["days_left"]):float(row["price"]) for _,row in panel.iterrows()}; timeline=sorted(quotes,reverse=True); timeline=timeline[:max_wait+1]
        if len(timeline)<2:continue
        first=timeline[0]
        bucket="0-2" if first<=2 else "3-7" if first<=7 else "8-14" if first<=14 else "15-21" if first<=21 else "22-30" if first<=30 else "31+"
        ratios=ratio_samples(transitions,route,cls,tier,bucket).to_numpy(dtype=float); expected_ratio=float(np.mean(ratios)); risk=float(np.mean(ratios>1))
        # Fixed and random policies pick a day before observing prices; advisor policies can stop only on current quote.
        random_day=int(rng.choice(timeline))
        choices={"book_immediately":first,"fixed_21_day":None,"random_day":random_day,"advisor_v1":None,"advisor_v2":None}
        for index,day in enumerate(timeline):
            if choices["fixed_21_day"] is None and (day<=21 or day==timeline[-1]):choices["fixed_21_day"]=day
            current=quotes[day]; projected=current*expected_ratio
            saving=current-projected
            if choices["advisor_v1"] is None and (saving<min_saving or risk>max_risk or day==timeline[-1]):choices["advisor_v1"]=day
            # Bellman solve sees only the current quote and train-derived expected ratios.
            horizon=timeline[index:]
            expected_prices={d:current*(expected_ratio**(day-d)) for d in horizon}
            book_day,_=solve(expected_prices,{d:[expected_ratio] for d in horizon})
            if choices["advisor_v2"] is None and (book_day==day or day==timeline[-1]):choices["advisor_v2"]=day
        choices["fixed_21_day"]=choices["fixed_21_day"] or timeline[-1]
        choices["advisor_v1"]=choices["advisor_v1"] or timeline[-1]; choices["advisor_v2"]=choices["advisor_v2"] or timeline[-1]
        oracle_day=min(timeline,key=lambda d:quotes[d])
        for policy,day in {**choices,"oracle":oracle_day}.items():
            paid=quotes[day]; rows.append({"flight":flight,"route":route,"class":cls,"start_days_left":first,"policy":policy,"booking_day_left":day,"paid_inr":paid,"saving_vs_now_inr":quotes[first]-paid,"oracle_regret_inr":paid-quotes[oracle_day],"oracle_day_left":oracle_day})
    return pd.DataFrame(rows)

def summarize(results:pd.DataFrame)->pd.DataFrame:
    if results.empty:return pd.DataFrame()
    return results.groupby(["route","class","start_days_left","policy"],as_index=False).agg(mean_saving_inr=("saving_vs_now_inr","mean"),median_saving_inr=("saving_vs_now_inr","median"),win_rate=("saving_vs_now_inr",lambda x:float((x>0).mean())),mean_regret_inr=("oracle_regret_inr","mean"),worst_downside_inr=("saving_vs_now_inr","min"),p10_saving_inr=("saving_vs_now_inr",lambda x:float(x.quantile(.1))),flights=("flight","nunique"))
