import numpy as np
import pandas as pd
import pytest

from farewise.advisor.deal import check_deal
from farewise.advisor.heuristic import advise, choose_wait
from farewise.advisor.optimal_stopping import optimal_book_day, solve
from farewise.advisor.transitions import build_transitions, ratio_samples
from farewise.data.clean import clean_fares
from farewise.data.synthetic import generate_fares
from farewise.evaluation.metrics import pinball_loss, smape
from farewise.features.build import build_features
from farewise.service.city_service import canonical_city, get_indian_cities
from farewise.service.predict_service import FareQuery


def test_generator_is_deterministic():
    pd.testing.assert_frame_equal(generate_fares(8,3),generate_fares(8,3))

def test_clean_schema_duplicates_and_invalid_values():
    frame=generate_fares(5,3); frame["Unnamed: 0"]=range(len(frame)); frame=pd.concat([frame,frame.iloc[[0]]],ignore_index=True)
    cleaned=clean_fares(frame); assert len(cleaned)==len(frame)-1 and "Unnamed: 0" not in cleaned
    with pytest.raises(ValueError,match="Missing"):clean_fares(pd.DataFrame())
    frame=generate_fares(2,1);frame.loc[0,"price"]=-3
    with pytest.raises(ValueError):clean_fares(frame)

def test_features_keep_direction_and_buckets():
    frame=clean_fares(generate_fares(8,2)); features=build_features(frame)
    assert features.route.str.contains("→").all() and "days_bucket" in features and "flight" not in features

def test_advisor_choose_wait_and_backward_induction():
    assert advise(4000,3000,.1)["action"]=="WAIT 1 DAYS"
    assert choose_wait(4000,{1:3000},{1:.1},500,.3)["wait_days"]==1
    assert optimal_book_day({1:100,2:120})==1
    # At day 2, paying 105 beats an expected continuation value of 110.
    assert solve({1:100,2:105},{2:[1.1]})==(2,105)
    # At day 2, wait when today's quote is 120 and expected continuation is 110.
    assert solve({1:100,2:120},{2:[.8]})==(1,96)
    with pytest.raises(ValueError):solve({},[])

def test_transitions_build_and_fallback():
    frame=clean_fares(generate_fares(12,5)); transitions=build_transitions(frame,min_samples=5)
    assert len(transitions)>0 and transitions.ratio.gt(0).all()
    row=frame.iloc[0]; selected=ratio_samples(transitions,f"{row.source_city}->{row.destination_city}",row["class"],"low_cost","31+")
    assert len(selected)>0

def test_deal_percentile_and_validation():
    result=check_deal(pd.Series([10,20,30,40,50]),5);assert result["label"]=="Great deal" and result["percentile"]==0
    with pytest.raises(ValueError):check_deal(pd.Series(dtype=float),10)

def test_metrics():
    assert smape(np.array([0.,10.]),np.array([0.,10.]))==0
    assert pinball_loss(np.array([1.,2.]),np.array([0.,3.]),.5)==.5

def test_query_validates_route():
    with pytest.raises(ValueError):FareQuery(source="Delhi",destination="Delhi",days_left=3)
    assert FareQuery(source="Delhi",destination="Mumbai",days_left=7).days_left==7

def test_indian_airport_city_catalog_and_aliases():
    cities = get_indian_cities()
    assert len(cities) >= 100
    assert {"Delhi", "Mumbai", "Chennai", "Guwahati", "Goa"}.issubset(cities)
    assert canonical_city("Bengaluru") == "Bangalore"
    assert canonical_city("Prayagraj") == "Allahabad"


def test_invalid_stop_mapping_and_airline_consistency():
    bad_stops=generate_fares(2,21);bad_stops.loc[0,"stops"]="mystery"
    with pytest.raises(ValueError,match="Unrecognized stops"):clean_fares(bad_stops)
    bad_airline=generate_fares(3,22);bad_airline.loc[1,"airline"]="Other"
    with pytest.raises(ValueError,match="exactly one airline"):clean_fares(bad_airline)

def test_transition_fallbacks_and_empty_input():
    frame=clean_fares(generate_fares(6,25));transitions=build_transitions(frame,min_samples=500)
    assert transitions.cohort_fallback.all()
    assert len(ratio_samples(transitions,"unknown-route","Economy","unknown","31+"))>0
    assert len(build_transitions(frame.iloc[:0]))==0

def test_service_prediction_advice_deal_and_routes():
    from farewise.service.advise_service import advise_route
    from farewise.service.data_service import fare_curves, route_summary
    from farewise.service.deal_service import check_quote
    from farewise.service.predict_service import predict_fare
    data=clean_fares(generate_fares(15,31));row=data.iloc[0]
    query=FareQuery(source=row.source_city,destination=row.destination_city,days_left=int(row.days_left),fare_class=row["class"])
    assert predict_fare(data,query)["available"]
    assert advise_route(data,query,float(row.price))["data_rows"]>0
    assert check_quote(data,query,float(row.price))["available"]
    assert not route_summary(data).empty
    assert not fare_curves(data,query.source,query.destination,query.fare_class).empty
