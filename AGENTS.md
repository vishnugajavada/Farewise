# FareWise agent rules

Use `PROJECT_SPEC.md`, `docs/PLAN.md` and `docs/PROGRESS.md` as project context. No external APIs, keys, scraping, paid services or runtime network calls. Raw datasets must not be committed. Use deterministic generators and group-aware validation. Keep business logic in service/model/advisor modules, not Streamlit. Every metric in docs/UI must come from an actual run and synthetic findings must be labeled. Update decisions and progress after behavior changes. Run the Windows workflow with `python scripts/tasks.py <setup|data|train|evaluate|simulate|app|test|lint>`.
