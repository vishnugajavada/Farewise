# Progress

Implemented the Windows task runner, deterministic synthetic and optional CSV ingestion, cleaning and schema reporting, fare features, model comparisons and artifacts, transition-based advice, group-held-out policy simulation, prediction/advice/data services and seven Streamlit pages.

The latest measured run is **SYNTHETIC**: 6,410 rows across 500 flight groups. Ridge won unseen-flight GroupKFold MAE at ₹2,793.54; LightGBM won the held-out days-left <=14 block at ₹4,459.52. Ridge's nominal 80% conformal interval coverage was 78.9%, below target. See `docs/EVALUATION.md` and `docs/MODEL_CARD.md`. SHAP global importance was generated; request-level explanation uses cohort shifts for the Ridge champion.

Verification with the project `.venv` on Python 3.13: setup completed; all 14 tests passed with 89.66% coverage; Ruff passed. Data preparation, training, evaluation, simulation, compileall and app startup at `http://localhost:8501` succeeded. A clean local initial commit (`af05147`) was created. There is no raw real-data CSV, so no real-fare performance is measured. No Git remote or GitHub CLI is configured, and publishing plus Streamlit Cloud deployment still require the destination repository and signed-in account; see `docs/USER_TODO.md`.
