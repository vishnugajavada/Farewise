from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml


def check_deal(history: pd.Series, quote: float) -> dict[str, object]:
    if history.empty or quote <= 0:
        raise ValueError("A positive quote and non-empty fare history are required")
    p10, p50, p90 = history.quantile([.1, .5, .9]).tolist()
    percentile = float((history <= quote).mean() * 100)
    config=yaml.safe_load(Path("configs/advisor.yaml").read_text(encoding="utf-8"))["deal_percentiles"]
    label = "Great deal" if percentile <= config["great"] else "Fair" if percentile <= config["fair"] else "Above expected" if percentile <= config["above_expected"] else "Overpriced"
    return {"p10": float(p10), "p50": float(p50), "p90": float(p90), "percentile": percentile, "label": label}
