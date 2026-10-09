# Evaluation results

All reported metrics below come from the current run. Label: **SYNTHETIC** unless a manually supplied raw CSV was loaded.

## Unseen-flight GroupKFold
| validation | model | mae_inr | rmse_inr | smape_percent | r2_price | r2_log_price | interval80_coverage | interval80_mean_width_inr | pinball_p10 | pinball_p90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unseen-flight GroupKFold | LightGBM | 2885.45 | 4453.48 | 31.74 | 0.68 | 0.62 | 0.79 | 7695.23 | 727.74 | 854.75 |
| unseen-flight GroupKFold | RandomForest | 2865.74 | 4423.95 | 31.66 | 0.69 | 0.63 | 0.79 | 7472.97 | 724.00 | 833.78 |
| unseen-flight GroupKFold | Ridge | 2793.54 | 4339.50 | 30.87 | 0.70 | 0.65 | 0.79 | 7339.55 | 703.03 | 830.44 |
| unseen-flight GroupKFold | global_class | 3237.45 | 5205.41 | 34.48 | 0.56 | 0.52 | — | — | — | — |
| unseen-flight GroupKFold | route_class | 3627.41 | 5912.62 | 36.92 | 0.43 | 0.45 | — | — | — | — |
| unseen-flight GroupKFold | route_class_days | 3106.94 | 5088.02 | 32.30 | 0.58 | 0.60 | — | — | — | — |

Unseen-flight MAE winner: Ridge (₹2793.54); strongest listed mean baseline: route_class_days (₹3106.94).

## Held-out days-left block (days_left <= 14)
| mae_inr | rmse_inr | smape_percent | r2_price | r2_log_price | model | validation | rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5509.76 | 8424.60 | 47.28 | 0.31 | 0.16 | Ridge | held-out days_left <=14 | 2078.00 |
| 4820.79 | 7176.34 | 42.97 | 0.50 | 0.37 | RandomForest | held-out days_left <=14 | 2078.00 |
| 4459.52 | 7093.53 | 35.91 | 0.51 | 0.51 | LightGBM | held-out days_left <=14 | 2078.00 |
| 5450.66 | 8380.22 | 46.37 | 0.31 | 0.19 | global_class | held-out days_left <=14 | 2078.00 |
| 5344.06 | 8199.63 | 45.75 | 0.34 | 0.21 | route_class | held-out days_left <=14 | 2078.00 |
| 5344.06 | 8199.63 | 45.75 | 0.34 | 0.21 | route_class_days | held-out days_left <=14 | 2078.00 |

Near-departure MAE winner: LightGBM (₹4459.52).

Model comparisons use identical folds; flight groups do not cross train/test boundaries. Conformal calibration groups are excluded from fit. LightGBM is omitted when unavailable. Actual interval coverage and calibration width are reported above. Slice metrics, permutation-importance drivers and a global SHAP summary are saved under `models/`; per-query cohort driver shifts are not SHAP values.

## Held-out flight policy simulation (SYNTHETIC)

Training and transition statistics use a separate 80% flight-group partition; the policies run on the remaining 20% and only use current observed fares plus training-derived transitions. The oracle uses hindsight and is an upper bound. Route/class/start-day detailed rows are in `data/processed/policy_summary.csv`; individual outcomes are in `data/processed/policy_simulation.csv`.

| policy | mean_saving_inr | median_saving_inr | win_rate | mean_regret_inr | worst_downside_inr | p10_saving_inr | flights |
| --- | --- | --- | --- | --- | --- | --- | --- |
| advisor_v1 | 0.00 | 0.00 | 0.00 | 1336.48 | 0.00 | 0.00 | 100.00 |
| advisor_v2 | 0.00 | 0.00 | 0.00 | 1336.48 | 0.00 | 0.00 | 100.00 |
| book_immediately | 0.00 | 0.00 | 0.00 | 1336.48 | 0.00 | 0.00 | 100.00 |
| fixed_21_day | -135.68 | -109.89 | 0.43 | 1472.16 | -9838.03 | -1527.66 | 100.00 |
| oracle | 1336.48 | 822.36 | 0.86 | 0.00 | 0.00 | 0.00 | 100.00 |
| random_day | -383.90 | -117.59 | 0.36 | 1720.38 | -12444.72 | -1732.43 | 100.00 |
