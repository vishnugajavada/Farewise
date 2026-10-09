# Remaining user actions

The project implementation and local checks are complete. A clean initial commit exists locally (`af05147`). The remaining steps need dataset access or signed-in account choices:

1. Optional real-data evaluation: manually download the Kaggle Flight Price Prediction CSV, review its source licence and attribution requirements, place it in `data/raw/`, then run `data`, `train`, `evaluate` and `simulate`. No raw data should be committed.
2. Publish: no Git remote is configured and no GitHub CLI is installed. Connect the GitHub integration or add the destination repository as `origin`, then push branch `master` (or rename it to `main` first if you prefer).
3. Deploy: after the repository is pushed, sign in to Streamlit Community Cloud, choose that repository and branch, set the entry point to `src/farewise/ui/app.py`, select Python 3.11, then deploy. Root `requirements.txt` installs the project dependencies.

The public Kaggle competition dataset listing is marked invitation-required, so no real CSV was obtained; synthetic evaluation remains clearly labeled. Local verification already completed with `.venv`: task-runner setup; 14 tests passed (89.66% coverage); Ruff passed; data, train, evaluate and simulate succeeded; the app started at `http://localhost:8501`.
