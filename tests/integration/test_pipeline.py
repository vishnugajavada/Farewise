from sklearn.model_selection import GroupKFold

from farewise.advisor.transitions import build_transitions
from farewise.data.clean import clean_fares
from farewise.data.synthetic import generate_fares
from farewise.evaluation.policy_sim import simulate, summarize


def test_split_has_no_flight_leakage():
    data=clean_fares(generate_fares(25,4)); groups=data.flight
    for train,test in GroupKFold(n_splits=5).split(data,groups=groups):
        assert not (set(groups.iloc[train]) & set(groups.iloc[test]))

def test_heldout_policy_pipeline_and_determinism():
    data=clean_fares(generate_fares(30,8)); groups=sorted(data.flight.unique()); train=data[data.flight.isin(groups[:20])]; held=data[data.flight.isin(groups[20:])]
    first=simulate(train,held,seed=3); second=simulate(train,held,seed=3)
    assert not first.empty and first.equals(second)
    assert set(first.policy)=={"book_immediately","fixed_21_day","random_day","advisor_v1","advisor_v2","oracle"}
    assert "flight" not in build_transitions(train).columns
    assert not summarize(first).empty


def test_model_smoke_recovers_signal_and_beats_baseline():
    from pathlib import Path

    import numpy as np

    from farewise.models.train import evaluate_models

    data=clean_fares(generate_fares(80,12))
    by_day=data.groupby("days_left").price.median()
    assert np.corrcoef(by_day.index.to_numpy(),by_day.to_numpy())[0,1] < 0
    output_dir=Path("models/test_smoke")
    result=evaluate_models(data,output_dir=output_dir,seed=12)
    summary=result["summary"].set_index("model")
    assert summary.loc["RandomForest","mae_inr"] < summary.loc["global_class","mae_inr"]
    assert (output_dir/"fare_model.joblib").exists()
    assert (output_dir/"metadata.json").exists()
