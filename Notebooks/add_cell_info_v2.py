import polars as pl
import geopandas as gpd
from pyproj import Geod

geod = Geod(ellps="WGS84")

cell_data = pl.read_parquet("data/parquet/cell_info.parquet")
df = pl.read_parquet("data/parquet/processed/dl.with_cluster.parquet")
coverages = gpd.read_parquet("data/parquet/coverages/coverages.parquet")
intersections_2 = gpd.read_parquet(
    "data/parquet/coverages/coverages_intersect_2.parquet"
)

coverages = pl.DataFrame(
    {
        "centroid_longitude": coverages.clipped_coverage_centroid.x,
        "centroid_latitude": coverages.clipped_coverage_centroid.y,
        "PCI": coverages["PCI"],
    }
)

intersections_2 = pl.DataFrame(
    {
        "sorted_cell_pairs": intersections_2["sorted_cell_pairs"],
        "intersection_2_convex_hull": intersections_2["convex_hull"],
        "intersection_2_area_m2": intersections_2["area_m2"],
        "intersection_2_centroid_lon": intersections_2["centroid"].x,
        "intersection_2_centroid_lat": intersections_2["centroid"].y,
    }
)

pci_cols = [col for col in df.columns if "PCI" in col]

for i, pci_col in enumerate(pci_cols):
    df = df.join(
        cell_data.select(
            pl.col("Longitude"),
            pl.col("Latitude"),
            pl.col("Azimuth [°]").radians().sin().alias(f"Azimuth_nn{i}_cell_sin"),
            pl.col("Azimuth [°]").radians().cos().alias(f"Azimuth_nn{i}_cell_cos"),
            pl.when(pl.col("MIMO") == "64T64R").then(64)
            .when(pl.col("MIMO") == "32T32R").then(32)
            .otherwise(None)
            .alias(f"mimo_nn{i}_cell"),
            "PCI",
        ),
        left_on=pci_col,
        right_on="PCI",
        how="left",
        suffix=f"_nn{i}_cell",
    )

    # joining connected cell's azimuth in degrees, which is going to be used for geod fwd function below.
    if i == 0:
        df = df.join(
            cell_data.select(
                pl.col("Azimuth [°]").alias("Azimuth_nn0_cell"),
                "PCI",
            ),
            left_on=pci_col,
            right_on="PCI",
            how="left",
        )

    df = df.join(
        coverages.select(
            pl.col("centroid_longitude").alias(f"centroid_lon_nn{i}_cell_coverage"),
            pl.col("centroid_latitude").alias(f"centroid_lat_nn{i}_cell_coverage"),
            "PCI",
        ),
        left_on=pci_col,
        right_on="PCI",
        how="left",
    )
df = (
    df.with_columns(
        pl.concat_list([pl.col("NR_UE_PCI_0"), pl.col("NR_UE_Nbr_PCI_0")])
        .list.sort()
        .alias("sorted_cell_pairs")
    )
    .join(intersections_2, how="left", on="sorted_cell_pairs")
    .drop("sorted_cell_pairs")
)

ue_lon, ue_lat, _ = geod.fwd(
    lons=df["Longitude_nn0_cell"],
    lats=df["Latitude_nn0_cell"],
    az=df["Azimuth_nn0_cell"],
    #dist=df["distance"], old column name
    dist=df["pl_distance"],
)

df = df.with_columns(
    [pl.Series("pl_predicted_longitude", ue_lon), pl.Series("pl_predicted_latitude", ue_lat)
    ]
)


"""
old df column names

df = df.with_columns([
    (pl.col("spectral_efficiency") / pl.col("mimo_nn0_cell")).alias("efficiency_per_antenna"),
    (pl.col("m_NR_UE_SINR_0") / pl.col("mimo_nn0_cell")).alias("sinr_per_antenna"),
    (pl.col("mimo_nn0_cell") / (pl.col("distance") + 1)).alias("mimo_distance_ratio"),
    (pl.col("mimo_nn0_cell") * pl.col("m_App_Throughput_DL")).alias("mimo_throughput_potential"),
    (pl.col("signal_loss_ratio") * pl.col("mimo_nn0_cell")).alias("scaled_loss_ratio"),
    (pl.col("Azimuth_nn0_cell_cos") * -pl.col("m_NR_UE_RSRP_0")).alias("directional_rsrp_nn0_lon"),
    (pl.col("Azimuth_nn0_cell_sin") * -pl.col("m_NR_UE_RSRP_0")).alias("directional_rsrp_nn0_lat"),
    (pl.col("Azimuth_nn1_cell_cos") * -pl.col("m_NR_UE_Nbr_RSRP_1")).alias("directional_rsrp_nn1_lon"),
    (pl.col("Azimuth_nn1_cell_sin") * -pl.col("m_NR_UE_Nbr_RSRP_1")).alias("directional_rsrp_nn1_lat"),
    (pl.col("Azimuth_nn2_cell_cos") * -pl.col("m_NR_UE_Nbr_RSRP_2")).alias("directional_rsrp_nn2_lon"),
    (pl.col("Azimuth_nn2_cell_sin") * -pl.col("m_NR_UE_Nbr_RSRP_2")).alias("directional_rsrp_nn2_lat"),
    (pl.col("Azimuth_nn3_cell_cos") * -pl.col("m_NR_UE_Nbr_RSRP_3")).alias("directional_rsrp_nn3_lon"),
    (pl.col("Azimuth_nn3_cell_sin") * -pl.col("m_NR_UE_Nbr_RSRP_3")).alias("directional_rsrp_nn3_lat"),
])
"""

df = df.with_columns([
    (pl.col("spectral_efficiency") / pl.col("mimo_nn0_cell")).alias("efficiency_per_antenna"),
    (pl.col("NR_UE_SINR_0") / pl.col("mimo_nn0_cell")).alias("sinr_per_antenna"),
    (pl.col("mimo_nn0_cell") / (pl.col("pl_distance") + 1)).alias("mimo_distance_ratio"),
    (pl.col("mimo_nn0_cell") * pl.col("App_Throughput_DL")).alias("mimo_throughput_potential"),
    (pl.col("signal_loss_ratio") * pl.col("mimo_nn0_cell")).alias("scaled_loss_ratio"),
    (pl.col("Azimuth_nn0_cell_cos") * -pl.col("NR_UE_RSRP_0")).alias("directional_rsrp_nn0_lon"),
    (pl.col("Azimuth_nn0_cell_sin") * -pl.col("NR_UE_RSRP_0")).alias("directional_rsrp_nn0_lat"),
    (pl.col("Azimuth_nn1_cell_cos") * -pl.col("NR_UE_Nbr_RSRP_1")).alias("directional_rsrp_nn1_lon"),
    (pl.col("Azimuth_nn1_cell_sin") * -pl.col("NR_UE_Nbr_RSRP_1")).alias("directional_rsrp_nn1_lat"),
    (pl.col("Azimuth_nn2_cell_cos") * -pl.col("NR_UE_Nbr_RSRP_2")).alias("directional_rsrp_nn2_lon"),
    (pl.col("Azimuth_nn2_cell_sin") * -pl.col("NR_UE_Nbr_RSRP_2")).alias("directional_rsrp_nn2_lat"),
    (pl.col("Azimuth_nn3_cell_cos") * -pl.col("NR_UE_Nbr_RSRP_3")).alias("directional_rsrp_nn3_lon"),
    (pl.col("Azimuth_nn3_cell_sin") * -pl.col("NR_UE_Nbr_RSRP_3")).alias("directional_rsrp_nn3_lat"),
])

df.write_parquet("data/parquet/processed/dl.with_cluster_cell_info.parquet")
