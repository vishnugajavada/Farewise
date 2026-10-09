from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

from farewise.data.loader import load_data
from farewise.evaluation.policy_sim import simulate, summarize
from farewise.models.train import evaluate_models


def _markdown(frame:pd.DataFrame)->str:
    if frame.empty:return "No rows."
    cols=list(frame.columns); lines=["| "+" | ".join(cols)+" |","| "+" | ".join(["---"]*len(cols))+" |"]
    for row in frame.itertuples(index=False,name=None):
        vals=["—" if pd.isna(value) else f"{value:.2f}" if isinstance(value,(float,int)) else str(value) for value in row]
        lines.append("| "+" | ".join(vals)+" |")
    return "\n".join(lines)

def _report(results:dict[str,object],simulation:pd.DataFrame|None=None)->str:
    summary=results["summary"][ ["validation","model","mae_inr","rmse_inr","smape_percent","r2_price","r2_log_price","interval80_coverage","interval80_mean_width_inr","pinball_p10","pinball_p90"] ].copy(); days=results["days_left"]
    cv_best=summary.loc[summary.mae_inr.idxmin()] if not summary.empty else None
    cv_baselines=summary[summary.model.isin(["global_class","route_class","route_class_days"])]
    cv_base=cv_baselines.loc[cv_baselines.mae_inr.idxmin()] if not cv_baselines.empty else None
    near_best=days.loc[days.mae_inr.idxmin()] if not days.empty else None
    comparison=(f"Unseen-flight MAE winner: {cv_best.model} (₹{cv_best.mae_inr:.2f}); strongest listed mean baseline: {cv_base.model} (₹{cv_base.mae_inr:.2f})." if cv_best is not None and cv_base is not None else "Unseen-flight baseline comparison unavailable.")
    near_comparison=f"Near-departure MAE winner: {near_best.model} (₹{near_best.mae_inr:.2f})." if near_best is not None else "Near-departure comparison unavailable."
    note="Model comparisons use identical folds; flight groups do not cross train/test boundaries. Conformal calibration groups are excluded from fit. LightGBM is omitted when unavailable. Actual interval coverage and calibration width are reported above. Slice metrics and permutation-importance drivers are saved under `models/`; per-query cohort driver shifts are not SHAP values."
    text=["# Evaluation results","","All reported metrics below come from the current run. Label: **SYNTHETIC** unless a manually supplied raw CSV was loaded.","","## Unseen-flight GroupKFold",_markdown(summary),"",comparison,"","## Held-out days-left block (days_left <= 14)",_markdown(days) if not days.empty else "Not available for this dataset.","",near_comparison,"",note,"","## Policy simulation",_markdown(summarize(simulation)) if simulation is not None and not simulation.empty else "No simulation records."]
    return "\n".join(text)+"\n"

def main()->None:
    command=sys.argv[1] if len(sys.argv)>1 else "evaluate"; data=load_data()
    if command=="train":
        result=evaluate_models(data); print(json.dumps(result["metadata"],indent=2))
    elif command=="evaluate":
        result=evaluate_models(data); Path("docs/EVALUATION.md").write_text(_report(result),encoding="utf-8"); print(result["summary"].to_string(index=False))
    elif command=="simulate":
        splitter=GroupShuffleSplit(n_splits=1,test_size=.2,random_state=42); train_idx,test_idx=next(splitter.split(data,groups=data.flight)); train=data.iloc[train_idx].copy(); heldout=data.iloc[test_idx].copy()
        result=simulate(train,heldout); Path("data/processed").mkdir(parents=True,exist_ok=True); result.to_csv("data/processed/policy_simulation.csv",index=False)
        grouped=summarize(result); grouped.to_csv("data/processed/policy_summary.csv",index=False)
        summary=result.groupby("policy",as_index=False).agg(mean_saving_inr=("saving_vs_now_inr","mean"),median_saving_inr=("saving_vs_now_inr","median"),win_rate=("saving_vs_now_inr",lambda x:float((x>0).mean())),mean_regret_inr=("oracle_regret_inr","mean"),worst_downside_inr=("saving_vs_now_inr","min"),p10_saving_inr=("saving_vs_now_inr",lambda x:float(x.quantile(.1))),flights=("flight","nunique"))
        path=Path("docs/EVALUATION.md"); text=path.read_text(encoding="utf-8") if path.exists() else "# Evaluation\n"
        text=text.split("## Policy simulation")[0].split("## Held-out flight policy simulation")[0].rstrip()+"\n"
        text += "\n## Held-out flight policy simulation (SYNTHETIC)\n\nTraining and transition statistics use a separate 80% flight-group partition; the policies run on the remaining 20% and only use current observed fares plus training-derived transitions. The oracle uses hindsight and is an upper bound. Route/class/start-day detailed rows are in `data/processed/policy_summary.csv`; individual outcomes are in `data/processed/policy_simulation.csv`.\n\n"+_markdown(summary)+"\n"
        path.write_text(text,encoding="utf-8"); print(summary.to_string(index=False))
    else:raise SystemExit(f"Unknown command: {command}")
if __name__=="__main__":main()
