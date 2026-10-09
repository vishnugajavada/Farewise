# Remaining user actions

The project implementation and local checks are complete. The project is published to [GitHub](https://github.com/vishnugajavada/Farewise) on branch `main` (`af05147`, `d9f283a`). The remaining steps need dataset access or a signed-in Streamlit account:

1. Optional real-data evaluation: manually download the Kaggle Flight Price Prediction CSV, review its source licence and attribution requirements, place it in `data/raw/`, then run `data`, `train`, `evaluate` and `simulate`. No raw data should be committed.
2. Deploy: sign in to [Streamlit Community Cloud](https://share.streamlit.io/), choose the published repository and `main` branch, set the entry point to `src/farewise/ui/app.py`, select Python 3.11, then deploy. Root `requirements.txt` installs the project dependencies. The deployment must be started from your authenticated Streamlit account; after it returns the app URL, add it to the README.

The public Kaggle competition dataset listing is marked invitation-required, so no real CSV was obtained; synthetic evaluation remains clearly labeled. Local verification already completed with `.venv`: task-runner setup; 14 tests passed (89.66% coverage); Ruff passed; data, train, evaluate and simulate succeeded; the app started at `http://localhost:8501`.
