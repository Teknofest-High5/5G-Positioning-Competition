import os
from pathlib import Path
import polars as pl
import pickle
from sklearn.ensemble import StackingRegressor
from sklearn.multioutput import MultiOutputRegressor
from lightgbm import LGBMRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score
from sklearn.metrics import make_scorer
import optuna
import webbrowser
from datetime import datetime
from xgboost import XGBRegressor
from cell_util.ml import CustomCV
from calculations_util.distance import haversine_np

df = (
    pl.read_parquet("data/parquet/processed/dl.with_cluster_cell_info.parquet")
    .drop_nulls(["Longitude", "Latitude"])
    .select(
        "pl_distance",
        "log1p_pl_distance",
        "pl_per_meter",
        "pl_predicted_longitude",
        "pl_predicted_latitude",
        "throughput_per_meter",
        "spectral_efficiency",
        "sinr_per_meter",
        "sinr_over_rsrp",
        "signal_loss_ratio",
        "rsrq_delta",
        "rsrp_delta",
        "scaled_loss_ratio",
        "mimo_throughput_potential",
        "mimo_distance_ratio",
        "sinr_per_antenna",
        "efficiency_per_antenna",
        "modulation_efficiency",
        "mimo_nn0_cell",
        "mimo_nn1_cell",
        "mimo_nn2_cell",
        "mimo_nn3_cell",
        "Longitude",
        "Latitude",
        "NR_UE_Pathloss_DL_0",
        "Longitude_nn0_cell",
        "Latitude_nn0_cell",
        "Longitude_nn1_cell",
        "Latitude_nn1_cell",
        "Longitude_nn2_cell",
        "Latitude_nn2_cell",
        "Longitude_nn3_cell",
        "Latitude_nn3_cell",
        "Azimuth_nn0_cell_cos",
        "Azimuth_nn0_cell_sin",
        "Azimuth_nn1_cell_cos",
        "Azimuth_nn1_cell_sin",
        "Azimuth_nn2_cell_cos",
        "Azimuth_nn2_cell_sin",
        "Azimuth_nn3_cell_cos",
        "Azimuth_nn3_cell_sin",
        "directional_rsrp_nn0_lon",
        "directional_rsrp_nn0_lat",
        "directional_rsrp_nn1_lon",
        "directional_rsrp_nn1_lat",
        "directional_rsrp_nn2_lon",
        "directional_rsrp_nn2_lat",
        "directional_rsrp_nn3_lon",
        "directional_rsrp_nn3_lat",
        "cluster",
        "NR_UE_RSRP_0",
        "NR_UE_Nbr_RSRP_0",
        "NR_UE_Nbr_RSRP_1",
        "NR_UE_Nbr_RSRP_2",
        "NR_UE_Nbr_RSRP_3",
        "NR_UE_SINR_0",
        "NR_UE_RB_Num_DL_0",
        "NR_UE_RSRQ_0",
        "NR_UE_Nbr_RSRQ_0",
        "NR_UE_Nbr_RSRQ_1",
        "NR_UE_Nbr_RSRQ_2",
        "NR_UE_Nbr_RSRQ_3",
        "NR_UE_BLER_DL_0",
        "NR_UE_Timing_Advance",
        "rach_attempt",
        "rach_ok",
        "ho_attempt",
        "ho_ok",
        "App_Throughput_DL",
        "NR_UE_Throughput_PDCP_DL",
        "NR_UE_Ack_As_Nack_DL_0",
        "NR_UE_NACK_Rate_DL_0",
        "NR_UE_Power_Tx_PUSCH_0",
        "NR_UE_Power_Tx_PRACH_0",
        "NR_UE_NACK_Rate_UL_0",
        "modulation_avg_encoded",
        "modulation_avg_log2_bits",
        "cce_level_encoded",
        "mcs_index",
        "centroid_lon_nn0_cell_coverage",
        "centroid_lat_nn0_cell_coverage",
        "centroid_lon_nn1_cell_coverage",
        "centroid_lat_nn1_cell_coverage",
        "centroid_lon_nn2_cell_coverage",
        "centroid_lat_nn2_cell_coverage",
        "centroid_lon_nn3_cell_coverage",
        "centroid_lat_nn3_cell_coverage",
        "intersection_2_centroid_lon",
        "intersection_2_centroid_lat",
    )
    .to_pandas()
)

with open("data/folds/folds.pkl", "rb") as f:
    folds = pickle.load(f)


y = df[["Latitude", "Longitude"]].to_numpy()

X = df.drop(["Latitude", "Longitude", "cluster"], axis=1).to_numpy()

scorer = make_scorer(score_func=haversine_np, greater_is_better=False)


def objective(trial):
    n_estimators = trial.suggest_int("n_estimators", 100, 700)
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 0.01)
    max_depth = trial.suggest_int("max_depth", 3, 20)
    # gamma = trial.suggest_float("gamma", 0.0, 1e-6) # trials may stuck at score -850.9125320592835 when upper bound = 1-e2 or higher
    reg_alpha = trial.suggest_float("reg_alpha", 1e-4, 0.20)
    reg_lambda = trial.suggest_float("reg_lambda", 0.0, 0.15)
    subsample = trial.suggest_float("subsample", 0.5, 1.0)
    colsample_bytree = trial.suggest_float("colsample_bytree", 0.5, 1.0)
    #colsample_bylevel = trial.suggest_float("colsample_bylevel", 0.5, 1.0)
    #colsample_bynode = trial.suggest_float("colsample_bynode", 0.5, 1.0)
    min_child_weight = trial.suggest_int("min_child_weight", 1, 60)
    grow_policy = trial.suggest_categorical("grow_policy", ["depthwise", "lossguide"])

    if grow_policy == "lossguide":
        max_leaves, max_depth = trial.suggest_int("max_leaves", 16, 512), 0
    else:
        max_leaves = 0

    xgb = XGBRegressor(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        max_leaves=max_leaves,
        reg_alpha=reg_alpha,
        reg_lambda=reg_lambda,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        min_child_weight=min_child_weight,
        grow_policy=grow_policy,
        sampling_method="uniform",
        tree_method="hist",
        n_jobs=-1,
        objective="reg:squarederror",
        seed=23,
    )

    """
    lgbm_n_estimators = trial.suggest_int("lgbm_n_estimators", 100, 600)
    lgbm_learning_rate = trial.suggest_float("lgbm_learning_rate", 1e-3, 0.01)
    lgbm_max_depth = trial.suggest_int("lgbm_max_depth", 3, 12)
    lgbm_reg_alpha = (trial.suggest_float("lgbm_reg_alpha", 0.0, 0.15),)
    lgbm_reg_lambda = (trial.suggest_float("lgbm_reg_lambda", 0.0, 0.15),)
    lgbm_importance_type = (
        trial.suggest_categorical("lgbm_importance_type", ["split", "gain"]),
    )
    lgbm_subsample = trial.suggest_float("lgbm_subsample", 0.8, 1.0)

    lgbm = LGBMRegressor(
        n_estimators=lgbm_n_estimators,
        learning_rate=lgbm_learning_rate,
        max_depth=lgbm_max_depth,
        reg_alpha=lgbm_reg_alpha,
        reg_lambda=lgbm_reg_lambda,
        subsample=lgbm_subsample,
        importance_type=lgbm_importance_type,
        objective="regression",
        n_jobs=-1,
        random_state=23,
        verbose=-1,
    )
    """

    #degree = trial.suggest_int("poly_degree", 1, 4)
    """
    meta_learner = make_pipeline(
        PolynomialFeatures(degree=degree, include_bias=False),
        RandomForestRegressor(n_estimators=100, random_state=23, n_jobs=-1),
    )

    stacking = StackingRegressor(
        estimators=[("xgb", xgb)],
        final_estimator=meta_learner,
        n_jobs=-1,
    )
    """
    model = MultiOutputRegressor(xgb)

    scores = cross_val_score(
        model, X, y, scoring=scorer, cv=CustomCV(folds, df["cluster"])
    )
    return scores.mean()


study = optuna.create_study(
    direction="maximize", sampler=optuna.samplers.RandomSampler(seed=23)
)
# study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=23))

study.optimize(objective, n_trials=4000, n_jobs=5)
print(f"\nBest Parameters:\n{study.best_params}\n")


os.makedirs("optuna/plots", exist_ok=True)
os.makedirs("optuna/trial-data", exist_ok=True)

timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
study.trials_dataframe().to_csv(f"optuna/trial-data/optuna_trials_{timestamp}.csv")

fig_hist = optuna.visualization.plot_optimization_history(study)
fig_hist.write_html(f"optuna/plots/optimization_history_{timestamp}.html")

fig_imp = optuna.visualization.plot_param_importances(study)
fig_imp.write_html(f"optuna/plots/param_importances_{timestamp}.html")

fig_slice = optuna.visualization.plot_slice(
    study, params=list(study.best_trial.params.keys())
)
fig_slice.write_html(f"optuna/plots/param_slice_{timestamp}.html")

open_webbrowser = True
if open_webbrowser:
    webbrowser.open(
        Path(f"optuna/plots/optimization_history_{timestamp}.html").resolve().as_uri()
    )
    webbrowser.open(
        Path(f"optuna/plots/param_importances_{timestamp}.html").resolve().as_uri()
    )
    webbrowser.open(
        Path(f"optuna/plots/param_slice_{timestamp}.html").resolve().as_uri()
    )
