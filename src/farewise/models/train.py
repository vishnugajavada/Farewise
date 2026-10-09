from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from farewise.evaluation.metrics import pinball_loss, smape
from farewise.features.build import build_features


def _model(name: str,seed: int) -> Pipeline:
    numeric=["duration","days_left","red_eye"]
    def prep(x:pd.DataFrame)->ColumnTransformer:
        cats=[c for c in x if c not in numeric and c!="stops_ordinal"]
        return ColumnTransformer([("num",Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler())]),numeric),("cat",Pipeline([("impute",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]),cats)],remainder="passthrough")
    if name=="Ridge": est=Ridge(alpha=4.0)
    elif name=="RandomForest": est=RandomForestRegressor(n_estimators=80,min_samples_leaf=4,max_features=.8,random_state=seed,n_jobs=1)
    elif name=="LightGBM":
        try:
            from lightgbm import LGBMRegressor
        except ImportError as exc: raise RuntimeError("LightGBM is not installed") from exc
        est=LGBMRegressor(n_estimators=160,learning_rate=.05,num_leaves=20,verbosity=-1,random_state=seed,n_jobs=1)
    else: est=HistGradientBoostingRegressor(max_iter=100,learning_rate=.08,l2_regularization=2,random_state=seed)
    return Pipeline([("prep",prep(pd.DataFrame(columns=numeric+["stops_ordinal"]))),("model",est)])

def _pipeline(name:str,features:pd.DataFrame,seed:int)->Pipeline:
    numeric=["duration","days_left","red_eye"]; cats=[c for c in features if c not in numeric and c!="stops_ordinal"]
    pre=ColumnTransformer([("num",Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler())]),numeric),("cat",Pipeline([("impute",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]),cats)],remainder="passthrough")
    if name=="Ridge":est=Ridge(alpha=4.0)
    elif name=="RandomForest":est=RandomForestRegressor(n_estimators=80,min_samples_leaf=4,max_features=.8,random_state=seed,n_jobs=1)
    elif name=="LightGBM":
        from lightgbm import LGBMRegressor
        est=LGBMRegressor(n_estimators=160,learning_rate=.05,num_leaves=20,verbosity=-1,random_state=seed,n_jobs=1)
    else:est=HistGradientBoostingRegressor(max_iter=100,learning_rate=.08,l2_regularization=2,random_state=seed)
    return Pipeline([("prep",pre),("model",est)])

def _metrics(y:np.ndarray,p:np.ndarray)->dict[str,float]:
    return {"mae_inr":float(mean_absolute_error(y,p)),"rmse_inr":float(mean_squared_error(y,p)**.5),"smape_percent":smape(y,p),"r2_price":float(r2_score(y,p)),"r2_log_price":float(r2_score(np.log(y),np.log(np.maximum(p,1))))}

def _baseline_predictions(train:pd.DataFrame,test:pd.DataFrame,name:str)->np.ndarray:
    key={"global_class":["class"],"route_class":["route","class"],"route_class_days":["route","class","days_bucket"]}[name]
    lookup=train.groupby(key,observed=True).price.mean(); global_mean=float(train.price.mean())
    values=[]
    for _,row in test.iterrows():
        k=tuple(row[c] for c in key); k=k[0] if len(k)==1 else k
        try: values.append(float(lookup.loc[k]))
        except KeyError:
            if name=="route_class_days":
                try:values.append(float(train.groupby(["route","class"],observed=True).price.mean().loc[(row.route,row["class"])]))
                except KeyError: values.append(global_mean)
            else:values.append(global_mean)
    return np.asarray(values)

def evaluate_models(data:pd.DataFrame,output_dir:str|Path="models",seed:int=42)->dict[str,object]:
    x=build_features(data).reset_index(drop=True); y=data.price.astype(float).reset_index(drop=True); groups=data.flight.astype(str).reset_index(drop=True)
    if groups.nunique()<5: raise ValueError("At least five flight groups are required")
    folds=GroupKFold(n_splits=5); models=["Ridge","RandomForest","LightGBM"]; records=[]; predictions={n:np.full(len(data),np.nan) for n in models}; intervals=np.full((len(data),2),np.nan)
    for fold,(tr,te) in enumerate(folds.split(x,y,groups),1):
        train=x.iloc[tr]
        # Reserve training groups for split-conformal calibration; calibration groups never train the predictor.
        from sklearn.model_selection import GroupShuffleSplit
        inner=GroupShuffleSplit(n_splits=1,test_size=.2,random_state=seed+fold); fit_local,cal_local=next(inner.split(train,groups=groups.iloc[tr]))
        fit_idx=tr[fit_local]; cal_idx=tr[cal_local]
        for name in models:
            try: model=_pipeline(name,x,seed+fold)
            except ImportError: continue
            model.fit(x.iloc[fit_idx],np.log(y.iloc[fit_idx])); cal=np.exp(model.predict(x.iloc[cal_idx])); resid=np.abs(y.iloc[cal_idx].to_numpy()-cal); q=float(np.quantile(resid,min(1,.8*(len(resid)+1)/len(resid)),method="higher"))
            pred=np.exp(model.predict(x.iloc[te])); predictions[name][te]=pred; intervals[te,0]=np.maximum(0,pred-q); intervals[te,1]=pred+q
            metrics=_metrics(y.iloc[te].to_numpy(),pred); metrics.update({"model":name,"validation":"unseen-flight GroupKFold","fold":fold,"rows":len(te),"interval80_coverage":float(np.mean((y.iloc[te].to_numpy()>=pred-q)&(y.iloc[te].to_numpy()<=pred+q))),"interval80_mean_width_inr":2*q,"pinball_p10":pinball_loss(y.iloc[te].to_numpy(),pred-q,.1),"pinball_p90":pinball_loss(y.iloc[te].to_numpy(),pred+q,.9)}); records.append(metrics)
        # Shared test folds for all transparent mean baselines.
        base_x=x.copy(); base_x["price"]=y;
        for name in ("global_class","route_class","route_class_days"):
            pred=_baseline_predictions(base_x.iloc[tr],base_x.iloc[te],name); m=_metrics(y.iloc[te].to_numpy(),pred); m.update({"model":name,"validation":"unseen-flight GroupKFold","fold":fold,"rows":len(te)}); records.append(m)
    # Champion artifacts trained on all rows; OOF results above remain untouched.
    available_models=[name for name in models if np.isfinite(predictions[name]).any()]
    champion=min(available_models,key=lambda name:float(np.mean([r["mae_inr"] for r in records if r["model"]==name])))
    model=_pipeline(champion,x,seed); model.fit(x,np.log(y)); Path(output_dir).mkdir(parents=True,exist_ok=True); joblib.dump(model,Path(output_dir)/"fare_model.joblib")
    record=pd.DataFrame(records); record.to_csv(Path(output_dir)/"fold_metrics.csv",index=False)
    summary=record.groupby(["validation","model"],as_index=False).mean(numeric_only=True)
    # Held-out days-left blocks: train only on >=15 days and evaluate near-departure rows.
    near=data.days_left<=14; far=data.days_left>14; day_rows=[]
    if near.any() and far.any():
        for name in models:
            try: m=_pipeline(name,x,seed)
            except ImportError: continue
            m.fit(x.loc[far],np.log(y.loc[far])); pred=np.exp(m.predict(x.loc[near])); z=_metrics(y.loc[near].to_numpy(),pred); z.update({"model":name,"validation":"held-out days_left <=14","rows":int(near.sum())}); day_rows.append(z)
        for name in ("global_class","route_class","route_class_days"):
            far_x=x.loc[far].copy(); far_x["price"]=y.loc[far]
            near_x=x.loc[near].copy(); near_x["price"]=y.loc[near]
            pred=_baseline_predictions(far_x,near_x,name); z=_metrics(y.loc[near].to_numpy(),pred); z.update({"model":name,"validation":"held-out days_left <=14","rows":int(near.sum())}); day_rows.append(z)
    days=pd.DataFrame(day_rows); metrics_path=Path(output_dir)/"evaluation_summary.csv"; pd.concat([summary,days],ignore_index=True).to_csv(metrics_path,index=False)
    # Test fold slices from forest OOF predictions.
    forest=predictions["RandomForest"]; valid=np.isfinite(forest); rows=[]
    slice_data=data.copy();slice_data["route"]=slice_data.source_city.astype(str)+"->"+slice_data.destination_city.astype(str)
    for col in ["class","route","airline","days_left","stops"]:
        temp=slice_data.loc[valid,[col,"price"]].copy(); temp["prediction"]=forest[valid]; temp["slice"]=pd.cut(temp[col], [0,2,7,14,21,30,float("inf")],labels=["0-2","3-7","8-14","15-21","22-30","31+"]) if col=="days_left" else temp[col]
        for label,g in temp.groupby("slice",observed=True): rows.append({"slice_dimension":col,"slice":str(label),"rows":len(g),"mae_inr":float(np.mean(np.abs(g.price-g.prediction)))})
    pd.DataFrame(rows).to_csv(Path(output_dir)/"slice_metrics.csv",index=False)
    curves=data.groupby(["source_city","destination_city","class","days_left"],as_index=False).price.median(); curves.to_csv(Path(output_dir)/"fare_curves.csv",index=False)
    # Global SHAP values when installed; deterministic permutation rankings remain as fallback.
    from sklearn.inspection import permutation_importance
    fitted=_pipeline("RandomForest",x,seed); fitted.fit(x,np.log(y)); imp=permutation_importance(fitted,x,np.log(y),n_repeats=2,random_state=seed,n_jobs=1,scoring="neg_mean_absolute_error")
    pd.DataFrame({"feature":x.columns,"importance":imp.importances_mean}).sort_values("importance",ascending=False).to_csv(Path(output_dir)/"drivers.csv",index=False)
    shap_available=False
    try:
        import shap
        sampled=x.sample(min(100,len(x)),random_state=seed); transformed=fitted.named_steps["prep"].transform(sampled)
        if hasattr(transformed,"toarray"): transformed=transformed.toarray()
        transformed=np.asarray(transformed,dtype=float)
        shap_values=shap.TreeExplainer(fitted.named_steps["model"])(transformed).values
        names=fitted.named_steps["prep"].get_feature_names_out(); impacts=np.abs(shap_values).mean(axis=0)
        pd.DataFrame({"feature":names,"mean_abs_shap_log_price":impacts}).sort_values("mean_abs_shap_log_price",ascending=False).to_csv(Path(output_dir)/"shap_summary.csv",index=False);shap_available=True
    except Exception:  # noqa: BLE001
        # SHAP is optional; permutation importance above remains available.
        shap_available=False
    metadata={"data_rows":len(data),"flight_groups":int(groups.nunique()),"data_source":"synthetic unless raw CSV configured","champion":champion,"sklearn_version":sklearn.__version__,"shap_available":shap_available,"metrics_csv":str(metrics_path),"interval_method":"split conformal, absolute fare residuals, 80% nominal; calibrated on groups held out from fit","conformal_radius_inr":float(record.loc[record.model==champion,"interval80_mean_width_inr"].mean()/2),"group_cv_metrics":record.groupby("model")[["mae_inr","rmse_inr","r2_price"]].mean(numeric_only=True).to_dict(orient="index")}
    (Path(output_dir)/"metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    return {"summary":summary,"days_left":days,"fold_metrics":record,"metadata":metadata}

def fit_model(data:pd.DataFrame,model_dir:str|Path="models",seed:int=42)->dict[str,float]:
    result=evaluate_models(data,model_dir,seed); row=result["summary"].query("model == 'RandomForest'").iloc[0]; return {k:float(row[k]) for k in ("mae_inr","rmse_inr","r2_price")}
