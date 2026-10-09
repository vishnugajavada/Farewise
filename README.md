# FareWise

FareWise estimates domestic flight fare ranges and gives explainable, historically grounded book-or-wait guidance. It supports a manually downloaded CSV or a deterministic synthetic demo. There are no APIs, keys, or runtime network calls. Synthetic results are demonstrations, not evidence of real fare performance.

## Architecture

```mermaid
flowchart LR
  D[CSV or seeded synthetic panel] --> C[Schema checks and cleaning]
  C --> F[Feature builder]
  F --> M[Group-aware models and calibration]
  C --> T[Training-only fare transitions]
  M --> E[Evaluation and held-out policy simulation]
  T --> E
  E --> S[Validated Python services]
  S --> U[Streamlit pages]
```

## Windows PowerShell quick start

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe scripts\tasks.py setup
.venv\Scripts\python.exe scripts\tasks.py data
.venv\Scripts\python.exe scripts\tasks.py train
.venv\Scripts\python.exe scripts\tasks.py evaluate
.venv\Scripts\python.exe scripts\tasks.py simulate
.venv\Scripts\python.exe scripts\tasks.py test
.venv\Scripts\python.exe scripts\tasks.py lint
.venv\Scripts\python.exe scripts\tasks.py app
```

`data` selects the first CSV under `data/raw/` when available (`source: auto` in `configs/data.yaml`); otherwise it creates synthetic observations. `train`, `evaluate`, and `simulate` save artifacts and CSV outputs under `models/` and `data/processed/`. LightGBM is included in the project dependencies and compared when importable.

## Latest measured results

The current evaluation is **SYNTHETIC** and appears in [docs/EVALUATION.md](docs/EVALUATION.md). It includes unseen-flight GroupKFold and a held-out near-departure days-left block. Ridge and RandomForest are compared against three mean baselines; interval coverage uses a training-group calibration split. Do not interpret these simulated results as live or real-fare accuracy.

| Validation (SYNTHETIC) | Model / policy | MAE or mean saving (INR) |
| --- | --- | ---: |
| Unseen-flight GroupKFold MAE | Ridge | 2,793.54 |
| Unseen-flight GroupKFold MAE | RandomForest | 2,865.74 |
| Unseen-flight GroupKFold MAE | Best mean baseline (route/class/day bucket) | 3,106.94 |
| Held-out days-left <=14 MAE | LightGBM | 4,459.52 |
| Held-out days-left <=14 MAE | Best mean baseline (route/class) | 5,344.06 |
| Held-out policy mean saving vs book now | Advisor v1 / v2 | 0.00 |
| Held-out policy mean saving vs book now | Fixed 21-day rule | -135.68 |
| Held-out policy mean saving vs book now | Random day | -383.90 |

Ridge is the selected champion by unseen-flight mean absolute error; LightGBM performs best on the near-departure block. The champion's nominal 80% conformal interval achieved 78.9% coverage, below target. Both advisors tied immediate booking in this synthetic policy run; the hindsight oracle averaged ₹1,336.48 saving and is not an implementable strategy. SHAP global summary was generated; per-query explanations use a cohort fallback for the Ridge champion. Full results and downside slices are in `docs/EVALUATION.md`.

| Evidence | Output |
| --- | --- |
| Fold metrics and interval coverage | `models/fold_metrics.csv` |
| Validation summary | `models/evaluation_summary.csv` |
| Slice metrics, permutation drivers and SHAP summary | `models/slice_metrics.csv`, `models/drivers.csv`, `models/shap_summary.csv` |
| Fare-vs-days-left cohorts | `models/fare_curves.csv` |
| Held-out policy outcomes | `data/processed/policy_simulation.csv` |

## Data and limitations

To use real data, download the Kaggle **Flight Price Prediction** (EaseMyTrip) CSV manually and place it in `data/raw/`. Review the source's current licence/attribution conditions before using or redistributing it. The widely circulated snapshot covers Feb–Mar 2022 and has no journey date, so repeated days-left rows may describe different physical departures. Synthetic panels cannot establish real-world predictive quality. The advice is descriptive decision support, never a guarantee or travel recommendation.

## Docker

Build and run with `docker compose up --build`, then open `http://localhost:8501`.

## Streamlit Community Cloud

1. Push this repository to GitHub.
2. Sign in to Streamlit Community Cloud and choose **Create app**.
3. Select the repository and branch; set the main file to `src/farewise/ui/app.py`.
4. Deploy. The app starts on synthetic data without the private raw CSV.
