# Model card

## Intended use
FareWise provides exploratory estimates and historical decision support for Indian domestic fares. It is not a booking engine, live fare source, or travel recommendation.

## Data
This run used 6,410 seeded synthetic fare observations across 500 simulated flight groups, with 1–60 days-left values. No real CSV was present. Synthetic values do not represent measured market accuracy.

## Validation and measured results (SYNTHETIC)
Unseen-flight GroupKFold: Ridge MAE ₹2,794, RMSE ₹4,339, R² 0.695; RandomForest MAE ₹2,866, RMSE ₹4,424, R² 0.685; LightGBM MAE ₹2,885. Ridge had the lowest cross-validation MAE, so it is the current champion. Models beat the global class mean baseline (MAE ₹3,237) and route/class/day-bucket mean baseline (₹3,107).

Held-out days-left <=14 block: LightGBM MAE ₹4,460, RandomForest ₹4,821, Ridge ₹5,510 and best mean baseline (route/class, ₹5,344). Champion Ridge's 80% split-conformal intervals achieved 78.9% OOF coverage, below nominal 80%; mean interval width was ₹7,339. See `docs/EVALUATION.md` for all metrics.

## Limitations
No external real-fare validation has been performed. Current artifacts are trained on synthetic rows and should not be presented as actual fare guidance. The synthetic data includes deliberately simulated fare dynamics. LightGBM was measured in this run. SHAP global importance is saved; per-query explanation falls back to cohort median shifts for the Ridge champion.
