# Decisions

- `source: auto` reads the first CSV in `data/raw/`, otherwise it uses deterministic synthetic observations. No raw CSV was present for this evaluation.
- The synthetic panel fixes flight, route, class, schedule, stops and duration across horizons; it deliberately models fares that often rise closer to departure and includes rare generated anomalies. Rows at different horizons are not asserted to be the same real departure.
- Exact duplicate rows are dropped. Price outliers are flagged by a robust median absolute deviation rule on log fares and retained for transparent reporting. Unknown stop labels, invalid numeric ranges and flight-to-airline conflicts fail validation.
- Flight code is retained for grouping and excluded from model features. Unseen-flight evaluation uses GroupKFold; a separate near-departure block tests days_left <=14. Policy test flights are separate from model-transition training flights.
- Fare models target log(price). Split conformal intervals calibrate absolute fare residuals using held-out training groups. Actual coverage in the synthetic run was below nominal, so the shortfall is documented.
- The measured dependency set includes LightGBM and SHAP. Ridge is selected as champion by lowest unseen-flight GroupKFold MAE; LightGBM remains useful on the held-out near-departure block. Global SHAP summary is generated; request-time explanation falls back to cohort median shifts for the Ridge champion.
- The v1 advisor follows configured saving/risk thresholds. The v2 policy uses backward induction with training-only transition ratios. The simulation's hindsight oracle is for an upper bound only.
- Synthetic evaluation and policy results are not claims about market performance. The 2022 Kaggle snapshot lacks journey dates and repeated days-left observations may refer to different physical departures.
- Optional FastAPI remains deferred; the validated Python services and Streamlit UI cover the intended local demo.
- The trip input uses a date picker and converts the selected travel date to a days-left feature; explanation rows are presented as readable fare-signal cards, and the bundled hero photo plus explicit light theme keeps the UI self-contained across local, Docker and Community Cloud runs.
- Sidebar navigation uses selected-state buttons rather than radio controls; the form submit button forces high-contrast white text for legibility.
