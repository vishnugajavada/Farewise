from __future__ import annotations

import numpy as np
import pandas as pd

REQUIRED = {"airline", "flight", "source_city", "departure_time", "stops", "arrival_time", "destination_city", "class", "duration", "days_left", "price"}

def clean_fares(frame: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    input_rows = len(frame)
    data = frame.drop(columns=[c for c in frame if c.lower().startswith("unnamed:")], errors="ignore").copy()
    before_dedup = len(data)
    data = data.drop_duplicates().reset_index(drop=True)
    duplicates_removed = before_dedup - len(data)
    if data.empty:
        raise ValueError("Input data must contain at least one fare row")
    for col in ["airline", "flight", "source_city", "departure_time", "stops", "arrival_time", "destination_city", "class"]:
        data[col] = data[col].astype(str).str.strip()
    data["days_left"] = pd.to_numeric(data.days_left, errors="raise").astype(int)
    data["duration"] = pd.to_numeric(data.duration, errors="raise")
    data["price"] = pd.to_numeric(data.price, errors="raise")
    if (data[["days_left", "duration", "price"]] <= 0).any().any():
        raise ValueError("days_left, duration, and price must be positive")
    data["stops_ordinal"] = data.stops.map({"zero": 0, "one": 1, "two_or_more": 2, "non-stop": 0, "1 stop": 1, "2+ stops": 2})
    if data["stops_ordinal"].isna().any():
        unknown = sorted(data.loc[data["stops_ordinal"].isna(), "stops"].unique())
        raise ValueError(f"Unrecognized stops values: {unknown}")
    if data.days_left.gt(365).any():
        raise ValueError("days_left must not exceed 365")
    airline_counts = data.groupby("flight", observed=True).airline.nunique()
    if airline_counts.gt(1).any():
        raise ValueError("Each flight code must map to exactly one airline")
    data["outlier_flag"] = False
    logp = np.log(data.price)
    groups = data.groupby(["source_city", "destination_city", "class"], observed=True).groups
    for indices in groups.values():
        values = logp.loc[indices]
        median = values.median()
        mad = (values - median).abs().median()
        if mad > 0:
            data.loc[indices, "outlier_flag"] = ((values - median).abs() > 4.5 * 1.4826 * mad).to_numpy()
    data.attrs["input_rows"] = input_rows
    data.attrs["duplicate_rows_removed"] = duplicates_removed
    data.attrs["outlier_rows_flagged"] = int(data.outlier_flag.sum())
    return data
