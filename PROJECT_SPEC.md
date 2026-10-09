# FareWise project specification

FareWise is an explainable fare range and book-now-or-wait prototype for Indian domestic routes. It works offline with a deterministic synthetic panel and optionally with a manually downloaded Kaggle Flight Price Prediction CSV. It has no live pricing connections.

## Requirements

- Python 3.11+, typed source layout under `src/farewise`, Windows task runner, Streamlit UI, Docker files and CI.
- Validate the expected columns `airline`, `flight`, `source_city`, `departure_time`, `stops`, `arrival_time`, `destination_city`, `class`, `duration`, `days_left`, `price`. Normalize categories, remove exact duplicates, flag robust log-price outliers and fail on invalid schema/ranges.
- Generate deterministic panel-shaped synthetic observations. Build direction-aware routes, ordered day-left/time features and airline tiers from config.
- Compare class, route/class, and route/class/day-bucket mean baselines with Ridge, RandomForest and LightGBM using unseen-flight GroupKFold and held-out day-left blocks. Report INR errors, sMAPE, R², interval coverage/pinball loss, slices and model artifacts.
- Build empirical price-transition cohorts with fallback. Offer thresholded short-wait advice, a backward-induction policy and quote percentile labels.
- Simulate on held-out flights against immediate, fixed 21-day, random, v1, v2 and hindsight policies. Report savings, regret and downside.
- Expose typed service functions to seven Streamlit pages. Keep data window, uncertainty and limitations visible.
- Never invent evaluation results. Label synthetic findings; report failures to beat baselines.

See `docs/PROGRESS.md` for implementation and verification status.
