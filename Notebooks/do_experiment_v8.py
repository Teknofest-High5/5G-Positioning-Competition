# runs base station and neighbor models with optuna parameters and logs the best scores to a markdown table.
from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import KFold
from cell_util.ml import custom_cross_val_score
from calculations_util.distance import haversine_np_utm
import polars as pl
from pyproj import Transformer
from pyproj import Geod
import pickle
import glob
import os

geod = Geod(ellps="WGS84")

os.makedirs("model_scores", exist_ok=True)
with open("model_scores/model_scores_2_cells.md", "w") as f:
    f.write(
        "| Cell | Neighbor Cell | Mean of Fold Means | Max of Fold Means | Mean of Fold Max | Max of Fold Max |\n"
    )
    f.write("|---|---|---|---|---|---|\n")

data = pl.read_parquet(
    "data/parquet/processed/concat_dl_ul_cell_info.parquet"
).drop_nulls(["Longitude", "Latitude"])

transformer = Transformer.from_crs("EPSG:4326", "EPSG:32635", always_xy=True)

column_pairs = [
    ("Longitude", "Latitude"),
    ("Longitude_nn0_cell", "Latitude_nn0_cell"),
    ("Longitude_nn1_cell", "Latitude_nn1_cell"),
    ("Longitude_nn2_cell", "Latitude_nn2_cell"),
    ("Longitude_nn3_cell", "Latitude_nn3_cell"),
    ("pl_predicted_longitude", "pl_predicted_latitude"),
    ("centroid_lon_nn0_cell_coverage", "centroid_lat_nn0_cell_coverage"),
    ("centroid_lon_nn1_cell_coverage", "centroid_lat_nn1_cell_coverage"),
    ("centroid_lon_nn2_cell_coverage", "centroid_lat_nn2_cell_coverage"),
    ("centroid_lon_nn3_cell_coverage", "centroid_lat_nn3_cell_coverage"),
]

for lon_col, lat_col in column_pairs:
    if lon_col in data.columns and lat_col in data.columns:
        lon_array = data.select(lon_col).to_numpy().flatten()
        lat_array = data.select(lat_col).to_numpy().flatten()

        longitude, latitude = transformer.transform(lon_array, lat_array)

        data = data.with_columns(
            [
                pl.Series(lon_col, longitude),
                pl.Series(lat_col, latitude),
            ]
        )

data = data.select(
    "log1p_pl_distance",
    "pl_distance",
    "scaled_loss_ratio",
    "mimo_nn0_cell",
    "mimo_nn1_cell",
    "mimo_nn2_cell",
    "mimo_nn3_cell",
    "NR_UE_BLER_DL_0",
    "App_Throughput_DL",
    "NR_UE_Ack_As_Nack_DL_0",
    "NR_UE_NACK_Rate_DL_0",
    "NR_UE_Power_Tx_PUSCH_0",
    "NR_UE_Power_Tx_PRACH_0",
    "NR_UE_NACK_Rate_UL_0",
    "modulation_avg_log2_bits",
    "NR_UE_RSRP_0_mw",
    "NR_UE_Nbr_RSRP_0_mw",
    "NR_UE_Nbr_RSRP_1_mw",
    "NR_UE_Nbr_RSRP_2_mw",
    "NR_UE_Nbr_RSRP_3_mw",
    "NR_UE_RSRQ_0_mw",
    "NR_UE_Nbr_RSRQ_0_mw",
    "NR_UE_Nbr_RSRQ_1_mw",
    "NR_UE_Nbr_RSRQ_2_mw",
    "NR_UE_Nbr_RSRQ_3_mw",
    "NR_UE_SINR_0_mw",
    "NR_UE_Pathloss_DL_0_mw",
    "NR_UE_Power_Tx_PUSCH_0_mw",
    "NR_UE_Power_Tx_PRACH_0_mw",
    "rsrp_best_neighbor_diff",
    "rsrq_best_neighbor_diff",
    "NR_UE_RSRP_0",
    "NR_UE_RSRQ_0",
    "NR_UE_SINR_0",
    "NR_UE_Nbr_RSRP_0",
    "NR_UE_Nbr_RSRP_1",
    "NR_UE_Nbr_RSRP_2",
    "NR_UE_Nbr_RSRP_3",
    "NR_UE_Nbr_RSRQ_0",
    "NR_UE_Nbr_RSRQ_1",
    "NR_UE_Nbr_RSRQ_2",
    "NR_UE_Nbr_RSRQ_3",
    "Longitude",
    "Latitude",
    "Longitude_nn0_cell",
    "Latitude_nn0_cell",
    "directional_rsrp_nn0_lon",
    "directional_rsrp_nn0_lon_mw",
    "directional_rsrp_nn0_lat",
    "directional_rsrp_nn0_lat_mw",
    "directional_rsrp_nn1_lon",
    "directional_rsrp_nn1_lon_mw",
    "directional_rsrp_nn1_lat",
    "directional_rsrp_nn1_lat_mw",
    "directional_rsrp_nn2_lon",
    "directional_rsrp_nn2_lon_mw",
    "directional_rsrp_nn2_lat",
    "directional_rsrp_nn2_lat_mw",
    "directional_rsrp_nn3_lon",
    "directional_rsrp_nn3_lon_mw",
    "directional_rsrp_nn3_lat",
    "directional_rsrp_nn3_lat_mw",
    "directional_rsrq_nn0_lon",
    "directional_rsrq_nn0_lon_mw",
    "directional_rsrq_nn0_lat",
    "directional_rsrq_nn0_lat_mw",
    "directional_rsrq_nn1_lon",
    "directional_rsrq_nn1_lon_mw",
    "directional_rsrq_nn1_lat",
    "directional_rsrq_nn1_lat_mw",
    "directional_rsrq_nn2_lon",
    "directional_rsrq_nn2_lon_mw",
    "directional_rsrq_nn2_lat",
    "directional_rsrq_nn2_lat_mw",
    "directional_rsrq_nn3_lon",
    "directional_rsrq_nn3_lon_mw",
    "directional_rsrq_nn3_lat",
    "directional_rsrq_nn3_lat_mw",
    "directional_sinr_nn0_lon",
    "directional_sinr_nn0_lon_mw",
    "directional_sinr_nn0_lat",
    "directional_sinr_nn0_lat_mw",
    "Azimuth_nn0_cell_sin",
    "Azimuth_nn0_cell_cos",
    "Azimuth_nn1_cell_sin",
    "Azimuth_nn1_cell_cos",
    "Azimuth_nn2_cell_sin",
    "Azimuth_nn2_cell_cos",
    "Azimuth_nn3_cell_sin",
    "Azimuth_nn3_cell_cos",
    "Longitude_nn1_cell",
    "Latitude_nn1_cell",
    "Longitude_nn2_cell",
    "Latitude_nn2_cell",
    "Longitude_nn3_cell",
    "Latitude_nn3_cell",
    "NR_UE_RSRP_0_log10_mw",
    "NR_UE_Nbr_RSRP_0_log10_mw",
    "NR_UE_Nbr_RSRP_1_log10_mw",
    "NR_UE_Nbr_RSRP_2_log10_mw",
    "NR_UE_Nbr_RSRP_3_log10_mw",
    "NR_UE_RSRQ_0_log10_mw",
    "NR_UE_Nbr_RSRQ_0_log10_mw",
    "NR_UE_Nbr_RSRQ_1_log10_mw",
    "NR_UE_Nbr_RSRQ_2_log10_mw",
    "NR_UE_Nbr_RSRQ_3_log10_mw",
    "NR_UE_SINR_0_log10_mw",
    "NR_UE_Pathloss_DL_0_log10_mw",
    "NR_UE_Power_Tx_PUSCH_0_log10_mw",
    "NR_UE_Power_Tx_PRACH_0_log10_mw",
    "pl_predicted_longitude",
    "pl_predicted_latitude",
    "sinr_rsrp_ratio",
    "sinr_rsrq_ratio",
    "pathloss_rsrp_ratio",
    "throughput_rsrp_ratio",
    "rsrq_rsrp_ratio",
    "sinr_pathloss_ratio",
    "pathloss_sinr_ratio",
    "throughput_sinr_ratio",
    "throughput_pathloss_ratio",
    "throughput_sinr_interaction",
    "rsrp_sinr_interaction",
    "modulation_rb_bit_potential",
    "sinr_per_meter_pl",
    "rsrp_delta",
    "rsrq_delta",
    "rach_attempt",
    "rach_ok",
    "ho_attempt",
    "ho_ok",
    "modulation_avg_encoded",
    "cce_level_encoded",
    "mcs_index",
    "intersection_2_centroid_lon",
    "intersection_2_centroid_lat",
    "NR_UE_Throughput_PDCP_DL",
    "NR_UE_Timing_Advance",
    "NR_UE_Pathloss_DL_0",
    "centroid_lon_nn0_cell_coverage",
    "centroid_lat_nn0_cell_coverage",
    "centroid_lon_nn1_cell_coverage",
    "centroid_lat_nn1_cell_coverage",
    "centroid_lon_nn2_cell_coverage",
    "centroid_lat_nn2_cell_coverage",
    "centroid_lon_nn3_cell_coverage",
    "centroid_lat_nn3_cell_coverage",
    "NR_UE_PCI_0",
    "NR_UE_Nbr_PCI_0",
)

n = 5
kf = KFold(n_splits=n, shuffle=True, random_state=23)


cell_pairs = {
    3: (13, 23, 68, None),
    13: (3, 68, None),
    23: (3, 40, None),
    30: (40, 59, None),
    40: (23, 30, None),
    48: (76,),
    59: (30, 68, 76, None),
    68: (3, 59, 76, None),
    76: (48, 59, None),
}

for cell, neighbors in cell_pairs.items():
    data_cell = data.filter(pl.col("NR_UE_PCI_0") == cell)
    for neighbor in neighbors:
        if neighbor is None:
            df = data_cell.filter(pl.col("NR_UE_Nbr_PCI_0").is_null())
        else:
            df = data_cell.filter(pl.col("NR_UE_Nbr_PCI_0") == neighbor)

        nbr_cell = "null" if neighbor is None else neighbor
        print(f"\nModel for pci {cell} and neighbor {nbr_cell}")

        param_paths = glob.glob(
            f"optuna/cell_models/{cell}_{nbr_cell}/best_params_*.pkl"
        )
        os.makedirs(f"optuna/cell_models/{cell}_{nbr_cell}/y_data", exist_ok=True)

        y = df["Latitude", "Longitude"].to_numpy()
        X = df.drop("Latitude", "Longitude", "NR_UE_PCI_0", "NR_UE_Nbr_PCI_0")

        best_score = float("inf")

        for param_path in param_paths:
            with open(param_path, "rb") as f:
                best_params = pickle.load(f)

            model = MultiOutputRegressor(
                XGBRegressor(
                    **best_params,
                    sampling_method="uniform",
                    tree_method="hist",
                    n_jobs=-1,
                    objective="reg:squarederror",
                    seed=23,
                )
            )

            result = custom_cross_val_score(
                model,
                X,
                y,
                cv=kf,
                use_imputer=False,
                scorer=haversine_np_utm,
                return_max=True,
                percentiles=[95, 99],
                return_y_pred=True,
                return_y_test=True,
                return_feature_importances=True,
            )

            scores, max_scores, percentile_scores = (
                result["scores"],
                result["max_scores"],
                result["percentiles"],
            )

            if scores.mean() < best_score:
                best_path = param_path
                best_score = scores.mean()
                final_params = best_params
                best_scores = scores
                best_max_scores = max_scores
                final_percentiles = percentile_scores
                with open(
                    f"optuna/cell_models/{cell}_{nbr_cell}/final_params.pkl", "wb"
                ) as f:
                    pickle.dump(final_params, f)
                feature_importances = []
                for fold_idx in range(n):
                    y_test = result[f"y_test_{fold_idx}"]
                    y_pred = result[f"y_pred_{fold_idx}"]
                    pl.DataFrame(
                        {
                            "y_test": y_test,
                            "y_pred": y_pred,
                        }
                    ).write_parquet(
                        f"optuna/cell_models/{cell}_{nbr_cell}/y_data/fold_{fold_idx}.parquet"
                    )

                    feature_importances.extend(
                        [
                            {
                                "fold": fold_idx,
                                "target": "Latitude",
                                "feature": feature,
                                "importance": importance,
                            }
                            for feature, importance in result[
                                f"importances_lat_{fold_idx}"
                            ].items()
                        ]
                    )

                    feature_importances.extend(
                        [
                            {
                                "fold": fold_idx,
                                "target": "Longitude",
                                "feature": feature,
                                "importance": importance,
                            }
                            for feature, importance in result[
                                f"importances_lon_{fold_idx}"
                            ].items()
                        ]
                    )

                pl.DataFrame(feature_importances).write_parquet(
                    f"optuna/cell_models/{cell}_{nbr_cell}/feature_importances.parquet"
                )

        # print(f"Best Param Path: {param_path}")

        print(
            f"Mean of Fold Mean = {best_scores.mean():.4f} | Max of Fold Mean = {max(best_scores):.4f} | Mean of Fold Max = {best_max_scores.mean():.4f} | Max of 95th = {max(final_percentiles[95]):.4f} | Max of 99th = {max(final_percentiles[99]):.4f} | Max of Fold Max = {max(best_max_scores):.4f}"
        )

        with open("model_scores/model_scores_2_cells.md", "a") as f:
            f.write(
                f"| {cell} | {nbr_cell} | {best_scores.mean():.4f} | {max(best_scores):.4f} | {best_max_scores.mean():.4f} | {max(best_max_scores):.4f} |\n"
            )
