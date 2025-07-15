# hyperparameter tuning for cell id combination -3- specific models
import os
from pathlib import Path
import polars as pl
import pickle
from sklearn.multioutput import MultiOutputRegressor
import optuna
import webbrowser
from pyproj import Transformer
from datetime import datetime
from xgboost import XGBRegressor
from cell_util.ml import custom_cross_val_score
from calculations_util.distance import haversine_np_utm
from sklearn.model_selection import KFold
from pyproj import Geod

geod = Geod(ellps="WGS84")

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
    "NR_UE_Nbr_PCI_1"
)

kf = KFold(n_splits=5, shuffle=True, random_state=23)


cell_combinations= [
    [3, 13, None],
    [3, 13, 23],
    [3, 13, 68],
    [3, 23, None],
    [3, 23, 68],
    [3, 68, None],
    [13, 3, None],
    [13, 68, None],
    [23, 3, 40],
    [23, 40, None],
    [30, 40, None],
    [30, 59, None],
    [40, 23, None],
    [40, 30, None],
    [48, 76, None],
    [59, 30, None],
    [59, 30, 76],
    [59, 68, None],
    [59, 68, 76],
    [59, 76, None],
    [68, 3, None],
    [68, 3, 13],
    [68, 3, 59],
    [68, 59, None],
    [68, 59, 76],
    [68, 76, None],
    [76, 48, None],
    [76, 59, 68],
]


for combination in cell_combinations:
    df = data.filter(pl.col("NR_UE_PCI_0") == combination[0]) 
    cell = combination[0]
    if combination[1] is None:
        df = df.filter(pl.col("NR_UE_Nbr_PCI_0").is_null())
        nbr_cell_0 = "null"
    else:
        df = df.filter(pl.col("NR_UE_Nbr_PCI_0") == combination[1])
        nbr_cell_0 = combination[1]

    if combination[2] is None:
        df = df.filter(pl.col("NR_UE_Nbr_PCI_1").is_null())
        nbr_cell_1 = "null"
    else:
        df = df.filter(pl.col("NR_UE_Nbr_PCI_1") == combination[2])
        nbr_cell_1 = combination[2]

    print(f"\nModel for pci {cell} and neighbors {nbr_cell_0}, {nbr_cell_1}")

    y = df["Latitude", "Longitude"].to_numpy()
    X = df.drop("Latitude", "Longitude", "NR_UE_PCI_0", "NR_UE_Nbr_PCI_0", "NR_UE_Nbr_PCI_1").to_numpy()

    def objective(trial):
        n_estimators = trial.suggest_int("n_estimators", 3, 500)
        learning_rate = trial.suggest_float("learning_rate", 5e-3, 0.3)
        gamma = trial.suggest_float("gamma", 0, 8)
        max_depth = trial.suggest_int("max_depth", 3, 8)
        reg_alpha = trial.suggest_float("reg_alpha", 0.0, 0.4)
        reg_lambda = trial.suggest_float("reg_lambda", 0.0, 0.4)
        subsample = trial.suggest_float("subsample", 0.5, 1.0)
        colsample_bytree = trial.suggest_float("colsample_bytree", 0.5, 1.0)
        min_child_weight = trial.suggest_int("min_child_weight", 1, 5)

        model = MultiOutputRegressor(
            XGBRegressor(
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                gamma=gamma,
                max_depth=max_depth,
                reg_alpha=reg_alpha,
                reg_lambda=reg_lambda,
                subsample=subsample,
                colsample_bytree=colsample_bytree,
                min_child_weight=min_child_weight,
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
            )

        scores, max_scores = result["scores"], result["max_scores"]

        print(scores)
        print(max_scores)

        trial.set_user_attr("max_of_max_scores", max(max_scores))
        trial.set_user_attr("mean_of_max_scores", max_scores.mean())
        return scores.mean()

        # study = optuna.create_study(irection="minimize", sampler=optuna.samplers.RandomSampler(seed=23))

    study = optuna.create_study(
            direction="minimize",
            sampler=optuna.samplers.TPESampler(n_startup_trials=300, seed=23),
        )

    study.optimize(objective, n_trials=600, n_jobs=5)
    best_trial = study.best_trial
    print(f"\nBest Parameters:\n{best_trial.params}")
    print(f"Best Score Mean: {best_trial.value:.4f}")
    print(
            f"Best Score Mean of Max: {best_trial.user_attrs.get('mean_of_max_scores'):.4f}"
    )
    print(
        f"Best Score Max of Max: {best_trial.user_attrs.get('max_of_max_scores'):.4f}"
    )

    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    os.makedirs(f"optuna/cell_models/{cell}_{nbr_cell_0}_{nbr_cell_1}", exist_ok=True)
    os.makedirs(f"optuna/plots/cell_model_plots/{cell}_{nbr_cell_0}_{nbr_cell_1}", exist_ok=True)
    os.makedirs(f"optuna/trial-data/cell_models/{cell}_{nbr_cell_0}_{nbr_cell_1}", exist_ok=True)

    with open(f"optuna/cell_models/{cell}_{nbr_cell_0}_{nbr_cell_1}/best_params_{timestamp}.pkl", "wb") as f:
        pickle.dump(best_trial.params, f)

    study.trials_dataframe().to_csv(
        f"optuna/trial-data/cell_models/{cell}_{nbr_cell_0}_{nbr_cell_1}/optuna_trials_{timestamp}.csv"
    )

    fig_hist = optuna.visualization.plot_optimization_history(study)
    fig_hist.write_html(
        f"optuna/plots/cell_model_plots/{cell}_{nbr_cell_0}_{nbr_cell_1}/optimization_history_{timestamp}.html"
    )

    fig_imp = optuna.visualization.plot_param_importances(study)
    fig_imp.write_html(
        f"optuna/plots/cell_model_plots/{cell}_{nbr_cell_0}_{nbr_cell_1}/param_importances_{timestamp}.html"
    )

    fig_slice = optuna.visualization.plot_slice(
        study, params=list(study.best_trial.params.keys())
    )
    fig_slice.write_html(
        f"optuna/plots/cell_model_plots/{cell}_{nbr_cell_0}_{nbr_cell_1}/param_slice_{timestamp}.html"
    )

    open_webbrowser = False
    if open_webbrowser:
        webbrowser.open(
            Path(
                    f"optuna/plots/cell_model_plots/{cell}_{nbr_cell_0}_{nbr_cell_1}/optimization_history_{timestamp}.html"
                )
                .resolve()
                .as_uri()
            )
        webbrowser.open(
                Path(
                    f"optuna/plots/cell_model_plots/{cell}_{nbr_cell_0}_{nbr_cell_1}/param_importances_{timestamp}.html"
                )
                .resolve()
                .as_uri()
            )
        webbrowser.open(
                Path(f"optuna/plots/cell_model_plots/{cell}_{nbr_cell_0}_{nbr_cell_1}/param_slice_{timestamp}.html")
                .resolve()
                .as_uri()
            )
