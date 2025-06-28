import polars as pl
import pickle
from sklearn.multioutput import MultiOutputRegressor
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score
from sklearn.metrics import make_scorer

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

params = {
    "n_estimators": 212,
    "learning_rate": 0.002587,
    "max_depth": 9,
    "reg_alpha": 0.004842,
    "reg_lambda": 0.092771,
    "subsample": 0.807007,
    "colsample_bytree": 0.811025,
    "min_child_weight": 1,
    "grow_policy": "depthwise",
    "max_leaves": 0,
}


reg = MultiOutputRegressor(
    XGBRegressor(
        **params,
        sampling_method="uniform",
        tree_method="hist",
        n_jobs=-1,
        objective="reg:squarederror",
        seed=23,
    )
)

y = df[["Latitude", "Longitude"]].to_numpy()

X = df.drop(["Latitude", "Longitude", "cluster"], axis=1).to_numpy()

scorer = make_scorer(score_func=haversine_np, greater_is_better=False)

scores = cross_val_score(reg, X, y, scoring=scorer, cv=CustomCV(folds, df["cluster"]))

print(f"Mean = {scores.mean()} | Stddev = {scores.std()}\n")

print("Scores:\n", scores)

reg.fit(X, y)

feature_names = df.drop(["Latitude", "Longitude", "cluster"], axis=1).columns
for i, target_name in enumerate(["Latitude", "Longitude"]):
    model = reg.estimators_[i]
    importances = model.feature_importances_

    importance_df = pl.DataFrame(
        {"Feature": feature_names, "Importance": importances}
    ).sort("Importance", descending=True)

    print(f"\nTop 10 Feature Importance for {target_name}")
    print(importance_df.head(10))


y_pred = reg.predict(X)

plt.figure(figsize=(8, 6))
plt.scatter(y[:, 1], y[:, 0], c="blue", label="True", alpha=0.5, s=10)
plt.scatter(y_pred[:, 1], y_pred[:, 0], c="red", label="Predicted", alpha=0.5, s=10)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend()
plt.title("True vs Predicted Locations")
plt.grid(True)
plt.tight_layout()
plt.show()
