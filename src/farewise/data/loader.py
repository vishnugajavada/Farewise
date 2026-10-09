from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from farewise.data.clean import clean_fares
from farewise.data.synthetic import generate_fares


def load_data(config_path: str | Path = "configs/data.yaml") -> pd.DataFrame:
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    raw = Path(config.get("raw_dir", "data/raw"))
    csvs = sorted(raw.glob("*.csv")) if raw.exists() else []
    source = config.get("source", "auto")
    if source not in {"auto", "csv", "synthetic"}:
        raise ValueError("source must be auto, csv, or synthetic")
    if source == "csv" and not csvs:
        raise FileNotFoundError(f"No CSV files found under {raw}")
    if csvs and source in {"auto", "csv"}:
        frame = pd.read_csv(csvs[0])
    else:
        frame = generate_fares(int(config.get("synthetic_flights", 500)), int(config.get("seed", 42)))
    return clean_fares(frame)
