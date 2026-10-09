# Remaining user actions

The project implementation and local checks are complete. The remaining steps need your local data/account choices:

1. Optional real-data evaluation: manually download the Kaggle Flight Price Prediction CSV, review its source licence and attribution requirements, place it in `data/raw/`, then run `data`, `train`, `evaluate` and `simulate`. No raw data should be committed.
2. Commit and publish: `.git` is exposed read-only in this workspace, so `git add`/`git commit` could not create `.git/index.lock`. In VS Code Source Control, review and stage the intended project files, commit, then publish the branch to your GitHub repository.
3. Deploy: sign in to Streamlit Community Cloud, create an app from the published repository and branch, set the entry point to `src/farewise/ui/app.py`, then deploy. The synthetic-data app is locally verified and runs without private data.

Local verification already completed with `.venv`: task-runner setup; 14 tests passed (89.66% coverage); Ruff passed; data, train, evaluate and simulate succeeded; the app started at `http://localhost:8501`.
