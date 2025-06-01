import numpy as np
import pandas as pd
import polars as pl
import matplotlib.pyplot as plt
import geopandas as gpd
from path_config import PathConfig
from pathlib import Path
from shapely.geometry import Point, Polygon

paths = PathConfig()


def calculate_rsrp_and_heatmap(
    grid_data: pd.DataFrame,
    bs_longitude: float,
    bs_latitude: float,
    bs_height: float = 30,
    ue_height: float = 0,
    azimuth: float = 0,
    digital_downtilt: float = 5,
    ssb_power: float = 17.91,
    carrier_freq_mhz: float = 3500,
    vertical_bw_deg: float = 10,
    horizontal_bw_deg: float = 65,
    sidelobe_suppression_db: float = 16,
    front_back_ratio_db: float = 25,
    plot_heatmap: bool = False,
    path_loss_strategy: str = "FSPL",
    create_parquet_file: bool = False,
    path=paths._processed_coverage_dir,
    grid_spacing="unknown_grid_spacing_",
):
    dx = (
        (grid_data["Longitude"] - bs_longitude)
        * 111320
        * np.cos(np.radians(bs_latitude))
    )
    dy = (grid_data["Latitude"] - bs_latitude) * 111320
    dz = ue_height - bs_height

    distance_3d = np.sqrt(dx**2 + dy**2 + dz**2)
    distance_2d = np.sqrt(dx**2 + dy**2)

    horizontal_angle = (np.degrees(np.arctan2(dx, dy)) - azimuth) % 360
    horizontal_angle = np.where(
        horizontal_angle > 180, 360 - horizontal_angle, horizontal_angle
    )

    vertical_angle = np.degrees(np.arctan2(-dz, distance_2d)) - digital_downtilt

    def gain(
        horizontal_bw_deg,
        vertical_bw_deg,
        horizontal_angle,
        vertical_angle,
        sidelobe_suppression_db,
        front_back_ratio_db,
    ):
        directivity = 41253 / (horizontal_bw_deg * vertical_bw_deg)
        half_hbwd = horizontal_bw_deg / 2
        half_vbwd = vertical_bw_deg / 2

        max_gain = 10 * np.log10(directivity)

        gain_horizontal = np.maximum(
            -12 * (horizontal_angle / half_hbwd) ** 2, -front_back_ratio_db
        )
        gain_vertical = np.maximum(
            -12 * (vertical_angle / half_vbwd) ** 2, -sidelobe_suppression_db
        )

        return max_gain + gain_horizontal + gain_vertical

    total_gain = gain(
        horizontal_bw_deg,
        vertical_bw_deg,
        horizontal_angle,
        vertical_angle,
        sidelobe_suppression_db,
        front_back_ratio_db,
    )

    def fspl(distance_3d, carrier_freq_mhz):
        d = np.maximum(distance_3d, 1) / 1000
        return 20 * np.log10(d) + 20 * np.log10(carrier_freq_mhz) + 32.44

    def gpp_umi_nlos(distance_3d, carrier_freq_mhz, ue_height):
        d = np.maximum(distance_3d, 10)
        return (
            13.54
            + 39.08 * np.log10(d)
            + 20 * np.log10(carrier_freq_mhz)
            - 0.6 * (ue_height - 1.5)
        )

    def gpp_umi_los(distance_3d, carrier_freq_mhz, bs_height, ue_height):
        if ue_height == 0:
            ue_height = 1.5  # yükseklik girilmediğinde fonskiyonun patlamaması lokasyon yüksekliği 3gpp için yükseklik kabul edilen 1.5m ile değiştiriliyor.

        dbp = (bs_height * ue_height * carrier_freq_mhz * (1e6)) / (3e8)
        pl = np.where(
            distance_3d <= dbp,
            fspl(distance_3d, carrier_freq_mhz),
            fspl(dbp, carrier_freq_mhz)
            + 40 * np.log10(np.maximum(distance_3d / dbp, 1e-9)),
        )
        return pl

    if path_loss_strategy == "FSPL":
        path_loss = fspl(distance_3d, carrier_freq_mhz)
    elif path_loss_strategy == "3GPP_UMi_NLOS":
        path_loss = gpp_umi_nlos(distance_3d, carrier_freq_mhz, ue_height)
    elif path_loss_strategy == "3GPP_UMi_LOS":
        path_loss = gpp_umi_los(distance_3d, carrier_freq_mhz, bs_height, ue_height)

    elif path_loss_strategy == "ALL":
        grid_data["RSRP_dBm_FSPL"] = (
            ssb_power + total_gain - fspl(distance_3d, carrier_freq_mhz)
        )
        grid_data["RSRP_dBm_3GPP_UMi_NLOS"] = (
            ssb_power
            + total_gain
            - gpp_umi_nlos(distance_3d, carrier_freq_mhz, ue_height)
        )
        grid_data["RSRP_dBm_3GPP_UMi_LOS"] = (
            ssb_power
            + total_gain
            - gpp_umi_los(distance_3d, carrier_freq_mhz, bs_height, ue_height)
        )

        if create_parquet_file:
            grid_data.to_parquet(path / f"calculated_{grid_spacing}m_coverage.parquet")
        return grid_data

    rsrp = ssb_power + total_gain - path_loss
    grid_data["RSRP_dBm"] = rsrp

    if plot_heatmap:
        plt.figure(figsize=(10, 8))
        sc = plt.scatter(
            grid_data["Longitude"], grid_data["Latitude"], c=rsrp, cmap="viridis", s=10
        )
        plt.colorbar(sc, label="dBm")
        plt.title("RSRP Heatmap")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.grid(True)
        plt.show()

    if create_parquet_file:
        grid_data.to_parquet(path / f"calculated_{grid_spacing}m_coverage.parquet")

    return grid_data


def create_grid_data(
    border_data,
    grid_spacing,
    path=paths._processed_harita_dir,
    keep_geometry=False,
    create_parquet_file=False,
):
    if Path(path / f"grid_{grid_spacing}m_data.parquet").exists():
        return pd.read_parquet(path / f"grid_{grid_spacing}m_data.parquet")

    utm_crs = "EPSG:32635"
    crs = "EPSG:4326"
    border_data = border_data.to_crs(utm_crs)

    minx, miny, maxx, maxy = border_data.total_bounds
    x_coords = np.arange(minx, maxx, grid_spacing)
    y_coords = np.arange(miny, maxy, grid_spacing)
    grid_points = [Point(x, y) for x in x_coords for y in y_coords]

    grid_gdf = gpd.GeoDataFrame(geometry=grid_points, crs=utm_crs).to_crs(utm_crs)
    border_polygon = Polygon(border_data.geometry.iloc[0])

    grid_gdf = grid_gdf[grid_gdf.geometry.within(border_polygon)]
    grid_gdf = grid_gdf.to_crs(crs)

    if not keep_geometry:
        grid_gdf = pd.DataFrame(
            np.column_stack((grid_gdf.geometry.x, grid_gdf.geometry.y))
        ).rename({0: "Longitude", 1: "Latitude"}, axis=1)

    if create_parquet_file:
        grid_gdf.to_parquet(path / f"grid_{grid_spacing}m_data.parquet")

    return grid_gdf


def create_calculate_grid_rsrp(
    bs_data,
    border_data,
    path_loss_strategy,
    grid_spacing,
    path=paths._processed_coverage_dir,
    create_file=False,
):
    if Path(path / f"calculated_grid_rsrp_{grid_spacing}m_data.parquet").exists():
        return pd.read_parquet(
            path / f"calculated_grid_rsrp_{grid_spacing}m_data.parquet"
        )

    grid_data = create_grid_data(
        border_data=border_data,
        grid_spacing=grid_spacing,
        create_parquet_file=False,
    )

    for idx, row in bs_data.iterrows():
        if row["MIMO"] == "64T64R":
            sidelobe_suppression_db = 16
        else:
            sidelobe_suppression_db = 12

        grid_data_calculations = calculate_rsrp_and_heatmap(
            grid_data=grid_data.loc[:, ["Longitude", "Latitude"]],
            bs_longitude=row["Longitude"],
            bs_latitude=row["Latitude"],
            bs_height=row["Height"],
            azimuth=row["Azimuth"],
            vertical_bw_deg=row["Vertical_Beamwidth"],
            sidelobe_suppression_db=sidelobe_suppression_db,
            path_loss_strategy=path_loss_strategy,
            create_parquet_file=False,
            grid_spacing=grid_spacing,
        )

        grid_data_calculations = grid_data_calculations.add_suffix(f"_PCI_{row['PCI']}")

        coordinate_cols = [f"Longitude_PCI_{row['PCI']}", f"Latitude_PCI_{row['PCI']}"]

        grid_data = grid_data.merge(
            grid_data_calculations,
            left_on=["Longitude", "Latitude"],
            right_on=coordinate_cols,
            how="left",
        )
        grid_data = grid_data.drop(columns=coordinate_cols)

    if create_file:
        grid_data.to_parquet(
            path / f"calculated_grid_rsrp_{grid_spacing}m_data.parquet"
        )

    return grid_data


def create_measured_signal_coverage(
    data: pl.DataFrame,
    bs_data: pl.DataFrame,
    group_by_loc: bool = True,
    group_by_time: bool = False,
    fill_nan: float = -500.0,
    create_file: bool = False,
    path: PathConfig = paths._processed_measured_coverage_dir,
):
    pci_cols = [col for col in data.columns if "PCI" in col]
    rsrp_cols = [col for col in data.columns if "RSRP" in col]
    select_cols = pci_cols + rsrp_cols + ["Longitude", "Latitude"]

    if group_by_time:
        select_cols.append("Time")
        data = (
            data.select(select_cols)
            .group_by("Time")
            .agg(
                pl.col(rsrp_cols).mean(),
                pl.col(pci_cols).filter(pl.col(pci_cols).is_not_null()).mode().last(),
                pl.col(["Longitude", "Latitude"]).filter(pl.col(["Longitude", "Latitude"]).is_not_null()).mode().last()
            )
        )

    if group_by_loc:
        data = (
            data.select(select_cols)
            .group_by(["Longitude", "Latitude"])
            .agg(
                pl.col(rsrp_cols).mean(),
                pl.col(pci_cols).filter(pl.col(pci_cols).is_not_null()).mode().last(),
            )
        )
    column_names = ["Latitude", "Longitude"] + [str(pci) for pci in bs_data["PCI"]]

    all_pcis = set()
    for row in data.iter_rows(named=True):
        for pci_col in pci_cols:
            pci = row[pci_col]
            if pci is not None:
                all_pcis.add(str(pci))

    # print(f"ALL PCIS: {sorted(all_pcis)}")

    schema = {"Longitude": pl.Float64, "Latitude": pl.Float64}

    for pci in all_pcis:
        schema[pci] = pl.Float64

    signal_dict_list = []

    for row in data.iter_rows(named=True):
        temp_dict = {"Longitude": row["Longitude"], "Latitude": row["Latitude"]}

        for pci in all_pcis:
            temp_dict[pci] = np.nan

        for pci_col, rsrp_col in zip(pci_cols, rsrp_cols):
            pci = row[pci_col]
            if pci is not None:
                rsrp_value = row[rsrp_col]
                if rsrp_value is not None:
                    temp_dict[str(pci)] = float(rsrp_value)

        signal_dict_list.append(temp_dict)

    signal_data = pl.DataFrame(signal_dict_list, schema=schema)

    signal_data = signal_data.select(column_names).with_columns(
        pl.all().cast(pl.Float64, strict=False)
    )
    # print(f"DataFrame shape: {signal_data.shape}")
    # print(f"Columns: {signal_data.columns}")
    signal_data = signal_data.fill_nan(fill_nan)

    if create_file:
        signal_data.write_parquet(path / "measured_signal_coverage.parquet")

    return signal_data


if __name__ == "__main__":
    border = gpd.read_file(paths.border_path)
    kabinets = pd.read_csv(paths.kabinets_path)
    dl_data = pl.read_parquet(
        paths._processed_saha_olcum_dir / "merged_data_dl.parquet"
    )
    """
    grid_data = create_calculate_grid_rsrp(
        bs_data=kabinets,
        border_data=border,
        path_loss_strategy="ALL",
        grid_spacing=1,
        create_file=True,
    )
    """
    
    create_measured_signal_coverage(
        dl_data, kabinets, group_by_loc=True, group_by_time=False, create_file=True
    )
