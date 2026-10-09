from __future__ import annotations

from pathlib import Path

import yaml

from farewise.data.clean import REQUIRED
from farewise.data.loader import load_data

config=yaml.safe_load(Path("configs/data.yaml").read_text(encoding="utf-8"))
data=load_data()
out=Path(config.get("processed_path","data/processed/fares.parquet"))
out.parent.mkdir(parents=True,exist_ok=True)
try:
    data.to_parquet(out,index=False)
except ImportError:
    out=out.with_suffix(".csv")
    data.to_csv(out,index=False)
csvs=sorted(Path(config.get("raw_dir","data/raw")).glob("*.csv"))
source=f"CSV: {csvs[0].name}" if csvs else "seeded synthetic generator"
panel=data.groupby(["flight","source_city","destination_city","class"]).days_left.nunique()
report=(f"# Data quality report\n\nSource: {source}\n\nInput rows: {data.attrs.get('input_rows',len(data))}\n\nClean rows: {len(data)}\n\nExact duplicate rows removed: {data.attrs.get('duplicate_rows_removed',0)}\n\nRequired schema columns: {', '.join(sorted(REQUIRED))}\n\nDays left range: {data.days_left.min()}–{data.days_left.max()}\n\nDuration range (hours): {data.duration.min():.2f}–{data.duration.max():.2f}\n\nFare range (INR): {data.price.min():.2f}–{data.price.max():.2f}\n\nClass counts: {data['class'].value_counts().to_dict()}\n\nStops counts: {data.stops.value_counts().to_dict()}\n\nFlagged price outliers (retained): {data.attrs.get('outlier_rows_flagged',int(data.outlier_flag.sum()))}\n\nDistinct horizons per flight-route-class panel: min {panel.min()}, median {panel.median():.0f}, max {panel.max()}\n\nRows at different horizons may represent different physical departures. Synthetic values are illustrative, not observed market data.\n")
Path("docs/DATA_SOURCES.md").write_text(report,encoding="utf-8")
print(f"Wrote {len(data)} rows to {out}")
