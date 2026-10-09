# Build plan

- [x] A. Project scaffold, Windows task runner, CI and container files
- [x] B. Seeded synthetic and auto-selected CSV loader, schema validation, cleaning, outlier flags and data report
- [x] C. Route, time, stops, duration, airline tier and days-left features
- [x] D. Ridge/RandomForest/LightGBM, three baselines, unseen-flight GroupKFold, held-out days-left block, split-conformal intervals, slices and artifacts implemented and measured; interval coverage is below nominal
- [x] E. Ratio transition cohorts with fallback, configurable v1 advice, backward-induction v2 solver and deal percentiles
- [x] F. Held-out-flight comparison of immediate, fixed, random, v1, v2 and hindsight policies; route/class/start-day output
- [x] G. Validated Pydantic input and Python service functions for prediction, advice, data summaries and deal checks
- [x] H. Seven Streamlit pages; app startup verified locally
- [ ] I. Optional FastAPI API deferred because the preceding stages are not fully verified
- [x] J. Documentation and deployment files created; pytest and Ruff pass in the project environment
